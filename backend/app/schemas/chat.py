"""
Chat-related Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    text: str = Field(..., max_length=5000, min_length=1)
    sender_id: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Message text cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message must be 5000 characters or less')
        return v.strip()


class MessageCreate(MessageBase):
    receiver_id: str
    product_id: Optional[str] = None
    reply_to: Optional[str] = None  # ID of message being replied to


class Message(MessageBase):
    id: str
    receiver_id: str
    product_id: Optional[str] = None
    chat_room_id: str
    timestamp: datetime
    is_read: bool = False
    reply_to: Optional[str] = None  # ID of message being replied to


class ChatRoom(BaseModel):
    id: str
    user1_id: str
    user2_id: str
    product_id: Optional[str] = None
    last_message: str
    last_message_time: datetime
    unread_count_user1: int = 0
    unread_count_user2: int = 0
    created_at: datetime
