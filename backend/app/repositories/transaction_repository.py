"""
Transaction repository - all transaction-related database operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

logger = logging.getLogger(__name__)


class TransactionRepository:
    """Repository for transaction data access."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection("transaction_history")

    async def create(self, transaction_data: Dict[str, Any]) -> str:
        """Create a new transaction record."""
        transaction_data["created_at"] = datetime.now()

        doc_ref = self.collection.document()
        doc_ref.set(transaction_data)
        return doc_ref.id

    async def get_by_user(
        self, user_id: str, transaction_type: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get transaction history for a user."""
        query = self.collection.where(filter=FieldFilter("user_id", "==", user_id))

        if transaction_type:
            query = query.where(filter=FieldFilter("transaction_type", "==", transaction_type))

        query = query.order_by("created_at", direction="DESCENDING").limit(limit)

        transactions = []
        for doc in query.stream():
            transaction_data = doc.to_dict()
            transaction_data["id"] = doc.id
            transactions.append(transaction_data)

        return transactions

    async def get_by_seller(
        self,
        seller_id: str,
        product_id: Optional[str] = None,
        transaction_type_sold: Optional[bool] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get transaction history for a seller."""
        query = self.collection.where(filter=FieldFilter("seller_id", "==", seller_id))

        if product_id:
            query = query.where(filter=FieldFilter("product_id", "==", product_id))

        if transaction_type_sold is not None:
            query = query.where(
                filter=FieldFilter("transaction_type_sold", "==", transaction_type_sold)
            )

        query = query.order_by("created_at", direction="DESCENDING").limit(limit)

        transactions = []
        for doc in query.stream():
            transaction_data = doc.to_dict()
            transaction_data["id"] = doc.id
            transactions.append(transaction_data)

        return transactions

    async def get_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get transaction history for a product."""
        query = self.collection.where(filter=FieldFilter("product_id", "==", product_id))
        query = query.order_by("created_at", direction="DESCENDING")

        transactions = []
        for doc in query.stream():
            transaction_data = doc.to_dict()
            transaction_data["id"] = doc.id
            transactions.append(transaction_data)

        return transactions

    async def get_stats(self, seller_id: str, days: int = 30) -> Dict[str, Any]:
        """Get transaction statistics for a seller."""
        date_threshold = datetime.now() - timedelta(days=days)

        query = self.collection.where(filter=FieldFilter("seller_id", "==", seller_id))
        query = query.where(filter=FieldFilter("created_at", ">=", date_threshold))

        transactions = list(query.stream())

        total_sold = 0
        total_active = 0
        total_revenue = 0.0

        for doc in transactions:
            transaction_data = doc.to_dict()
            if transaction_data.get("transaction_type_sold"):
                total_sold += 1
                total_revenue += transaction_data.get("amount", 0)
            else:
                total_active += 1

        return {
            "period_days": days,
            "total_sold": total_sold,
            "total_active": total_active,
            "total_revenue": total_revenue,
            "total_transactions": len(transactions),
        }

    async def update(self, transaction_id: str, updates: Dict[str, Any]) -> bool:
        """Update transaction data."""
        doc_ref = self.collection.document(transaction_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        if "status" in updates and updates["status"] == "completed":
            updates["completed_at"] = datetime.now()

        doc_ref.update(updates)
        return True
