"""
Production-grade observability infrastructure for UNIFIND backend.

This module provides:
- Request correlation IDs
- Distributed tracing context
- Performance metrics collection
- Latency tracking
- Error tracking integration
- Audit logging
"""

import contextvars
import logging
import time
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional

# Context variables for request tracing
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)
trace_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "trace_id", default=None
)

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Metric types for observability."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ObservabilityContext:
    """
    Context manager for observability tracking.
    Provides request correlation, tracing, and metrics collection.
    """

    @staticmethod
    def set_request_id(request_id: str) -> None:
        """Set request ID in context."""
        request_id_ctx.set(request_id)

    @staticmethod
    def get_request_id() -> Optional[str]:
        """Get request ID from context."""
        return request_id_ctx.get()

    @staticmethod
    def set_user_id(user_id: str) -> None:
        """Set user ID in context."""
        user_id_ctx.set(user_id)

    @staticmethod
    def get_user_id() -> Optional[str]:
        """Get user ID from context."""
        return user_id_ctx.get()

    @staticmethod
    def set_trace_id(trace_id: str) -> None:
        """Set trace ID in context."""
        trace_id_ctx.set(trace_id)

    @staticmethod
    def get_trace_id() -> Optional[str]:
        """Get trace ID from context."""
        return trace_id_ctx.get()

    @staticmethod
    def get_context() -> Dict[str, Any]:
        """Get all context variables."""
        return {
            "request_id": request_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "trace_id": trace_id_ctx.get(),
        }


