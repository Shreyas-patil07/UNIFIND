"""
Firestore implementation of Product repository.
This implementation can be replaced with PostgreSQL without changing business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore import Increment, ArrayUnion, DELETE_FIELD
import logging

from app.repositories.base import ProductRepositoryInterface

logger = logging.getLogger(__name__)


class ProductRepository(ProductRepositoryInterface):
    """Repository for product data access."""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('products')
    
    async def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        doc = self.collection.document(product_id).get()
        if not doc.exists:
            return None
        
        product_data = doc.to_dict()
        product_data['id'] = doc.id
        return product_data
    
    async def get_all(
        self,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all products with optional filters and pagination."""
        query = self.collection
        
        if category:
            query = query.where(filter=FieldFilter('category', '==', category))
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        products = []
        for doc in query.stream():
            product_data = doc.to_dict()
            product_data['id'] = doc.id
            products.append(product_data)
        
        return products
    
    async def get_by_seller(
        self,
        seller_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all products for a seller (including inactive)."""
        query = self.collection.where('seller_id', '==', seller_id)
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        products = []
        for doc in query.stream():
            product_data = doc.to_dict()
            product_data['id'] = doc.id
            products.append(product_data)
        
        return products
    
    async def get_active_products(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all active products."""
        query = self.collection.where('is_active', '==', True).where('mark_as_sold', '==', False)
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        products = []
        for doc in query.stream():
            product_data = doc.to_dict()
            product_data['id'] = doc.id
            products.append(product_data)
        
        return products
    
    async def get_batch(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch fetch products by IDs."""
        products = []
        
        for product_id in product_ids:
            doc = self.collection.document(product_id).get()
            if doc.exists:
                product_data = doc.to_dict()
                product_data['id'] = doc.id
                products.append(product_data)
        
        return products
    
    async def create(self, product_data: Dict[str, Any]) -> str:
        """Create a new product and return the product ID."""
        product_data['views'] = 0
        product_data['viewed_by'] = []
        product_data['posted_date'] = datetime.now()
        product_data['updated_at'] = datetime.now()
        product_data['is_active'] = True
        product_data['mark_as_sold'] = False
        product_data['sold_to'] = None
        
        doc_ref = self.collection.document()
        doc_ref.set(product_data)
        return doc_ref.id
    
    async def update(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """Update product data."""
        doc_ref = self.collection.document(product_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        updates['updated_at'] = datetime.now()
        doc_ref.update(updates)
        return True
    
    async def delete(self, product_id: str) -> bool:
        """Delete a product."""
        doc_ref = self.collection.document(product_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True
    
    async def increment_view(self, product_id: str, user_id: str) -> bool:
        """Increment view count if user hasn't viewed before."""
        doc_ref = self.collection.document(product_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        product_data = doc.to_dict()
        viewed_by = product_data.get('viewed_by', [])
        
        if user_id not in viewed_by:
            doc_ref.update({
                'viewed_by': ArrayUnion([user_id]),
                'views': Increment(1)
            })
            return True
        
        return False
    
    async def mark_as_sold(self, product_id: str, buyer_id: Optional[str] = None) -> bool:
        """Mark product as sold."""
        doc_ref = self.collection.document(product_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        update_data = {
            'is_active': False,
            'sold_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        if buyer_id:
            update_data['sold_to'] = buyer_id
        
        doc_ref.update(update_data)
        return True
    
    async def mark_as_active(self, product_id: str) -> bool:
        """Mark product as active again."""
        doc_ref = self.collection.document(product_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        existing_product = doc.to_dict()
        
        update_data = {
            'is_active': True,
            'updated_at': datetime.now()
        }
        
        # Remove sold fields
        if 'sold_to' in existing_product:
            update_data['sold_to'] = DELETE_FIELD
        if 'sold_at' in existing_product:
            update_data['sold_at'] = DELETE_FIELD
        
        doc_ref.update(update_data)
        return True
    
    async def verify_ownership(self, product_id: str, user_id: str) -> bool:
        """Verify if user owns the product."""
        doc = self.collection.document(product_id).get()
        
        if not doc.exists:
            return False
        
        product_data = doc.to_dict()
        return product_data.get('seller_id') == user_id
    
    async def count_by_category(self, category: str) -> int:
        """Count products in a category."""
        query = self.collection.where('category', '==', category)
        docs = list(query.stream())
        return len(docs)
    
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search products by query string.
        Note: Firestore doesn't support full-text search natively.
        This is a basic implementation. For production, use Elasticsearch or Algolia.
        """
        query_lower = query.lower()
        
        # Start with base query
        db_query = self.collection.where('is_active', '==', True)
        
        if category:
            db_query = db_query.where('category', '==', category)
        
        db_query = db_query.limit(limit * 3)  # Fetch more to filter client-side
        
        products = []
        for doc in db_query.stream():
            product_data = doc.to_dict()
            
            # Client-side filtering (not ideal, but Firestore limitation)
            title = product_data.get('title', '').lower()
            description = product_data.get('description', '').lower()
            
            if query_lower in title or query_lower in description:
                product_data['id'] = doc.id
                products.append(product_data)
                
                if len(products) >= limit:
                    break
        
        return products
