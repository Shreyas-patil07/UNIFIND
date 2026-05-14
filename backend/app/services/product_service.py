"""
Product service - business logic for product operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product business logic."""

    def __init__(self, product_repo: ProductRepository, user_repo: UserRepository):
        self.product_repo = product_repo
        self.user_repo = user_repo

    async def get_product_by_id(
        self, product_id: str, viewer_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get product by ID and optionally track view (OPTIMIZED).

        Args:
            product_id: Product ID
            viewer_id: Optional user ID to track view

        Returns:
            Product data enriched with seller info
        """
        product = await self.product_repo.get_by_id(product_id)

        if not product:
            return None

        # Track unique view if viewer is authenticated
        # OPTIMIZATION: Don't refetch product after view increment
        if viewer_id:
            await self.product_repo.increment_view(product_id, viewer_id)
            # Update view count in memory instead of refetching
            product["views"] = product.get("views", 0) + 1

        # Enrich with seller info
        product = await self._enrich_with_seller(product)

        return product

    async def get_all_products(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        condition: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search_query: Optional[str] = None,
        sort: str = "newest",
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Get all products with filtering, sorting, and pagination (OPTIMIZED).
        
        PERFORMANCE: Pushes filters to Firestore, reduces Python-side filtering.

        Returns:
            Dictionary with items, total, page, page_size, pages
        """
        # Enforce max page size
        MAX_PAGE_SIZE = 100
        page_size = min(page_size, MAX_PAGE_SIZE)

        # Calculate offset for pagination
        offset = (page - 1) * page_size

        # Fetch products with Firestore filters (OPTIMIZATION: DB-level filtering)
        products = await self.product_repo.get_all(
            category=category,
            subcategory=subcategory,
            min_price=min_price,
            max_price=max_price,
            limit=page_size * 3,  # Fetch extra for search/condition filtering
            offset=offset
        )

        # Apply remaining Python-side filters (only search and condition)
        filtered_products = self._apply_filters(
            products,
            condition=condition,
            search_query=search_query,
        )

        # Sort products
        sorted_products = self._sort_products(filtered_products, sort)

        # Apply final pagination
        paginated_products = sorted_products[:page_size]

        # Enrich with seller info (batch operation)
        enriched_products = await self._enrich_products_batch(paginated_products)

        # Note: Total count is approximate since we don't fetch all products
        # For exact count, would need separate count query
        total = len(sorted_products)
        has_more = len(sorted_products) >= page_size

        return {
            "items": enriched_products,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            "has_more": has_more,
        }

    async def get_seller_products(self, seller_id: str) -> List[Dict[str, Any]]:
        """Get all products for a seller (including inactive)."""
        products = await self.product_repo.get_by_seller(seller_id)

        # Sort by posted_date descending
        products.sort(key=lambda x: x.get("posted_date", datetime.min), reverse=True)

        # Enrich with seller info
        enriched_products = await self._enrich_products_batch(products)

        return enriched_products

    async def get_products_batch(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Batch fetch products by IDs (for recently viewed, etc.).
        Only returns active products.
        """
        if not product_ids:
            return []

        # Fetch products by IDs
        products = []
        for product_id in product_ids:
            product = await self.product_repo.get_by_id(product_id)
            if product and product.get("is_active", True):
                products.append(product)

        # Enrich with seller info
        enriched_products = await self._enrich_products_batch(products)

        return enriched_products

    async def create_product(self, product_data: ProductCreate, seller_id: str) -> Dict[str, Any]:
        """Create a new product."""
        product_dict = product_data.model_dump()
        product_dict["seller_id"] = seller_id

        product_id = await self.product_repo.create(product_dict)

        # Get created product
        product = await self.product_repo.get_by_id(product_id)

        # Enrich with seller info
        product = await self._enrich_with_seller(product)

        return product

    async def update_product(
        self, product_id: str, product_data: ProductUpdate, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Update a product (partial update)."""
        # Verify ownership
        if not await self.product_repo.verify_ownership(product_id, user_id):
            return None

        # Get existing product for image cleanup
        existing_product = await self.product_repo.get_by_id(product_id)
        if not existing_product:
            return None

        # Handle image cleanup if images are being updated
        update_dict = product_data.model_dump(exclude_unset=True)

        if "images" in update_dict:
            old_images = set(existing_product.get("images", []))
            new_images = set(update_dict["images"])
            images_to_delete = old_images - new_images

            if images_to_delete:
                logger.info(f"Need to clean up {len(images_to_delete)} replaced images")
                # Image cleanup would be handled by cloudinary service

        # Update product
        success = await self.product_repo.update(product_id, update_dict)

        if not success:
            return None

        # Get updated product
        product = await self.product_repo.get_by_id(product_id)
        product = await self._enrich_with_seller(product)

        return product

    async def delete_product(self, product_id: str, user_id: str) -> bool:
        """Delete a product."""
        # Verify ownership
        if not await self.product_repo.verify_ownership(product_id, user_id):
            return False

        # Get product for image cleanup
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return False

        # Delete product
        success = await self.product_repo.delete(product_id)

        if success:
            logger.info(f"Successfully deleted product {product_id}")
            # Image cleanup would be handled by cloudinary service

        return success

    async def mark_as_sold(
        self, product_id: str, user_id: str, buyer_id: Optional[str] = None
    ) -> bool:
        """Mark product as sold."""
        # Verify ownership
        if not await self.product_repo.verify_ownership(product_id, user_id):
            return False

        return await self.product_repo.mark_as_sold(product_id, buyer_id)

    async def mark_as_active(self, product_id: str, user_id: str) -> bool:
        """Mark product as active again."""
        # Verify ownership
        if not await self.product_repo.verify_ownership(product_id, user_id):
            return False

        return await self.product_repo.mark_as_active(product_id)

    # Private helper methods

    async def _enrich_with_seller(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich single product with seller info."""
        seller_id = product.get("seller_id")
        if not seller_id:
            product["seller"] = None
            return product

        try:
            user = await self.user_repo.get_by_id(seller_id)
            if not user:
                product["seller"] = None
                return product

            profile = await self.user_repo.get_profile_by_user_id(seller_id)
            avatar = profile.get("avatar") if profile else None

            product["seller"] = {"id": seller_id, "name": user.get("name"), "avatar": avatar}
        except Exception as e:
            logger.error(f"Error enriching product {product.get('id')} with seller: {e}")
            product["seller"] = None

        return product

    async def _enrich_products_batch(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich multiple products with seller info (OPTIMIZED - batch operation).
        
        PERFORMANCE: Reduces N*2 queries to ~4 queries for typical batch.
        """
        if not products:
            return products

        # Collect unique seller IDs
        seller_ids = list(set(p.get("seller_id") for p in products if p.get("seller_id")))

        if not seller_ids:
            for product in products:
                product["seller"] = None
            return products

        # Batch fetch all users (OPTIMIZATION: 1-5 queries instead of N)
        users_map = await self.user_repo.get_batch(seller_ids)

        # Batch fetch all profiles (OPTIMIZATION: 1-5 queries instead of N)
        profiles_map = await self.user_repo.get_profiles_batch(seller_ids)

        # Enrich products
        for product in products:
            seller_id = product.get("seller_id")
            if not seller_id:
                product["seller"] = None
                continue

            user = users_map.get(seller_id)
            if not user:
                product["seller"] = None
                continue

            profile = profiles_map.get(seller_id, {})
            avatar = profile.get("avatar")

            product["seller"] = {"id": seller_id, "name": user.get("name"), "avatar": avatar}

        return products

    def _apply_filters(
        self,
        products: List[Dict[str, Any]],
        condition: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Apply Python-side filters to products (OPTIMIZED - reduced filters).
        
        Note: Price and subcategory filters now handled at DB level.
        """
        filtered = []

        for product in products:
            # Search filter (can't be done efficiently in Firestore)
            if search_query:
                query_lower = search_query.lower()
                searchable_text = f"{product.get('title', '')} {product.get('description', '')} {product.get('location', '')}".lower()
                if query_lower not in searchable_text:
                    continue

            # Condition filter (could be pushed to DB with index)
            if condition and product.get("condition") != condition:
                continue

            filtered.append(product)

        return filtered

    def _sort_products(self, products: List[Dict[str, Any]], sort: str) -> List[Dict[str, Any]]:
        """Sort products by specified criteria."""
        if sort == "newest":
            products.sort(key=lambda x: x.get("posted_date", datetime.min), reverse=True)
        elif sort == "oldest":
            products.sort(key=lambda x: x.get("posted_date", datetime.min))
        elif sort == "price-low":
            products.sort(key=lambda x: x.get("price", 0))
        elif sort == "price-high":
            products.sort(key=lambda x: x.get("price", 0), reverse=True)
        elif sort == "most-viewed":
            products.sort(key=lambda x: x.get("views", 0), reverse=True)

        return products
