"""
Integration tests for transaction routes.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionRoutes:
    """Test transaction endpoints."""

    async def test_get_user_transactions(
        self, client: AsyncClient, sample_user, sample_transaction
    ):
        """Test getting user's transaction history."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = sample_user["id"]

            with patch(
                "app.services.transaction_service.TransactionService.get_user_transactions"
            ) as mock_get:
                mock_get.return_value = [sample_transaction]

                response = await client.get("/api/transactions/history")

                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) > 0

    async def test_get_transaction_stats(self, client: AsyncClient, sample_user):
        """Test getting transaction statistics."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = sample_user["id"]

            with patch(
                "app.services.transaction_service.TransactionService.get_transaction_stats"
            ) as mock_stats:
                mock_stats.return_value = {
                    "total_sales": 5,
                    "total_purchases": 3,
                    "total_revenue": 500.0,
                    "total_spent": 300.0,
                }

                response = await client.get("/api/transactions/stats")

                assert response.status_code == 200
                data = response.json()
                assert "total_sales" in data
                assert "total_purchases" in data
