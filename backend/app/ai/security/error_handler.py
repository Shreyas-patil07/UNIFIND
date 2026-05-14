"""
Error Handler - Handle AI errors gracefully with retries and fallbacks.

Features:
- Structured error types
- Exponential backoff for retries
- Retry budget enforcement
- Error sanitization
- Fallback mechanisms
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds
MAX_BACKOFF = 8.0  # seconds
BACKOFF_MULTIPLIER = 2.0

T = TypeVar("T")


# ============================================================================
# Custom Error Types
# ============================================================================


class AISecurityError(Exception):
    """Raised when a security violation is detected."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AIValidationError(Exception):
    """Raised when AI output validation fails."""

    def __init__(self, message: str, raw_output: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.raw_output = raw_output


class AICostLimitError(Exception):
    """Raised when cost/token budget is exceeded."""

    def __init__(self, message: str, usage: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.usage = usage or {}


class AITimeoutError(Exception):
    """Raised when AI request times out."""

    def __init__(self, message: str, timeout: Optional[float] = None):
        super().__init__(message)
        self.message = message
        self.timeout = timeout


class AIRateLimitError(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after


# ============================================================================
# Error Handling Functions
# ============================================================================


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error message to prevent sensitive data leakage.

    Args:
        error: Exception object

    Returns:
        Sanitized error message
    """
    message = str(error)

    # Remove potential API keys (pattern: alphanumeric strings > 20 chars)
    import re

    message = re.sub(r"\b[A-Za-z0-9]{20,}\b", "[REDACTED]", message)

    # Remove potential file paths
    message = re.sub(r"[A-Za-z]:\\[^\s]+", "[PATH]", message)  # Windows
    message = re.sub(r"/[^\s]+", "[PATH]", message)  # Unix

    # Remove potential email addresses
    message = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]", message)

    # Truncate if too long
    if len(message) > 200:
        message = message[:200] + "..."

    return message


def calculate_backoff(attempt: int) -> float:
    """
    Calculate exponential backoff delay.

    Args:
        attempt: Retry attempt number (0-indexed)

    Returns:
        Delay in seconds
    """
    delay = INITIAL_BACKOFF * (BACKOFF_MULTIPLIER**attempt)
    return min(delay, MAX_BACKOFF)


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_retries: int = MAX_RETRIES,
    backoff_multiplier: float = BACKOFF_MULTIPLIER,
    **kwargs,
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        backoff_multiplier: Multiplier for backoff delay
        **kwargs: Keyword arguments for func

    Returns:
        Result from func

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            result = await func(*args, **kwargs)
            if attempt > 0:
                logger.info(f"Retry succeeded on attempt {attempt + 1}")
            return result

        except (AITimeoutError, AIRateLimitError) as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = calculate_backoff(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {sanitize_error_message(e)}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries} retry attempts failed")

        except (AISecurityError, AIValidationError, AICostLimitError) as e:
            # Don't retry on security, validation, or cost errors
            logger.error(f"Non-retryable error: {sanitize_error_message(e)}")
            raise

        except Exception as e:
            last_exception = e
            logger.error(f"Unexpected error on attempt {attempt + 1}: {sanitize_error_message(e)}")
            if attempt < max_retries - 1:
                delay = calculate_backoff(attempt)
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries} retry attempts failed")

    # If we get here, all retries failed
    if last_exception:
        raise last_exception
    else:
        raise Exception("All retry attempts failed with unknown error")


def handle_ai_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle AI error and return structured error response.

    Args:
        error: Exception object
        context: Optional context information

    Returns:
        Structured error response
    """
    context = context or {}

    # Determine error type and response
    if isinstance(error, AISecurityError):
        error_type = "security_violation"
        user_message = "Your request was blocked for security reasons. Please rephrase your query."
        status_code = 400

    elif isinstance(error, AIValidationError):
        error_type = "validation_error"
        user_message = "Unable to process AI response. Please try again."
        status_code = 500

    elif isinstance(error, AICostLimitError):
        error_type = "cost_limit_exceeded"
        user_message = "You have exceeded your usage limit. Please try again later."
        status_code = 429

    elif isinstance(error, AITimeoutError):
        error_type = "timeout"
        user_message = "Request timed out. Please try again with a shorter query."
        status_code = 504

    elif isinstance(error, AIRateLimitError):
        error_type = "rate_limit_exceeded"
        user_message = "Too many requests. Please wait a moment and try again."
        status_code = 429

    else:
        error_type = "unknown_error"
        user_message = "An unexpected error occurred. Please try again."
        status_code = 500

    # Log the error
    logger.error(
        f"AI Error [{error_type}]: {sanitize_error_message(error)}", extra={"context": context}
    )

    # Return structured response
    return {
        "error": True,
        "error_type": error_type,
        "message": user_message,
        "status_code": status_code,
        "timestamp": time.time(),
        "context": context,
    }


def create_fallback_response(
    response_type: str, reason: str = "AI service unavailable"
) -> Dict[str, Any]:
    """
    Create a fallback response when AI fails.

    Args:
        response_type: Type of response (intent, ranking, etc.)
        reason: Reason for fallback

    Returns:
        Fallback response
    """
    logger.warning(f"Creating fallback response for {response_type}: {reason}")

    if response_type == "intent":
        return {
            "category": "Other",
            "subject": "Not specified",
            "semester": "Not specified",
            "max_price": None,
            "condition": "Any",
            "intent_summary": "Unable to extract intent. Using default values.",
            "fallback": True,
            "fallback_reason": reason,
        }

    elif response_type == "ranking":
        return {
            "results": [],
            "fallback": True,
            "fallback_reason": reason,
        }

    else:
        return {
            "fallback": True,
            "fallback_reason": reason,
        }


class ErrorBudget:
    """
    Track error budget to prevent cascading failures.

    Implements circuit breaker pattern.
    """

    def __init__(self, max_errors: int = 10, window_seconds: int = 60):
        """
        Initialize error budget.

        Args:
            max_errors: Maximum errors allowed in window
            window_seconds: Time window in seconds
        """
        self.max_errors = max_errors
        self.window_seconds = window_seconds
        self.errors: list[float] = []
        self.circuit_open = False
        self.circuit_open_until = 0.0

    def record_error(self):
        """Record an error occurrence."""
        current_time = time.time()
        self.errors.append(current_time)

        # Remove old errors outside window
        cutoff_time = current_time - self.window_seconds
        self.errors = [t for t in self.errors if t > cutoff_time]

        # Check if circuit should open
        if len(self.errors) >= self.max_errors:
            self.circuit_open = True
            self.circuit_open_until = current_time + self.window_seconds
            logger.error(
                f"Circuit breaker opened: {len(self.errors)} errors in {self.window_seconds}s"
            )

    def record_success(self):
        """Record a successful operation."""
        current_time = time.time()

        # Close circuit if cooldown period passed
        if self.circuit_open and current_time > self.circuit_open_until:
            self.circuit_open = False
            self.errors = []
            logger.info("Circuit breaker closed after successful operation")

    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        current_time = time.time()

        # Auto-close circuit after cooldown
        if self.circuit_open and current_time > self.circuit_open_until:
            self.circuit_open = False
            self.errors = []
            logger.info("Circuit breaker auto-closed after cooldown")

        return self.circuit_open

    def get_error_rate(self) -> float:
        """Get current error rate (errors per second)."""
        if not self.errors:
            return 0.0

        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        recent_errors = [t for t in self.errors if t > cutoff_time]

        return len(recent_errors) / self.window_seconds


# Global error budget for AI service
ai_error_budget = ErrorBudget(max_errors=10, window_seconds=60)
