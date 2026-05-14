# ============================================================================
# UNIFIND Backend - Production-Grade Multi-Stage Dockerfile
# ============================================================================
# Optimized for:
# - Minimal image size (<200MB target)
# - Fast builds with layer caching
# - Security (non-root user, minimal attack surface)
# - Deterministic builds (pinned dependencies)
# - Production reliability (health checks, graceful shutdown)
# ============================================================================

# ============================================================================
# Stage 1: Builder - Compile dependencies
# ============================================================================
FROM python:3.11-slim AS builder

# Build arguments
ARG ENVIRONMENT=production

# Set working directory
WORKDIR /build

# Install build dependencies (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for optimal layer caching
COPY requirements-prod.txt .

# Install Python dependencies to user directory
# --user flag installs to ~/.local which we'll copy to final image
RUN pip install --no-cache-dir --user --no-warn-script-location \
    -r requirements-prod.txt

# Verify critical packages are installed
RUN python -c "import fastapi, uvicorn, gunicorn, firebase_admin, google.generativeai, cloudinary" || \
    (echo "ERROR: Critical packages not installed" && exit 1)

# ============================================================================
# Stage 2: Production - Minimal runtime image
# ============================================================================
FROM python:3.11-slim AS production

# Metadata
LABEL maintainer="UNIFIND Team"
LABEL version="2.1.0"
LABEL description="UNIFIND Backend API - Production Image"

# Build arguments
ARG ENVIRONMENT=production
ARG BUILD_DATE
ARG VCS_REF

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH=/home/appuser/.local/bin:$PATH \
    ENVIRONMENT=${ENVIRONMENT} \
    PORT=8000 \
    WORKERS=4

# Install runtime dependencies only (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Health check and debugging
    curl \
    # File type detection
    libmagic1 \
    # Process management
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user with specific UID/GID for security
RUN groupadd -r -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -m -s /bin/bash appuser && \
    mkdir -p /app /home/appuser/.local && \
    chown -R appuser:appuser /app /home/appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./scripts ./scripts

# Make scripts executable
RUN chmod +x ./scripts/*.sh || true

# Copy configuration files (for reference only, use env vars in production)
COPY --chown=appuser:appuser ./.env.example ./.env.example

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appuser /app/logs /app/tmp

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check - verify app is responding correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command: Run with gunicorn for production
# Can be overridden with docker run command
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keepalive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--access-logformat", "%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\" %(D)s", \
     "--preload", \
     "--graceful-timeout", "30"]

# ============================================================================
# Stage 3: Development - Includes dev tools
# ============================================================================
FROM production AS development

USER root

# Install development dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Development uses uvicorn with auto-reload
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload", \
     "--log-level", "debug"]

# ============================================================================
# Build Instructions:
# ============================================================================
# Production build:
#   docker build --target production -t unifind-backend:latest .
#
# Development build:
#   docker build --target development -t unifind-backend:dev .
#
# Build with metadata:
#   docker build --target production \
#     --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#     --build-arg VCS_REF=$(git rev-parse --short HEAD) \
#     -t unifind-backend:latest .
#
# Run production:
#   docker run -p 8000:8000 --env-file .env unifind-backend:latest
#
# Run development:
#   docker run -p 8000:8000 -v $(pwd)/app:/app/app --env-file .env unifind-backend:dev
# ============================================================================
