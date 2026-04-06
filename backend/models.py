from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime


# User Models (Core Authentication Data)
class UserBase(BaseModel):
    name: str
    email: EmailStr
    college: str


class UserCreate(UserBase):
    firebase_uid: str


class User(UserBase):
    id: str
    firebase_uid: str
    email_verified: bool = False
    created_at: datetime


# User Profile Models (Extended Information)
class UserProfileBase(BaseModel):
    # Public fields
    branch: Optional[str] = None
    avatar: Optional[str] = None
    cover_gradient: Optional[str] = "from-blue-600 to-purple-600"
    bio: Optional[str] = None
    trust_score: float = 0.0
    rating: float = 0.0
    review_count: int = 0
    member_since: str
    
    # Private fields (not shown to public)
    phone: Optional[str] = None
    hostel_room: Optional[str] = None
    branch_change_history: Optional[List[Dict]] = []
    photo_change_history: Optional[List[Dict]] = []
    dark_mode: bool = False


class UserProfileCreate(UserProfileBase):
    user_id: str


class UserProfile(UserProfileBase):
    id: str
    user_id: str
    updated_at: datetime


# Transaction History Models
class TransactionBase(BaseModel):
    user_id: str
    product_id: str
    transaction_type: str  # "buy" or "sell"
    amount: float
    status: str  # "pending", "completed", "cancelled"
    other_party_id: str  # buyer_id if selling, seller_id if buying


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: str
    created_at: datetime
    completed_at: Optional[datetime] = None


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
    receiver_id: str
    product_id: Optional[str] = None
    chat_room_id: str
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


# AI Need Board Models
class NeedBoardRequest(BaseModel):
    query: str


class ExtractedIntent(BaseModel):
    category: str
    subject: str
    semester: str
    max_price: Optional[float] = None
    condition: str
    intent_summary: str


class RankedResult(BaseModel):
    id: str | int
    match_score: int  # 0–100
    reason: str
    title: Optional[str] = None
    price: Optional[float] = None


class NeedBoardResponse(BaseModel):
    extracted: ExtractedIntent
    rankedResults: List[RankedResult]
