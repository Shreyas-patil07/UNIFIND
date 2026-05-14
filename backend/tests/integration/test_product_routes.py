"""
Integration tests for product routes.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestProductRoutes:
    """Test product endpoints."""

    async def test_get_products_success(self, client: AsyncClient):
        """Test getting products list."""
        mock_products = {
            "products": [{"id": "prod-1", "title": "Laptop", "price": 500.0, "status": "active"}],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }

        with patch("app.services.product_service.ProductService.get_all_products") as mock_get:
            mock_get.return_value = mock_products

            response = await client.get("/api/products")

            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            assert "total" in data

    async def test_get_products_with_filters(self, client: AsyncClient):
        """Test getting products with filters."""
        with patch("app.services.product_service.ProductService.get_all_products") as mock_get:
            mock_get.return_value = {"products": [], "total": 0, "page": 1, "page_size": 20}

            response = await client.get(
                "/api/products",
                params={
                    "category": "Electronics",
                    "min_price": 100,
                    "max_price": 1000,
                    "condition": "Like New",
                },
            )

            assert response.status_code == 200
            mock_get.assert_called_once()

    async def test_get_products_with_search(self, client: AsyncClient):
        """Test searching products."""
        with patch("app.services.product_service.ProductService.get_all_products") as mock_get:
            mock_get.return_value = {"products": [], "total": 0, "page": 1, "page_size": 20}

            response = await client.get("/api/products", params={"q": "laptop"})

            assert response.status_code == 200

    async def test_get_product_by_id_success(self, client: AsyncClient, sample_product):
        """Test getting a specific product."""
        with patch("app.services.product_service.ProductService.get_product_by_id") as mock_get:
            mock_get.return_value = sample_product

            response = await client.get(f"/api/products/{sample_product['id']}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == sample_product["id"]
            assert data["title"] == sample_product["title"]

    async def test_get_product_not_found(self, client: AsyncClient):
        """Test getting non-existent product."""
        with patch("app.services.product_service.ProductService.get_product_by_id") as mock_get:
            mock_get.return_value = None

            response = await client.get("/api/products/nonexistent-id")

            assert response.status_code == 404

    async def test_create_product_success(self, client: AsyncClient, sample_product):
        """Test creating a new product."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = "test-user-123"

            with patch("app.services.product_service.ProductService.create_product") as mock_create:
                mock_create.return_value = sample_product

                product_data = {
                    "title": "New Product",
                    "description": "Test description",
                    "price": 99.99,
                    "category": "Electronics",
                    "subcategory": "Laptops",
                    "condition": "Like New",
                    "images": ["https://example.com/image.jpg"],
                }

                response = await client.post("/api/products", json=product_data)

                assert response.status_code == 201
                assert "id" in response.json()

    async def test_create_product_invalid_data(self, client: AsyncClient):
        """Test creating product with invalid data."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = "test-user-123"

            response = await client.post(
                "/api/products",
                json={"title": "", "price": -10},  # Invalid: empty title  # Invalid: negative price
            )

            assert response.status_code == 422

    async def test_update_product_success(self, client: AsyncClient, sample_product):
        """Test updating a product."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = sample_product["seller_id"]

            with patch("app.services.product_service.ProductService.update_product") as mock_update:
                updated_product = {**sample_product, "title": "Updated Title"}
                mock_update.return_value = updated_product

                response = await client.patch(
                    f"/api/products/{sample_product['id']}", json={"title": "Updated Title"}
                )

                assert response.status_code == 200
                assert response.json()["title"] == "Updated Title"

    async def test_update_product_unauthorized(self, client: AsyncClient, sample_product):
        """Test updating product by non-owner."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = "different-user-id"

            with patch("app.services.product_service.ProductService.update_product") as mock_update:
                mock_update.return_value = None  # Unauthorized

                response = await client.patch(
                    f"/api/products/{sample_product['id']}", json={"title": "Hacked Title"}
                )

                assert response.status_code == 403

    async def test_delete_product_success(self, client: AsyncClient, sample_product):
        """Test deleting a product."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = sample_product["seller_id"]

            with patch("app.services.product_service.ProductService.delete_product") as mock_delete:
                mock_delete.return_value = True

                response = await client.delete(f"/api/products/{sample_product['id']}")

                assert response.status_code == 200
                assert "deleted" in response.json()

    async def test_delete_product_unauthorized(self, client: AsyncClient, sample_product):
        """Test deleting product by non-owner."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = "different-user-id"

            with patch("app.services.product_service.ProductService.delete_product") as mock_delete:
                mock_delete.return_value = False

                response = await client.delete(f"/api/products/{sample_product['id']}")

                assert response.status_code == 403

    async def test_mark_product_as_sold(self, client: AsyncClient, sample_product):
        """Test marking product as sold."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = sample_product["seller_id"]

            with patch("app.services.product_service.ProductService.mark_as_sold") as mock_sold:
                mock_sold.return_value = True

                with patch(
                    "app.services.product_service.ProductService.get_product_by_id"
                ) as mock_get:
                    mock_get.return_value = sample_product

                    with patch(
                        "app.services.transaction_service.TransactionService.create_product_sold_transaction"
                    ):
                        response = await client.patch(
                            f"/api/products/{sample_product['id']}/mark-sold",
                            json={"buyer_id": "buyer-123"},
                        )

                        assert response.status_code == 200
                        assert "buyer_id" in response.json()

    async def test_get_batch_products(self, client: AsyncClient):
        """Test batch fetching products."""
        product_ids = ["prod-1", "prod-2", "prod-3"]

        with patch("app.services.product_service.ProductService.get_products_batch") as mock_batch:
            mock_batch.return_value = [
                {"id": "prod-1", "title": "Product 1"},
                {"id": "prod-2", "title": "Product 2"},
            ]

            response = await client.post("/api/products/batch", json={"product_ids": product_ids})

            assert response.status_code == 200
            assert len(response.json()) == 2
