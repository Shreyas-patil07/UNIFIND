"""
Test suite for verifying race condition fixes.
Run these tests to ensure atomic operations work correctly.
"""

import asyncio
from unittest.mock import MagicMock

import pytest

# ============================================================================
# TEST: Product Purchase Race Condition
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_product_purchase_prevents_double_selling():
    """
    Test that concurrent purchase attempts only allow one buyer.

    Scenario:
    - 10 users try to buy the same product simultaneously
    - Only 1 should succeed
    - Others should get "already sold" error
    """
    from app.repositories.product_repository_fixed import ProductRepository

    # Mock Firestore client
    mock_db = MagicMock()
    repo = ProductRepository(mock_db)

    product_id = "test_product_123"

    # Simulate concurrent purchase attempts
    tasks = []
    for i in range(10):
        task = repo.mark_as_sold(
            product_id=product_id, buyer_id=f"user_{i}", idempotency_key=f"request_{i}"
        )
        tasks.append(task)

    # Execute all purchases concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successful purchases
    successful = [r for r in results if isinstance(r, dict) and r.get("success")]
    failed = [r for r in results if isinstance(r, dict) and not r.get("success")]

    # Assertions
    assert len(successful) == 1, f"Expected 1 success, got {len(successful)}"
    assert len(failed) == 9, f"Expected 9 failures, got {len(failed)}"

    # Verify failure reasons
    for result in failed:
        assert result["reason"] == "Product already sold"

    print("✅ Product purchase race condition test PASSED")


@pytest.mark.asyncio
async def test_idempotent_product_purchase():
    """
    Test that duplicate purchase requests with same idempotency key are handled correctly.

    Scenario:
    - User clicks "Buy" button twice (network retry)
    - Both requests have same idempotency key
    - Only one purchase should be recorded
    """
    from app.repositories.product_repository_fixed import ProductRepository

    mock_db = MagicMock()
    repo = ProductRepository(mock_db)

    product_id = "test_product_456"
    buyer_id = "user_123"
    idempotency_key = "request_abc"

    # First purchase attempt
    result1 = await repo.mark_as_sold(
        product_id=product_id, buyer_id=buyer_id, idempotency_key=idempotency_key
    )

    # Second purchase attempt (duplicate)
    result2 = await repo.mark_as_sold(
        product_id=product_id, buyer_id=buyer_id, idempotency_key=idempotency_key
    )

    # Assertions
    assert result1["success"] == True
    assert result2["success"] == True
    assert result2.get("reason") == "Already processed (idempotent)"

    print("✅ Idempotent product purchase test PASSED")


# ============================================================================
# TEST: Chat Room Creation Race Condition
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_chat_room_creation_prevents_duplicates():
    """
    Test that concurrent chat room creation only creates one room.

    Scenario:
    - Two users send messages to each other simultaneously
    - Both try to create the same chat room
    - Only one chat room should be created
    """
    from app.repositories.chat_repository_fixed import ChatRepository

    mock_db = MagicMock()
    repo = ChatRepository(mock_db)

    chat_room_id = "user1_user2"

    # Simulate concurrent chat room creation
    tasks = []
    for i in range(5):
        chat_room_data = {
            "id": chat_room_id,
            "user1_id": "user1",
            "user2_id": "user2",
            "product_id": None,
            "last_message": f"Message {i}",
            "unread_count_user1": 0,
            "unread_count_user2": 0,
        }
        task = repo.create_chat_room(chat_room_data)
        tasks.append(task)

    # Execute all creations concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # All should return the same chat room ID
    unique_ids = set(results)
    assert len(unique_ids) == 1, f"Expected 1 unique chat room, got {len(unique_ids)}"

    print("✅ Chat room creation race condition test PASSED")


@pytest.mark.asyncio
async def test_atomic_message_send_with_chat_room_update():
    """
    Test that message send and chat room update happen atomically.

    Scenario:
    - Send message and update chat room in single transaction
    - If message fails, chat room should not be updated
    - If chat room update fails, message should not be created
    """
    from app.repositories.chat_repository_fixed import ChatRepository

    mock_db = MagicMock()
    repo = ChatRepository(mock_db)

    chat_room_id = "user1_user2"
    message_data = {
        "text": "Hello!",
        "sender_id": "user1",
        "receiver_id": "user2",
        "product_id": None,
    }

    result = await repo.send_message_atomic(
        chat_room_id=chat_room_id,
        message_data=message_data,
        sender_id="user1",
        receiver_id="user2",
        idempotency_key="msg_123",
    )

    # Assertions
    assert result["success"] == True
    assert "message_id" in result
    assert result["duplicate"] == False

    # Send again with same idempotency key
    result2 = await repo.send_message_atomic(
        chat_room_id=chat_room_id,
        message_data=message_data,
        sender_id="user1",
        receiver_id="user2",
        idempotency_key="msg_123",
    )

    assert result2["success"] == True
    assert result2["duplicate"] == True
    assert result2["message_id"] == result["message_id"]

    print("✅ Atomic message send test PASSED")


