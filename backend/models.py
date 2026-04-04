from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# User Models
class UserBase(BaseModel):
    name: str
    email: EmailStr
    college: str
    avatar: Optional[str] = None


class UserCreate(UserBase):
    firebase_uid: str


class User(UserBase):
    id: str
    firebase_uid: str
    trust_score: float = 0.0
    rating: float = 0.0
    review_count: int = 0
    member_since: str
    created_at: datetime


# Product Models
class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    category: str
    condition: str
    condition_score: int
    location: str
    images: List[str] = []
    specifications: Optional[Dict] = {}


class ProductCreate(ProductBase):
    seller_id: str


class Product(ProductBase):
    id: str
    seller_id: str
    views: int = 0
    posted_date: datetime
    is_active: bool = True


# Chat Models
class MessageBase(BaseModel):
    text: str
    sender_id: str


class MessageCreate(MessageBase):
    receiver_id: str
    product_id: Optional[str] = None


class Message(MessageBase):
    id: str
    timestamp: datetime
    is_read: bool = False


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


# Review Models
class ReviewBase(BaseModel):
    rating: int
    comment: str
    reviewer_id: str
    reviewed_user_id: str


class ReviewCreate(ReviewBase):
    product_id: Optional[str] = None


class Review(ReviewBase):
    id: str
    product_id: Optional[str] = None
    created_at: datetime
