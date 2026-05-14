"""
Products API routes - refactored to use ProductService.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user, get_optional_user
from app.api.dependencies.services import get_product_service, get_transaction_service
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/products")


@router.get("", response_model=Dict[str, Any])
async def get_products(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort: Optional[str] = Query("newest", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: ProductService = Depends(get_product_service),
):
    """Get all products with server-side filtering, sorting, and pagination."""
    return await service.get_all_products(
        category=category,
        subcategory=subcategory,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        search_query=q,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.post("/batch", response_model=List[Product])
async def get_products_batch(
    product_ids: List[str] = Body(..., embed=True, max_length=50),
    service: ProductService = Depends(get_product_service),
):
    """Batch fetch products by IDs (for recently viewed, etc.)"""
    if not product_ids:
        return []

    # Service will handle filtering to active products only
    products = await service.get_products_batch(product_ids[:50])
    return products


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    """Create a new product listing"""
    try:
        return await service.create_product(product, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/seller/me", response_model=List[Product])
async def get_seller_products(
    user_id: str = Depends(get_current_user), service: ProductService = Depends(get_product_service)
):
    """Get all products for the authenticated seller (including inactive/sold)"""
    return await service.get_seller_products(user_id)


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str,
    user_id: Optional[str] = Depends(get_optional_user),
    service: ProductService = Depends(get_product_service),
):
    """Get a specific product by ID and track unique views per user"""
    product = await service.get_product_by_id(product_id, viewer_id=user_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product: ProductCreate,
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    """Update a product listing (full update)"""
    # Convert ProductCreate to dict for update
    product_update = ProductUpdate(**product.model_dump())

    updated_product = await service.update_product(product_id, product_update, user_id)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this product"
        )

    return updated_product


@router.patch("/{product_id}", response_model=Product)
async def partial_update_product(
    product_id: str,
    product: ProductUpdate,
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    """Partially update a product listing (PATCH)"""
    updated_product = await service.update_product(product_id, product, user_id)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this product"
        )

    return updated_product


@router.get("/{product_id}/interested-buyers")
async def get_interested_buyers(
    product_id: str,
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    """Get all users who have messaged about this product"""
    try:
        return await service.get_interested_buyers(product_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{product_id}/mark-sold")
async def mark_product_as_sold(
    product_id: str,
    request_body: dict = Body({}),
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Mark a product as sold and create a transaction history record"""
    buyer_id = request_body.get("buyer_id")

    success = await service.mark_as_sold(product_id, user_id, buyer_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this product"
        )

    # Get product for transaction amount
    product = await service.get_product_by_id(product_id)
    if product:
        await transaction_service.create_product_sold_transaction(
            product_id, user_id, product.get("price", 0), buyer_id
        )

    return {"message": "Product marked as sold successfully", "buyer_id": buyer_id}


@router.patch("/{product_id}/mark-active")
async def mark_product_as_active(
    product_id: str,
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    """Mark a product as active again and create a transaction history record"""
    success = await service.mark_as_active(product_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to modify this product"
        )

    # Get product for transaction amount
    product = await service.get_product_by_id(product_id)
    if product:
        await transaction_service.create_product_active_transaction(
            product_id, user_id, product.get("price", 0)
        )

    return {"message": "Product marked as active successfully"}


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    user_id: str = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    """Delete a product listing"""
    success = await service.delete_product(product_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete this product"
        )

    return {"message": "Product deleted successfully", "deleted": {"product": product_id}}
