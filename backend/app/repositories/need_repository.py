"""
Firestore implementation of Need repository.
This implementation can be replaced with PostgreSQL without changing business logic.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from app.repositories.base import NeedRepositoryInterface

logger = logging.getLogger(__name__)


class NeedRepository(NeedRepositoryInterface):
    """Repository for need data access."""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection = db.collection("needs")

    async def create(self, need_data: Dict[str, Any]) -> str:
        """Create a new need."""
        need_data["created_at"] = datetime.now()
        need_data["status"] = "open"
        need_data["matched_listings"] = []
        need_data["interested_sellers"] = []

        doc_ref = self.collection.document()
        doc_ref.set(need_data)
        return doc_ref.id

    async def get_by_id(self, need_id: str) -> Optional[Dict[str, Any]]:
        """Get need by ID."""
        doc = self.collection.document(need_id).get()
        if not doc.exists:
            return None

        need_data = doc.to_dict()
        need_data["id"] = doc.id
        return need_data

    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all needs posted by a user."""
        query = self.collection.where("user_id", "==", user_id).order_by(
            "created_at", direction="DESCENDING"
        )

        if offset:
            query = query.offset(offset)

        query = query.limit(limit)

        needs = []
        for doc in query.stream():
            need_data = doc.to_dict()
            need_data["id"] = doc.id
            needs.append(need_data)

        return needs

    async def get_open_needs(
        self, limit: int = 100, offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all open needs."""
        query = self.collection.where("status", "==", "open").order_by(
            "created_at", direction="DESCENDING"
        )

        if offset:
            query = query.offset(offset)

        query = query.limit(limit)

        needs = []
        for doc in query.stream():
            need_data = doc.to_dict()
            need_data["id"] = doc.id
            needs.append(need_data)

        return needs

    async def get_by_category(
        self, category: str, limit: int = 50, offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get needs by category."""
        query = (
            self.collection.where("category", "==", category)
            .where("status", "==", "open")
            .order_by("created_at", direction="DESCENDING")
        )

        if offset:
            query = query.offset(offset)

        query = query.limit(limit)

        needs = []
        for doc in query.stream():
            need_data = doc.to_dict()
            need_data["id"] = doc.id
            needs.append(need_data)

        return needs

    async def get_recent_by_user(self, user_id: str, days: int = 1) -> List[Dict[str, Any]]:
        """Get recent needs by user (for rate limiting)."""
        date_threshold = datetime.now() - timedelta(days=days)

        query = self.collection.where("user_id", "==", user_id).where(
            "created_at", ">=", date_threshold
        )

        needs = []
        for doc in query.stream():
            need_data = doc.to_dict()
            need_data["id"] = doc.id
            needs.append(need_data)

        return needs

    async def update(self, need_id: str, updates: Dict[str, Any]) -> bool:
        """Update need data."""
        doc_ref = self.collection.document(need_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.update(updates)
        return True

    async def update_matched_listings(self, need_id: str, listing_ids: List[str]) -> bool:
        """Update matched listings for a need."""
        return await self.update(need_id, {"matched_listings": listing_ids})

    async def add_interested_seller(self, need_id: str, seller_id: str) -> bool:
        """Add a seller to interested sellers list."""
        doc_ref = self.collection.document(need_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        need_data = doc.to_dict()
        interested_sellers = need_data.get("interested_sellers", [])

        if seller_id not in interested_sellers:
            interested_sellers.append(seller_id)
            doc_ref.update({"interested_sellers": interested_sellers})

        return True

    async def mark_as_fulfilled(self, need_id: str, product_id: Optional[str] = None) -> bool:
        """Mark a need as fulfilled."""
        updates = {"status": "fulfilled", "fulfilled_at": datetime.now()}

        if product_id:
            updates["fulfilled_with_product"] = product_id

        return await self.update(need_id, updates)

    async def mark_as_expired(self, need_id: str) -> bool:
        """Mark a need as expired."""
        return await self.update(need_id, {"status": "expired", "expired_at": datetime.now()})

    async def delete(self, need_id: str) -> bool:
        """Delete a need."""
        doc_ref = self.collection.document(need_id)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        doc_ref.delete()
        return True

    async def verify_ownership(self, need_id: str, user_id: str) -> bool:
        """Verify if user owns the need."""
        doc = self.collection.document(need_id).get()

        if not doc.exists:
            return False

        need_data = doc.to_dict()
        return need_data.get("user_id") == user_id

    async def get_needs_by_college(
        self, college: str, limit: int = 50, offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get open needs by college."""
        query = (
            self.collection.where("college", "==", college)
            .where("status", "==", "open")
            .order_by("created_at", direction="DESCENDING")
        )

        if offset:
            query = query.offset(offset)

        query = query.limit(limit)

        needs = []
        for doc in query.stream():
            need_data = doc.to_dict()
            need_data["id"] = doc.id
            needs.append(need_data)

        return needs