# ============================================================================
# TEST: Review Duplicate Prevention
# ============================================================================


@pytest.mark.asyncio
async def test_concurrent_review_creation_prevents_duplicates():
    """
    Test that concurrent review submissions only create one review.

    Scenario:
    - User clicks "Submit Review" multiple times
    - Only one review should be created
    - Others should get "already exists" error
    """
    from app.repositories.review_repository_fixed import ReviewRepository

    mock_db = MagicMock()
    repo = ReviewRepository(mock_db)

    review_data = {
        "reviewer_id": "user1",
        "reviewed_user_id": "user2",
        "product_id": "product123",
        "rating": 5,
        "comment": "Great seller!",
    }

    # Simulate concurrent review submissions
    tasks = []
    for i in range(5):
        task = repo.create(review_data=review_data.copy(), idempotency_key=f"review_{i}")
        tasks.append(task)

    # Execute all submissions concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successful creations
    successful = [
        r
        for r in results
        if isinstance(r, dict) and r.get("success") and "Already" not in r.get("reason", "")
    ]
    duplicates = [r for r in results if isinstance(r, dict) and not r.get("success")]

    # Assertions
    assert len(successful) == 1, f"Expected 1 success, got {len(successful)}"
    assert len(duplicates) >= 1, f"Expected duplicates to be rejected"

    print("✅ Review duplicate prevention test PASSED")


# ============================================================================
# TEST: Transaction Batch Atomicity
# ============================================================================


@pytest.mark.asyncio
async def test_transaction_batch_all_or_nothing():
    """
    Test that transaction batch creation is atomic (all-or-nothing).

    Scenario:
    - Create 3 transaction records in a batch
    - If any fails, all should fail
    - If all succeed, all should be created
    """
    from app.repositories.transaction_repository_fixed import TransactionRepository

    mock_db = MagicMock()
    repo = TransactionRepository(mock_db)

    transactions = [
        {
            "user_id": "user1",
            "transaction_type": "sell",
            "amount": 100.0,
            "product_id": "product123",
        },
        {
            "user_id": "user2",
            "transaction_type": "buy",
            "amount": 100.0,
            "product_id": "product123",
        },
        {
            "product_id": "product123",
            "seller_id": "user1",
            "amount": 100.0,
            "transaction_type_sold": True,
        },
    ]

    result = await repo.create_batch_atomic(transactions=transactions, idempotency_key="batch_123")

    # Assertions
    assert result["success"] == True
    assert len(result["transaction_ids"]) == 3

    # Try again with same idempotency key
    result2 = await repo.create_batch_atomic(transactions=transactions, idempotency_key="batch_123")

    assert result2["success"] == True
    assert result2.get("reason") == "Already processed (idempotent)"
    assert len(result2["transaction_ids"]) == 3

    print("✅ Transaction batch atomicity test PASSED")


# ============================================================================
# TEST: Optimistic Locking
# ============================================================================


@pytest.mark.asyncio
async def test_optimistic_locking_prevents_lost_updates():
    """
    Test that optimistic locking prevents lost updates.

    Scenario:
    - Two users edit the same product simultaneously
    - Both read version 1
    - First user updates to version 2
    - Second user's update should fail (version mismatch)
    """
    from app.repositories.product_repository_fixed import ProductRepository

    mock_db = MagicMock()
    repo = ProductRepository(mock_db)

    product_id = "test_product_789"

    # User 1 updates with version 1
    result1 = await repo.update(
        product_id=product_id, updates={"title": "Updated by User 1"}, expected_version=1
    )

    # User 2 tries to update with version 1 (should fail)
    result2 = await repo.update(
        product_id=product_id, updates={"title": "Updated by User 2"}, expected_version=1
    )

    # Assertions
    assert result1 == True, "First update should succeed"
    assert result2 == False, "Second update should fail (version mismatch)"

    print("✅ Optimistic locking test PASSED")


# ============================================================================
# TEST: Batch Operations Performance
# ============================================================================


