"""
Transaction-related Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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


# Product Transaction History Models (for mark as sold/active tracking)
class ProductTransactionHistoryBase(BaseModel):
    amount: float
    product_id: str
    seller_id: str
    status: str  # "completed"
    transaction_type_sold: bool  # True when marked as sold, False when marked as active


class ProductTransactionHistoryCreate(ProductTransactionHistoryBase):
    pass


class ProductTransactionHistory(ProductTransactionHistoryBase):
    id: str
    created_at: datetime
