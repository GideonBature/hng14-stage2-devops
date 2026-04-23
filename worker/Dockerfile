# Build stage
FROM python:3.11-alpine AS builder

WORKDIR /app

# Upgrade packages and install build dependencies
RUN apk upgrade --no-cache && \
    apk add --no-cache gcc musl-dev linux-headers

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel jaraco.context && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-alpine AS production

# Upgrade packages and create non-root user
RUN apk upgrade --no-cache && \
    addgroup -S appuser && adduser -S appuser -G appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY worker.py .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app /home/appuser/.local

# Switch to non-root user
USER appuser

# Health check - verify worker is actively processing
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD test -f /tmp/worker_healthy && \
        test $(( $(date +%s) - $(stat -c %Y /tmp/worker_healthy) )) -lt 60 || exit 1

# Run the worker
CMD ["python", "worker.py"]
