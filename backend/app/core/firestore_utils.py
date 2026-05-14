"""
Firestore utilities for monitoring, retry logic, and performance optimization.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable

from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


# ============================================================================
# MONITORING & PERFORMANCE TRACKING
# ============================================================================


class FirestoreMetrics:
    """Track Firestore operation metrics."""

    def __init__(self):
        self.query_count = 0
        self.slow_queries = []
        self.failed_queries = []
        self.total_duration = 0.0

    def record_query(self, operation: str, duration: float, success: bool = True):
        """Record a query execution."""
        self.query_count += 1
        self.total_duration += duration

        if duration > 1.0:  # Slow query threshold
            self.slow_queries.append(
                {"operation": operation, "duration": duration, "timestamp": time.time()}
            )

        if not success:
            self.failed_queries.append(
                {"operation": operation, "duration": duration, "timestamp": time.time()}
            )

    def get_stats(self) -> dict:
        """Get current metrics."""
        return {
            "total_queries": self.query_count,
            "slow_queries": len(self.slow_queries),
            "failed_queries": len(self.failed_queries),
            "avg_duration": self.total_duration / self.query_count if self.query_count > 0 else 0,
        }


# Global metrics instance
_metrics = FirestoreMetrics()


def get_firestore_metrics() -> FirestoreMetrics:
    """Get global Firestore metrics instance."""
    return _metrics


def monitor_query(operation_name: str, slow_threshold: float = 1.0):
    """
    Decorator to monitor Firestore query performance.

    Args:
        operation_name: Name of the operation for logging
        slow_threshold: Threshold in seconds for slow query warning

    Example:
        @monitor_query("get_product_by_id")
        async def get_by_id(self, product_id: str):
            # ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Log slow queries
                if duration > slow_threshold:
                    logger.warning(
                        f"SLOW QUERY: {operation_name} took {duration:.2f}s",
                        extra={
                            "operation": operation_name,
                            "duration": duration,
                            "threshold": slow_threshold,
                            "args_preview": str(args)[:100],
                        },
                    )
                else:
                    logger.debug(f"{operation_name} completed in {duration:.3f}s")

                # Record metrics
                _metrics.record_query(operation_name, duration, success=True)

                return result

            except Exception as e:
                success = False
                duration = time.time() - start_time

                logger.error(
                    f"QUERY FAILED: {operation_name} after {duration:.2f}s: {e}",
                    extra={
                        "operation": operation_name,
                        "duration": duration,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )

                # Record metrics
                _metrics.record_query(operation_name, duration, success=False)

                raise

        return wrapper

    return decorator


# ============================================================================
# RETRY LOGIC
# ============================================================================


def retry_on_transient_error(
    max_retries: int = 3, backoff_factor: float = 0.5, max_backoff: float = 10.0
):
    """
    Retry decorator for transient Firestore errors.

    Retries on:
    - DeadlineExceeded (timeout)
    - ServiceUnavailable (503)
    - InternalServerError (500)
    - Aborted (transaction conflicts)

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Base backoff time in seconds
        max_backoff: Maximum backoff time in seconds

    Example:
        @retry_on_transient_error(max_retries=3)
        async def get_by_id(self, product_id: str):
            # ...
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except (
                    google_exceptions.DeadlineExceeded,
                    google_exceptions.ServiceUnavailable,
                    google_exceptions.InternalServerError,
                    google_exceptions.Aborted,
                ) as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        wait_time = min(backoff_factor * (2**attempt), max_backoff)

                        logger.warning(
                            f"Transient error in {func.__name__}, "
                            f"retrying in {wait_time:.2f}s "
                            f"(attempt {attempt + 1}/{max_retries}): {e}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt + 1,
                                "max_retries": max_retries,
                                "wait_time": wait_time,
                                "error_type": type(e).__name__,
                            },
                        )

                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"Max retries exceeded for {func.__name__}: {e}",
                            extra={
                                "function": func.__name__,
                                "max_retries": max_retries,
                                "error_type": type(e).__name__,
                            },
                        )
                        raise

                except Exception as e:
                    # Don't retry non-transient errors
                    logger.error(
                        f"Non-retryable error in {func.__name__}: {e}",
                        extra={"function": func.__name__, "error_type": type(e).__name__},
                    )
                    raise

            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# BATCH UTILITIES
# ============================================================================


def chunk_list(items: list, chunk_size: int):
    """
    Split a list into chunks of specified size.

    Args:
        items: List to split
        chunk_size: Size of each chunk

    Yields:
        Chunks of the list

    Example:
        for chunk in chunk_list(product_ids, 500):
            process_batch(chunk)
    """
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


async def batch_get_documents(db, collection_name: str, doc_ids: list) -> list:
    """
    Efficiently batch fetch documents by IDs.

    Args:
        db: Firestore client
        collection_name: Collection name
        doc_ids: List of document IDs

    Returns:
        List of document data dicts

    Example:
        products = await batch_get_documents(db, 'products', product_ids)
    """
    if not doc_ids:
        return []

    collection = db.collection(collection_name)
    documents = []

    # Firestore batch get supports up to 500 documents
    for chunk in chunk_list(doc_ids, 500):
        doc_refs = [collection.document(doc_id) for doc_id in chunk]

        # Batch get all documents in this chunk
        docs = db.get_all(doc_refs)

        for doc in docs:
            if doc.exists:
                doc_data = doc.to_dict()
                doc_data["id"] = doc.id
                documents.append(doc_data)

    return documents


# ============================================================================
# IDEMPOTENCY UTILITIES
# ============================================================================

import hashlib
import uuid


def generate_idempotency_key(*args) -> str:
    """
    Generate deterministic idempotency key from arguments.

    Args:
        *args: Arguments to hash

    Returns:
        SHA256 hash as hex string

    Example:
        key = generate_idempotency_key('product', product_id, user_id, timestamp)
    """
    key_string = "_".join(str(arg) for arg in args)
    return hashlib.sha256(key_string.encode()).hexdigest()


def generate_request_id() -> str:
    """
    Generate unique request ID for idempotency.

    Returns:
        UUID4 as string

    Example:
        request_id = generate_request_id()
    """
    return str(uuid.uuid4())


# ============================================================================
# TIMESTAMP UTILITIES
# ============================================================================

from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Get current UTC timestamp.

    Returns:
        Current datetime in UTC

    Example:
        created_at = utc_now()
    """
    return datetime.now(timezone.utc)


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is in UTC timezone.

    Args:
        dt: Datetime to convert

    Returns:
        Datetime in UTC

    Example:
        utc_time = ensure_utc(some_datetime)
    """
    if dt.tzinfo is None:
        # Naive datetime, assume UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        return dt.astimezone(timezone.utc)


# ============================================================================
# QUERY OPTIMIZATION UTILITIES
# ============================================================================


class QueryBuilder:
    """
    Helper class for building optimized Firestore queries.
    
    Example:
        query = QueryBuilder(db.collection('products'))\\
            .where('category', '==', 'electronics')\\
            .where('is_active', '==', True)\\
            .order_by('posted_date', 'DESCENDING')\\
            .limit(20)\\
            .build()
    """

    def __init__(self, collection_ref):
        self.query = collection_ref

    def where(self, field: str, op: str, value: Any):
        """Add where clause."""
        from google.cloud.firestore_v1.base_query import FieldFilter

        self.query = self.query.where(filter=FieldFilter(field, op, value))
        return self

    def order_by(self, field: str, direction: str = "ASCENDING"):
        """Add order by clause."""
        self.query = self.query.order_by(field, direction=direction)
        return self

    def limit(self, count: int):
        """Add limit clause."""
        self.query = self.query.limit(count)
        return self

    def offset(self, count: int):
        """Add offset clause (use cursor-based pagination instead if possible)."""
        self.query = self.query.offset(count)
        return self

    def start_after(self, doc_snapshot):
        """Add cursor for pagination."""
        self.query = self.query.start_after(doc_snapshot)
        return self

    def build(self):
        """Build and return the query."""
        return self.query


# ============================================================================
# TRANSACTION HELPERS
# ============================================================================


async def run_transaction(db, transaction_func: Callable, *args, **kwargs):
    """
    Run a Firestore transaction with automatic retry.

    Args:
        db: Firestore client
        transaction_func: Function decorated with @transactional
        *args, **kwargs: Arguments to pass to transaction function

    Returns:
        Result from transaction function

    Example:
        result = await run_transaction(db, update_product_atomic, product_id, updates)
    """
    transaction = db.transaction()

    try:
        return transaction_func(transaction, *args, **kwargs)
    except google_exceptions.Aborted as e:
        logger.warning(f"Transaction aborted, will be retried by Firestore: {e}")
        raise
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================


def validate_document_id(doc_id: str) -> bool:
    """
    Validate Firestore document ID.

    Args:
        doc_id: Document ID to validate

    Returns:
        True if valid, False otherwise

    Rules:
    - Must not be empty
    - Must not contain forward slashes
    - Must not be solely periods
    - Must be <= 1500 bytes
    """
    if not doc_id:
        return False

    if "/" in doc_id:
        return False

    if doc_id in [".", ".."]:
        return False

    if len(doc_id.encode("utf-8")) > 1500:
        return False

    return True


def validate_field_path(field_path: str) -> bool:
    """
    Validate Firestore field path.

    Args:
        field_path: Field path to validate

    Returns:
        True if valid, False otherwise
    """
    if not field_path:
        return False

    # Field paths cannot start or end with a period
    if field_path.startswith(".") or field_path.endswith("."):
        return False

    # Field paths cannot contain consecutive periods
    if ".." in field_path:
        return False

    return True


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Monitor and retry a query
-------------------------------------

from app.core.firestore_utils import monitor_query, retry_on_transient_error

class ProductRepository:
    @monitor_query("get_product_by_id", slow_threshold=0.5)
    @retry_on_transient_error(max_retries=3)
    async def get_by_id(self, product_id: str):
        doc = self.collection.document(product_id).get()
        # ...


Example 2: Batch fetch documents
---------------------------------

from app.core.firestore_utils import batch_get_documents

product_ids = ['id1', 'id2', 'id3', ...]
products = await batch_get_documents(db, 'products', product_ids)


Example 3: Generate idempotency key
------------------------------------

from app.core.firestore_utils import generate_idempotency_key

idempotency_key = generate_idempotency_key(
    'product_purchase',
    product_id,
    user_id,
    timestamp
)


Example 4: Build optimized query
---------------------------------

from app.core.firestore_utils import QueryBuilder

query = QueryBuilder(db.collection('products'))\\
    .where('category', '==', 'electronics')\\
    .where('is_active', '==', True)\\
    .order_by('posted_date', 'DESCENDING')\\
    .limit(20)\\
    .build()

products = list(query.stream())


Example 5: Get metrics
----------------------

from app.core.firestore_utils import get_firestore_metrics

metrics = get_firestore_metrics()
stats = metrics.get_stats()
print(f"Total queries: {stats['total_queries']}")
print(f"Slow queries: {stats['slow_queries']}")
print(f"Average duration: {stats['avg_duration']:.3f}s")
"""
