import redis
import time
import os
import signal
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

running = True

def signal_handler(signum, frame):
    global running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def process_job(job_id):
    logger.info(f"Processing job {job_id}")
    redis_client.hset(f"job:{job_id}", "status", "processing")
    time.sleep(2)  # simulate work
    redis_client.hset(f"job:{job_id}", "status", "completed")
    logger.info(f"Completed job: {job_id}")

def main():
    logger.info("Worker started, waiting for jobs...")
    while running:
        try:
            # Write heartbeat file for health check
            open("/tmp/worker_healthy", "w").close()
            
            job = redis_client.brpop("job_queue", timeout=1)
            if job:
                _, job_id = job
                process_job(job_id)
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error processing job: {e}")
    
    logger.info("Worker shutdown complete")
    sys.exit(0)

if __name__ == "__main__":
    main()