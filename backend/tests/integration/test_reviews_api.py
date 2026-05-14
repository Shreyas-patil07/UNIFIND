"""
Integration tests for review API endpoints.
Tests review creation and management.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from tests.factories import ReviewFactory, TransactionFactory


@pytest.mark.integration
@pytest.mark.asyncio
class TestReviewAPI:
    """Test review API endpoints."""

    async def test_create_review_success(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product, auth_headers
    ):
        """Test creating a review."""
        buyer = create_test_user(id="buyer-123")
        seller = create_test_user(id="seller-456", email="seller@example.com")
        product = create_test_product(seller_id=seller["id"])

        # Create transaction
        transaction = TransactionFactory.create(
            buyer_id=buyer["id"], seller_id=seller["id"], product_id=product["id"]
        )
        mock_db.collection("transactions").document(transaction["id"]).set(transaction)

        review_data = {
            "reviewed_user_id": seller["id"],
            "product_id": product["id"],
            "transaction_id": transaction["id"],
            "rating": 5,
            "comment": "Great seller!",
        }

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=buyer["firebase_uid"]
        ):
            response = await client.post("/api/reviews", json=review_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Great seller!"
        assert "id" in data

    async def test_create_review_duplicate(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test creating duplicate review."""
        buyer = create_test_user(id="buyer-123")
        seller = create_test_user(id="seller-456", email="seller@example.com")

        # Create existing review
        review = ReviewFactory.create(
            reviewer_id=buyer["id"],
            reviewed_user_id=seller["id"],
            product_id="prod-123",
            transaction_id="trans-123",
        )
        mock_db.collection("reviews").document(review["id"]).set(review)

        # Try to create duplicate
        review_data = {
            "reviewed_user_id": seller["id"],
            "product_id": "prod-123",
            "transaction_id": "trans-123",
            "rating": 4,
            "comment": "Duplicate review",
        }

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=buyer["firebase_uid"]
        ):
            response = await client.post("/api/reviews", json=review_data, headers=auth_headers)

        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    async def test_create_review_invalid_rating(self, client: AsyncClient, auth_headers):
        """Test creating review with invalid rating."""
        review_data = {
            "reviewed_user_id": "seller-123",
            "product_id": "prod-123",
            "rating": 6,  # Invalid: must be 1-5
            "comment": "Test",
        }

        response = await client.post("/api/reviews", json=review_data, headers=auth_headers)

        assert response.status_code == 422

    async def test_get_user_reviews(self, client: AsyncClient, mock_db, create_test_user):
        """Test getting reviews for a user."""
        user = create_test_user()

        # Create reviews
        for i in range(3):
            review = ReviewFactory.create(reviewed_user_id=user["id"], rating=5 - i)
            mock_db.collection("reviews").document(review["id"]).set(review)

        response = await client.get(f"/api/users/{user['id']}/reviews")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_get_review_by_id(self, client: AsyncClient, mock_db):
        """Test getting a specific review."""
        review = ReviewFactory.create()
        mock_db.collection("reviews").document(review["id"]).set(review)

        response = await client.get(f"/api/reviews/{review['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == review["id"]
        assert data["rating"] == review["rating"]

    async def test_update_review(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test updating a review."""
        reviewer = create_test_user()
        review = ReviewFactory.create(reviewer_id=reviewer["id"])
        mock_db.collection("reviews").document(review["id"]).set(review)

        update_data = {"rating": 4, "comment": "Updated comment"}

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=reviewer["firebase_uid"]
        ):
            response = await client.put(
                f"/api/reviews/{review['id']}", json=update_data, headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 4
        assert data["comment"] == "Updated comment"

    async def test_delete_review(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test deleting a review."""
        reviewer = create_test_user()
        review = ReviewFactory.create(reviewer_id=reviewer["id"])
        mock_db.collection("reviews").document(review["id"]).set(review)

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=reviewer["firebase_uid"]
        ):
            response = await client.delete(f"/api/reviews/{review['id']}", headers=auth_headers)

        assert response.status_code == 200

        # Verify deleted
        doc = mock_db.collection("reviews").document(review["id"]).get()
        assert not doc.exists

    async def test_get_product_reviews(self, client: AsyncClient, mock_db, create_test_product):
        """Test getting reviews for a product."""
        product = create_test_product()

        # Create reviews for product
        for i in range(2):
            review = ReviewFactory.create(product_id=product["id"])
            mock_db.collection("reviews").document(review["id"]).set(review)

        response = await client.get(f"/api/products/{product['id']}/reviews")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_calculate_user_rating(self, client: AsyncClient, mock_db, create_test_user):
        """Test calculating average user rating."""
        user = create_test_user()

        # Create reviews with different ratings
        ratings = [5, 4, 5, 3, 4]
        for rating in ratings:
            review = ReviewFactory.create(reviewed_user_id=user["id"], rating=rating)
            mock_db.collection("reviews").document(review["id"]).set(review)

        response = await client.get(f"/api/users/{user['id']}/rating")

        assert response.status_code == 200
        data = response.json()
        assert "average_rating" in data
        assert "total_reviews" in data
        assert data["total_reviews"] == 5
        assert 4.0 <= data["average_rating"] <= 4.5
