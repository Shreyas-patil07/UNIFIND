"""Pydantic schemas for request/response validation."""

from app.schemas.user import (
    UserBase, UserCreate, User,
    UserProfileBase, UserProfileCreate, UserProfile
)
from app.schemas.product import (
    ProductBase, ProductCreate, ProductUpdate, Product
)
from app.schemas.chat import (
    MessageBase, MessageCreate, Message, ChatRoom
)
from app.schemas.transaction import (
    TransactionBase, TransactionCreate, Transaction,
    ProductTransactionHistoryBase, ProductTransactionHistoryCreate, ProductTransactionHistory
)
from app.schemas.review import (
    ReviewBase, ReviewCreate, Review
)
from app.schemas.need import (
    NeedBoardRequest, ExtractedIntent, RankedResult, NeedBoardResponse,
    NeedCreate, Need, NeedResponse,
    SellerDemandBanner, SellerNeedFeed, NeedFulfillRequest
)
from app.schemas.auth import (
    SendVerificationRequest, VerifyEmailRequest
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "User",
    "UserProfileBase", "UserProfileCreate", "UserProfile",
    # Product schemas
    "ProductBase", "ProductCreate", "ProductUpdate", "Product",
    # Chat schemas
    "MessageBase", "MessageCreate", "Message", "ChatRoom",
    # Transaction schemas
    "TransactionBase", "TransactionCreate", "Transaction",
    "ProductTransactionHistoryBase", "ProductTransactionHistoryCreate", "ProductTransactionHistory",
    # Review schemas
    "ReviewBase", "ReviewCreate", "Review",
    # Need schemas
    "NeedBoardRequest", "ExtractedIntent", "RankedResult", "NeedBoardResponse",
    "NeedCreate", "Need", "NeedResponse",
    "SellerDemandBanner", "SellerNeedFeed", "NeedFulfillRequest",
    # Auth schemas
    "SendVerificationRequest", "VerifyEmailRequest",
]
