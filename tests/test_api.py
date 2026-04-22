import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
import redis

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis client for all tests."""
    with patch("main.redis_client") as mock:
        mock.ping.return_value = True
        mock.hset.return_value = True
        mock.lpush.return_value = 1
        mock.hget.return_value = "completed"
        yield mock


def test_health_check_returns_healthy():
    """Test that health check returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_job_returns_job_id():
    """Test that creating a job returns a valid job ID."""
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


def test_create_job_pushes_to_redis_queue(mock_redis):
    """Test that job creation pushes to Redis queue."""
    client.post("/jobs")
    assert mock_redis.lpush.called
    args = mock_redis.lpush.call_args[0]
    assert args[0] == "job_queue"


def test_create_job_sets_status_in_redis(mock_redis):
    """Test that job creation sets status in Redis hash."""
    client.post("/jobs")
    assert mock_redis.hset.called


def test_get_job_returns_status(mock_redis):
    """Test that getting a job returns its status."""
    response = client.get("/jobs/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "completed"
    mock_redis.hget.assert_called_with("job:test-job-123", "status")


def test_get_job_not_found(mock_redis):
    """Test that getting a non-existent job returns error."""
    mock_redis.hget.return_value = None
    response = client.get("/jobs/non-existent")
    assert response.status_code == 200
    assert "error" in response.json()


def test_health_check_handles_redis_failure():
    """Test that health check handles Redis connection failure."""
    with patch("main.redis_client") as mock:
        mock.ping.side_effect = redis.ConnectionError("connection refused")
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "unhealthy"
