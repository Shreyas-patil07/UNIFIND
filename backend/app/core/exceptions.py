"""
Centralized exception handling for UNIFIND backend.

Provides:
- Custom exception classes
- Structured error responses
- Error tracking integration
- Security-aware error messages
"""

import logging
from typing import Any, Dict, Optional

from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.observability import ObservabilityContext, error_tracker, metrics

logger = logging.getLogger(__name__)


class UniFindException(Exception):
    """Base exception for UNIFIND application."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(UniFindException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            **kwargs,
        )


class AuthorizationError(UniFindException):
    """Authorization failed - insufficient permissions."""

    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            **kwargs,
        )


class ResourceNotFoundError(UniFindException):
    """Requested resource not found."""

    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
            **kwargs,
        )


class ValidationError(UniFindException):
    """Data validation failed."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field

        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs,
        )


class BusinessRuleError(UniFindException):
    """Business rule violation."""

    def __init__(self, message: str, rule: Optional[str] = None, **kwargs):
        details = kwargs.pop("details", {})
        if rule:
            details["rule"] = rule

        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_RULE_ERROR",
            details=details,
            **kwargs,
        )


class RateLimitError(UniFindException):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR",
            **kwargs,
        )


class ExternalServiceError(UniFindException):
    """External service error."""

    def __init__(self, service: str, message: str, **kwargs):
        super().__init__(
            message=f"{service} error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
            **kwargs,
        )


class ExceptionHandler:
    """
    Centralized exception handler with observability integration.
    """

    @staticmethod
    async def unifind_exception_handler(request: Request, exc: UniFindException) -> JSONResponse:
        """
        Handle custom UNIFIND exceptions.

        Args:
            request: FastAPI request
            exc: UNIFIND exception

        Returns:
            JSON error response
        """
        # Log the exception
        logger.warning(
            f"Application error: {exc.error_code} - {exc.message}",
            extra={
                "extra_data": {
                    "error_code": exc.error_code,
                    "status_code": exc.status_code,
                    "path": request.url.path,
                    "method": request.method,
                    **exc.details,
                    **ObservabilityContext.get_context(),
                }
            },
        )

        # Track error
        error_tracker.capture_exception(
            exc,
            context={
                "error_code": exc.error_code,
                "path": request.url.path,
                "method": request.method,
            },
            level="warning",
        )

        # Record metric
        metrics.increment(
            "errors.application",
            tags={"error_code": exc.error_code, "status_code": str(exc.status_code)},
        )

        # Build response
        error_response = {
            "error": exc.error_code,
            "message": exc.message,
            "request_id": ObservabilityContext.get_request_id(),
        }

        # Include details in non-production environments
        if not settings.is_production and exc.details:
            error_response["details"] = exc.details

        return JSONResponse(status_code=exc.status_code, content=error_response)

    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle FastAPI HTTP exceptions.

        Args:
            request: FastAPI request
            exc: HTTP exception

        Returns:
            JSON error response
        """
        # Log the exception
        log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR
        logger.log(
            log_level,
            f"HTTP error {exc.status_code}: {exc.detail}",
            extra={
                "extra_data": {
                    "status_code": exc.status_code,
                    "path": request.url.path,
                    "method": request.method,
                    **ObservabilityContext.get_context(),
                }
            },
        )

        # Track error
        if exc.status_code >= 500:
            error_tracker.capture_exception(
                exc, context={"path": request.url.path, "method": request.method}
            )

        # Record metric
        metrics.increment("errors.http", tags={"status_code": str(exc.status_code)})

        # Build response
        error_response = {
            "error": "HTTP_ERROR",
            "message": exc.detail if isinstance(exc.detail, str) else "An error occurred",
            "request_id": ObservabilityContext.get_request_id(),
        }

        return JSONResponse(status_code=exc.status_code, content=error_response)

    @staticmethod
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle request validation errors.

        Args:
            request: FastAPI request
            exc: Validation error

        Returns:
            JSON error response
        """
        # Log validation error
        logger.warning(
            f"Validation error on {request.url.path}",
            extra={
                "extra_data": {
                    "errors": exc.errors(),
                    "path": request.url.path,
                    "method": request.method,
                    **ObservabilityContext.get_context(),
                }
            },
        )

        # Record metric
        metrics.increment("errors.validation", tags={"path": request.url.path})

        # Build response
        error_response = {
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "request_id": ObservabilityContext.get_request_id(),
        }

        # Include validation details in non-production
        if not settings.is_production:
            error_response["details"] = exc.errors()

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response
        )

    @staticmethod
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle unexpected exceptions.

        Args:
            request: FastAPI request
            exc: Unhandled exception

        Returns:
            JSON error response
        """
        # Log the exception with full traceback
        logger.error(
            f"Unhandled exception on {request.url.path}: {type(exc).__name__}: {str(exc)}",
            extra={
                "extra_data": {
                    "exception_type": type(exc).__name__,
                    "path": request.url.path,
                    "method": request.method,
                    **ObservabilityContext.get_context(),
                }
            },
            exc_info=True,
        )

        # Track error
        error_tracker.capture_exception(
            exc, context={"path": request.url.path, "method": request.method}
        )

        # Record metric
        metrics.increment("errors.unhandled", tags={"exception_type": type(exc).__name__})

        # Build response (never expose internal details in production)
        error_response = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": ObservabilityContext.get_request_id(),
        }

        # Include exception details in non-production
        if not settings.is_production:
            error_response["details"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response
        )


# Create handler instance
exception_handler = ExceptionHandler()
