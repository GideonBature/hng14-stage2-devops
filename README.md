# Job Processor - Microservices Application

A containerized job processing system built with FastAPI, Node.js, Redis, and Docker.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│     API     │────▶│    Redis    │
│  (Node.js)  │◀────│  (FastAPI)  │◀────│   (Queue)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                         ┌──────▼──────┐
                                         │    Worker   │
                                         │   (Python)  │
                                         └─────────────┘
```

### Services

- **Frontend** (Node.js/Express): Web UI for submitting and tracking jobs
- **API** (Python/FastAPI): REST API for job creation and status retrieval
- **Worker** (Python): Background worker that processes jobs from the queue
- **Redis**: Message queue and state storage

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-fork-url>
cd hng14-stage2-devops
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your values (optional - defaults work for local development)
```

### 3. Start the Stack

```bash
docker-compose up -d
```

### 4. Verify Services are Running

```bash
# Check all containers are healthy
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:3000/health
```

### 5. Access the Application

Open your browser to: http://localhost:3000

## Successful Startup

When all services are running correctly, you should see:

```
NAME                STATUS              PORTS
redis               healthy (up Xs)
api                 healthy (up Xs)     0.0.0.0:8000->8000/tcp
worker              healthy (up Xs)
frontend            healthy (up Xs)     0.0.0.0:3000->3000/tcp
```

### Testing the Application

1. Open http://localhost:3000 in your browser
2. Click "Submit New Job"
3. You should see a job ID appear
4. The status will automatically poll and show "completed" after ~2 seconds

## Development

### Running Tests

```bash
cd api
pip install -r requirements.txt
pytest tests/ -v --cov=.
```

### Building Images Locally

```bash
# API
docker build -t job-processor-api ./api

# Worker
docker build -t job-processor-worker ./worker

# Frontend
docker build -t job-processor-frontend ./frontend
```

### Stopping the Stack

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (clears all data)
docker-compose down -v
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis hostname | redis |
| `REDIS_PORT` | Redis port | 6379 |
| `REDIS_PASSWORD` | Redis password | (none) |
| `API_HOST` | API bind host | 0.0.0.0 |
| `API_PORT` | API port | 8000 |
| `FRONTEND_PORT` | Frontend port | 3000 |
| `API_URL` | URL for API (used by frontend) | http://api:8000 |
| `APP_ENV` | Application environment | production |

## API Endpoints

### Health Check
```bash
GET /health
Response: {"status": "healthy"}
```

### Create Job
```bash
POST /jobs
Response: {"job_id": "uuid-string"}
```

### Get Job Status
```bash
GET /jobs/{job_id}
Response: {"job_id": "uuid-string", "status": "queued|processing|completed"}
```

## CI/CD Pipeline

The project includes a GitHub Actions workflow with the following stages:

1. **Lint**: Python (flake8), JavaScript (eslint), Dockerfiles (hadolint)
2. **Test**: pytest with coverage reporting
3. **Build**: Build and push images to local registry
4. **Security Scan**: Trivy vulnerability scanning
5. **Integration Test**: End-to-end job processing test
6. **Deploy**: Rolling update deployment (main branch only)

### Pipeline Status

![CI/CD Pipeline](https://github.com/<your-username>/hng14-stage2-devops/workflows/CI/CD%20Pipeline/badge.svg)

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions pipeline
├── api/
│   ├── Dockerfile             # API service Dockerfile
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── tests/
│       └── test_api.py        # Unit tests
├── frontend/
│   ├── Dockerfile             # Frontend Dockerfile
│   ├── app.js                 # Express application
│   ├── package.json           # Node.js dependencies
│   └── views/
│       └── index.html         # Web UI
├── worker/
│   ├── Dockerfile             # Worker Dockerfile
│   ├── worker.py              # Background worker
│   └── requirements.txt       # Python dependencies
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
├── FIXES.md                   # Bug fixes documentation
└── README.md                  # This file
```

## Production Considerations

- All services run as non-root users
- Multi-stage Docker builds minimize image size
- No secrets are copied into Docker images
- Health checks configured for all services
- Resource limits enforced (CPU: 0.5, Memory: 256M per service)
- Redis password authentication enabled
- Rolling update deployment strategy

## Troubleshooting

### Services won't start

Check logs:
```bash
docker-compose logs <service-name>
```

### Redis connection errors

Ensure Redis is healthy before other services start:
```bash
docker-compose up -d redis
sleep 5
docker-compose up -d
```

### Port conflicts

Change ports in `.env`:
```bash
API_PORT=8001
FRONTEND_PORT=3001
```

Then update docker-compose ports accordingly.

## License

This project is part of the HNG Internship DevOps Track.
