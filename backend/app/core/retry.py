"""
Retry logic and resilience patterns for external service calls.

Provides:
- Exponential backoff retry
- Circuit breaker pattern
- Timeout enforcement
- Fallback mechanisms
"""

import asyncio
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by stopping requests to failing services.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN for {func.__name__}. "
                    f"Service unavailable. Retry after {self.recovery_timeout}s"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    async def call_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Call async function through circuit breaker.

        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN for {func.__name__}. "
                    f"Service unavailable. Retry after {self.recovery_timeout}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker CLOSED - service recovered")

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker OPEN - {self.failure_count} failures exceeded threshold "
                f"({self.failure_threshold})"
            )

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self.last_failure_time,
            "recovery_timeout": self.recovery_timeout,
        }


# Global circuit breakers for external services
_circuit_breakers: Dict[str, CircuitBreaker] = {
    "firebase": CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    "gemini": CircuitBreaker(failure_threshold=3, recovery_timeout=30),
    "cloudinary": CircuitBreaker(failure_threshold=5, recovery_timeout=60),
    "email": CircuitBreaker(failure_threshold=3, recovery_timeout=120),
}


def get_circuit_breaker(service: str) -> CircuitBreaker:
    """
    Get circuit breaker for a service.

    Args:
        service: Service name (firebase, gemini, cloudinary, email)

    Returns:
        CircuitBreaker instance
    """
    if service not in _circuit_breakers:
        _circuit_breakers[service] = CircuitBreaker()
    return _circuit_breakers[service]


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    **kwargs,
) -> T:
    """
    Retry async function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
        **kwargs: Keyword arguments for func

    Returns:
        Function result

    Raises:
        Exception: If all retries fail
    """
    last_exception = None
    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
            result = await func(*args, **kwargs)
            if attempt > 1:
                logger.info(f"Retry succeeded on attempt {attempt} for {func.__name__}")
            return result

        except exceptions as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(
                    f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}",
                    exc_info=True,
                )
                raise

            # Calculate next delay with exponential backoff
            delay = min(delay * exponential_base, max_delay)

            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                f"Retrying in {delay:.2f}s..."
            )

            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise Exception(f"Retry failed for {func.__name__}")


def retry_sync_with_backoff(
    func: Callable[..., T],
    *args,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    **kwargs,
) -> T:
    """
    Retry synchronous function with exponential backoff.

    Args:
        func: Function to retry
        *args: Positional arguments for func
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
        **kwargs: Keyword arguments for func

    Returns:
        Function result

    Raises:
        Exception: If all retries fail
    """
    last_exception = None
    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
            result = func(*args, **kwargs)
            if attempt > 1:
                logger.info(f"Retry succeeded on attempt {attempt} for {func.__name__}")
            return result

        except exceptions as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(
                    f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}",
                    exc_info=True,
                )
                raise

            # Calculate next delay with exponential backoff
            delay = min(delay * exponential_base, max_delay)

            logger.warning(
                f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                f"Retrying in {delay:.2f}s..."
            )

            time.sleep(delay)

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise Exception(f"Retry failed for {func.__name__}")


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator to add retry logic to async functions.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @with_retry(max_attempts=3, initial_delay=1.0)
        async def fetch_data():
            # Your code here
            pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                *args,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                exceptions=exceptions,
                **kwargs,
            )

        return wrapper

    return decorator


def with_circuit_breaker(service: str):
    """
    Decorator to add circuit breaker to async functions.

    Args:
        service: Service name (firebase, gemini, cloudinary, email)

    Example:
        @with_circuit_breaker("gemini")
        async def call_gemini_api():
            # Your code here
            pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            breaker = get_circuit_breaker(service)
            return await breaker.call_async(func, *args, **kwargs)

        return wrapper

    return decorator


def with_timeout(seconds: float):
    """
    Decorator to add timeout to async functions.

    Args:
        seconds: Timeout in seconds

    Example:
        @with_timeout(30.0)
        async def long_running_task():
            # Your code here
            pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds}s")
                raise TimeoutError(f"Operation timed out after {seconds}s")

        return wrapper

    return decorator


def get_all_circuit_breaker_states() -> Dict[str, Dict[str, Any]]:
    """
    Get states of all circuit breakers.

    Returns:
        Dictionary of service name to circuit breaker state
    """
    return {service: breaker.get_state() for service, breaker in _circuit_breakers.items()}
