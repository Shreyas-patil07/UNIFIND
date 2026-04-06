from fastapi import APIRouter, HTTPException
from typing import Optional, List
from datetime import datetime
from database import get_db
from models import Product, ProductCreate

router = APIRouter()


@router.get("/products", response_model=List[Product])
async def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[str] = None,
    seller_id: Optional[str] = None
):
    """Get all products with optional filters"""
    db = get_db()
    products_ref = db.collection('products')
    
    # Apply filters
    query = products_ref
    if category:
        query = query.where('category', '==', category)
    if seller_id:
        query = query.where('seller_id', '==', seller_id)
    if condition:
        query = query.where('condition', '==', condition)
    
    products = []
    for doc in query.stream():
        product_data = doc.to_dict()
        product_data['id'] = doc.id
        
        # Apply price filters
        if min_price and product_data.get('price', 0) < min_price:
            continue
        if max_price and product_data.get('price', float('inf')) > max_price:
            continue
            
        products.append(product_data)
    
    return products


@router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    """Create a new product listing"""
    db = get_db()
    product_data = product.model_dump()
    product_data['views'] = 0
    product_data['posted_date'] = datetime.now()
    product_data['is_active'] = True
    
    doc_ref = db.collection('products').document()
    doc_ref.set(product_data)
    
    product_data['id'] = doc_ref.id
    return product_data


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID and increment view count"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Increment view count
    doc_ref.update({'views': (doc.to_dict().get('views', 0) + 1)})
    
    product_data = doc.to_dict()
    product_data['id'] = doc.id
    return product_data


@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductCreate):
    """Update a product listing"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_data = product.model_dump()
    doc_ref.update(product_data)
    
    product_data['id'] = product_id
    product_data['views'] = doc.to_dict().get('views', 0)
    product_data['posted_date'] = doc.to_dict().get('posted_date')
    product_data['is_active'] = doc.to_dict().get('is_active', True)
    
    return product_data


@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product listing (soft delete)"""
    db = get_db()
    doc_ref = db.collection('products').document(product_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete
    doc_ref.update({'is_active': False})
    
    return {"message": "Product deleted successfully"}
