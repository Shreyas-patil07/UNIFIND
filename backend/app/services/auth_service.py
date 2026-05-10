"""
Auth service - business logic for authentication operations.
"""
import logging
from firebase_admin import auth as admin_auth

from app.repositories.user_repository import UserRepository
from app.services.email_service import email_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication business logic."""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.email_service = email_service
    
    async def send_verification_email(
        self,
        email: str,
        firebase_uid: str
    ) -> str:
        """
        Send email verification link to user.
        
        Args:
            email: User email
            firebase_uid: Firebase UID
            
        Returns:
            Success message
        """
        # Check if user exists
        user = await self.user_repo.get_by_firebase_uid(firebase_uid)
        
        if not user:
            raise ValueError("User not found")
        
        # Check if already verified
        if user.get('email_verified', False):
            return "Email already verified"
        
        # Validate email service configuration
        if not settings.GMAIL_USER or not settings.GMAIL_APP_PASSWORD:
            raise ValueError("Email service not configured")
        
        # Generate verification token
        token = self.email_service.generate_verification_token(email)
        
        # Create verification URL
        frontend_url = settings.cors_origins_list[0]
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        # Send email
        try:
            await self.email_service.send_verification_email(email, verification_url)
            logger.info(f"Verification email sent to {email}")
            return "Verification email sent successfully"
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise Exception("Failed to send verification email. Please try again later.")
    
    async def verify_email(self, token: str) -> str:
        """
        Verify email using token.
        
        Args:
            token: Verification token
            
        Returns:
            Success message
        """
        # Verify token
        email = self.email_service.verify_token(token)
        
        if not email:
            raise ValueError("Invalid or expired verification token")
        
        # Find user by email
        users = await self.user_repo.get_all()
        user = None
        for u in users:
            if u.get('email') == email:
                user = u
                break
        
        if not user:
            raise ValueError("User not found")
        
        firebase_uid = user.get('firebase_uid')
        
        # Update user verification status in Firestore
        await self.user_repo.update(user['id'], {'email_verified': True})
        
        # Also update Firebase Auth emailVerified status
        if firebase_uid:
            try:
                admin_auth.update_user(firebase_uid, email_verified=True)
                logger.info(f"Updated Firebase Auth emailVerified for {firebase_uid}")
            except Exception as e:
                logger.warning(f"Could not update Firebase Auth emailVerified: {e}")
        
        # Invalidate token
        self.email_service.invalidate_token(token)
        
        logger.info(f"Email verified successfully for {email}")
        
        return "Email verified successfully"
    
    async def resend_verification_email(
        self,
        email: str,
        firebase_uid: str
    ) -> str:
        """
        Resend verification email.
        
        Args:
            email: User email
            firebase_uid: Firebase UID
            
        Returns:
            Success message
        """
        return await self.send_verification_email(email, firebase_uid)
