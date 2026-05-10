"""
Common response schemas and standardized API responses.
Ensures consistent response format across all endpoints.
"""
from typing import Optional, Any, List, Dict, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class Meta(BaseModel):
    """Metadata included in all API responses."""
    request_id: str = Field(..., description="Unique request identifier for tracing")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    version: str = Field(default="2.1.0", description="API version")


class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: Dict[str, Any] = Field(..., description="Error information")
    meta: Meta = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "details": [
                        {
                            "field": "email",
                            "message": "Invalid email format",
                            "code": "invalid_format"
                        }
                    ]
                },
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2026-05-10T12:00:00Z",
                    "version": "2.1.0"
                }
            }
        }


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success response."""
    data: T = Field(..., description="Response data")
    meta: Meta = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {"id": "123", "name": "Example"},
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2026-05-10T12:00:00Z",
                    "version": "2.1.0"
                }
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated response."""
    data: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination information")
    meta: Meta = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"id": "1", "name": "Item 1"},
                    {"id": "2", "name": "Item 2"}
                ],
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False
                },
                "meta": {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "timestamp": "2026-05-10T12:00:00Z",
                    "version": "2.1.0"
                }
            }
        }


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str = Field(..., description="Response message")
    meta: Meta = Field(..., description="Response metadata")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: Optional[str] = Field(None, description="Environment name")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "2.1.0",
                "environment": "production",
                "timestamp": "2026-05-10T12:00:00Z"
            }
        }


# Error codes
class ErrorCode:
    """Standard error codes."""
    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_REQUEST = "INVALID_REQUEST"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"


def create_error_response(
    code: str,
    message: str,
    details: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        code: Error code from ErrorCode class
        message: Human-readable error message
        details: Optional list of detailed error information
        request_id: Optional request ID for tracing
        
    Returns:
        dict: Standardized error response
    """
    error_data = {
        "code": code,
        "message": message
    }
    
    if details:
        error_data["details"] = [d.dict() for d in details]
    
    return {
        "error": error_data,
        "meta": {
            "request_id": request_id or "unknown",
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0"
        }
    }


def create_success_response(
    data: Any,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        request_id: Optional request ID for tracing
        
    Returns:
        dict: Standardized success response
    """
    return {
        "data": data,
        "meta": {
            "request_id": request_id or "unknown",
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0"
        }
    }


def create_paginated_response(
    data: List[Any],
    page: int,
    page_size: int,
    total: int,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized paginated response.
    
    Args:
        data: List of items
        page: Current page number
        page_size: Items per page
        total: Total number of items
        request_id: Optional request ID for tracing
        
    Returns:
        dict: Standardized paginated response
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    
    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "meta": {
            "request_id": request_id or "unknown",
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0"
        }
    }
