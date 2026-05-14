"""
Integration tests for user routes.
"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserRoutes:
    """Test user endpoints."""

    async def test_get_user_profile_success(self, client: AsyncClient, sample_user):
        """Test getting user profile."""
        with patch("app.services.user_service.UserService.get_user_by_id") as mock_get:
            mock_get.return_value = sample_user

            response = await client.get(f"/api/users/{sample_user['id']}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == sample_user["id"]
            assert data["email"] == sample_user["email"]

    async def test_get_user_profile_not_found(self, client: AsyncClient):
        """Test getting non-existent user."""
        with patch("app.services.user_service.UserService.get_user_by_id") as mock_get:
            mock_get.return_value = None

            response = await client.get("/api/users/nonexistent-id")

            assert response.status_code == 404

    async def test_create_user_success(self, client: AsyncClient, sample_user):
        """Test creating a new user."""
        with patch("app.services.user_service.UserService.create_user") as mock_create:
            mock_create.return_value = sample_user

            user_data = {
                "firebase_uid": "new-firebase-uid",
                "email": "newuser@example.com",
                "name": "New User",
                "university": "Test University",
            }

            response = await client.post("/api/users", json=user_data)

            assert response.status_code == 201
            assert "id" in response.json()

    async def test_create_user_duplicate_email(self, client: AsyncClient):
        """Test creating user with duplicate email."""
        with patch("app.services.user_service.UserService.create_user") as mock_create:
            mock_create.side_effect = ValueError("Email already exists")

            user_data = {
                "firebase_uid": "uid-123",
                "email": "existing@example.com",
                "name": "Test User",
                "university": "Test University",
            }

            response = await client.post("/api/users", json=user_data)

            assert response.status_code == 400

    async def test_update_user_profile(self, client: AsyncClient, sample_user):
        """Test updating user profile."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = sample_user["id"]

            with patch("app.services.user_service.UserService.update_user") as mock_update:
                updated_user = {**sample_user, "name": "Updated Name"}
                mock_update.return_value = updated_user

                response = await client.patch(
                    f"/api/users/{sample_user['id']}", json={"name": "Updated Name"}
                )

                assert response.status_code == 200
                assert response.json()["name"] == "Updated Name"

    async def test_update_user_unauthorized(self, client: AsyncClient, sample_user):
        """Test updating another user's profile."""
        with patch("app.api.dependencies.auth.get_current_user") as mock_auth:
            mock_auth.return_value = "different-user-id"

            with patch("app.services.user_service.UserService.update_user") as mock_update:
                mock_update.return_value = None

                response = await client.patch(
                    f"/api/users/{sample_user['id']}", json={"name": "Hacked Name"}
                )

                assert response.status_code == 403
