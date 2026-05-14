"""
Review service - business logic for review operations with transaction verification.
"""

import logging
from typing import Any, Dict, List

from app.core.authorization import PermissionValidator
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.schemas.review import ReviewCreate

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for review business logic."""

    def __init__(
        self,
        review_repo: ReviewRepository,
        user_repo: UserRepository,
        product_repo: ProductRepository,
        permission_validator: PermissionValidator,
    ):
        self.review_repo = review_repo
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.permission_validator = permission_validator

    async def create_review(self, review_data: ReviewCreate, reviewer_id: str) -> Dict[str, Any]:
        """
        Create a new review with comprehensive validation.

        Security checks:
        - Verify reviewer_id matches authenticated user
        - Prevent self-review
        - Verify transaction occurred (if product_id provided)
        - Prevent duplicate reviews

        Args:
            review_data: Review data
            reviewer_id: Authenticated reviewer ID

        Returns:
            Created review

        Raises:
            ValueError: If validation fails
        """
        # Verify reviewer_id matches authenticated user
        if review_data.reviewer_id != reviewer_id:
            raise ValueError("Cannot create review as another user")

        # Verify users exist
        reviewer = await self.user_repo.get_by_id(reviewer_id)
        if not reviewer:
            raise ValueError("Reviewer not found")

        reviewed_user = await self.user_repo.get_by_id(review_data.reviewed_user_id)
        if not reviewed_user:
            raise ValueError("Reviewed user not found")

        # Use centralized authorization validation
        self.permission_validator.validate_review_authorization(
            reviewer_id=reviewer_id,
            reviewee_id=review_data.reviewed_user_id,
            product_id=review_data.product_id,
        )

        # Additional check: If product_id provided, verify it's sold
        if review_data.product_id:
            product = await self.product_repo.get_by_id(review_data.product_id)
            if not product:
                raise ValueError("Product not found")

            if product.get("is_active", True):
                raise ValueError("Cannot review active product. Product must be marked as sold.")

            # Verify reviewer is involved in the transaction
            seller_id = product.get("seller_id")
            buyer_id = product.get("buyer_id")

            if reviewer_id not in [seller_id, buyer_id]:
                raise ValueError("You can only review users you've transacted with")

            # Verify reviewee is the other party
            expected_reviewee = buyer_id if reviewer_id == seller_id else seller_id
            if review_data.reviewed_user_id != expected_reviewee:
                raise ValueError("You can only review the other party in the transaction")

        # Check for duplicate review (additional check)
        existing = await self.review_repo.check_existing_review(
            reviewer_id, review_data.reviewed_user_id, review_data.product_id
        )

        if existing:
            raise ValueError("You have already reviewed this user for this product")

        # Create review
        review_dict = review_data.model_dump()
        review_id = await self.review_repo.create(review_dict)

        # Update user's rating
        await self._update_user_rating(review_data.reviewed_user_id)

        # Get created review
        review = await self.review_repo.get_by_id(review_id)

        logger.info(
            f"Created review {review_id} from {reviewer_id} for "
            f"{review_data.reviewed_user_id} (product: {review_data.product_id})"
        )

        return review

    async def get_reviews_for_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all reviews about a user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of reviews with reviewer info
        """
        reviews = await self.review_repo.get_for_user(user_id, limit)

        # Enrich with reviewer info
        enriched_reviews = []
        for review in reviews:
            reviewer_id = review.get("reviewer_id")
            if reviewer_id:
                reviewer = await self.user_repo.get_by_id(reviewer_id)
                if reviewer:
                    profile = await self.user_repo.get_profile_by_user_id(reviewer_id)
                    review["reviewer"] = {
                        "id": reviewer_id,
                        "name": reviewer.get("name"),
                        "avatar": profile.get("avatar") if profile else None,
                    }

            enriched_reviews.append(review)

        return enriched_reviews

    async def get_reviews_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all reviews written by a user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of reviews
        """
        return await self.review_repo.get_by_user(user_id, limit)

    async def get_reviews_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """
        Get all reviews for a product.

        Args:
            product_id: Product ID

        Returns:
            List of reviews with reviewer info
        """
        reviews = await self.review_repo.get_by_product(product_id)

        # Enrich with reviewer info
        enriched_reviews = []
        for review in reviews:
            reviewer_id = review.get("reviewer_id")
            if reviewer_id:
                reviewer = await self.user_repo.get_by_id(reviewer_id)
                if reviewer:
                    profile = await self.user_repo.get_profile_by_user_id(reviewer_id)
                    review["reviewer"] = {
                        "id": reviewer_id,
                        "name": reviewer.get("name"),
                        "avatar": profile.get("avatar") if profile else None,
                    }

            enriched_reviews.append(review)

        return enriched_reviews

    async def get_user_rating_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get rating statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Rating statistics
        """
        return await self.review_repo.get_user_rating_stats(user_id)

    async def _update_user_rating(self, user_id: str) -> None:
        """
        Update user's rating in profile based on reviews.

        Args:
            user_id: User ID
        """
        stats = await self.review_repo.get_user_rating_stats(user_id)

        # Update profile
        updates = {"rating": stats["average_rating"], "review_count": stats["total_reviews"]}

        await self.user_repo.update_profile(user_id, updates)

        logger.info(
            f"Updated rating for user {user_id}: {stats['average_rating']} ({stats['total_reviews']} reviews)"
        )
