"""
Firestore implementation of User repository.
This implementation can be replaced with PostgreSQL without changing business logic.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from google.cloud import firestore
import logging

from app.repositories.base import UserRepositoryInterface

logger = logging.getLogger(__name__)


class UserRepository(UserRepositoryInterface):
    """Repository for user data access."""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('users')
        self.profiles_collection = db.collection('user_profiles')
    
    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        doc = self.collection.document(user_id).get()
        if not doc.exists:
            return None
        
        user_data = doc.to_dict()
        user_data['id'] = doc.id
        return user_data
    
    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID."""
        users = self.collection.where('firebase_uid', '==', firebase_uid).limit(1).stream()
        
        for doc in users:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return user_data
        
        return None
    
    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all users with pagination."""
        query = self.collection
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        users = []
        for doc in query.stream():
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            users.append(user_data)
        return users
    
    async def create(self, user_data: Dict[str, Any]) -> str:
        """Create a new user and return the user ID."""
        user_data['email_verified'] = False
        user_data['created_at'] = datetime.now()
        
        user_ref = self.collection.document()
        user_ref.set(user_data)
        return user_ref.id
    
    async def update(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data."""
        doc_ref = self.collection.document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.update(updates)
        return True
    
    async def search_by_name(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search users by name (case-insensitive)."""
        users = []
        query_lower = query.lower()
        
        for doc in self.collection.stream():
            user_data = doc.to_dict()
            user_name = user_data.get('name', '').lower()
            
            if query_lower in user_name:
                user_data['id'] = doc.id
                users.append(user_data)
                
                if len(users) >= limit:
                    break
        
        return users
    
    # Profile operations
    async def get_profile_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID."""
        profiles = self.profiles_collection.where('user_id', '==', user_id).limit(1).stream()
        
        for doc in profiles:
            profile_data = doc.to_dict()
            profile_data['id'] = doc.id
            return profile_data
        
        return None
    
    async def create_profile(self, profile_data: Dict[str, Any]) -> str:
        """Create a new user profile."""
        profile_data['updated_at'] = datetime.now()
        
        profile_ref = self.profiles_collection.document()
        profile_ref.set(profile_data)
        return profile_ref.id
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        profiles = self.profiles_collection.where('user_id', '==', user_id).limit(1).stream()
        
        for doc in profiles:
            profile_ref = self.profiles_collection.document(doc.id)
            updates['updated_at'] = datetime.now()
            profile_ref.update(updates)
            return True
        
        return False
    
    async def get_profile_with_user(self, user_id: str, include_private: bool = False) -> Optional[Dict[str, Any]]:
        """Get combined user and profile data."""
        # Get user data
        user_doc = self.collection.document(user_id).get()
        if not user_doc.exists:
            return None
        
        user_data = user_doc.to_dict()
        user_data['id'] = user_doc.id
        
        # Get profile data
        profile_data = await self.get_profile_by_user_id(user_id)
        
        if not profile_data:
            # Create default profile data
            profile_data = {
                'user_id': user_id,
                'branch': None,
                'avatar': None,
                'cover_gradient': 'from-blue-600 to-purple-600',
                'bio': None,
                'trust_score': 0.0,
                'rating': 0.0,
                'review_count': 0,
                'member_since': user_data.get('created_at', '').split('T')[0].split('-')[0] if user_data.get('created_at') else str(datetime.now().year),
                'phone': None,
                'hostel_room': None,
                'branch_change_history': [],
                'photo_change_history': [],
                'dark_mode': False
            }
        
        # Remove private fields if not requested
        if not include_private:
            private_fields = ['phone', 'hostel_room', 'branch_change_history', 'photo_change_history', 'dark_mode']
            for field in private_fields:
                profile_data.pop(field, None)
                user_data.pop(field, None)
            user_data.pop('email', None)
        
        # Combine user and profile data
        combined_data = {
            **profile_data,
            **user_data,
            'user_id': user_id
        }
        
        return combined_data
