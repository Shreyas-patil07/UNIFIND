"""
Test data factories for creating realistic test objects.
Provides reusable factories for all domain models.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict


class UserFactory:
    """Factory for creating test user data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create user data with optional overrides."""
        user_id = kwargs.get("id", f"user-{uuid.uuid4().hex[:8]}")

        return {
            "id": user_id,
            "firebase_uid": kwargs.get("firebase_uid", f"firebase-{user_id}"),
            "email": kwargs.get("email", f"{user_id}@example.com"),
            "name": kwargs.get("name", f"User {user_id}"),
            "university": kwargs.get("university", "Test University"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "email_verified": kwargs.get("email_verified", True),
            "profile_picture": kwargs.get("profile_picture", f"https://example.com/{user_id}.jpg"),
            "bio": kwargs.get("bio", "Test bio"),
            "phone": kwargs.get("phone", "+1234567890"),
            "rating": kwargs.get("rating", 5.0),
            "total_reviews": kwargs.get("total_reviews", 0),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple users."""
        return [UserFactory.create(**kwargs) for _ in range(count)]


class ProductFactory:
    """Factory for creating test product data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create product data with optional overrides."""
        product_id = kwargs.get("id", f"product-{uuid.uuid4().hex[:8]}")

        return {
            "id": product_id,
            "title": kwargs.get("title", f"Product {product_id}"),
            "description": kwargs.get("description", "Test product description"),
            "price": kwargs.get("price", 99.99),
            "category": kwargs.get("category", "Electronics"),
            "subcategory": kwargs.get("subcategory", "Laptops"),
            "condition": kwargs.get("condition", "Like New"),
            "seller_id": kwargs.get("seller_id", "test-user-123"),
            "images": kwargs.get("images", [f"https://example.com/{product_id}.jpg"]),
            "status": kwargs.get("status", "active"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "updated_at": kwargs.get("updated_at", datetime.now().isoformat()),
            "views": kwargs.get("views", 0),
            "location": kwargs.get("location", "Test Location"),
            "tags": kwargs.get("tags", ["test", "product"]),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple products."""
        return [ProductFactory.create(**kwargs) for _ in range(count)]

    @staticmethod
    def create_sold(**kwargs) -> Dict[str, Any]:
        """Create a sold product."""
        kwargs["status"] = "sold"
        kwargs["sold_at"] = kwargs.get("sold_at", datetime.now().isoformat())
        kwargs["sold_to"] = kwargs.get("sold_to", "buyer-123")
        return ProductFactory.create(**kwargs)


class TransactionFactory:
    """Factory for creating test transaction data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create transaction data with optional overrides."""
        transaction_id = kwargs.get("id", f"transaction-{uuid.uuid4().hex[:8]}")

        return {
            "id": transaction_id,
            "product_id": kwargs.get("product_id", "test-product-123"),
            "seller_id": kwargs.get("seller_id", "test-user-123"),
            "buyer_id": kwargs.get("buyer_id", "test-buyer-456"),
            "amount": kwargs.get("amount", 99.99),
            "status": kwargs.get("status", "completed"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "completed_at": kwargs.get("completed_at", datetime.now().isoformat()),
            "payment_method": kwargs.get("payment_method", "cash"),
            "notes": kwargs.get("notes", ""),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple transactions."""
        return [TransactionFactory.create(**kwargs) for _ in range(count)]

    @staticmethod
    def create_pending(**kwargs) -> Dict[str, Any]:
        """Create a pending transaction."""
        kwargs["status"] = "pending"
        kwargs.pop("completed_at", None)
        return TransactionFactory.create(**kwargs)


class ReviewFactory:
    """Factory for creating test review data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create review data with optional overrides."""
        review_id = kwargs.get("id", f"review-{uuid.uuid4().hex[:8]}")

        return {
            "id": review_id,
            "reviewer_id": kwargs.get("reviewer_id", "test-user-123"),
            "reviewed_user_id": kwargs.get("reviewed_user_id", "test-user-456"),
            "product_id": kwargs.get("product_id", "test-product-123"),
            "transaction_id": kwargs.get("transaction_id", "test-transaction-123"),
            "rating": kwargs.get("rating", 5),
            "comment": kwargs.get("comment", "Great seller!"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple reviews."""
        return [ReviewFactory.create(**kwargs) for _ in range(count)]


class ChatRoomFactory:
    """Factory for creating test chat room data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create chat room data with optional overrides."""
        user1 = kwargs.get("user1_id", "user1")
        user2 = kwargs.get("user2_id", "user2")
        room_id = kwargs.get("id", f"{user1}_{user2}")

        return {
            "id": room_id,
            "participants": kwargs.get("participants", [user1, user2]),
            "product_id": kwargs.get("product_id"),
            "last_message": kwargs.get("last_message", "Hello"),
            "last_message_time": kwargs.get("last_message_time", datetime.now().isoformat()),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "unread_count": kwargs.get("unread_count", {}),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple chat rooms."""
        return [ChatRoomFactory.create(**kwargs) for _ in range(count)]


class MessageFactory:
    """Factory for creating test message data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create message data with optional overrides."""
        message_id = kwargs.get("id", f"message-{uuid.uuid4().hex[:8]}")

        return {
            "id": message_id,
            "chat_room_id": kwargs.get("chat_room_id", "user1_user2"),
            "sender_id": kwargs.get("sender_id", "user1"),
            "content": kwargs.get("content", "Test message"),
            "is_read": kwargs.get("is_read", False),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "product_id": kwargs.get("product_id"),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple messages."""
        return [MessageFactory.create(**kwargs) for _ in range(count)]


class NeedFactory:
    """Factory for creating test need data."""

    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """Create need data with optional overrides."""
        need_id = kwargs.get("id", f"need-{uuid.uuid4().hex[:8]}")

        return {
            "id": need_id,
            "user_id": kwargs.get("user_id", "test-user-123"),
            "title": kwargs.get("title", "Looking for laptop"),
            "description": kwargs.get("description", "Need a laptop for school"),
            "category": kwargs.get("category", "Electronics"),
            "budget_min": kwargs.get("budget_min", 500.0),
            "budget_max": kwargs.get("budget_max", 1000.0),
            "status": kwargs.get("status", "active"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "expires_at": kwargs.get(
                "expires_at", (datetime.now() + timedelta(days=30)).isoformat()
            ),
            "keywords": kwargs.get("keywords", ["laptop", "computer"]),
            "matched_products": kwargs.get("matched_products", []),
        }

    @staticmethod
    def create_batch(count: int, **kwargs) -> list:
        """Create multiple needs."""
        return [NeedFactory.create(**kwargs) for _ in range(count)]


# ==================== HELPER FUNCTIONS ====================


def create_user_with_products(mock_db, user_count: int = 1, products_per_user: int = 3):
    """Create users with associated products."""
    users = []
    products = []

    for i in range(user_count):
        user = UserFactory.create(id=f"user-{i}")
        mock_db.collection("users").document(user["id"]).set(user)
        users.append(user)

        for j in range(products_per_user):
            product = ProductFactory.create(id=f"product-{i}-{j}", seller_id=user["id"])
            mock_db.collection("products").document(product["id"]).set(product)
            products.append(product)

    return users, products


def create_transaction_with_review(mock_db, buyer_id: str, seller_id: str):
    """Create a complete transaction with product and review."""
    # Create product
    product = ProductFactory.create_sold(seller_id=seller_id, sold_to=buyer_id)
    mock_db.collection("products").document(product["id"]).set(product)

    # Create transaction
    transaction = TransactionFactory.create(
        product_id=product["id"], seller_id=seller_id, buyer_id=buyer_id
    )
    mock_db.collection("transactions").document(transaction["id"]).set(transaction)

    # Create review
    review = ReviewFactory.create(
        reviewer_id=buyer_id,
        reviewed_user_id=seller_id,
        product_id=product["id"],
        transaction_id=transaction["id"],
    )
    mock_db.collection("reviews").document(review["id"]).set(review)

    return product, transaction, review


def create_chat_with_messages(mock_db, user1_id: str, user2_id: str, message_count: int = 5):
    """Create a chat room with messages."""
    # Create chat room
    chat_room = ChatRoomFactory.create(user1_id=user1_id, user2_id=user2_id)
    mock_db.collection("chat_rooms").document(chat_room["id"]).set(chat_room)

    # Create messages
    messages = []
    for i in range(message_count):
        sender = user1_id if i % 2 == 0 else user2_id
        message = MessageFactory.create(
            chat_room_id=chat_room["id"], sender_id=sender, content=f"Message {i+1}"
        )
        mock_db.collection("messages").document(message["id"]).set(message)
        messages.append(message)

    return chat_room, messages
