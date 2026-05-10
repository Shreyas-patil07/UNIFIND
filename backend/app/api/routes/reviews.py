"""
Review routes - review creation and retrieval.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_review_service
from app.services.review_service import ReviewService
from app.schemas.review import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
    current_user: str = Depends(get_current_user)
):
    """Create a new review and update user rating."""
    try:
        review = await review_service.create_review(review_data, current_user)
        return review
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_reviews(
    user_id: str,
    limit: int = 50,
    review_service: ReviewService = Depends(get_review_service)
):
    """Get all reviews for a user."""
    reviews = await review_service.get_reviews_for_user(user_id, limit)
    return reviews


@router.get("/product/{product_id}", response_model=List[Dict[str, Any]])
async def get_product_reviews(
    product_id: str,
    review_service: ReviewService = Depends(get_review_service)
):
    """Get all reviews for a product."""
    reviews = await review_service.get_reviews_by_product(product_id)
    return reviews


@router.get("/user/{user_id}/stats", response_model=Dict[str, Any])
async def get_user_rating_stats(
    user_id: str,
    review_service: ReviewService = Depends(get_review_service)
):
    """Get rating statistics for a user."""
    stats = await review_service.get_user_rating_stats(user_id)
    return stats
