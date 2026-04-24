# Build stage
FROM python:3.11-alpine AS builder

WORKDIR /app

# Upgrade packages and install build dependencies
RUN apk upgrade --no-cache && \
    apk add --no-cache gcc musl-dev linux-headers && \
    rm -rf /var/cache/apk/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==26.0 setuptools==80.9.0 wheel==0.46.2 jaraco.context==6.1.0 && \
    pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user --force-reinstall --no-deps wheel==0.46.2 jaraco.context==6.1.0 && \
    rm -rf /usr/local/lib/python3.11/site-packages/setuptools/_vendor/wheel-0.45.1.dist-info \
           /usr/local/lib/python3.11/site-packages/setuptools/_vendor/jaraco.context-5.3.0.dist-info && \
    python -c "import importlib.metadata as m; assert m.version('wheel') == '0.46.2'; assert m.version('jaraco.context') == '6.1.0'"

# Production stage
FROM python:3.11-alpine AS production

# Upgrade packages and create non-root user
RUN apk upgrade --no-cache && \
    pip install --no-cache-dir --upgrade pip==26.0 setuptools==80.9.0 wheel==0.46.2 jaraco.context==6.1.0 && \
    rm -rf /usr/local/lib/python3.11/site-packages/setuptools/_vendor/wheel-0.45.1.dist-info \
           /usr/local/lib/python3.11/site-packages/setuptools/_vendor/jaraco.context-5.3.0.dist-info && \
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
