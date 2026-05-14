"""
Centralized response models for consistent API responses.
"""

from typing import Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Standard success response."""

    message: str
    status: str = "success"

    class Config:
        json_schema_extra = {
            "example": {"message": "Operation completed successfully", "status": "success"}
        }


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str

    class Config:
        json_schema_extra = {
            "example": {"error": "Validation Error", "detail": "Invalid request data"}
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {"items": [], "total": 100, "page": 1, "page_size": 20, "pages": 5}
        }


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str

    class Config:
        json_schema_extra = {"example": {"message": "Action completed successfully"}}


class CreatedResponse(BaseModel):
    """Response for resource creation."""

    message: str
    id: str

    class Config:
        json_schema_extra = {
            "example": {"message": "Resource created successfully", "id": "abc123"}
        }


class DeletedResponse(BaseModel):
    """Response for resource deletion."""

    message: str
    deleted: Dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Resource deleted successfully",
                "deleted": {"product": "abc123"},
            }
        }


class StatusResponse(BaseModel):
    """Health/status check response."""

    status: str
    version: str
    environment: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {"status": "ok", "version": "2.1.0", "environment": "production"}
        }


class ValidationErrorDetail(BaseModel):
    """Validation error detail."""

    loc: List[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Validation error response (422)."""

    error: str = "Validation Error"
    detail: List[ValidationErrorDetail]

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ],
            }
        }


class RateLimitResponse(BaseModel):
    """Rate limit exceeded response (429)."""

    error: str = "Rate Limit Exceeded"
    detail: str
    retry_after: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Rate Limit Exceeded",
                "detail": "Too many requests. Please wait 60 seconds.",
                "retry_after": 60,
            }
        }


class UnauthorizedResponse(BaseModel):
    """Unauthorized response (401)."""

    detail: str = "Authentication required"

    class Config:
        json_schema_extra = {"example": {"detail": "Missing authentication token"}}


class ForbiddenResponse(BaseModel):
    """Forbidden response (403)."""

    detail: str = "Not authorized to perform this action"

    class Config:
        json_schema_extra = {"example": {"detail": "Cannot access another user's data"}}


class NotFoundResponse(BaseModel):
    """Not found response (404)."""

    detail: str = "Resource not found"

    class Config:
        json_schema_extra = {"example": {"detail": "Product not found"}}


class ConflictResponse(BaseModel):
    """Conflict response (409)."""

    error: str = "Conflict"
    detail: str

    class Config:
        json_schema_extra = {"example": {"error": "Conflict", "detail": "Resource already exists"}}


class ServiceUnavailableResponse(BaseModel):
    """Service unavailable response (503)."""

    error: str = "Service Unavailable"
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Service Unavailable",
                "detail": "AI service temporarily unavailable",
            }
        }


class GatewayTimeoutResponse(BaseModel):
    """Gateway timeout response (504)."""

    error: str = "Gateway Timeout"
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Gateway Timeout",
                "detail": "AI service timeout. Please try again.",
            }
        }
