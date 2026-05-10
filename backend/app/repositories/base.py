"""
Abstract base repository interfaces.
These interfaces define contracts that all repository implementations must follow.
This enables easy database migration (e.g., Firestore → PostgreSQL) without changing business logic.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime

# Generic type for domain models
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface with common CRUD operations.
    All repositories should inherit from this and implement these methods.
    """
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> str:
        """Create new entity and return its ID."""
        pass
    
    @abstractmethod
    async def update(self, id: str, updates: Dict[str, Any]) -> bool:
        """Update entity. Returns True if successful."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete entity. Returns True if successful."""
        pass


class ProductRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    Product repository interface.
    Defines all product-related data access operations.
    """
    
    @abstractmethod
    async def get_all(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all products with optional filters and pagination."""
        pass
    
    @abstractmethod
    async def get_by_seller(
        self,
        seller_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all products for a seller."""
        pass
    
    @abstractmethod
    async def get_active_products(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all active (unsold) products."""
        pass
    
    @abstractmethod
    async def get_batch(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch fetch products by IDs."""
        pass
    
    @abstractmethod
    async def increment_view(self, product_id: str, user_id: str) -> bool:
        """Increment view count if user hasn't viewed before."""
        pass
    
    @abstractmethod
    async def mark_as_sold(self, product_id: str, buyer_id: Optional[str] = None) -> bool:
        """Mark product as sold."""
        pass
    
    @abstractmethod
    async def mark_as_active(self, product_id: str) -> bool:
        """Mark product as active again."""
        pass
    
    @abstractmethod
    async def verify_ownership(self, product_id: str, user_id: str) -> bool:
        """Verify if user owns the product."""
        pass
    
    @abstractmethod
    async def count_by_category(self, category: str) -> int:
        """Count products in a category."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search products by query string."""
        pass


class UserRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    User repository interface.
    Defines all user-related data access operations.
    """
    
    @abstractmethod
    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID."""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all users with pagination."""
        pass
    
    @abstractmethod
    async def search_by_name(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search users by name."""
        pass
    
    @abstractmethod
    async def get_profile_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID."""
        pass
    
    @abstractmethod
    async def create_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create a new user profile."""
        pass
    
    @abstractmethod
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        pass
    
    @abstractmethod
    async def get_profile_with_user(
        self,
        user_id: str,
        include_private: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Get combined user and profile data."""
        pass


class NeedRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    Need repository interface.
    Defines all need-related data access operations.
    """
    
    @abstractmethod
    async def get_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all needs posted by a user."""
        pass
    
    @abstractmethod
    async def get_open_needs(
        self,
        limit: int = 100,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all open needs."""
        pass
    
    @abstractmethod
    async def get_by_category(
        self,
        category: str,
        limit: int = 50,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get needs by category."""
        pass
    
    @abstractmethod
    async def get_recent_by_user(self, user_id: str, days: int = 1) -> List[Dict[str, Any]]:
        """Get recent needs by user (for rate limiting)."""
        pass
    
    @abstractmethod
    async def update_matched_listings(self, need_id: str, listing_ids: List[str]) -> bool:
        """Update matched listings for a need."""
        pass
    
    @abstractmethod
    async def add_interested_seller(self, need_id: str, seller_id: str) -> bool:
        """Add a seller to interested sellers list."""
        pass
    
    @abstractmethod
    async def mark_as_fulfilled(
        self,
        need_id: str,
        product_id: Optional[str] = None
    ) -> bool:
        """Mark a need as fulfilled."""
        pass
    
    @abstractmethod
    async def mark_as_expired(self, need_id: str) -> bool:
        """Mark a need as expired."""
        pass
    
    @abstractmethod
    async def verify_ownership(self, need_id: str, user_id: str) -> bool:
        """Verify if user owns the need."""
        pass
    
    @abstractmethod
    async def get_needs_by_college(
        self,
        college: str,
        limit: int = 50,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get open needs by college."""
        pass


class ChatRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    Chat repository interface.
    Defines all chat-related data access operations.
    """
    
    @abstractmethod
    async def get_by_participants(
        self,
        user1_id: str,
        user2_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get chat between two users."""
        pass
    
    @abstractmethod
    async def get_user_chats(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all chats for a user."""
        pass
    
    @abstractmethod
    async def add_message(
        self,
        chat_id: str,
        message_data: Dict[str, Any]
    ) -> bool:
        """Add a message to a chat."""
        pass
    
    @abstractmethod
    async def get_messages(
        self,
        chat_id: str,
        limit: int = 100,
        before_timestamp: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get messages from a chat with pagination."""
        pass
    
    @abstractmethod
    async def mark_as_read(self, chat_id: str, user_id: str) -> bool:
        """Mark chat as read for a user."""
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread chats for a user."""
        pass


class ReviewRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    Review repository interface.
    Defines all review-related data access operations.
    """
    
    @abstractmethod
    async def get_by_product(
        self,
        product_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all reviews for a product."""
        pass
    
    @abstractmethod
    async def get_by_user(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all reviews by a user."""
        pass
    
    @abstractmethod
    async def get_for_seller(
        self,
        seller_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all reviews for a seller."""
        pass
    
    @abstractmethod
    async def get_average_rating(self, seller_id: str) -> float:
        """Get average rating for a seller."""
        pass
    
    @abstractmethod
    async def has_reviewed(
        self,
        user_id: str,
        product_id: str
    ) -> bool:
        """Check if user has already reviewed a product."""
        pass


class TransactionRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    Transaction repository interface.
    Defines all transaction-related data access operations.
    """
    
    @abstractmethod
    async def get_by_buyer(
        self,
        buyer_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all transactions for a buyer."""
        pass
    
    @abstractmethod
    async def get_by_seller(
        self,
        seller_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all transactions for a seller."""
        pass
    
    @abstractmethod
    async def get_by_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction for a product."""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        transaction_id: str,
        status: str
    ) -> bool:
        """Update transaction status."""
        pass


class FriendshipRepositoryInterface(BaseRepository[Dict[str, Any]]):
    """
    Friendship repository interface.
    Defines all friendship-related data access operations.
    """
    
    @abstractmethod
    async def get_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all friends for a user."""
        pass
    
    @abstractmethod
    async def get_pending_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending friend requests for a user."""
        pass
    
    @abstractmethod
    async def get_sent_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get sent friend requests by a user."""
        pass
    
    @abstractmethod
    async def are_friends(self, user1_id: str, user2_id: str) -> bool:
        """Check if two users are friends."""
        pass
    
    @abstractmethod
    async def has_pending_request(self, from_user_id: str, to_user_id: str) -> bool:
        """Check if there's a pending friend request."""
        pass
    
    @abstractmethod
    async def accept_request(self, friendship_id: str) -> bool:
        """Accept a friend request."""
        pass
    
    @abstractmethod
    async def reject_request(self, friendship_id: str) -> bool:
        """Reject a friend request."""
        pass
