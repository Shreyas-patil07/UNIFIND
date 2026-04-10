from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List, Dict, Any
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore import Increment, ArrayUnion
from database import get_db
from models import Product, ProductCreate, ProductUpdate
from auth import get_current_user, get_optional_user
from services.cloudinary_service import extract_public_id, delete_product_image
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products")


@router.get("", response_model=Dict[str, Any])
async def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[str] = None,
    seller_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    Get active products with pagination and filters.
    Returns: { items: Product[], total: int, page: int, page_size: int, pages: int }
    """
    try:
        db = get_db()
        products_ref = db.collection('products')
        
        # Validate pagination params
        page = max(1, page)
        page_size = min(100, max(1, page_size))  # Max 100 items per page
        
        # Build query with filters
        query = products_ref.where(filter=FieldFilter('is_active', '==', True))
        
        # Only add one additional where clause to avoid index requirements
        if seller_id:
            query = query.where(filter=FieldFilter('seller_id', '==', seller_id))
        elif category:
            query = query.where(filter=FieldFilter('category', '==', category))
        
        # Fetch all matching documents (apply limit after filtering)
        products = []
        for doc in query.stream():
            product_data = doc.to_dict()
            product_data['id'] = doc.id
            
            # Apply remaining filters in Python
            if category and not seller_id and product_data.get('category') != category:
                continue
            if condition and product_data.get('condition') != condition:
                continue
            if min_price and product_data.get('price', 0) < min_price:
                continue
            if max_price and product_data.get('price', float('inf')) > max_price:
                continue
                
            products.append(product_data)
        
        # Sort by posted_date
        products.sort(key=lambda x: x.get('posted_date', datetime.min), reverse=True)
        
        # Apply pagination
        total = len(products)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_products = products[start_idx:end_idx]
        
        return {
            "items": paginated_products,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to fetch products", "detail": str(e)}
        )


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, user_id: str = Depends(get_current_user)):
    """Create a new product listing"""
    try:
        db = get_db()
        product_data = product.model_dump()
        product_data['views'] = 0
        product_data['viewed_by'] = []  # Initialize empty list for tracking unique viewers
        product_data['posted_date'] = datetime.now()
        product_data['updated_at'] = datetime.now()
        product_data['is_active'] = True
        
        # Override seller_id with authenticated user
        product_data['seller_id'] = user_id
        
        doc_ref = db.collection('products').document()
        doc_ref.set(product_data)
        
        product_data['id'] = doc_ref.id
        return product_data
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Validation Error", "detail": str(e)}
        )
    except Exception as e:
        # Handle server errors
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal Server Error", "detail": "Failed to create product"}
        )


@router.get("/seller/me", response_model=List[Product])
async def get_seller_products(user_id: str = Depends(get_current_user)):
    """Get all products for the authenticated seller"""
    db = get_db()
    products_ref = db.collection('products')
    
    # Query products where seller_id matches authenticated user
    query = products_ref.where('seller_id', '==', user_id)
    
    products = []
    for doc in query.stream():
        product_data = doc.to_dict()
        product_data['id'] = doc.id
        products.append(product_data)
    
    return products


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str, user_id: Optional[str] = Depends(get_optional_user)):
    """Get a specific product by ID and track unique views per user"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "detail": "Product not found"}
        )
    
    product_data = doc.to_dict()
    
    # Track unique views per user (only for authenticated users)
    if user_id:
        viewed_by = product_data.get('viewed_by', [])
        
        # Only increment view count if this user hasn't viewed before
        if user_id not in viewed_by:
            # Use atomic operations to prevent race conditions
            doc_ref.update({
                'viewed_by': ArrayUnion([user_id]),  # Atomic array add
                'views': Increment(1)  # Atomic increment
            })
            
            # Fetch updated data
            updated_doc = doc_ref.get()
            product_data = updated_doc.to_dict()
            
            logger.info(f"New view tracked for product {product_id} by user {user_id}. Total views: {product_data.get('views', 0)}")
        else:
            logger.info(f"User {user_id} already viewed product {product_id}. View not counted.")
    
    product_data['id'] = doc.id
    return product_data


@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductCreate, user_id: str = Depends(get_current_user)):
    """Update a product listing"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "detail": "Product not found"}
        )
    
    # Verify ownership
    existing_product = doc.to_dict()
    if existing_product.get('seller_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden", "detail": "Unauthorized to modify this product"}
        )
    
    product_data = product.model_dump()
    product_data['updated_at'] = datetime.now()
    doc_ref.update(product_data)
    
    product_data['id'] = product_id
    product_data['views'] = doc.to_dict().get('views', 0)
    product_data['posted_date'] = doc.to_dict().get('posted_date')
    product_data['is_active'] = doc.to_dict().get('is_active', True)
    product_data['seller_id'] = user_id
    
    return product_data


@router.patch("/{product_id}", response_model=Product)
async def partial_update_product(product_id: str, product: ProductUpdate, user_id: str = Depends(get_current_user)):
    """Partially update a product listing (PATCH)"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "detail": "Product not found"}
        )
    
    # Verify ownership (Requirement 6.5, 10.2)
    existing_product = doc.to_dict()
    if existing_product.get('seller_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden", "detail": "Unauthorized to modify this product"}
        )
    
    # Build update dict with only provided fields (Requirement 6.4)
    update_data = product.model_dump(exclude_unset=True)
    
    if update_data:
        # Update updated_at timestamp (Requirement 6.8)
        update_data['updated_at'] = datetime.now()
        doc_ref.update(update_data)
        
        # Fetch updated document
        updated_doc = doc_ref.get()
        product_data = updated_doc.to_dict()
        product_data['id'] = product_id
        
        return product_data
    else:
        # No fields to update, return existing product
        existing_product['id'] = product_id
        return existing_product


@router.delete("/{product_id}")
async def delete_product(product_id: str, user_id: str = Depends(get_current_user)):
    """Delete a product listing (soft delete)"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not Found", "detail": "Product not found"}
        )
    
    # Verify ownership
    existing_product = doc.to_dict()
    if existing_product.get('seller_id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Forbidden", "detail": "Unauthorized to modify this product"}
        )
    
    # Soft delete
    doc_ref.update({'is_active': False})

    # Best-effort Cloudinary cleanup — log failures but don't block the response
    for url in existing_product.get('images', []):
        public_id = extract_public_id(url)
        if public_id:
            try:
                delete_product_image(public_id)
            except Exception as e:
                logger.warning(
                    "Failed to delete Cloudinary image %s for product %s: %s",
                    public_id, product_id, e
                )

    return {"message": "Product deleted successfully"}
