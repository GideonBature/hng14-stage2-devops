from fastapi import FastAPI
import redis
import uuid
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)


@app.get("/health")
def health_check():
    try:
        redis_client.ping()
        return {"status": "healthy"}
    except redis.ConnectionError:
        return {"status": "unhealthy", "error": "redis connection failed"}


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    redis_client.lpush("job_queue", job_id)
    redis_client.hset(f"job:{job_id}", mapping={"status": "queued"})
    logger.info(f"Created job: {job_id}")
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = redis_client.hget(f"job:{job_id}", "status")
    if not status:
        return {"error": "not found"}
    return {"job_id": job_id, "status": status}
