# Multi-stage Dockerfile for RabbitRedux
# Supports both Flask (legacy) and FastAPI (recommended)
# TODO: Add NVIDIA GPU support with cuda base image
# TODO: Implement build caching optimization for faster rebuilds
# TODO: Add vulnerability scanning with trivy or grype

# Build stage
FROM python:3.10-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# TODO: Pin system package versions for reproducible builds
# TODO: Add security updates check during build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:${PATH}" \
    ENVIRONMENT=production \
    API_HOST=0.0.0.0 \
    API_PORT=8000

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
# TODO: Add capability dropping for enhanced security
# TODO: Implement read-only root filesystem
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app /app/model_cache /app/huggingface_cache && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
# TODO: Implement custom health check script with detailed diagnostics
# TODO: Add readiness probe for Kubernetes deployments
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

# Expose ports
EXPOSE 8000 5000

# Default to FastAPI (recommended)
# For Flask, use: docker run ... gunicorn --bind 0.0.0.0:5000 wsgi:app
# TODO: Add graceful shutdown handling for SIGTERM
# TODO: Implement pre-start script for model preloading
# TODO: Add resource limits configuration (CPU, memory)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Alternative commands (uncomment as needed):
# Flask with Gunicorn:
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "wsgi:app"]
#
# FastAPI with custom settings:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--timeout-keep-alive", "300"]
