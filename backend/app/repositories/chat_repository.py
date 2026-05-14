"""
Chat repository - all chat-related database operations.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud import firestore
from google.cloud.firestore import Increment

logger = logging.getLogger(__name__)


class ChatRepository:
    """Repository for chat data access."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.chat_rooms_collection = db.collection("chat_rooms")
        self.messages_collection = db.collection("messages")

    # Chat Room operations
    async def get_chat_room(self, chat_room_id: str) -> Optional[Dict[str, Any]]:
        """Get chat room by ID."""
        doc = self.chat_rooms_collection.document(chat_room_id).get()
        if not doc.exists:
            return None

        chat_data = doc.to_dict()
        chat_data["id"] = doc.id
        return chat_data

    async def create_chat_room(self, chat_room_data: Dict[str, Any]) -> str:
        """Create a new chat room."""
        chat_room_data["created_at"] = datetime.now(timezone.utc)

        # Use deterministic ID for chat rooms
        chat_room_id = chat_room_data.get("id")
        if chat_room_id:
            chat_room_ref = self.chat_rooms_collection.document(chat_room_id)
        else:
            chat_room_ref = self.chat_rooms_collection.document()

        chat_room_ref.set(chat_room_data)
        return chat_room_ref.id

    async def update_chat_room(self, chat_room_id: str, updates: Dict[str, Any]) -> bool:
        """Update chat room data."""
        doc_ref = self.chat_rooms_collection.document(chat_room_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.update(updates)
        return True

    async def get_user_chat_rooms(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all chat rooms for a user."""
        chats1 = self.chat_rooms_collection.where("user1_id", "==", user_id).stream()
        chats2 = self.chat_rooms_collection.where("user2_id", "==", user_id).stream()

        chat_rooms = []
        for doc in list(chats1) + list(chats2):
            chat_data = doc.to_dict()
            chat_data["id"] = doc.id
            chat_rooms.append(chat_data)

        return chat_rooms

    async def increment_unread_count(self, chat_room_id: str, user_field: str) -> bool:
        """Atomically increment unread count for a user."""
        doc_ref = self.chat_rooms_collection.document(chat_room_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.update({user_field: Increment(1)})
        return True

    async def reset_unread_count(self, chat_room_id: str, user_field: str) -> bool:
        """Reset unread count for a user."""
        doc_ref = self.chat_rooms_collection.document(chat_room_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.update({user_field: 0})
        return True

    # Message operations
    async def create_message(self, message_data: Dict[str, Any]) -> str:
        """Create a new message."""
        message_data["timestamp"] = datetime.now(timezone.utc)
        message_data["is_read"] = False

        message_ref = self.messages_collection.document()
        message_ref.set(message_data)
        return message_ref.id

    async def get_chat_messages(self, chat_room_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a chat room."""
        messages = []
        for doc in self.messages_collection.where("chat_room_id", "==", chat_room_id).stream():
            message_data = doc.to_dict()
            message_data["id"] = doc.id
            messages.append(message_data)

        return messages

    async def mark_messages_as_read(self, chat_room_id: str, receiver_id: str) -> int:
        """Mark all messages in a chat room as read for a receiver."""
        messages_query = (
            self.messages_collection.where("chat_room_id", "==", chat_room_id)
            .where("receiver_id", "==", receiver_id)
            .where("is_read", "==", False)
        )

        batch = self.db.batch()
        count = 0

        for msg_doc in messages_query.stream():
            batch.update(msg_doc.reference, {"is_read": True})
            count += 1

        batch.commit()
        return count

    async def verify_chat_participant(self, chat_room_id: str, user_id: str) -> bool:
        """Verify if user is a participant in the chat room."""
        chat_room = await self.get_chat_room(chat_room_id)

        if not chat_room:
            return False

        return user_id in [chat_room.get("user1_id"), chat_room.get("user2_id")]
