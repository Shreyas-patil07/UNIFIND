from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


# User Models (Core Authentication Data)
class UserBase(BaseModel):
    name: str = Field(..., max_length=150, min_length=1)
    email: EmailStr
    college: str = Field(..., max_length=200, min_length=1)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v) > 150:
            raise ValueError('Name must be 150 characters or less')
        return v.strip()
    
    @field_validator('college')
    @classmethod
    def validate_college(cls, v):
        if not v or not v.strip():
            raise ValueError('College cannot be empty')
        if len(v) > 200:
            raise ValueError('College must be 200 characters or less')
        return v.strip()


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
    branch: Optional[str] = Field(None, max_length=200)
    avatar: Optional[str] = None
    cover_gradient: Optional[str] = "from-blue-600 to-purple-600"
    bio: Optional[str] = Field(None, max_length=500)
    trust_score: float = Field(default=0.0, ge=0.0, le=100.0)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    review_count: int = Field(default=0, ge=0)
    member_since: str
    
    # Private fields (not shown to public)
    phone: Optional[str] = Field(None, max_length=20)
    hostel_room: Optional[str] = Field(None, max_length=50)
    branch_change_history: Optional[List[Dict]] = []
    photo_change_history: Optional[List[Dict]] = []
    dark_mode: bool = False
    need_board_searches: Optional[List[Dict]] = []  # [{"timestamp": int, "query": str}]
    
    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('Bio must be 500 characters or less')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is not None and len(v) > 20:
            raise ValueError('Phone number must be 20 characters or less')
        return v


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
    title: str = Field(..., max_length=200, min_length=1)
    description: str = Field(..., max_length=2000, min_length=1)
    price: float = Field(..., gt=0, le=10000000)
    category: str = Field(..., min_length=1)
    condition: str = Field(..., min_length=1)
    condition_score: int = Field(..., ge=0, le=100)
    location: str = Field(..., max_length=200, min_length=1)
    images: List[str] = Field(..., min_length=1, max_length=5)
    specifications: Optional[Dict] = {}

    @field_validator('images')
    @classmethod
    def validate_image_urls(cls, v):
        if not v:
            raise ValueError('At least one image is required')
        if len(v) > 5:
            raise ValueError('Maximum 5 images allowed')
        for url in v:
            if not isinstance(url, str) or not url.startswith('https://res.cloudinary.com/'):
                raise ValueError('Each image must be a valid Cloudinary URL (https://res.cloudinary.com/...)')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be 200 characters or less')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        if len(v) > 2000:
            raise ValueError('Description must be 2000 characters or less')
        return v.strip()
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        if not v or not v.strip():
            raise ValueError('Location cannot be empty')
        if len(v) > 200:
            raise ValueError('Location must be 200 characters or less')
        return v.strip()


class ProductCreate(ProductBase):
    seller_id: str


class ProductUpdate(BaseModel):
    """Model for partial product updates (PATCH)"""
    title: Optional[str] = Field(None, max_length=200, min_length=1)
    description: Optional[str] = Field(None, max_length=2000, min_length=1)
    price: Optional[float] = Field(None, gt=0, le=10000000)
    category: Optional[str] = Field(None, min_length=1)
    condition: Optional[str] = Field(None, min_length=1)
    condition_score: Optional[int] = Field(None, ge=0, le=100)
    location: Optional[str] = Field(None, max_length=200, min_length=1)
    images: Optional[List[str]] = Field(None, min_length=1, max_length=5)
    specifications: Optional[Dict] = None

    @field_validator('images')
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None:
            if len(v) < 1:
                raise ValueError('At least one image is required')
            if len(v) > 5:
                raise ValueError('Maximum 5 images allowed')
            for url in v:
                if not isinstance(url, str) or not url.startswith('https://res.cloudinary.com/'):
                    raise ValueError('Each image must be a valid Cloudinary URL (https://res.cloudinary.com/...)')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty')
            if len(v) > 200:
                raise ValueError('Title must be 200 characters or less')
            return v.strip()
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Description cannot be empty')
            if len(v) > 2000:
                raise ValueError('Description must be 2000 characters or less')
            return v.strip()
        return v
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Location cannot be empty')
            if len(v) > 200:
                raise ValueError('Location must be 200 characters or less')
            return v.strip()
        return v


class Product(ProductBase):
    id: str
    seller_id: str
    views: int = 0
    viewed_by: List[str] = []  # List of user IDs who have viewed this product
    posted_date: datetime
    updated_at: datetime
    is_active: bool = True


# Chat Models
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
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., max_length=1000, min_length=1)
    reviewer_id: str
    reviewed_user_id: str
    
    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v):
        if not v or not v.strip():
            raise ValueError('Review comment cannot be empty')
        if len(v) > 1000:
            raise ValueError('Review comment must be 1000 characters or less')
        return v.strip()


class ReviewCreate(ReviewBase):
    product_id: Optional[str] = None


class Review(ReviewBase):
    id: str
    product_id: Optional[str] = None
    created_at: datetime


# AI Need Board Models
class NeedBoardRequest(BaseModel):
    query: str = Field(..., max_length=500, min_length=1)
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v) > 500:
            raise ValueError('Query must be 500 characters or less')
        return v.strip()


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
    images: Optional[List[str]] = []


class NeedBoardResponse(BaseModel):
    extracted: ExtractedIntent
    rankedResults: List[RankedResult]
    searches_remaining: int
