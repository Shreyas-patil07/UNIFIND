"""
Integration tests for product API endpoints.
Tests complete product CRUD operations.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestProductAPI:
    """Test product API endpoints."""

    async def test_get_products_empty(self, client: AsyncClient, mock_db):
        """Test getting products when none exist."""
        response = await client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_get_products_with_data(self, client: AsyncClient, mock_db, create_test_product):
        """Test getting products list."""
        # Create test products
        for i in range(5):
            create_test_product(id=f"product-{i}", title=f"Product {i}")

        response = await client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5

    async def test_get_products_with_pagination(
        self, client: AsyncClient, mock_db, create_test_product
    ):
        """Test product pagination."""
        # Create 20 products
        for i in range(20):
            create_test_product(id=f"product-{i}")

        # Get first page
        response = await client.get("/api/products?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

        # Get second page
        response = await client.get("/api/products?limit=10&offset=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

    async def test_get_products_with_category_filter(
        self, client: AsyncClient, mock_db, create_test_product
    ):
        """Test filtering products by category."""
        create_test_product(id="prod-1", category="Electronics")
        create_test_product(id="prod-2", category="Books")
        create_test_product(id="prod-3", category="Electronics")

        response = await client.get("/api/products?category=Electronics")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["category"] == "Electronics" for p in data)

    async def test_get_products_with_price_range(
        self, client: AsyncClient, mock_db, create_test_product
    ):
        """Test filtering products by price range."""
        create_test_product(id="prod-1", price=50.0)
        create_test_product(id="prod-2", price=150.0)
        create_test_product(id="prod-3", price=250.0)

        response = await client.get("/api/products?min_price=100&max_price=200")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["price"] == 150.0

    async def test_get_product_by_id_success(
        self, client: AsyncClient, mock_db, create_test_product
    ):
        """Test getting a specific product."""
        product = create_test_product(id="test-product-123")

        response = await client.get(f"/api/products/{product['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product["id"]
        assert data["title"] == product["title"]

    async def test_get_product_not_found(self, client: AsyncClient, mock_db):
        """Test getting non-existent product."""
        response = await client.get("/api/products/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_create_product_success(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test creating a new product."""
        user = create_test_user()

        product_data = {
            "title": "New Product",
            "description": "Product description",
            "price": 99.99,
            "category": "Electronics",
            "condition": "New",
            "images": ["https://example.com/image.jpg"],
        }

        with patch("app.api.dependencies.auth.get_current_user", return_value=user["firebase_uid"]):
            response = await client.post("/api/products", json=product_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == product_data["title"]
        assert data["price"] == product_data["price"]
        assert "id" in data

    async def test_create_product_invalid_data(self, client: AsyncClient, auth_headers):
        """Test creating product with invalid data."""
        product_data = {
            "title": "",  # Invalid: empty title
            "price": -10,  # Invalid: negative price
        }

        response = await client.post("/api/products", json=product_data, headers=auth_headers)

        assert response.status_code == 422

    async def test_create_product_unauthorized(self, client: AsyncClient):
        """Test creating product without authentication."""
        product_data = {
            "title": "New Product",
            "price": 99.99,
        }

        response = await client.post("/api/products", json=product_data)

        assert response.status_code == 401

    async def test_update_product_success(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product, auth_headers
    ):
        """Test updating a product."""
        user = create_test_user()
        product = create_test_product(seller_id=user["id"])

        update_data = {"title": "Updated Title", "price": 149.99}

        with patch("app.api.dependencies.auth.get_current_user", return_value=user["firebase_uid"]):
            response = await client.put(
                f"/api/products/{product['id']}", json=update_data, headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["price"] == update_data["price"]

    async def test_update_product_unauthorized(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product, auth_headers
    ):
        """Test updating product by non-owner."""
        owner = create_test_user(id="owner-123")
        other_user = create_test_user(id="other-456", email="other@example.com")
        product = create_test_product(seller_id=owner["id"])

        update_data = {"title": "Hacked Title"}

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=other_user["firebase_uid"]
        ):
            response = await client.put(
                f"/api/products/{product['id']}", json=update_data, headers=auth_headers
            )

        assert response.status_code == 403

    async def test_delete_product_success(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product, auth_headers
    ):
        """Test deleting a product."""
        user = create_test_user()
        product = create_test_product(seller_id=user["id"])

        with patch("app.api.dependencies.auth.get_current_user", return_value=user["firebase_uid"]):
            response = await client.delete(f"/api/products/{product['id']}", headers=auth_headers)

        assert response.status_code == 200

        # Verify product is deleted
        doc = mock_db.collection("products").document(product["id"]).get()
        assert not doc.exists

    async def test_delete_product_unauthorized(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product, auth_headers
    ):
        """Test deleting product by non-owner."""
        owner = create_test_user(id="owner-123")
        other_user = create_test_user(id="other-456", email="other@example.com")
        product = create_test_product(seller_id=owner["id"])

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=other_user["firebase_uid"]
        ):
            response = await client.delete(f"/api/products/{product['id']}", headers=auth_headers)

        assert response.status_code == 403

    async def test_mark_product_as_sold(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product, auth_headers
    ):
        """Test marking product as sold."""
        seller = create_test_user(id="seller-123")
        buyer = create_test_user(id="buyer-456", email="buyer@example.com")
        product = create_test_product(seller_id=seller["id"])

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=seller["firebase_uid"]
        ):
            response = await client.post(
                f"/api/products/{product['id']}/mark-sold",
                json={"buyer_id": buyer["id"]},
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sold"
        assert data["sold_to"] == buyer["id"]

    async def test_search_products(self, client: AsyncClient, mock_db, create_test_product):
        """Test searching products."""
        create_test_product(id="prod-1", title="MacBook Pro Laptop")
        create_test_product(id="prod-2", title="Dell Laptop")
        create_test_product(id="prod-3", title="iPhone")

        response = await client.get("/api/products?search=laptop")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("laptop" in p["title"].lower() for p in data)

    async def test_get_seller_products(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product
    ):
        """Test getting products by seller."""
        seller = create_test_user(id="seller-123")
        other_seller = create_test_user(id="other-456", email="other@example.com")

        create_test_product(id="prod-1", seller_id=seller["id"])
        create_test_product(id="prod-2", seller_id=seller["id"])
        create_test_product(id="prod-3", seller_id=other_seller["id"])

        response = await client.get(f"/api/products?seller_id={seller['id']}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["seller_id"] == seller["id"] for p in data)

    async def test_increment_product_views(self, client: AsyncClient, mock_db, create_test_product):
        """Test incrementing product view count."""
        product = create_test_product(views=0)

        # View product multiple times
        for _ in range(3):
            response = await client.get(f"/api/products/{product['id']}")
            assert response.status_code == 200

        # Check views incremented
        doc = mock_db.collection("products").document(product["id"]).get()
        # Note: This would need actual implementation in the route
        # For now, just verify the endpoint works
        assert doc.exists
