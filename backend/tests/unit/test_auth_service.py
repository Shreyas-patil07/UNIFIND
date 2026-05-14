"""
Unit tests for AuthService.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.auth_service import AuthService


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthService:
    """Test AuthService business logic."""

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create AuthService instance with mocked dependencies."""
        return AuthService(mock_db)

    async def test_send_verification_email_success(self, auth_service, mock_db, sample_user):
        """Test sending verification email to existing user."""
        # Mock user document
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_user

        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = [
            mock_doc
        ]

        with patch("app.services.auth_service.send_verification_email_smtp") as mock_smtp:
            mock_smtp.return_value = None

            result = await auth_service.send_verification_email(
                sample_user["email"], sample_user["firebase_uid"]
            )

            assert "sent" in result.lower()
            mock_smtp.assert_called_once()

    async def test_send_verification_email_user_not_found(self, auth_service, mock_db):
        """Test sending verification email to non-existent user."""
        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = []

        with pytest.raises(ValueError, match="not found"):
            await auth_service.send_verification_email("nonexistent@example.com", "invalid-uid")

    async def test_verify_email_success(self, auth_service, mock_db, sample_user):
        """Test email verification with valid token."""
        # Mock token validation
        with patch("app.core.security.verify_token") as mock_verify:
            mock_verify.return_value = {"user_id": sample_user["id"]}

            # Mock user document
            mock_doc_ref = MagicMock()
            mock_db.collection.return_value.document.return_value = mock_doc_ref

            result = await auth_service.verify_email("valid-token")

            assert "verified" in result.lower()
            mock_doc_ref.update.assert_called_once()

    async def test_verify_email_invalid_token(self, auth_service):
        """Test email verification with invalid token."""
        with patch("app.core.security.verify_token") as mock_verify:
            mock_verify.side_effect = ValueError("Invalid token")

            with pytest.raises(ValueError, match="Invalid"):
                await auth_service.verify_email("invalid-token")

    async def test_resend_verification_already_verified(self, auth_service, mock_db, sample_user):
        """Test resending verification to already verified user."""
        verified_user = {**sample_user, "email_verified": True}

        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = verified_user

        mock_db.collection.return_value.where.return_value.limit.return_value.get.return_value = [
            mock_doc
        ]

        with pytest.raises(ValueError, match="already verified"):
            await auth_service.resend_verification_email(
                verified_user["email"], verified_user["firebase_uid"]
            )
