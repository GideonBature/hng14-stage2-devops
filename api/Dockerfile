# Build stage
FROM python:3.11-alpine AS builder

WORKDIR /app

# Upgrade packages and install build dependencies
RUN apk upgrade --no-cache && \
    apk add --no-cache gcc musl-dev linux-headers && \
    rm -rf /var/cache/apk/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==25.3 setuptools==78.0.0 wheel==0.46.2 jaraco.context==6.1.0 && \
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
COPY main.py .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app /home/appuser/.local

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