class PerformanceTracker:
    """
    Track performance metrics for operations.
    Provides latency tracking and performance logging.
    """

    def __init__(self, operation_name: str, threshold_ms: float = 1000.0):
        """
        Initialize performance tracker.

        Args:
            operation_name: Name of the operation being tracked
            threshold_ms: Threshold in milliseconds for slow operation warning
        """
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: Optional[float] = None
        self.metadata: Dict[str, Any] = {}

    def __enter__(self):
        """Start tracking."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop tracking and log metrics."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

        # Build log context
        log_context = {
            "operation": self.operation_name,
            "duration_ms": round(self.duration_ms, 2),
            "threshold_ms": self.threshold_ms,
            **ObservabilityContext.get_context(),
            **self.metadata,
        }

        # Log based on performance
        if exc_type is not None:
            logger.error(
                f"Operation '{self.operation_name}' failed after {self.duration_ms:.2f}ms",
                extra={"extra_data": log_context},
                exc_info=(exc_type, exc_val, exc_tb),
            )
        elif self.duration_ms > self.threshold_ms:
            logger.warning(
                f"Slow operation '{self.operation_name}': {self.duration_ms:.2f}ms "
                f"(threshold: {self.threshold_ms}ms)",
                extra={"extra_data": log_context},
            )
        else:
            logger.debug(
                f"Operation '{self.operation_name}' completed in {self.duration_ms:.2f}ms",
                extra={"extra_data": log_context},
            )

        return False  # Don't suppress exceptions

    def add_metadata(self, **kwargs) -> None:
        """Add metadata to the performance tracking."""
        self.metadata.update(kwargs)


def track_performance(operation_name: str, threshold_ms: float = 1000.0):
    """
    Decorator to track function performance.

    Args:
        operation_name: Name of the operation
        threshold_ms: Threshold for slow operation warning

    Example:
        @track_performance("database_query", threshold_ms=500)
        async def get_user(user_id: str):
            ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with PerformanceTracker(operation_name, threshold_ms) as tracker:
                # Add function metadata
                tracker.add_metadata(function=func.__name__, module=func.__module__)
                result = await func(*args, **kwargs)
                return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with PerformanceTracker(operation_name, threshold_ms) as tracker:
                tracker.add_metadata(function=func.__name__, module=func.__module__)
                result = func(*args, **kwargs)
                return result

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class MetricsCollector:
    """
    Collect and aggregate metrics for monitoring.
    In production, this would integrate with Prometheus, DataDog, etc.
    """

    def __init__(self):
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._logger = logging.getLogger(f"{__name__}.metrics")

    def increment(
        self, metric_name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""
        self._record_metric(MetricType.COUNTER, metric_name, value, tags)

    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a gauge metric."""
        self._record_metric(MetricType.GAUGE, metric_name, value, tags)

    def histogram(
        self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a histogram metric."""
        self._record_metric(MetricType.HISTOGRAM, metric_name, value, tags)

    def timing(
        self, metric_name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a timing metric."""
        self._record_metric(MetricType.TIMER, metric_name, duration_ms, tags)

    def _record_metric(
        self,
        metric_type: MetricType,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a metric with context."""
        metric_data = {
            "type": metric_type.value,
            "name": metric_name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat(),
            **ObservabilityContext.get_context(),
        }

        # Log metric (in production, send to metrics backend)
        self._logger.info(
            f"METRIC: {metric_name}={value} type={metric_type.value}",
            extra={"extra_data": metric_data},
        )

        # Store for aggregation
        if metric_name not in self._metrics:
            self._metrics[metric_name] = {
                "type": metric_type.value,
                "count": 0,
                "sum": 0.0,
                "min": float("inf"),
                "max": float("-inf"),
            }

        stats = self._metrics[metric_name]
        stats["count"] += 1
        stats["sum"] += value
        stats["min"] = min(stats["min"], value)
        stats["max"] = max(stats["max"], value)

    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all collected metrics."""
        return self._metrics.copy()

    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()


# Global metrics collector instance
metrics = MetricsCollector()


class ErrorTracker:
    """
    Track and report errors for monitoring.
    Integrates with Sentry or similar error tracking services.
    """

    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.errors")
        self._sentry_enabled = False
        self._error_count = 0

    def capture_exception(
        self, exception: Exception, context: Optional[Dict[str, Any]] = None, level: str = "error"
    ) -> None:
        """
        Capture and report an exception.

        Args:
            exception: The exception to capture
            context: Additional context information
            level: Error level (error, warning, info)
        """
        self._error_count += 1

        error_data = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "error_count": self._error_count,
            "level": level,
            **(context or {}),
            **ObservabilityContext.get_context(),
        }

        # Log error with full context
        self._logger.error(
            f"Exception captured: {type(exception).__name__}: {str(exception)}",
            extra={"extra_data": error_data},
            exc_info=exception,
        )

        # In production, send to Sentry
        if self._sentry_enabled:
            try:
                import sentry_sdk

                sentry_sdk.capture_exception(exception)
            except ImportError:
                pass

        # Increment error metric
        metrics.increment(
            "errors.total", tags={"exception_type": type(exception).__name__, "level": level}
        )

    def capture_message(
        self, message: str, level: str = "info", context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Capture a message for monitoring.

        Args:
            message: The message to capture
            level: Message level
            context: Additional context
        """
        message_data = {
            "message": message,
            "level": level,
            **(context or {}),
            **ObservabilityContext.get_context(),
        }

        log_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.log(log_level, message, extra={"extra_data": message_data})

    def enable_sentry(self, dsn: str, environment: str, release: Optional[str] = None) -> None:
        """
        Enable Sentry integration.

        Args:
            dsn: Sentry DSN
            environment: Environment name
            release: Release version
        """
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_sdk.init(
                dsn=dsn,
                environment=environment,
                release=release,
                traces_sample_rate=0.1,  # 10% of transactions
                profiles_sample_rate=0.1,  # 10% of transactions
                integrations=[
                    FastApiIntegration(),
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                ],
                before_send=self._before_send_sentry,
            )

            self._sentry_enabled = True
            self._logger.info("Sentry integration enabled")
        except ImportError:
            self._logger.warning("Sentry SDK not installed, error tracking disabled")

    def _before_send_sentry(
        self, event: Dict[str, Any], hint: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Filter and enrich Sentry events before sending.

        Args:
            event: Sentry event
            hint: Event hint with exception info

        Returns:
            Modified event or None to drop
        """
        # Add custom context
        event.setdefault("contexts", {})
        event["contexts"]["observability"] = ObservabilityContext.get_context()

        # Filter sensitive data
        if "request" in event:
            request = event["request"]
            # Remove sensitive headers
            if "headers" in request:
                sensitive_headers = ["authorization", "cookie", "x-api-key"]
                for header in sensitive_headers:
                    request["headers"].pop(header, None)

        return event


# Global error tracker instance
error_tracker = ErrorTracker()
