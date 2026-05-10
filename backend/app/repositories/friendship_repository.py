"""
Friendship repository - all friendship-related database operations.
"""
from typing import List, Dict, Any
from datetime import datetime
from google.cloud import firestore
import logging

logger = logging.getLogger(__name__)


class FriendshipRepository:
    """Repository for friendship data access."""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection('friendships')
    
    async def create(self, friendship_data: Dict[str, Any]) -> str:
        """Create a new friendship record."""
        friendship_data['created_at'] = datetime.now()
        friendship_data['status'] = 'pending'
        
        doc_ref = self.collection.document()
        doc_ref.set(friendship_data)
        return doc_ref.id
    
    async def get_friendship(self, user_id: str, friend_id: str) -> List[Dict[str, Any]]:
        """Get friendship record between two users."""
        friendships = self.collection.where('user_id', '==', user_id)\
            .where('friend_id', '==', friend_id)\
            .stream()
        
        results = []
        for doc in friendships:
            friendship_data = doc.to_dict()
            friendship_data['id'] = doc.id
            results.append(friendship_data)
        
        return results
    
    async def get_active_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active friendships for a user."""
        friendships = self.collection.where('user_id', '==', user_id)\
            .where('status', '==', 'active')\
            .stream()
        
        friends = []
        for doc in friendships:
            friendship_data = doc.to_dict()
            friendship_data['id'] = doc.id
            friends.append(friendship_data)
        
        return friends
    
    async def get_pending_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending friend requests for a user (where user is the recipient)."""
        requests = self.collection.where('friend_id', '==', user_id)\
            .where('status', '==', 'pending')\
            .stream()
        
        pending = []
        for doc in requests:
            request_data = doc.to_dict()
            request_data['id'] = doc.id
            pending.append(request_data)
        
        return pending
    
    async def check_friendship_status(self, user_id: str, friend_id: str) -> str:
        """Check friendship status between two users."""
        # Check if they are friends (active)
        active_friendship = self.collection.where('user_id', '==', user_id)\
            .where('friend_id', '==', friend_id)\
            .where('status', '==', 'active')\
            .limit(1)\
            .stream()
        
        if any(active_friendship):
            return "friends"
        
        # Check if current user sent a pending request
        sent_request = self.collection.where('user_id', '==', user_id)\
            .where('friend_id', '==', friend_id)\
            .where('status', '==', 'pending')\
            .limit(1)\
            .stream()
        
        if any(sent_request):
            return "request_sent"
        
        # Check if current user received a pending request
        received_request = self.collection.where('user_id', '==', friend_id)\
            .where('friend_id', '==', user_id)\
            .where('status', '==', 'pending')\
            .limit(1)\
            .stream()
        
        if any(received_request):
            return "request_received"
        
        return "none"
    
    async def accept_friend_request(self, user_id: str, friend_id: str) -> bool:
        """Accept a friend request and create reciprocal friendship."""
        # Find the pending request
        requests = list(self.collection.where('user_id', '==', friend_id)\
            .where('friend_id', '==', user_id)\
            .where('status', '==', 'pending')\
            .limit(1)\
            .stream())
        
        if not requests:
            return False
        
        doc = requests[0]
        original_data = doc.to_dict()
        original_created_at = original_data.get('created_at', datetime.now())
        accepted_at = datetime.now()
        
        # Batch update for atomic operation
        batch = self.db.batch()
        
        # Update original request to active
        batch.update(doc.reference, {
            'status': 'active',
            'accepted_at': accepted_at
        })
        
        # Check if reciprocal friendship already exists
        existing_reciprocal = list(self.collection.where('user_id', '==', user_id)\
            .where('friend_id', '==', friend_id)\
            .limit(1)\
            .stream())
        
        if existing_reciprocal:
            # Update existing reciprocal to active
            batch.update(existing_reciprocal[0].reference, {
                'status': 'active',
                'accepted_at': accepted_at
            })
        else:
            # Create reciprocal friendship
            reciprocal_ref = self.collection.document()
            batch.set(reciprocal_ref, {
                'user_id': user_id,
                'friend_id': friend_id,
                'created_at': original_created_at,
                'status': 'active',
                'accepted_at': accepted_at
            })
        
        batch.commit()
        return True
    
    async def reject_friend_request(self, user_id: str, friend_id: str) -> bool:
        """Reject a friend request."""
        requests = list(self.collection.where('user_id', '==', friend_id)\
            .where('friend_id', '==', user_id)\
            .where('status', '==', 'pending')\
            .limit(1)\
            .stream())
        
        if not requests:
            return False
        
        requests[0].reference.delete()
        return True
    
    async def remove_friendship(self, user_id: str, friend_id: str) -> bool:
        """Remove friendship in both directions."""
        friendships1 = self.collection.where('user_id', '==', user_id)\
            .where('friend_id', '==', friend_id)\
            .stream()
        friendships2 = self.collection.where('user_id', '==', friend_id)\
            .where('friend_id', '==', user_id)\
            .stream()
        
        deleted = False
        for doc in list(friendships1) + list(friendships2):
            doc.reference.delete()
            deleted = True
        
        return deleted
    
    async def get_friend_ids(self, user_id: str) -> set:
        """Get set of friend IDs for a user (for efficient lookups)."""
        friendships = self.collection.where('user_id', '==', user_id)\
            .where('status', '==', 'active')\
            .stream()
        
        friend_ids = set()
        for friendship in friendships:
            friend_data = friendship.to_dict()
            friend_ids.add(friend_data.get('friend_id'))
        
        return friend_ids
