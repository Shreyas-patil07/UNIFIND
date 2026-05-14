"""
Authentication-related Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr


class SendVerificationRequest(BaseModel):
    email: EmailStr
    firebase_uid: str


class VerifyEmailRequest(BaseModel):
    token: str
