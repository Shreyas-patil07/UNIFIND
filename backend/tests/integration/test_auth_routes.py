"""
Integration tests for authentication routes.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthRoutes:
    """Test authentication endpoints."""
    
    async def test_send_verification_email_success(self, client: AsyncClient):
        """Test sending verification email successfully."""
        with patch('app.services.auth_service.AuthService.send_verification_email') as mock_send:
            mock_send.return_value = "Verification email sent successfully"
            
            response = await client.post(
                "/api/auth/send-verification",
                json={
                    "email": "test@example.com",
                    "firebase_uid": "test-uid-123"
                }
            )
            
            assert response.status_code == 200
            assert "message" in response.json()
            mock_send.assert_called_once()
    
    async def test_send_verification_email_user_not_found(self, client: AsyncClient):
        """Test sending verification email for non-existent user."""
        with patch('app.services.auth_service.AuthService.send_verification_email') as mock_send:
            mock_send.side_effect = ValueError("User not found")
            
            response = await client.post(
                "/api/auth/send-verification",
                json={
                    "email": "nonexistent@example.com",
                    "firebase_uid": "invalid-uid"
                }
            )
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    
    async def test_send_verification_email_invalid_data(self, client: AsyncClient):
        """Test sending verification email with invalid data."""
        response = await client.post(
            "/api/auth/send-verification",
            json={
                "email": "invalid-email",
                "firebase_uid": ""
            }
        )
        
        assert response.status_code == 422
    
    async def test_verify_email_success(self, client: AsyncClient):
        """Test email verification with valid token."""
        with patch('app.services.auth_service.AuthService.verify_email') as mock_verify:
            mock_verify.return_value = "Email verified successfully"
            
            response = await client.post(
                "/api/auth/verify-email",
                json={"token": "valid-token-123"}
            )
            
            assert response.status_code == 200
            assert "message" in response.json()
            mock_verify.assert_called_once_with("valid-token-123")
    
    async def test_verify_email_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token."""
        with patch('app.services.auth_service.AuthService.verify_email') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid or expired token")
            
            response = await client.post(
                "/api/auth/verify-email",
                json={"token": "invalid-token"}
            )
            
            assert response.status_code == 400
            assert "Invalid" in response.json()["detail"]
    
    async def test_resend_verification_email_success(self, client: AsyncClient):
        """Test resending verification email."""
        with patch('app.services.auth_service.AuthService.resend_verification_email') as mock_resend:
            mock_resend.return_value = "Verification email resent successfully"
            
            response = await client.post(
                "/api/auth/resend-verification",
                json={
                    "email": "test@example.com",
                    "firebase_uid": "test-uid-123"
                }
            )
            
            assert response.status_code == 200
            assert "message" in response.json()
    
    async def test_resend_verification_email_already_verified(self, client: AsyncClient):
        """Test resending verification email for already verified user."""
        with patch('app.services.auth_service.AuthService.resend_verification_email') as mock_resend:
            mock_resend.side_effect = ValueError("Email already verified")
            
            response = await client.post(
                "/api/auth/resend-verification",
                json={
                    "email": "verified@example.com",
                    "firebase_uid": "verified-uid"
                }
            )
            
            assert response.status_code == 400
