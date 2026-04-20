# Bug Fixes Documentation

This document lists all bugs found in the original codebase and the fixes applied.

## Summary of Issues Found

### 1. API Service (`api/main.py`)

#### Issue 1.1: Hardcoded Redis Host
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** Redis host was hardcoded to "localhost", which won't work in Docker containers where services communicate over a network.
- **Fix:** Changed to use environment variables with sensible defaults:
  ```python
  REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
  REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
  REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
  ```

#### Issue 1.2: Missing Health Check Endpoint
- **File:** `api/main.py`
- **Line:** N/A (missing)
- **Problem:** No health check endpoint available for Docker and orchestration tools to verify service health.
- **Fix:** Added `/health` endpoint that checks Redis connectivity:
  ```python
  @app.get("/health")
  def health_check():
      try:
          redis_client.ping()
          return {"status": "healthy"}
      except redis.ConnectionError:
          return {"status": "unhealthy", "error": "redis connection failed"}
  ```

#### Issue 1.3: Inefficient Redis Operations
- **File:** `api/main.py`
- **Line:** 13-14
- **Problem:** Using separate calls for hset operations and not using decode_responses.
- **Fix:** Used `decode_responses=True` in Redis client and used `mapping` parameter for hset:
  ```python
  redis_client.hset(f"job:{job_id}", mapping={"status": "queued"})
  ```

#### Issue 1.4: Inconsistent Queue Name
- **File:** `api/main.py`
- **Line:** 13
- **Problem:** Queue name "job" was inconsistent with worker expectations.
- **Fix:** Changed to "job_queue" for consistency with worker.

#### Issue 1.5: Missing Logging
- **File:** `api/main.py`
- **Line:** N/A (missing)
- **Problem:** No logging for debugging and monitoring.
- **Fix:** Added proper logging configuration and log statements.

---

### 2. Worker Service (`worker/worker.py`)

#### Issue 2.1: Hardcoded Redis Host
- **File:** `worker/worker.py`
- **Line:** 6
- **Problem:** Redis host was hardcoded to "localhost", which won't work in Docker containers.
- **Fix:** Changed to use environment variables:
  ```python
  REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
  REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
  REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
  ```

#### Issue 2.2: No Graceful Shutdown
- **File:** `worker/worker.py`
- **Line:** 14-18
- **Problem:** Infinite loop with no signal handling for graceful shutdown. When Docker sends SIGTERM, the worker would be forcefully killed, potentially losing jobs.
- **Fix:** Added signal handlers for SIGTERM and SIGINT:
  ```python
  running = True

  def signal_handler(signum, frame):
      global running
      logger.info(f"Received signal {signum}, shutting down gracefully...")
      running = False

  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT, signal_handler)
  ```

#### Issue 2.3: No Error Handling
- **File:** `worker/worker.py`
- **Line:** 14-18
- **Problem:** No try-catch blocks for Redis connection errors or job processing errors.
- **Fix:** Wrapped job processing in try-catch with proper logging:
  ```python
  while running:
      try:
          job = redis_client.brpop("job_queue", timeout=1)
          if job:
              _, job_id = job
              process_job(job_id)
      except redis.ConnectionError as e:
          logger.error(f"Redis connection error: {e}")
          time.sleep(1)
      except Exception as e:
          logger.error(f"Error processing job: {e}")
  ```

#### Issue 2.4: Missing Processing Status
- **File:** `worker/worker.py`
- **Line:** 9-11
- **Problem:** Job status jumps directly from "queued" to "completed" without "processing" state.
- **Fix:** Added intermediate status update:
  ```python
  def process_job(job_id):
      logger.info(f"Processing job {job_id}")
      redis_client.hset(f"job:{job_id}", "status", "processing")
      time.sleep(2)  # simulate work
      redis_client.hset(f"job:{job_id}", "status", "completed")
      logger.info(f"Completed job: {job_id}")
  ```

#### Issue 2.5: Inconsistent Queue Name
- **File:** `worker/worker.py`
- **Line:** 15
- **Problem:** Queue name "job" was inconsistent with API.
- **Fix:** Changed to "job_queue" for consistency.

#### Issue 2.6: Missing Logging
- **File:** `worker/worker.py`
- **Line:** N/A (missing)
- **Problem:** Using print statements instead of proper logging.
- **Fix:** Replaced print with proper logging module.

---

### 3. Frontend Service (`frontend/app.js`)

#### Issue 3.1: Hardcoded API URL
- **File:** `frontend/app.js`
- **Line:** 6
- **Problem:** API URL was hardcoded to "http://localhost:8000", which won't work in Docker.
- **Fix:** Changed to use environment variables with fallback:
  ```javascript
  const API_URL = process.env.API_URL || 'http://localhost:8000';
  const PORT = process.env.FRONTEND_PORT || 3000;
  ```

#### Issue 3.2: Missing Health Check Endpoint
- **File:** `frontend/app.js`
- **Line:** N/A (missing)
- **Problem:** No health check endpoint for Docker.
- **Fix:** Added `/health` endpoint that checks API connectivity:
  ```javascript
  app.get('/health', async (req, res) => {
    try {
      await axios.get(`${API_URL}/health`);
      res.json({ status: 'healthy', api: 'connected' });
    } catch (err) {
      res.status(503).json({ status: 'unhealthy', api: 'disconnected', error: err.message });
    }
  });
  ```

#### Issue 3.3: Poor Error Handling
- **File:** `frontend/app.js`
- **Line:** 15-17, 24-26
- **Problem:** Generic error messages with no logging or details.
- **Fix:** Added console.error logging and more descriptive error messages:
  ```javascript
  } catch (err) {
    console.error('Error submitting job:', err.message);
    res.status(500).json({ error: "Failed to submit job", details: err.message });
  }
  ```

#### Issue 3.4: Hardcoded Port and Host
- **File:** `frontend/app.js`
- **Line:** 29-31
- **Problem:** Port and host were hardcoded.
- **Fix:** Made port configurable and bound to 0.0.0.0 for Docker:
  ```javascript
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Frontend running on port ${PORT}`);
    console.log(`API URL: ${API_URL}`);
  });
  ```

---

### 4. Configuration Issues

#### Issue 4.1: Committed .env File with Secrets
- **File:** `api/.env`
- **Line:** 1-2
- **Problem:** `.env` file containing secrets was committed to the repository.
- **Fix:** 
  1. Added `.env` to `.gitignore`
  2. Removed the file from git tracking
  3. Created `.env.example` with placeholder values

#### Issue 4.2: Missing .gitignore
- **File:** N/A
- **Problem:** No `.gitignore` file to prevent sensitive files from being committed.
- **Fix:** Created comprehensive `.gitignore` covering:
  - Environment variables (.env files)
  - Python cache files (__pycache__, *.pyc)
  - Node modules
  - IDE files
  - OS files

#### Issue 4.3: Unpinned Dependencies
- **File:** `api/requirements.txt`, `worker/requirements.txt`
- **Problem:** Dependencies were not pinned, leading to potential breaking changes.
- **Fix:** Pinned all dependencies to specific versions:
  - API: fastapi==0.109.0, uvicorn==0.27.0, redis==5.0.1
  - Worker: redis==5.0.1

---

## Testing

All fixes have been verified through:
1. Unit tests with mocked Redis (6 tests covering health checks, job creation, job retrieval)
2. Integration tests that verify end-to-end job processing
3. Docker Compose local testing

## Security Improvements

1. No secrets in Docker images
2. All services run as non-root users
3. Multi-stage builds to minimize attack surface
4. Health checks for all services
5. Resource limits enforced in docker-compose
