"""Pydantic schemas for request/response validation."""

from app.schemas.auth import SendVerificationRequest, VerifyEmailRequest
from app.schemas.chat import ChatRoom, Message, MessageBase, MessageCreate
from app.schemas.need import (
    ExtractedIntent,
    Need,
    NeedBoardRequest,
    NeedBoardResponse,
    NeedCreate,
    NeedFulfillRequest,
    NeedResponse,
    RankedResult,
    SellerDemandBanner,
    SellerNeedFeed,
)
from app.schemas.product import Product, ProductBase, ProductCreate, ProductUpdate
from app.schemas.review import Review, ReviewBase, ReviewCreate
from app.schemas.transaction import (
    ProductTransactionHistory,
    ProductTransactionHistoryBase,
    ProductTransactionHistoryCreate,
    Transaction,
    TransactionBase,
    TransactionCreate,
)
from app.schemas.user import (
    User,
    UserBase,
    UserCreate,
    UserProfile,
    UserProfileBase,
    UserProfileCreate,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "User",
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfile",
    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "Product",
    # Chat schemas
    "MessageBase",
    "MessageCreate",
    "Message",
    "ChatRoom",
    # Transaction schemas
    "TransactionBase",
    "TransactionCreate",
    "Transaction",
    "ProductTransactionHistoryBase",
    "ProductTransactionHistoryCreate",
    "ProductTransactionHistory",
    # Review schemas
    "ReviewBase",
    "ReviewCreate",
    "Review",
    # Need schemas
    "NeedBoardRequest",
    "ExtractedIntent",
    "RankedResult",
    "NeedBoardResponse",
    "NeedCreate",
    "Need",
    "NeedResponse",
    "SellerDemandBanner",
    "SellerNeedFeed",
    "NeedFulfillRequest",
    # Auth schemas
    "SendVerificationRequest",
    "VerifyEmailRequest",
]
