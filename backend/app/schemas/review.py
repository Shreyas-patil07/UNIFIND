"""
Review-related Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


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
