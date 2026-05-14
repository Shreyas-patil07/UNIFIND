"""
Observability middleware for request tracking and monitoring.

Provides:
- Request correlation IDs
- Performance tracking
- Error tracking
- Metrics collection
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.observability import ObservabilityContext, error_tracker, metrics

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request observability.

    Tracks:
    - Request correlation IDs
    - Request/response timing
    - HTTP metrics
    - Error rates
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._request_count = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with observability tracking."""

        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Generate trace ID for distributed tracing
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())

        # Set context variables
        ObservabilityContext.set_request_id(request_id)
        ObservabilityContext.set_trace_id(trace_id)

        # Store in request state for access in routes
        request.state.request_id = request_id
        request.state.trace_id = trace_id

        # Get client information
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")

        # Increment request counter
        self._request_count += 1

        # Start timing
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "extra_data": {
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "request_count": self._request_count,
                }
            },
        )

        # Record request metric
        metrics.increment(
            "http.requests.total",
            tags={"method": request.method, "path": self._normalize_path(request.url.path)},
        )

        # Process request
        response = None
        error = None

        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            # Track error
            error_tracker.capture_exception(
                e,
                context={
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_ip,
                },
            )
            raise
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Add observability headers to response
            if response:
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Trace-ID"] = trace_id
                response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

                status_code = response.status_code
            else:
                status_code = 500

            # Determine log level
            log_level = self._get_log_level(status_code)

            # Log response
            logger.log(
                log_level,
                f"← {request.method} {request.url.path} [{status_code}] {duration_ms:.2f}ms",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "trace_id": trace_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": round(duration_ms, 2),
                        "client_ip": client_ip,
                        "error": str(error) if error else None,
                    }
                },
            )

            # Record metrics
            metrics.timing(
                "http.request.duration_ms",
                duration_ms,
                tags={
                    "method": request.method,
                    "path": self._normalize_path(request.url.path),
                    "status_code": str(status_code),
                },
            )

            metrics.increment(
                "http.responses.total",
                tags={
                    "method": request.method,
                    "path": self._normalize_path(request.url.path),
                    "status_code": str(status_code),
                    "status_class": f"{status_code // 100}xx",
                },
            )

            # Track slow requests
            if duration_ms > 1000:
                metrics.increment(
                    "http.requests.slow",
                    tags={"method": request.method, "path": self._normalize_path(request.url.path)},
                )

                logger.warning(
                    f"Slow request: {request.method} {request.url.path} took {duration_ms:.2f}ms",
                    extra={
                        "extra_data": {
                            "request_id": request_id,
                            "duration_ms": round(duration_ms, 2),
                        }
                    },
                )

            # Track errors
            if status_code >= 400:
                metrics.increment(
                    "http.errors.total",
                    tags={
                        "method": request.method,
                        "path": self._normalize_path(request.url.path),
                        "status_code": str(status_code),
                        "error_type": "client_error" if status_code < 500 else "server_error",
                    },
                )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Considers proxy headers for accurate IP detection.
        """
        # Check X-Forwarded-For header (from proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for metrics to avoid high cardinality.

        Replaces IDs and dynamic segments with placeholders.
        """
        # Replace UUIDs and IDs with placeholders
        import re

        # Replace UUID patterns
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{id}",
            path,
            flags=re.IGNORECASE,
        )

        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)

        # Replace long alphanumeric strings (likely IDs)
        path = re.sub(r"/[a-zA-Z0-9]{20,}", "/{id}", path)

        return path

    def _get_log_level(self, status_code: int) -> int:
        """Get appropriate log level based on status code."""
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        else:
            return logging.INFO
