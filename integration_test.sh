#!/bin/bash
set -e

TIMEOUT=120
START=$(date +%s)

echo "Starting integration test..."

# Create test env
cat > .env << EOF
REDIS_PASSWORD=test_password
APP_ENV=production
REGISTRY=localhost:5000
EOF

# Start services
docker compose up -d

# Wait for API health
echo "Waiting for API to be healthy..."
API_HEALTHY=false
for i in $(seq 1 30); do
  if docker compose exec -T api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())" 2>/dev/null | grep -q "healthy"; then
    echo "API is healthy"
    API_HEALTHY=true
    break
  fi
  echo "Waiting for API... ($i/30)"
  sleep 2
  
  # Check timeout
  ELAPSED=$(( $(date +%s) - START ))
  if [ "$ELAPSED" -gt "$TIMEOUT" ]; then
    echo "Integration test timed out after ${TIMEOUT}s"
    docker compose logs
    docker compose down -v
    exit 1
  fi
done

if [ "$API_HEALTHY" = "false" ]; then
  echo "API never became healthy"
  docker compose logs api
  docker compose down -v
  exit 1
fi

# Wait for frontend health
echo "Waiting for frontend to be healthy..."
FRONTEND_HEALTHY=false
for i in $(seq 1 30); do
  if curl -sf http://localhost:3000/health | grep -q "healthy"; then
    echo "Frontend is healthy"
    FRONTEND_HEALTHY=true
    break
  fi
  echo "Waiting for frontend... ($i/30)"
  sleep 2
  
  ELAPSED=$(( $(date +%s) - START ))
  if [ "$ELAPSED" -gt "$TIMEOUT" ]; then
    echo "Integration test timed out after ${TIMEOUT}s"
    docker compose logs
    docker compose down -v
    exit 1
  fi
done

if [ "$FRONTEND_HEALTHY" = "false" ]; then
  echo "Frontend never became healthy"
  docker compose logs frontend
  docker compose down -v
  exit 1
fi

# Test job submission
echo "Testing job submission..."
JOB_RESPONSE=$(curl -sf -X POST http://localhost:3000/submit)
echo "Response: $JOB_RESPONSE"

JOB_ID=$(echo "$JOB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

# Poll for completion
echo "Polling for job completion..."
COMPLETED=false
for i in $(seq 1 30); do
  STATUS_RESPONSE=$(curl -sf "http://localhost:3000/status/$JOB_ID")
  echo "Poll $i: $STATUS_RESPONSE"
  STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
  if [ "$STATUS" = "completed" ]; then
    echo "Job completed successfully"
    COMPLETED=true
    break
  fi
  sleep 2
  
  ELAPSED=$(( $(date +%s) - START ))
  if [ "$ELAPSED" -gt "$TIMEOUT" ]; then
    echo "Integration test timed out after ${TIMEOUT}s"
    docker compose logs
    docker compose down -v
    exit 1
  fi
done

if [ "$COMPLETED" = "false" ]; then
  echo "Job did not complete within time limit"
  docker compose down -v
  exit 1
fi

# Cleanup
docker compose down -v

echo "Integration test passed!"
