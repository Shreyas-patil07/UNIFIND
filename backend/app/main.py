"""
UNIFIND Backend API - FastAPI Application
Production-ready with comprehensive security hardening and layered architecture.
Enhanced with production-grade observability and operational monitoring.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

# Import refactored routes
from app.api.routes import (
    auth,
    chats,
    need_board,
    needs,
    products,
    reviews,
    transactions,
    uploads,
    users,
)
from app.core.audit import AuditEventType, audit_logger
from app.core.config import settings
from app.core.database import get_db, init_firebase
from app.core.exceptions import UniFindException, exception_handler
from app.core.health import health_checker
from app.core.logging import setup_logging
from app.core.observability import error_tracker, metrics
from app.core.security import limiter, rate_limit_exceeded_handler
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    startup_start = time.time()
    logger.info("=" * 80)
    logger.info("Starting UNIFIND API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: 2.1.0")
    logger.info("=" * 80)

    # Initialize Firebase
    try:
        logger.info("Initializing Firebase...")
        init_firebase()
        logger.info("✓ Firebase initialized successfully")

        # Log audit event
        audit_logger.log_admin_event(
            event_type=AuditEventType.ADMIN_CONFIG_CHANGED,
            admin_id="system",
            action="startup",
            details={"environment": settings.ENVIRONMENT},
        )
    except Exception as e:
        logger.error(f"✗ Failed to initialize Firebase: {e}")
        error_tracker.capture_exception(e, context={"phase": "startup"})
        raise

    # Validate security configuration
    if settings.ENVIRONMENT == "production":
        logger.info("Validating production security configuration...")
        if "*" in settings.CORS_ORIGINS:
            raise ValueError("CORS wildcard (*) not allowed in production")
        if not all(origin.startswith("https://") for origin in settings.cors_origins_list):
            logger.warning("⚠ Production CORS origins should use HTTPS")
        logger.info("✓ Security configuration validated")

    # Initialize Sentry (if configured)
    sentry_dsn = getattr(settings, "SENTRY_DSN", None)
    if sentry_dsn:
        logger.info("Initializing Sentry error tracking...")
        error_tracker.enable_sentry(
            dsn=sentry_dsn, environment=settings.ENVIRONMENT, release="2.1.0"
        )
        logger.info("✓ Sentry initialized")

    # Perform initial health check
    try:
        logger.info("Performing initial health check...")
        health_status = await health_checker.check_readiness()
        if health_status["ready"]:
            logger.info("✓ All systems ready")
        else:
            logger.warning("⚠ Some systems not ready")
            logger.warning(f"Health check details: {health_status}")
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")

    startup_duration = (time.time() - startup_start) * 1000
    logger.info("=" * 80)
    logger.info(f"✓ UNIFIND API started successfully in {startup_duration:.2f}ms")
    logger.info("=" * 80)

    # Record startup metric
    metrics.timing("app.startup.duration_ms", startup_duration)

    yield

    # Shutdown
    shutdown_start = time.time()
    logger.info("=" * 80)
    logger.info("Shutting down UNIFIND API...")

    # Log audit event
    audit_logger.log_admin_event(
        event_type=AuditEventType.ADMIN_CONFIG_CHANGED,
        admin_id="system",
        action="shutdown",
        details={"environment": settings.ENVIRONMENT},
    )

    # Graceful shutdown: Allow in-flight requests to complete
    logger.info("Waiting for in-flight requests to complete...")
    import asyncio

    await asyncio.sleep(2)  # Allow requests to drain

    # Close database connections
    logger.info("Closing database connections...")
    try:
        from app.core.database import cleanup_firebase

        cleanup_firebase()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

    shutdown_duration = (time.time() - shutdown_start) * 1000
    logger.info(f"✓ UNIFIND API shutdown complete in {shutdown_duration:.2f}ms")
    logger.info("=" * 80)


# Initialize FastAPI app
app = FastAPI(
    title="UNIFIND API",
    description="College marketplace platform API with AI-powered matching",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Register custom exception handlers
app.add_exception_handler(UniFindException, exception_handler.unifind_exception_handler)
app.add_exception_handler(HTTPException, exception_handler.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handler.validation_exception_handler)
app.add_exception_handler(Exception, exception_handler.unhandled_exception_handler)

# Observability Middleware (MUST be early in chain)
app.add_middleware(ObservabilityMiddleware)

# Security Headers Middleware (MUST be first)
app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration - Strict in production
origins = settings.cors_origins_list
logger.info(f"CORS ORIGINS CONFIGURED: {origins}")

# Validate CORS configuration
if settings.ENVIRONMENT == "production":
    for origin in origins:
        if not origin.startswith("https://"):
            logger.warning(f"Non-HTTPS origin in production: {origin}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=3600,
)

# GZip Compression - compress responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Remove old request logging middleware - now handled by ObservabilityMiddleware
# The ObservabilityMiddleware provides enhanced tracking with correlation IDs,
# distributed tracing, metrics, and error tracking


# Global exception handlers (legacy - now using centralized exception handler)
# Keeping for backward compatibility but handlers are registered above


# Include refactored routers with /api prefix (canonical)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(chats.router, prefix="/api", tags=["chats"])
app.include_router(reviews.router, prefix="/api", tags=["reviews"])
app.include_router(transactions.router, prefix="/api", tags=["transactions"])
app.include_router(uploads.router, prefix="/api", tags=["uploads"])
app.include_router(needs.router, prefix="/api", tags=["needs"])
app.include_router(need_board.router, prefix="/api", tags=["need-board"])

# ============================================================================
# COMPATIBILITY ROUTES (DEPRECATED - Frontend expects routes without /api prefix)
# ============================================================================
# These routes provide backward compatibility for frontend code that calls
# endpoints without the /api prefix. They duplicate the canonical routes above.
#
# ⚠️ DEPRECATION NOTICE: These routes are deprecated and will be removed in v3.0.0
# All new code should use /api prefix. Frontend migration in progress.
#
# Migration Timeline:
# - v2.1.0 (current): Compatibility routes active with deprecation warnings
# - v2.2.0: Frontend migration complete, compatibility routes return 410 Gone
# - v3.0.0: Compatibility routes removed entirely
# ============================================================================


# Deprecation warning middleware for compatibility routes
from fastapi import Request

@app.middleware("http")
async def compatibility_deprecation_middleware(request: Request, call_next):
    """Log deprecation warnings for compatibility routes."""
    path = request.url.path

    # Check if using deprecated compatibility routes
    if path.startswith("/auth/") and not path.startswith("/api/auth/"):
        logger.warning(
            f"DEPRECATED ROUTE: {path} - Use /api/auth/* instead. "
            f"This route will be removed in v3.0.0",
            extra={
                "extra_data": {
                    "deprecated_path": path,
                    "recommended_path": f"/api{path}",
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("User-Agent", "unknown"),
                }
            },
        )
        # Add deprecation header to response
        response = await call_next(request)
        response.headers["X-Deprecated-Route"] = "true"
        response.headers["X-Deprecated-Message"] = "Use /api prefix. Removal in v3.0.0"
        response.headers["X-Recommended-Route"] = f"/api{path}"
        return response

    if path.startswith("/upload/") and not path.startswith("/api/upload/"):
        logger.warning(
            f"DEPRECATED ROUTE: {path} - Use /api/upload/* instead. "
            f"This route will be removed in v3.0.0",
            extra={
                "extra_data": {
                    "deprecated_path": path,
                    "recommended_path": f"/api{path}",
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("User-Agent", "unknown"),
                }
            },
        )
        response = await call_next(request)
        response.headers["X-Deprecated-Route"] = "true"
        response.headers["X-Deprecated-Message"] = "Use /api prefix. Removal in v3.0.0"
        response.headers["X-Recommended-Route"] = f"/api{path}"
        return response

    return await call_next(request)


# Auth routes without /api prefix (for email verification page)
# DEPRECATED: Use /api/auth/* instead
app.include_router(auth.router, prefix="/auth", tags=["auth-compat-DEPRECATED"])

# Upload routes without /api prefix (for image upload services)
# DEPRECATED: Use /api/upload/* instead
app.include_router(uploads.router, prefix="/upload", tags=["upload-compat-DEPRECATED"])


# Health check endpoints
@app.get("/")
@app.head("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "UNIFIND API",
        "version": "2.1.0",
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
        "architecture": "layered",
    }


@app.get("/health")
async def health_check():
    """
    Basic health check endpoint for monitoring and load balancers.
    Returns simple status without detailed checks.
    """
    return {"status": "ok", "version": "2.1.0"}


@app.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    Checks if the application is alive and should not be restarted.
    """
    result = await health_checker.check_liveness()
    return result


@app.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    Checks if the application is ready to serve traffic.
    """
    result = await health_checker.check_readiness()

    if not result["ready"]:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=result)

    return result


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with dependency status.
    Should be protected in production (admin only).
    """
    result = await health_checker.check_health(include_details=True)

    if result["status"] == "unhealthy":
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=result)

    return result


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint for monitoring."""
    return {"status": "ok", "version": "2.1.0", "environment": settings.ENVIRONMENT}


@app.get("/api/metrics")
async def get_metrics():
    """
    Get application metrics.
    Should be protected in production (monitoring systems only).
    """
    return {"metrics": metrics.get_metrics(), "timestamp": time.time()}


@app.get("/api/ready")
async def api_readiness_check():
    """API readiness check for load balancers."""
    try:
        db = get_db()
        # Simple check to verify Firebase connection
        _ = db.collection("_health_check").limit(1).get()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        error_tracker.capture_exception(e, context={"check": "readiness"})
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": "Service unavailable"},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info" if settings.ENVIRONMENT == "production" else "debug",
    )
