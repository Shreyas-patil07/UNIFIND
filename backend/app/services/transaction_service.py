"""
Transaction service - business logic for transaction operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.repositories.product_repository import ProductRepository
from app.repositories.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction business logic."""

    def __init__(self, transaction_repo: TransactionRepository, product_repo: ProductRepository):
        self.transaction_repo = transaction_repo
        self.product_repo = product_repo

    async def get_transaction_history(
        self,
        user_id: str,
        product_id: Optional[str] = None,
        transaction_type_sold: Optional[bool] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Get transaction history for a user.

        Args:
            user_id: User ID (seller)
            product_id: Optional product filter
            transaction_type_sold: Optional sold status filter
            limit: Maximum results

        Returns:
            Dictionary with transactions and count
        """
        transactions = await self.transaction_repo.get_by_seller(
            user_id, product_id=product_id, transaction_type_sold=transaction_type_sold, limit=limit
        )

        # Enrich with product details
        enriched_transactions = []
        for transaction in transactions:
            product_id_val = transaction.get("product_id")
            if product_id_val:
                try:
                    product = await self.product_repo.get_by_id(product_id_val)
                    if product:
                        transaction["product"] = {
                            "id": product_id_val,
                            "title": product.get("title"),
                            "images": product.get("images", []),
                            "price": product.get("price"),
                        }
                except Exception as e:
                    logger.warning(f"Error fetching product {product_id_val}: {e}")
                    transaction["product"] = None

            enriched_transactions.append(transaction)

        return {"transactions": enriched_transactions, "count": len(enriched_transactions)}

    async def get_transaction_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get transaction statistics for a user.

        Args:
            user_id: User ID (seller)
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        return await self.transaction_repo.get_stats(user_id, days)

    async def get_product_transaction_history(
        self, product_id: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history for a specific product.

        Args:
            product_id: Product ID
            user_id: User ID (must be seller)

        Returns:
            List of transactions
        """
        # Verify ownership
        if not await self.product_repo.verify_ownership(product_id, user_id):
            raise ValueError("Unauthorized to view this product's transaction history")

        return await self.transaction_repo.get_by_product(product_id)

    async def create_product_sold_transaction(
        self, product_id: str, seller_id: str, amount: float, buyer_id: Optional[str] = None
    ) -> None:
        """
        Create transaction records when product is marked as sold.

        Args:
            product_id: Product ID
            seller_id: Seller user ID
            amount: Transaction amount
            buyer_id: Optional buyer user ID
        """
        # Create product transaction history record
        transaction_data = {
            "amount": amount,
            "product_id": product_id,
            "seller_id": seller_id,
            "status": "completed",
            "transaction_type_sold": True,
        }
        await self.transaction_repo.create(transaction_data)

        logger.info(f"Created transaction history for product {product_id} marked as sold")

        # Create transaction records if buyer is specified
        if buyer_id:
            base_transaction = {
                "product_id": product_id,
                "seller_id": seller_id,
                "buyer_id": buyer_id,
                "amount": amount,
                "status": "completed",
                "completed_at": datetime.now(),
            }

            # Create seller transaction (sell)
            seller_transaction = {
                **base_transaction,
                "user_id": seller_id,
                "transaction_type": "sell",
                "other_party_id": buyer_id,
            }
            await self.transaction_repo.create(seller_transaction)

            # Create buyer transaction (buy)
            buyer_transaction = {
                **base_transaction,
                "user_id": buyer_id,
                "transaction_type": "buy",
                "other_party_id": seller_id,
            }
            await self.transaction_repo.create(buyer_transaction)

            logger.info(f"Created transaction records for sale to buyer {buyer_id}")

    async def create_product_active_transaction(
        self, product_id: str, seller_id: str, amount: float
    ) -> None:
        """
        Create transaction record when product is marked as active.

        Args:
            product_id: Product ID
            seller_id: Seller user ID
            amount: Transaction amount
        """
        transaction_data = {
            "amount": amount,
            "product_id": product_id,
            "seller_id": seller_id,
            "status": "completed",
            "transaction_type_sold": False,
        }
        await self.transaction_repo.create(transaction_data)

        logger.info(f"Created transaction history for product {product_id} marked as active")
