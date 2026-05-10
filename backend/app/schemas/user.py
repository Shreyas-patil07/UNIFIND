"""
User-related Pydantic schemas for request/response validation.
"""
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


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile - all fields optional."""
    branch: Optional[str] = Field(None, max_length=200)
    avatar: Optional[str] = None
    cover_gradient: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    hostel_room: Optional[str] = Field(None, max_length=50)
    dark_mode: Optional[bool] = None
    
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
