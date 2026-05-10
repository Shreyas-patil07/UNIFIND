"""
Chat service - business logic for chat operations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from app.repositories.chat_repository import ChatRepository
from app.repositories.friendship_repository import FriendshipRepository
from app.schemas.chat import MessageCreate

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat business logic."""
    
    def __init__(
        self,
        chat_repo: ChatRepository,
        friendship_repo: FriendshipRepository
    ):
        self.chat_repo = chat_repo
        self.friendship_repo = friendship_repo
    
    def _generate_chat_room_id(
        self,
        user1_id: str,
        user2_id: str,
        product_id: Optional[str] = None
    ) -> str:
        """Generate consistent chat room ID."""
        chat_room_id = f"{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
        if product_id:
            chat_room_id += f"_{product_id}"
        return chat_room_id
    
    async def send_message(
        self,
        message_data: MessageCreate,
        authenticated_user: str
    ) -> Dict[str, Any]:
        """
        Send a message and create/update chat room.
        
        Args:
            message_data: Message data
            authenticated_user: Authenticated user ID
            
        Returns:
            Created message data
        """
        # Security: Verify sender_id matches authenticated user
        if message_data.sender_id != authenticated_user:
            raise ValueError("Cannot send message as another user")
        
        # Generate chat room ID
        chat_room_id = self._generate_chat_room_id(
            message_data.sender_id,
            message_data.receiver_id,
            message_data.product_id
        )
        
        logger.info(f"Sending message in chat room: {chat_room_id}")
        
        # Find or create chat room
        chat_room = await self.chat_repo.get_chat_room(chat_room_id)
        
        if not chat_room:
            # Create new chat room
            chat_room_data = {
                'id': chat_room_id,
                'user1_id': min(message_data.sender_id, message_data.receiver_id),
                'user2_id': max(message_data.sender_id, message_data.receiver_id),
                'product_id': message_data.product_id,
                'last_message': message_data.text,
                'last_message_time': datetime.now(timezone.utc),
                'unread_count_user1': 1 if message_data.receiver_id == min(message_data.sender_id, message_data.receiver_id) else 0,
                'unread_count_user2': 1 if message_data.receiver_id == max(message_data.sender_id, message_data.receiver_id) else 0
            }
            await self.chat_repo.create_chat_room(chat_room_data)
            logger.info(f"Created new chat room: {chat_room_id}")
        else:
            # Update existing chat room
            unread_field = 'unread_count_user1' if message_data.receiver_id == chat_room['user1_id'] else 'unread_count_user2'
            
            updates = {
                'last_message': message_data.text,
                'last_message_time': datetime.now(timezone.utc)
            }
            
            await self.chat_repo.update_chat_room(chat_room_id, updates)
            await self.chat_repo.increment_unread_count(chat_room_id, unread_field)
            
            logger.info(f"Updated existing chat room: {chat_room_id}")
        
        # Create message
        message_dict = message_data.model_dump()
        message_dict['chat_room_id'] = chat_room_id
        
        message_id = await self.chat_repo.create_message(message_dict)
        
        # Get created message
        message = await self.chat_repo.get_chat_room(chat_room_id)  # Simplified
        message_dict['id'] = message_id
        
        logger.info(f"Created message with id: {message_id}")
        
        return message_dict
    
    async def get_user_chats(
        self,
        user_id: str,
        friends_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all chat rooms for a user.
        
        Args:
            user_id: User ID
            friends_only: Filter to friends only
            
        Returns:
            List of chat rooms
        """
        logger.info(f"Getting chats for user {user_id}, friends_only={friends_only}")
        
        # Get chat rooms
        chat_rooms = await self.chat_repo.get_user_chat_rooms(user_id)
        
        if not friends_only:
            return chat_rooms
        
        # Filter to friends only
        friend_ids = await self.friendship_repo.get_friend_ids(user_id)
        logger.info(f"Found {len(friend_ids)} friends")
        
        filtered_chats = []
        for chat in chat_rooms:
            other_user_id = chat['user2_id'] if chat['user1_id'] == user_id else chat['user1_id']
            
            is_friend = other_user_id in friend_ids
            chat['is_friend'] = is_friend
            
            if is_friend:
                filtered_chats.append(chat)
        
        logger.info(f"Returning {len(filtered_chats)} chats")
        
        return filtered_chats
    
    async def get_chat_messages(
        self,
        chat_room_id: str,
        authenticated_user: str
    ) -> List[Dict[str, Any]]:
        """
        Get all messages in a chat room.
        
        Args:
            chat_room_id: Chat room ID
            authenticated_user: Authenticated user ID
            
        Returns:
            List of messages sorted by timestamp
        """
        logger.info(f"Fetching messages for chat_room_id: {chat_room_id}")
        
        # Verify user is a participant
        is_participant = await self.chat_repo.verify_chat_participant(chat_room_id, authenticated_user)
        
        if not is_participant:
            raise ValueError("Not authorized to view this chat")
        
        # Get messages
        messages = await self.chat_repo.get_chat_messages(chat_room_id)
        
        # Sort by timestamp
        messages.sort(key=lambda x: x.get('timestamp', datetime.min))
        
        logger.info(f"Found {len(messages)} messages")
        
        return messages
    
    async def get_or_create_chat_room(
        self,
        user1_id: str,
        user2_id: str,
        product_id: Optional[str] = None,
        authenticated_user: str = None
    ) -> Dict[str, Any]:
        """
        Get or create a chat room between two users.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            product_id: Optional product ID
            authenticated_user: Authenticated user ID
            
        Returns:
            Chat room data
        """
        # Security: Verify authenticated user is one of the participants
        if authenticated_user and authenticated_user not in [user1_id, user2_id]:
            raise ValueError("Cannot create/access chat room for other users")
        
        # Generate chat room ID
        chat_room_id = self._generate_chat_room_id(user1_id, user2_id, product_id)
        
        # Try to get existing chat room
        chat_room = await self.chat_repo.get_chat_room(chat_room_id)
        
        if chat_room:
            return chat_room
        
        # Create new chat room
        chat_room_data = {
            'id': chat_room_id,
            'user1_id': min(user1_id, user2_id),
            'user2_id': max(user1_id, user2_id),
            'product_id': product_id,
            'last_message': '',
            'last_message_time': datetime.now(timezone.utc),
            'unread_count_user1': 0,
            'unread_count_user2': 0
        }
        
        await self.chat_repo.create_chat_room(chat_room_data)
        
        return chat_room_data
    
    async def mark_messages_as_read(
        self,
        chat_room_id: str,
        user_id: str
    ) -> int:
        """
        Mark all messages in a chat room as read for a user.
        
        Args:
            chat_room_id: Chat room ID
            user_id: User ID
            
        Returns:
            Number of messages marked as read
        """
        # Verify user is a participant
        is_participant = await self.chat_repo.verify_chat_participant(chat_room_id, user_id)
        
        if not is_participant:
            raise ValueError("Not authorized to access this chat")
        
        # Get chat room to determine unread field
        chat_room = await self.chat_repo.get_chat_room(chat_room_id)
        
        if not chat_room:
            raise ValueError("Chat room not found")
        
        unread_field = 'unread_count_user1' if user_id == chat_room['user1_id'] else 'unread_count_user2'
        
        # Reset unread count
        await self.chat_repo.reset_unread_count(chat_room_id, unread_field)
        
        # Mark messages as read
        count = await self.chat_repo.mark_messages_as_read(chat_room_id, user_id)
        
        return count
