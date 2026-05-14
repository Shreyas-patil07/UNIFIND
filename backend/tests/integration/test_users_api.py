"""
Integration tests for user API endpoints.
Tests user profile management and operations.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserAPI:
    """Test user API endpoints."""

    async def test_get_user_profile_success(self, client: AsyncClient, mock_db, create_test_user):
        """Test getting user profile."""
        user = create_test_user()

        response = await client.get(f"/api/users/{user['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user["id"]
        assert data["email"] == user["email"]
        assert data["name"] == user["name"]

    async def test_get_user_profile_not_found(self, client: AsyncClient, mock_db):
        """Test getting non-existent user."""
        response = await client.get("/api/users/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_create_user_success(self, client: AsyncClient, mock_db):
        """Test creating a new user."""
        user_data = {
            "firebase_uid": "new-firebase-uid",
            "email": "newuser@example.com",
            "name": "New User",
            "university": "Test University",
        }

        response = await client.post("/api/users", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "id" in data
        assert data["email_verified"] == False

    async def test_create_user_duplicate_email(
        self, client: AsyncClient, mock_db, create_test_user
    ):
        """Test creating user with duplicate email."""
        existing_user = create_test_user()

        user_data = {
            "firebase_uid": "new-firebase-uid",
            "email": existing_user["email"],  # Duplicate
            "name": "New User",
            "university": "Test University",
        }

        response = await client.post("/api/users", json=user_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    async def test_create_user_invalid_data(self, client: AsyncClient):
        """Test creating user with invalid data."""
        user_data = {"email": "invalid-email", "name": ""}  # Invalid email format  # Empty name

        response = await client.post("/api/users", json=user_data)

        assert response.status_code == 422

    async def test_update_user_profile(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test updating user profile."""
        user = create_test_user()

        update_data = {"name": "Updated Name", "bio": "Updated bio", "phone": "+9876543210"}

        with patch("app.api.dependencies.auth.get_current_user", return_value=user["firebase_uid"]):
            response = await client.put(
                f"/api/users/{user['id']}", json=update_data, headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["bio"] == update_data["bio"]

    async def test_update_user_unauthorized(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test updating another user's profile."""
        user1 = create_test_user(id="user-1")
        user2 = create_test_user(id="user-2", email="user2@example.com")

        update_data = {"name": "Hacked Name"}

        with patch(
            "app.api.dependencies.auth.get_current_user", return_value=user2["firebase_uid"]
        ):
            response = await client.put(
                f"/api/users/{user1['id']}", json=update_data, headers=auth_headers
            )

        assert response.status_code == 403

    async def test_get_user_products(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product
    ):
        """Test getting user's products."""
        user = create_test_user()

        # Create products for user
        for i in range(3):
            create_test_product(id=f"prod-{i}", seller_id=user["id"])

        response = await client.get(f"/api/users/{user['id']}/products")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(p["seller_id"] == user["id"] for p in data)

    async def test_get_user_reviews(self, client: AsyncClient, mock_db, create_test_user):
        """Test getting user's reviews."""
        user = create_test_user()

        # Create reviews for user
        from tests.factories import ReviewFactory

        for i in range(2):
            review = ReviewFactory.create(reviewed_user_id=user["id"])
            mock_db.collection("reviews").document(review["id"]).set(review)

        response = await client.get(f"/api/users/{user['id']}/reviews")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_user_stats(
        self, client: AsyncClient, mock_db, create_test_user, create_test_product
    ):
        """Test getting user statistics."""
        user = create_test_user()

        # Create some products
        create_test_product(seller_id=user["id"], status="active")
        create_test_product(seller_id=user["id"], status="sold")

        response = await client.get(f"/api/users/{user['id']}/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        assert "active_products" in data
        assert "sold_products" in data

    async def test_delete_user_account(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers
    ):
        """Test deleting user account."""
        user = create_test_user()

        with patch("app.api.dependencies.auth.get_current_user", return_value=user["firebase_uid"]):
            response = await client.delete(f"/api/users/{user['id']}", headers=auth_headers)

        assert response.status_code == 200

        # Verify user is deleted
        doc = mock_db.collection("users").document(user["id"]).get()
        assert not doc.exists

    async def test_upload_profile_picture(
        self, client: AsyncClient, mock_db, create_test_user, auth_headers, mock_cloudinary
    ):
        """Test uploading profile picture."""
        user = create_test_user()

        # Create fake image file
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}

        with patch("app.api.dependencies.auth.get_current_user", return_value=user["firebase_uid"]):
            response = await client.post(
                f"/api/users/{user['id']}/profile-picture", files=files, headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "profile_picture" in data
        assert "cloudinary.com" in data["profile_picture"]

    async def test_search_users(self, client: AsyncClient, mock_db, create_test_user):
        """Test searching users."""
        create_test_user(id="user-1", name="John Doe", email="john@example.com")
        create_test_user(id="user-2", name="Jane Smith", email="jane@example.com")
        create_test_user(id="user-3", name="Bob Johnson", email="bob@example.com")

        response = await client.get("/api/users?search=john")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # John Doe and Bob Johnson

    async def test_get_user_by_firebase_uid(self, client: AsyncClient, mock_db, create_test_user):
        """Test getting user by Firebase UID."""
        user = create_test_user()

        response = await client.get(f"/api/users/firebase/{user['firebase_uid']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user["id"]
        assert data["firebase_uid"] == user["firebase_uid"]
