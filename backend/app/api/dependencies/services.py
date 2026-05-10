"""
Service dependencies for dependency injection.
"""
from app.core.database import get_db
from app.repositories import (
    UserRepository,
    ProductRepository,
    ChatRepository,
    TransactionRepository,
    FriendshipRepository,
    ReviewRepository,
    NeedRepository
)
from app.services.product_service import ProductService
from app.services.user_service import UserService
from app.services.chat_service import ChatService
from app.services.transaction_service import TransactionService
from app.services.review_service import ReviewService
from app.services.auth_service import AuthService
from app.services.need_service import NeedService


def get_product_service() -> ProductService:
    """Factory for ProductService with dependencies."""
    db = get_db()
    product_repo = ProductRepository(db)
    user_repo = UserRepository(db)
    return ProductService(product_repo, user_repo)


def get_user_service() -> UserService:
    """Factory for UserService with dependencies."""
    db = get_db()
    user_repo = UserRepository(db)
    friendship_repo = FriendshipRepository(db)
    return UserService(user_repo, friendship_repo)


def get_chat_service() -> ChatService:
    """Factory for ChatService with dependencies."""
    db = get_db()
    chat_repo = ChatRepository(db)
    friendship_repo = FriendshipRepository(db)
    return ChatService(chat_repo, friendship_repo)


def get_transaction_service() -> TransactionService:
    """Factory for TransactionService with dependencies."""
    db = get_db()
    transaction_repo = TransactionRepository(db)
    product_repo = ProductRepository(db)
    return TransactionService(transaction_repo, product_repo)


def get_review_service() -> ReviewService:
    """Factory for ReviewService with dependencies."""
    db = get_db()
    review_repo = ReviewRepository(db)
    user_repo = UserRepository(db)
    return ReviewService(review_repo, user_repo)


def get_auth_service() -> AuthService:
    """Factory for AuthService with dependencies."""
    db = get_db()
    user_repo = UserRepository(db)
    return AuthService(user_repo)


def get_need_service() -> NeedService:
    """Factory for NeedService with dependencies."""
    db = get_db()
    need_repo = NeedRepository(db)
    product_repo = ProductRepository(db)
    user_repo = UserRepository(db)
    return NeedService(need_repo, product_repo, user_repo)
