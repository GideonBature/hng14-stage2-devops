import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("main.redis_client") as mock:
        mock.ping.return_value = True
        mock.hset.return_value = True
        mock.lpush.return_value = 1
        mock.hget.return_value = "completed"
        yield mock


def test_health_check_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_healthy_status():
    response = client.get("/health")
    assert response.json()["status"] == "healthy"


def test_health_check_returns_json_content_type():
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


def test_create_job_returns_200():
    response = client.post("/jobs")
    assert response.status_code == 200


def test_create_job_returns_job_id():
    response = client.post("/jobs")
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


def test_create_job_pushes_to_redis(mock_redis):
    client.post("/jobs")
    assert mock_redis.lpush.called
    args = mock_redis.lpush.call_args[0]
    assert args[0] == "job_queue"


def test_create_job_stores_status_in_redis(mock_redis):
    client.post("/jobs")
    assert mock_redis.hset.called


def test_get_job_returns_200():
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200


def test_get_job_returns_status():
    response = client.get("/jobs/test-job-123")
    data = response.json()
    assert "status" in data
    assert data["status"] == "completed"


def test_get_job_returns_job_id_in_response():
    response = client.get("/jobs/test-job-123")
    data = response.json()
    assert data["job_id"] == "test-job-123"


def test_get_job_queries_correct_redis_key(mock_redis):
    client.get("/jobs/abc-123")
    mock_redis.hget.assert_called_with("job:abc-123", "status")


def test_health_check_handles_redis_failure():
    import redis
    with patch("main.redis_client") as mock:
        mock.ping.side_effect = redis.ConnectionError("connection refused")
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "unhealthy"
