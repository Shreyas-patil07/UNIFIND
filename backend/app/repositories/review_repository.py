"""
Review repository - all review-related database operations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from google.cloud import firestore
import logging

logger = logging.getLogger(__name__)


class ReviewRepository:
    """Repository for review data access."""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('reviews')
    
    async def create(self, review_data: Dict[str, Any]) -> str:
        """Create a new review."""
        review_data['created_at'] = datetime.now()
        
        doc_ref = self.collection.document()
        doc_ref.set(review_data)
        return doc_ref.id
    
    async def get_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review by ID."""
        doc = self.collection.document(review_id).get()
        if not doc.exists:
            return None
        
        review_data = doc.to_dict()
        review_data['id'] = doc.id
        return review_data
    
    async def get_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all reviews for a user (as reviewer)."""
        query = self.collection.where('reviewer_id', '==', user_id)\
            .order_by('created_at', direction='DESCENDING')\
            .limit(limit)
        
        reviews = []
        for doc in query.stream():
            review_data = doc.to_dict()
            review_data['id'] = doc.id
            reviews.append(review_data)
        
        return reviews
    
    async def get_for_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all reviews about a user (as reviewed user)."""
        query = self.collection.where('reviewed_user_id', '==', user_id)\
            .order_by('created_at', direction='DESCENDING')\
            .limit(limit)
        
        reviews = []
        for doc in query.stream():
            review_data = doc.to_dict()
            review_data['id'] = doc.id
            reviews.append(review_data)
        
        return reviews
    
    async def get_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all reviews for a product."""
        query = self.collection.where('product_id', '==', product_id)\
            .order_by('created_at', direction='DESCENDING')
        
        reviews = []
        for doc in query.stream():
            review_data = doc.to_dict()
            review_data['id'] = doc.id
            reviews.append(review_data)
        
        return reviews
    
    async def get_user_rating_stats(self, user_id: str) -> Dict[str, Any]:
        """Calculate rating statistics for a user."""
        reviews = await self.get_for_user(user_id, limit=1000)
        
        if not reviews:
            return {
                'average_rating': 0.0,
                'total_reviews': 0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
        
        total_rating = sum(r.get('rating', 0) for r in reviews)
        average_rating = total_rating / len(reviews)
        
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating = review.get('rating', 0)
            if 1 <= rating <= 5:
                rating_distribution[rating] += 1
        
        return {
            'average_rating': round(average_rating, 2),
            'total_reviews': len(reviews),
            'rating_distribution': rating_distribution
        }
    
    async def check_existing_review(
        self,
        reviewer_id: str,
        reviewed_user_id: str,
        product_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Check if a review already exists."""
        query = self.collection.where('reviewer_id', '==', reviewer_id)\
            .where('reviewed_user_id', '==', reviewed_user_id)
        
        if product_id:
            query = query.where('product_id', '==', product_id)
        
        query = query.limit(1)
        
        for doc in query.stream():
            review_data = doc.to_dict()
            review_data['id'] = doc.id
            return review_data
        
        return None
    
    async def update(self, review_id: str, updates: Dict[str, Any]) -> bool:
        """Update review data."""
        doc_ref = self.collection.document(review_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.update(updates)
        return True
    
    async def delete(self, review_id: str) -> bool:
        """Delete a review."""
        doc_ref = self.collection.document(review_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True
