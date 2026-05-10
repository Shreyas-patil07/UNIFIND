"""
User service - business logic for user operations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.repositories.user_repository import UserRepository
from app.repositories.friendship_repository import FriendshipRepository
from app.schemas.user import UserCreate, UserProfileCreate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user business logic."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        friendship_repo: FriendshipRepository
    ):
        self.user_repo = user_repo
        self.friendship_repo = friendship_repo
    
    async def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user with profile.
        
        Args:
            user_data: User registration data
            
        Returns:
            Dictionary with user and profile data
        """
        # Check if user already exists
        existing_user = await self.user_repo.get_by_firebase_uid(user_data.firebase_uid)
        if existing_user:
            raise ValueError("User with this Firebase UID already exists")
        
        # Create user
        user_dict = user_data.model_dump()
        user_id = await self.user_repo.create(user_dict)
        
        # Create default profile
        profile_data = {
            'user_id': user_id,
            'branch': None,
            'avatar': None,
            'cover_gradient': 'from-blue-600 to-purple-600',
            'bio': None,
            'trust_score': 0.0,
            'rating': 0.0,
            'review_count': 0,
            'member_since': str(datetime.now().year),
            'phone': None,
            'hostel_room': None,
            'branch_change_history': [],
            'photo_change_history': [],
            'dark_mode': False
        }
        
        profile_id = await self.user_repo.create_profile(profile_data)
        
        # Get created user and profile
        user = await self.user_repo.get_by_id(user_id)
        profile = await self.user_repo.get_profile_by_user_id(user_id)
        
        return {
            'user': user,
            'profile': profile
        }
    
    async def get_user_profile(
        self,
        user_id: str,
        requesting_user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get user profile with appropriate privacy settings.
        
        Args:
            user_id: User ID to get profile for
            requesting_user_id: ID of user requesting the profile
            
        Returns:
            Combined user and profile data
        """
        # Determine if private fields should be included
        include_private = (requesting_user_id == user_id)
        
        profile = await self.user_repo.get_profile_with_user(user_id, include_private)
        
        return profile
    
    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile with history tracking.
        
        Args:
            user_id: User ID
            updates: Fields to update
            
        Returns:
            Updated profile data
        """
        # Track branch changes
        if 'branch' in updates:
            profile = await self.user_repo.get_profile_by_user_id(user_id)
            if profile:
                old_branch = profile.get('branch')
                if old_branch and old_branch != updates['branch']:
                    branch_history = profile.get('branch_change_history', [])
                    branch_history.append({
                        'from': old_branch,
                        'to': updates['branch'],
                        'timestamp': datetime.now().isoformat()
                    })
                    updates['branch_change_history'] = branch_history
        
        # Track photo changes
        if 'avatar' in updates:
            profile = await self.user_repo.get_profile_by_user_id(user_id)
            if profile:
                old_avatar = profile.get('avatar')
                if old_avatar and old_avatar != updates['avatar']:
                    photo_history = profile.get('photo_change_history', [])
                    photo_history.append({
                        'url': old_avatar,
                        'timestamp': datetime.now().isoformat()
                    })
                    updates['photo_change_history'] = photo_history
        
        # Update profile
        success = await self.user_repo.update_profile(user_id, updates)
        
        if not success:
            return None
        
        # Return updated profile
        return await self.user_repo.get_profile_with_user(user_id, include_private=True)
    
    async def search_users(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search users by name.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of users with basic profile info
        """
        if not query or len(query) < 2:
            return []
        
        users = await self.user_repo.search_by_name(query, limit)
        
        # Enrich with profile data (avatar, bio)
        enriched_users = []
        for user in users:
            profile = await self.user_repo.get_profile_by_user_id(user['id'])
            if profile:
                user['avatar'] = profile.get('avatar')
                user['bio'] = profile.get('bio')
            
            # Remove sensitive data
            user.pop('email', None)
            user.pop('firebase_uid', None)
            
            enriched_users.append(user)
        
        return enriched_users
    
    # Friend management
    
    async def send_friend_request(self, user_id: str, friend_id: str) -> Dict[str, Any]:
        """
        Send a friend request.
        
        Args:
            user_id: Requesting user ID
            friend_id: Target user ID
            
        Returns:
            Result with status
        """
        if user_id == friend_id:
            raise ValueError("Cannot add yourself as a friend")
        
        # Verify both users exist
        user = await self.user_repo.get_by_id(user_id)
        friend = await self.user_repo.get_by_id(friend_id)
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        if not friend:
            raise ValueError(f"Friend {friend_id} not found")
        
        # Check if friendship already exists
        existing = await self.friendship_repo.get_friendship(user_id, friend_id)
        if existing:
            for friendship in existing:
                if friendship.get('status') == 'pending':
                    raise ValueError("Friend request already sent")
                elif friendship.get('status') == 'active':
                    raise ValueError("Already friends")
        
        # Check if there's a pending request from the other user
        reverse_request = await self.friendship_repo.get_friendship(friend_id, user_id)
        for friendship in reverse_request:
            if friendship.get('status') == 'pending':
                # Auto-accept mutual request
                await self.friendship_repo.accept_friend_request(user_id, friend_id)
                return {"message": "Friend request accepted", "status": "active"}
        
        # Create friend request
        friendship_data = {
            'user_id': user_id,
            'friend_id': friend_id
        }
        
        friendship_id = await self.friendship_repo.create(friendship_data)
        
        return {"message": "Friend request sent", "friendship_id": friendship_id, "status": "pending"}
    
    async def accept_friend_request(self, user_id: str, friend_id: str) -> bool:
        """Accept a friend request."""
        return await self.friendship_repo.accept_friend_request(user_id, friend_id)
    
    async def reject_friend_request(self, user_id: str, friend_id: str) -> bool:
        """Reject a friend request."""
        return await self.friendship_repo.reject_friend_request(user_id, friend_id)
    
    async def remove_friend(self, user_id: str, friend_id: str) -> bool:
        """Remove a friend."""
        return await self.friendship_repo.remove_friendship(user_id, friend_id)
    
    async def get_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's friends list.
        
        Args:
            user_id: User ID
            
        Returns:
            List of friends with profile info
        """
        friendships = await self.friendship_repo.get_active_friends(user_id)
        
        friends = []
        for friendship in friendships:
            friend_id = friendship['friend_id']
            
            # Get friend's user data
            friend = await self.user_repo.get_by_id(friend_id)
            if not friend:
                continue
            
            # Get friend's profile
            profile = await self.user_repo.get_profile_by_user_id(friend_id)
            if profile:
                friend['avatar'] = profile.get('avatar')
                friend['bio'] = profile.get('bio')
            
            # Remove sensitive data
            friend.pop('email', None)
            friend.pop('firebase_uid', None)
            
            friends.append(friend)
        
        return friends
    
    async def get_pending_friend_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get pending friend requests for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of users who sent friend requests
        """
        requests = await self.friendship_repo.get_pending_requests(user_id)
        
        # Remove duplicates
        seen_requesters = set()
        pending_requests = []
        
        for request in requests:
            requester_id = request['user_id']
            
            if requester_id in seen_requesters:
                # Delete duplicate
                continue
            
            seen_requesters.add(requester_id)
            
            # Get requester's user data
            requester = await self.user_repo.get_by_id(requester_id)
            if not requester:
                continue
            
            requester['request_id'] = request['id']
            requester['created_at'] = request.get('created_at')
            
            # Get requester's profile
            profile = await self.user_repo.get_profile_by_user_id(requester_id)
            if profile:
                requester['avatar'] = profile.get('avatar')
                requester['bio'] = profile.get('bio')
            
            # Remove sensitive data
            requester.pop('email', None)
            requester.pop('firebase_uid', None)
            
            pending_requests.append(requester)
        
        return pending_requests
    
    async def check_friendship_status(self, user_id: str, friend_id: str) -> str:
        """
        Check friendship status between two users.
        
        Returns:
            "friends", "request_sent", "request_received", or "none"
        """
        return await self.friendship_repo.check_friendship_status(user_id, friend_id)
