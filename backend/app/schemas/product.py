"""
Product-related Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("images")
    @classmethod
    def validate_image_urls(cls, v):
        if not v:
            raise ValueError("At least one image is required")
        if len(v) > 5:
            raise ValueError("Maximum 5 images allowed")
        for url in v:
            if not isinstance(url, str) or not url.startswith("https://res.cloudinary.com/"):
                raise ValueError(
                    "Each image must be a valid Cloudinary URL (https://res.cloudinary.com/...)"
                )
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        if len(v) > 2000:
            raise ValueError("Description must be 2000 characters or less")
        return v.strip()

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if not v or not v.strip():
            raise ValueError("Location cannot be empty")
        if len(v) > 200:
            raise ValueError("Location must be 200 characters or less")
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
    mark_as_sold: Optional[bool] = None
    sold_to: Optional[str] = None  # Firebase UID of the buyer

    @field_validator("images")
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None:
            if len(v) < 1:
                raise ValueError("At least one image is required")
            if len(v) > 5:
                raise ValueError("Maximum 5 images allowed")
            for url in v:
                if not isinstance(url, str) or not url.startswith("https://res.cloudinary.com/"):
                    raise ValueError(
                        "Each image must be a valid Cloudinary URL (https://res.cloudinary.com/...)"
                    )
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            if len(v) > 200:
                raise ValueError("Title must be 200 characters or less")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Description cannot be empty")
            if len(v) > 2000:
                raise ValueError("Description must be 2000 characters or less")
            return v.strip()
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Location cannot be empty")
            if len(v) > 200:
                raise ValueError("Location must be 200 characters or less")
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
    mark_as_sold: bool = False
    sold_to: Optional[str] = None  # Firebase UID of the buyer
