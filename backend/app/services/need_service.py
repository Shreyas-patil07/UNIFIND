"""
Need service - business logic for need operations (Demand → Supply Engine).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.ai.prompts.intent_extractor import extract_intent
from app.ai.ranking.need_matcher import (
    extract_keywords,
    match_need_to_listings,
    match_need_to_sellers,
    normalize_text,
    rank_needs_for_seller,
)
from app.repositories.need_repository import NeedRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.need import NeedCreate

logger = logging.getLogger(__name__)

# Rate limiting
MAX_NEEDS_PER_DAY = 5
NEED_EXPIRY_DAYS = 7


class NeedService:
    """Service for need business logic."""

    def __init__(
        self, need_repo: NeedRepository, product_repo: ProductRepository, user_repo: UserRepository
    ):
        self.need_repo = need_repo
        self.product_repo = product_repo
        self.user_repo = user_repo

    def _extract_tags_from_text(self, text: str) -> List[str]:
        """Extract meaningful tags from text."""
        keywords = extract_keywords(text)
        # Limit to top 5 most relevant keywords
        return list(keywords)[:5]

    def _generate_title_from_text(self, text: str) -> str:
        """Generate a concise title from raw text."""
        normalized = normalize_text(text)
        words = normalized.split()
        # Take first 8 words as title
        title_words = words[:8]
        title = " ".join(title_words)
        if len(words) > 8:
            title += "..."
        return title.capitalize()

    async def create_need(self, need_data: NeedCreate, user_id: str) -> Dict[str, Any]:
        """
        Create a new need (buyer posts what they're looking for).

        Process:
        1. Check rate limit
        2. Extract structured data from raw text using AI
        3. Store need in database
        4. Find matching listings
        5. Notify relevant sellers

        Args:
            need_data: Need creation data
            user_id: User ID creating the need

        Returns:
            Dictionary with need and matched listings
        """
        current_time = datetime.now()

        # Check rate limit (5 needs per day)
        yesterday = current_time - timedelta(days=1)
        recent_needs = await self.need_repo.get_by_user_since(user_id, yesterday)

        if len(recent_needs) >= MAX_NEEDS_PER_DAY:
            raise ValueError(
                f"Daily limit reached. You can post {MAX_NEEDS_PER_DAY} needs per day."
            )

        # Extract intent using AI
        logger.info(f"Extracting intent from: {need_data.raw_text[:50]}...")
        intent = await extract_intent(need_data.raw_text, user_id=user_id)

        # Generate structured data
        title = self._generate_title_from_text(need_data.raw_text)
        tags = self._extract_tags_from_text(need_data.raw_text)

        # Get user's college
        user = await self.user_repo.get_by_id(user_id)
        college = user.get("college", "Unknown") if user else "Unknown"

        # Create price range if max_price is specified
        price_range = None
        if intent.get("max_price"):
            price_range = {"min": 0, "max": float(intent["max_price"])}

        # Create need object
        need_dict = {
            "user_id": user_id,
            "raw_text": need_data.raw_text,
            "title": title,
            "category": intent.get("category", "Other"),
            "tags": tags,
            "price_range": price_range,
            "college": college,
            "location": None,
            "status": "open",
            "matched_listings": [],
            "interested_sellers": [],
        }

        # Save to database
        need_id = await self.need_repo.create(need_dict)
        logger.info(f"Created need {need_id} for user {user_id}")

        # Find matching listings
        active_products = await self.product_repo.get_active_products(limit=100)

        listings = []
        for product in active_products:
            # Extract tags from product
            product_tags = [product.get("category", "")]
            product_tags.extend(self._extract_tags_from_text(product.get("title", "")))

            listings.append(
                {
                    "id": product["id"],
                    "title": product.get("title", ""),
                    "description": product.get("description", ""),
                    "price": product.get("price", 0),
                    "category": product.get("category", ""),
                    "tags": product_tags,
                    "images": product.get("images", []),
                }
            )

        logger.info(f"Found {len(listings)} active listings to match against")

        # Match need to listings
        matches = match_need_to_listings(need_dict, listings, limit=10)

        # Store matched listing IDs
        matched_ids = [m["id"] for m in matches]
        await self.need_repo.update(need_id, {"matched_listings": matched_ids})

        logger.info(f"Found {len(matches)} matching listings for need {need_id}")

        # Find relevant sellers to notify
        sellers_data = []
        products_by_seller = {}

        for listing in listings:
            seller_id = None
            for product in active_products:
                if product["id"] == listing["id"]:
                    seller_id = product.get("seller_id")
                    break

            if seller_id and seller_id != user_id:  # Don't notify the buyer
                if seller_id not in products_by_seller:
                    products_by_seller[seller_id] = []
                products_by_seller[seller_id].append(listing)

        for seller_id, seller_listings in products_by_seller.items():
            sellers_data.append({"user_id": seller_id, "listings": seller_listings})

        relevant_sellers = match_need_to_sellers(need_dict, sellers_data, limit=20)
        logger.info(f"Identified {len(relevant_sellers)} relevant sellers")

        # Get created need
        need = await self.need_repo.get_by_id(need_id)

        return {"need": need, "matched_listings": matches}

    async def get_need_matches(self, need_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get matching listings for a specific need.

        Args:
            need_id: Need ID
            user_id: User ID (must be need owner)

        Returns:
            List of matched listings
        """
        # Get need
        need = await self.need_repo.get_by_id(need_id)

        if not need:
            raise ValueError("Need not found")

        # Verify ownership
        if need.get("user_id") != user_id:
            raise ValueError("Not authorized to view this need")

        # Get matched listings
        matched_ids = need.get("matched_listings", [])

        if not matched_ids:
            return []

        # Fetch listing details
        matches = []
        for product_id in matched_ids[:10]:
            product = await self.product_repo.get_by_id(product_id)
            if product:
                matches.append(
                    {
                        "id": product_id,
                        "title": product.get("title"),
                        "price": product.get("price"),
                        "images": product.get("images", []),
                        "category": product.get("category"),
                    }
                )

        return matches

    async def get_seller_feed(self, seller_id: str) -> Dict[str, Any]:
        """
        Get feed of relevant needs for a seller.
        Shows needs that match the seller's listings.

        Args:
            seller_id: Seller user ID

        Returns:
            Dictionary with needs and count
        """
        # Get seller's active listings
        seller_products = await self.product_repo.get_by_seller(
            seller_id, is_active=True, mark_as_sold=False
        )

        seller_listings = []
        for product in seller_products:
            product_tags = [product.get("category", "")]
            product_tags.extend(self._extract_tags_from_text(product.get("title", "")))

            seller_listings.append(
                {
                    "id": product["id"],
                    "title": product.get("title", ""),
                    "description": product.get("description", ""),
                    "category": product.get("category", ""),
                    "tags": product_tags,
                }
            )

        if not seller_listings:
            return {"needs": [], "total_count": 0}

        # Get open needs
        open_needs = await self.need_repo.get_by_status("open", limit=50)

        needs_list = []
        for need in open_needs:
            needs_list.append({"id": need["id"], **need})

        # Rank needs by relevance
        ranked_needs = rank_needs_for_seller(seller_listings, needs_list, limit=10)

        # Enrich with user info
        for need in ranked_needs:
            user_id = need.get("user_id")
            user = await self.user_repo.get_by_id(user_id)
            if user:
                need["buyer_name"] = user.get("name", "Anonymous")
                need["buyer_college"] = user.get("college", "Unknown")

        return {"needs": ranked_needs, "total_count": len(ranked_needs)}

    async def get_seller_banner(self, seller_id: str) -> Dict[str, Any]:
        """
        Get banner data for seller dashboard.
        Shows count of relevant needs.

        Args:
            seller_id: Seller user ID

        Returns:
            Banner data dictionary
        """
        # Get seller's active listings
        seller_products = await self.product_repo.get_by_seller(
            seller_id, is_active=True, mark_as_sold=False
        )

        seller_listings = []
        seller_categories = set()

        for product in seller_products:
            category = product.get("category", "")
            seller_categories.add(category)

            product_tags = [category]
            product_tags.extend(self._extract_tags_from_text(product.get("title", "")))

            seller_listings.append(
                {
                    "id": product["id"],
                    "title": product.get("title", ""),
                    "description": product.get("description", ""),
                    "category": category,
                    "tags": product_tags,
                }
            )

        if not seller_listings:
            return {
                "total_relevant_needs": 0,
                "top_categories": [],
                "message": "List items to see buyer demand",
            }

        # Get open needs
        open_needs = await self.need_repo.get_by_status("open", limit=100)

        needs_list = []
        for need in open_needs:
            needs_list.append({"id": need["id"], **need})

        # Rank needs
        ranked_needs = rank_needs_for_seller(seller_listings, needs_list, limit=50)

        # Get top categories
        category_counts = {}
        for need in ranked_needs:
            cat = need.get("category", "Other")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat for cat, _ in top_categories[:3]]

        # Generate message
        count = len(ranked_needs)
        if count == 0:
            message = "No active buyer needs match your items"
        elif count == 1:
            message = "1 buyer needs items you can sell"
        else:
            message = f"{count} buyers need items you can sell"

        return {"total_relevant_needs": count, "top_categories": top_categories, "message": message}

    async def fulfill_need(self, need_id: str, product_id: Optional[str], user_id: str) -> bool:
        """
        Mark a need as fulfilled.

        Args:
            need_id: Need ID
            product_id: Optional product ID that fulfilled the need
            user_id: User ID (must be need owner)

        Returns:
            True if successful
        """
        # Get need
        need = await self.need_repo.get_by_id(need_id)

        if not need:
            raise ValueError("Need not found")

        # Verify ownership
        if need.get("user_id") != user_id:
            raise ValueError("Not authorized to modify this need")

        # Update status
        updates = {
            "status": "fulfilled",
            "fulfilled_at": datetime.now(),
            "fulfilled_with_product": product_id,
        }

        return await self.need_repo.update(need_id, updates)

    async def save_need(self, need_id: str, seller_id: str) -> bool:
        """
        Save a need (seller expresses interest).

        Args:
            need_id: Need ID
            seller_id: Seller user ID

        Returns:
            True if successful
        """
        # Get need
        need = await self.need_repo.get_by_id(need_id)

        if not need:
            raise ValueError("Need not found")

        interested_sellers = need.get("interested_sellers", [])

        # Add seller if not already interested
        if seller_id not in interested_sellers:
            interested_sellers.append(seller_id)
            return await self.need_repo.update(need_id, {"interested_sellers": interested_sellers})

        return True

    async def get_my_needs(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get all needs posted by the current user.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of needs
        """
        needs = await self.need_repo.get_by_user(user_id, limit=limit)
        return needs
