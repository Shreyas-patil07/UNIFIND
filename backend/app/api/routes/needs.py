"""
Needs API - Demand → Supply Engine
Production-ready endpoints for need posting and matching.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_need_service
from app.services.need_service import NeedService
from app.schemas.need import (
    NeedCreate,
    NeedResponse,
    SellerDemandBanner,
    SellerNeedFeed,
    NeedFulfillRequest
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/needs", tags=["needs"])


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_need(
    request: NeedCreate,
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new need (buyer posts what they're looking for).
    
    Process:
    1. Extract structured data from raw text
    2. Store need in database
    3. Find matching listings
    4. Notify relevant sellers
    """
    try:
        result = await need_service.create_need(request, current_user)
        return result
    except ValueError as e:
        if "Daily limit reached" in str(e):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating need: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create need. Please try again."
        )


@router.get("/match/{need_id}")
async def get_need_matches(
    need_id: str,
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """Get matching listings for a specific need."""
    try:
        matches = await need_service.get_need_matches(need_id, current_user)
        return {'matches': matches}
    except ValueError as e:
        if "Not authorized" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/seller-feed", response_model=SellerNeedFeed)
async def get_seller_need_feed(
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """
    Get feed of relevant needs for a seller.
    Shows needs that match the seller's listings.
    """
    result = await need_service.get_seller_feed(current_user)
    return result


@router.get("/seller-banner", response_model=SellerDemandBanner)
async def get_seller_demand_banner(
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """
    Get banner data for seller dashboard.
    Shows count of relevant needs.
    """
    result = await need_service.get_seller_banner(current_user)
    return result


@router.post("/{need_id}/fulfill")
async def fulfill_need(
    need_id: str,
    request: NeedFulfillRequest,
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """Mark a need as fulfilled."""
    try:
        success = await need_service.fulfill_need(
            need_id,
            request.product_id,
            current_user
        )
        if success:
            return {'message': 'Need marked as fulfilled'}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update need"
        )
    except ValueError as e:
        if "Not authorized" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{need_id}/save")
async def save_need(
    need_id: str,
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """Save a need (seller expresses interest)."""
    try:
        success = await need_service.save_need(need_id, current_user)
        if success:
            return {'message': 'Need saved successfully'}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save need"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/my-needs")
async def get_my_needs(
    need_service: NeedService = Depends(get_need_service),
    current_user: str = Depends(get_current_user)
):
    """Get all needs posted by the current user."""
    needs = await need_service.get_my_needs(current_user, limit=20)
    return {'needs': needs}
