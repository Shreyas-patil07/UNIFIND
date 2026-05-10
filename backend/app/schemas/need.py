"""
Need-related Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime


# AI Need Board Models (Existing Search)
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


# NEW: Need Posting Models (Demand → Supply Engine)
class NeedCreate(BaseModel):
    """Request model for creating a new need"""
    raw_text: str = Field(..., max_length=500, min_length=1)
    
    @field_validator('raw_text')
    @classmethod
    def validate_raw_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Need description cannot be empty')
        if len(v) > 500:
            raise ValueError('Need description must be 500 characters or less')
        return v.strip()


class Need(BaseModel):
    """Structured need object stored in database"""
    id: str
    user_id: str
    raw_text: str
    title: str
    category: str
    tags: List[str]
    price_range: Optional[Dict[str, float]] = None  # {"min": 0, "max": 5000}
    college: str
    location: Optional[str] = None
    created_at: datetime
    status: str = "open"  # open, fulfilled, expired
    matched_listings: List[str] = []  # List of product IDs
    interested_sellers: List[str] = []  # List of user IDs who saved this need


class NeedResponse(BaseModel):
    """Response after creating a need"""
    need: Need
    matched_listings: List[RankedResult]


class SellerDemandBanner(BaseModel):
    """Banner data for seller dashboard"""
    total_relevant_needs: int
    top_categories: List[str]
    message: str


class SellerNeedFeed(BaseModel):
    """Feed of relevant needs for a seller"""
    needs: List[Dict]  # List of needs with relevance scores
    total_count: int


class NeedFulfillRequest(BaseModel):
    """Request to mark a need as fulfilled"""
    product_id: Optional[str] = None
