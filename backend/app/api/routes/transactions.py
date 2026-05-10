"""
Transaction routes - transaction history and statistics.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional, Dict, Any, List

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_transaction_service
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/history", response_model=Dict[str, Any])
async def get_transaction_history(
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    transaction_type_sold: Optional[bool] = Query(None, description="Filter by sold status"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: str = Depends(get_current_user)
):
    """
    Get transaction history for the authenticated user.
    Returns all transaction history records where the user is the seller.
    """
    try:
        result = await transaction_service.get_transaction_history(
            current_user,
            product_id=product_id,
            transaction_type_sold=transaction_type_sold,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to fetch transaction history", "detail": str(e)}
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_transaction_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: str = Depends(get_current_user)
):
    """
    Get transaction statistics for the authenticated user.
    Returns summary of sold/active products and revenue.
    """
    try:
        stats = await transaction_service.get_transaction_stats(current_user, days)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to fetch transaction stats", "detail": str(e)}
        )


@router.get("/product/{product_id}", response_model=List[Dict[str, Any]])
async def get_product_transaction_history(
    product_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: str = Depends(get_current_user)
):
    """
    Get transaction history for a specific product.
    Only the seller can view the transaction history.
    """
    try:
        transactions = await transaction_service.get_product_transaction_history(
            product_id,
            current_user
        )
        return transactions
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to fetch product transaction history", "detail": str(e)}
        )