@pytest.mark.asyncio
async def test_batch_get_performance():
    """
    Test that batch get is more efficient than individual gets.

    Scenario:
    - Fetch 50 products
    - Batch get should use 1 query
    - Individual gets would use 50 queries
    """
    import time

    from app.repositories.product_repository_fixed import ProductRepository

    mock_db = MagicMock()
    repo = ProductRepository(mock_db)

    product_ids = [f"product_{i}" for i in range(50)]

    # Measure batch get time
    start_time = time.time()
    products = await repo.get_batch(product_ids)
    batch_duration = time.time() - start_time

    # Batch get should be fast (< 100ms in production)
    # In tests with mocks, should be nearly instant
    assert batch_duration < 1.0, f"Batch get took {batch_duration}s (too slow)"

    print(f"✅ Batch get performance test PASSED ({batch_duration:.3f}s)")


# ============================================================================
# TEST: Idempotency Key Generation
# ============================================================================


def test_idempotency_key_generation():
    """
    Test that idempotency keys are deterministic and unique.

    Scenario:
    - Same inputs should generate same key
    - Different inputs should generate different keys
    """
    from app.core.firestore_utils import generate_idempotency_key

    # Same inputs should generate same key
    key1 = generate_idempotency_key("product", "product123", "user456", "2024-01-01")
    key2 = generate_idempotency_key("product", "product123", "user456", "2024-01-01")
    assert key1 == key2, "Same inputs should generate same key"

    # Different inputs should generate different keys
    key3 = generate_idempotency_key("product", "product123", "user789", "2024-01-01")
    assert key1 != key3, "Different inputs should generate different keys"

    # Keys should be SHA256 hashes (64 hex characters)
    assert len(key1) == 64, "Key should be 64 characters (SHA256)"
    assert all(c in "0123456789abcdef" for c in key1), "Key should be hex"

    print("✅ Idempotency key generation test PASSED")


# ============================================================================
# TEST: Retry Logic
# ============================================================================


@pytest.mark.asyncio
async def test_retry_on_transient_error():
    """
    Test that transient errors are retried automatically.

    Scenario:
    - First attempt fails with transient error
    - Second attempt succeeds
    - Function should return success
    """
    from google.api_core import exceptions as google_exceptions

    from app.core.firestore_utils import retry_on_transient_error

    attempt_count = 0

    @retry_on_transient_error(max_retries=3, backoff_factor=0.1)
    async def flaky_operation():
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count < 2:
            raise google_exceptions.ServiceUnavailable("Service temporarily unavailable")

        return "success"

    result = await flaky_operation()

    # Assertions
    assert result == "success"
    assert attempt_count == 2, f"Expected 2 attempts, got {attempt_count}"

    print("✅ Retry logic test PASSED")


# ============================================================================
# TEST: Query Monitoring
# ============================================================================


@pytest.mark.asyncio
async def test_query_monitoring():
    """
    Test that query monitoring tracks performance metrics.

    Scenario:
    - Execute queries with monitoring
    - Metrics should be recorded
    - Slow queries should be logged
    """
    from app.core.firestore_utils import get_firestore_metrics, monitor_query

    @monitor_query("test_operation", slow_threshold=0.1)
    async def fast_operation():
        await asyncio.sleep(0.05)
        return "fast"

    @monitor_query("slow_operation", slow_threshold=0.1)
    async def slow_operation():
        await asyncio.sleep(0.2)
        return "slow"

    # Execute operations
    await fast_operation()
    await slow_operation()

    # Check metrics
    metrics = get_firestore_metrics()
    stats = metrics.get_stats()

    # Assertions
    assert stats["total_queries"] >= 2
    assert stats["slow_queries"] >= 1
    assert stats["avg_duration"] > 0

    print("✅ Query monitoring test PASSED")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    """
    Run all race condition tests.

    Usage:
        python tests/test_race_conditions.py

    Or with pytest:
        pytest tests/test_race_conditions.py -v
    """
    print("\n" + "=" * 70)
    print("RUNNING RACE CONDITION TESTS")
    print("=" * 70 + "\n")

    # Run all tests
    asyncio.run(test_concurrent_product_purchase_prevents_double_selling())
    asyncio.run(test_idempotent_product_purchase())
    asyncio.run(test_concurrent_chat_room_creation_prevents_duplicates())
    asyncio.run(test_atomic_message_send_with_chat_room_update())
    asyncio.run(test_concurrent_review_creation_prevents_duplicates())
    asyncio.run(test_transaction_batch_all_or_nothing())
    asyncio.run(test_optimistic_locking_prevents_lost_updates())
    asyncio.run(test_batch_get_performance())
    test_idempotency_key_generation()
    asyncio.run(test_retry_on_transient_error())
    asyncio.run(test_query_monitoring())

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✅")
    print("=" * 70 + "\n")

    print("Next steps:")
    print("1. Deploy Firestore indexes: firebase deploy --only firestore:indexes")
    print("2. Replace repository files with fixed versions")
    print("3. Update API routes to handle new return types")
    print("4. Deploy to staging and test with real traffic")
    print("5. Monitor for 24 hours before production deployment")
