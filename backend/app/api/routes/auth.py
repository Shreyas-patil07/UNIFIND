"""
Authentication routes for email verification.
"""
from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.auth import SendVerificationRequest, VerifyEmailRequest
from app.services.auth_service import AuthService
from app.api.dependencies.services import get_auth_service

router = APIRouter(tags=["auth"])


@router.post("/send-verification")
async def send_verification_email(
    request: SendVerificationRequest,
    service: AuthService = Depends(get_auth_service)
):
    """Send email verification link to user"""
    try:
        message = await service.send_verification_email(request.email, request.firebase_uid)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    service: AuthService = Depends(get_auth_service)
):
    """Verify email using token"""
    try:
        message = await service.verify_email(request.token)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend-verification")
async def resend_verification_email(
    request: SendVerificationRequest,
    service: AuthService = Depends(get_auth_service)
):
    """Resend verification email"""
    try:
        message = await service.resend_verification_email(request.email, request.firebase_uid)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
