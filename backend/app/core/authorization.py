"""
Centralized Authorization Module
Provides reusable permission helpers and resource ownership validation.
"""

import logging
from functools import wraps
from typing import Callable, Optional

from fastapi import HTTPException, status
from google.cloud.firestore_v1 import Client as FirestoreClient

logger = logging.getLogger(__name__)


class AuthorizationError(HTTPException):
    """Custom exception for authorization failures."""

    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ResourceNotFoundError(HTTPException):
    """Custom exception for resource not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} not found: {resource_id}",
        )


class PermissionValidator:
    """
    Centralized permission validation logic.
    All ownership and authorization checks go through this class.
    """

    def __init__(self, db: FirestoreClient):
        self.db = db

    # ==================== PRODUCT PERMISSIONS ====================

    def validate_product_ownership(
        self, product_id: str, user_id: str, require_active: bool = False
    ) -> dict:
        """
        Validate that user owns the product.

        Args:
            product_id: Product document ID
            user_id: User ID to validate
            require_active: If True, product must be active

        Returns:
            dict: Product data if authorized

        Raises:
            ResourceNotFoundError: Product doesn't exist
            AuthorizationError: User doesn't own the product
        """
        product_ref = self.db.collection("products").document(product_id)
        product_doc = product_ref.get()

        if not product_doc.exists:
            raise ResourceNotFoundError("Product", product_id)

        product_data = product_doc.to_dict()

        if product_data.get("seller_id") != user_id:
            logger.warning(
                f"Authorization failed: User {user_id} attempted to access "
                f"product {product_id} owned by {product_data.get('seller_id')}"
            )
            raise AuthorizationError("You don't have permission to modify this product")

        if require_active and not product_data.get("is_active", False):
            raise AuthorizationError("Product is not active")

        return product_data

    def can_view_product_details(self, product_id: str, user_id: Optional[str] = None) -> bool:
        """
        Check if user can view product details (including sold products).
        Sellers can always view their own products.
        """
        product_ref = self.db.collection("products").document(product_id)
        product_doc = product_ref.get()

        if not product_doc.exists:
            return False

        product_data = product_doc.to_dict()

        # Seller can always view
        if user_id and product_data.get("seller_id") == user_id:
            return True

        # Others can only view active products
        return product_data.get("is_active", False)

    # ==================== CHAT PERMISSIONS ====================

    def validate_chat_participant(self, chat_room_id: str, user_id: str) -> dict:
        """
        Validate that user is a participant in the chat room.

        Args:
            chat_room_id: Chat room document ID
            user_id: User ID to validate

        Returns:
            dict: Chat room data if authorized

        Raises:
            ResourceNotFoundError: Chat room doesn't exist
            AuthorizationError: User is not a participant
        """
        chat_ref = self.db.collection("chat_rooms").document(chat_room_id)
        chat_doc = chat_ref.get()

        if not chat_doc.exists:
            raise ResourceNotFoundError("Chat room", chat_room_id)

        chat_data = chat_doc.to_dict()
        participants = chat_data.get("participants", [])

        if user_id not in participants:
            logger.warning(
                f"Authorization failed: User {user_id} attempted to access "
                f"chat room {chat_room_id} without being a participant"
            )
            raise AuthorizationError("You are not a participant in this chat")

        return chat_data

    def validate_chat_creation(self, user1_id: str, user2_id: str, requesting_user_id: str) -> None:
        """
        Validate that requesting user is one of the chat participants.

        Args:
            user1_id: First participant
            user2_id: Second participant
            requesting_user_id: User making the request

        Raises:
            AuthorizationError: Requesting user is not a participant
        """
        if requesting_user_id not in [user1_id, user2_id]:
            logger.warning(
                f"Authorization failed: User {requesting_user_id} attempted to "
                f"create/access chat between {user1_id} and {user2_id}"
            )
            raise AuthorizationError("You can only create chats where you are a participant")

    # ==================== REVIEW PERMISSIONS ====================

    def validate_review_authorization(
        self, reviewer_id: str, reviewee_id: str, product_id: Optional[str] = None
    ) -> None:
        """
        Validate that reviewer can review the reviewee.

        Rules:
        - Cannot review yourself
        - Must have a completed transaction (if product_id provided)
        - Cannot submit duplicate reviews for same transaction

        Args:
            reviewer_id: User submitting the review
            reviewee_id: User being reviewed
            product_id: Optional product ID for transaction verification

        Raises:
            AuthorizationError: Review not authorized
        """
        # Cannot review yourself
        if reviewer_id == reviewee_id:
            raise AuthorizationError("You cannot review yourself")

        # If product_id provided, verify transaction exists
        if product_id:
            # Check if product exists and was sold
            product_ref = self.db.collection("products").document(product_id)
            product_doc = product_ref.get()

            if not product_doc.exists:
                raise ResourceNotFoundError("Product", product_id)

            product_data = product_doc.to_dict()

            # Verify transaction occurred
            # Reviewer must be either buyer or seller
            seller_id = product_data.get("seller_id")
            buyer_id = product_data.get("buyer_id")

            if reviewer_id not in [seller_id, buyer_id]:
                raise AuthorizationError("You can only review users you've transacted with")

            # Verify reviewee is the other party
            if reviewer_id == seller_id and reviewee_id != buyer_id:
                raise AuthorizationError("Invalid review target")
            if reviewer_id == buyer_id and reviewee_id != seller_id:
                raise AuthorizationError("Invalid review target")

            # Check for duplicate review
            existing_reviews = (
                self.db.collection("reviews")
                .where("reviewer_id", "==", reviewer_id)
                .where("reviewee_id", "==", reviewee_id)
                .where("product_id", "==", product_id)
                .limit(1)
                .get()
            )

            if len(list(existing_reviews)) > 0:
                raise AuthorizationError("You have already reviewed this transaction")

    # ==================== NEED PERMISSIONS ====================

    def validate_need_ownership(self, need_id: str, user_id: str) -> dict:
        """
        Validate that user owns the need.

        Args:
            need_id: Need document ID
            user_id: User ID to validate

        Returns:
            dict: Need data if authorized

        Raises:
            ResourceNotFoundError: Need doesn't exist
            AuthorizationError: User doesn't own the need
        """
        need_ref = self.db.collection("needs").document(need_id)
        need_doc = need_ref.get()

        if not need_doc.exists:
            raise ResourceNotFoundError("Need", need_id)

        need_data = need_doc.to_dict()

        if need_data.get("user_id") != user_id:
            logger.warning(
                f"Authorization failed: User {user_id} attempted to access "
                f"need {need_id} owned by {need_data.get('user_id')}"
            )
            raise AuthorizationError("You don't have permission to access this need")

        return need_data

    # ==================== TRANSACTION PERMISSIONS ====================

    def validate_transaction_access(self, product_id: str, user_id: str) -> dict:
        """
        Validate that user can access transaction history for a product.
        Only the seller can view transaction history.

        Args:
            product_id: Product document ID
            user_id: User ID to validate

        Returns:
            dict: Product data if authorized

        Raises:
            ResourceNotFoundError: Product doesn't exist
            AuthorizationError: User is not the seller
        """
        return self.validate_product_ownership(product_id, user_id, require_active=False)

    # ==================== USER PERMISSIONS ====================

    def validate_self_only_access(
        self, target_user_id: str, requesting_user_id: str, action: str = "access this resource"
    ) -> None:
        """
        Validate that user can only access their own resources.

        Args:
            target_user_id: User ID of the resource owner
            requesting_user_id: User ID making the request
            action: Description of the action for error message

        Raises:
            AuthorizationError: User attempting to access another user's resource
        """
        if target_user_id != requesting_user_id:
            logger.warning(
                f"Authorization failed: User {requesting_user_id} attempted to "
                f"{action} for user {target_user_id}"
            )
            raise AuthorizationError(f"You can only {action} for yourself")

    def validate_friendship(self, user1_id: str, user2_id: str) -> bool:
        """
        Check if two users are friends.

        Args:
            user1_id: First user ID
            user2_id: Second user ID

        Returns:
            bool: True if users are friends
        """
        # Check user1's friends list
        user1_ref = self.db.collection("users").document(user1_id)
        user1_doc = user1_ref.get()

        if not user1_doc.exists:
            return False

        user1_data = user1_doc.to_dict()
        friends = user1_data.get("friends", [])

        return user2_id in friends


# ==================== DEPENDENCY INJECTION ====================


def get_permission_validator(db: FirestoreClient) -> PermissionValidator:
    """
    Factory function to create PermissionValidator instance.
    Use this in FastAPI dependencies.
    """
    return PermissionValidator(db)


# ==================== DECORATOR FOR OWNERSHIP VALIDATION ====================


def require_ownership(
    resource_type: str, id_param: str = "resource_id", user_param: str = "current_user"
):
    """
    Decorator to enforce resource ownership.

    Usage:
        @require_ownership("product", id_param="product_id")
        async def update_product(product_id: str, current_user: str = Depends(get_current_user)):
            ...

    Args:
        resource_type: Type of resource (product, need, etc.)
        id_param: Name of the parameter containing resource ID
        user_param: Name of the parameter containing user ID
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            resource_id = kwargs.get(id_param)
            user_id = kwargs.get(user_param)

            if not resource_id or not user_id:
                raise ValueError(f"Missing required parameters: {id_param} or {user_param}")

            # Validation logic would go here
            # This is a simplified version - full implementation would
            # integrate with PermissionValidator

            return await func(*args, **kwargs)

        return wrapper

    return decorator
