"""
Integration tests for authentication routes.
Tests email verification flow end-to-end.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthRoutes:
    """Test authentication endpoints."""

    async def test_send_verification_email_success(
        self, client: AsyncClient, mock_db, create_test_user, mock_email_service
    ):
        """Test sending verification email successfully."""
        # Create test user
        user = create_test_user(email_verified=False)

        with patch(
            "app.services.auth_service.AuthService.send_verification_email", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = "Verification email sent successfully"

            response = await client.post(
                "/api/auth/send-verification",
                json={"email": user["email"], "firebase_uid": user["firebase_uid"]},
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "sent" in data["message"].lower()

    async def test_send_verification_email_user_not_found(self, client: AsyncClient):
        """Test sending verification email for non-existent user."""
        with patch(
            "app.services.auth_service.AuthService.send_verification_email", new_callable=AsyncMock
        ) as mock_send:
            mock_send.side_effect = ValueError("User not found")

            response = await client.post(
                "/api/auth/send-verification",
                json={"email": "nonexistent@example.com", "firebase_uid": "invalid-uid"},
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    async def test_send_verification_email_invalid_data(self, client: AsyncClient):
        """Test sending verification email with invalid data."""
        response = await client.post(
            "/api/auth/send-verification", json={"email": "invalid-email", "firebase_uid": ""}
        )

        assert response.status_code == 422

    async def test_verify_email_success(self, client: AsyncClient, mock_db, create_test_user):
        """Test email verification with valid token."""
        user = create_test_user(email_verified=False)

        with patch(
            "app.services.auth_service.AuthService.verify_email", new_callable=AsyncMock
        ) as mock_verify:
            mock_verify.return_value = "Email verified successfully"

            response = await client.post(
                "/api/auth/verify-email", json={"token": "valid-token-123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "verified" in data["message"].lower()

    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token."""
        with patch(
            "app.services.auth_service.AuthService.verify_email", new_callable=AsyncMock
        ) as mock_verify:
            mock_verify.side_effect = ValueError("Invalid or expired token")

            response = await client.post("/api/auth/verify-email", json={"token": "invalid-token"})

            assert response.status_code == 400
            assert "Invalid" in response.json()["detail"]

    async def test_resend_verification_email_success(
        self, client: AsyncClient, mock_db, create_test_user, mock_email_service
    ):
        """Test resending verification email."""
        user = create_test_user(email_verified=False)

        with patch(
            "app.services.auth_service.AuthService.resend_verification_email",
            new_callable=AsyncMock,
        ) as mock_resend:
            mock_resend.return_value = "Verification email resent successfully"

            response = await client.post(
                "/api/auth/resend-verification",
                json={"email": user["email"], "firebase_uid": user["firebase_uid"]},
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

    async def test_resend_verification_email_already_verified(
        self, client: AsyncClient, mock_db, create_test_user
    ):
        """Test resending verification email for already verified user."""
        user = create_test_user(email_verified=True)

        with patch(
            "app.services.auth_service.AuthService.resend_verification_email",
            new_callable=AsyncMock,
        ) as mock_resend:
            mock_resend.side_effect = ValueError("Email already verified")

            response = await client.post(
                "/api/auth/resend-verification",
                json={"email": user["email"], "firebase_uid": user["firebase_uid"]},
            )

            assert response.status_code == 400
            assert "already verified" in response.json()["detail"].lower()

    async def test_verify_email_missing_token(self, client: AsyncClient):
        """Test email verification without token."""
        response = await client.post("/api/auth/verify-email", json={})

        assert response.status_code == 422

    async def test_send_verification_missing_fields(self, client: AsyncClient):
        """Test sending verification email with missing fields."""
        response = await client.post(
            "/api/auth/send-verification", json={"email": "test@example.com"}
        )

        assert response.status_code == 422
