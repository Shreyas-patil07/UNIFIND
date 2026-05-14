"""
Configuration management for UNIFIND backend.
Loads environment variables and provides settings object with strict validation.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All critical settings are validated on startup.
    """

    # Firebase Service Account Credentials
    FIREBASE_TYPE: str = "service_account"
    FIREBASE_PROJECT_ID: str = Field(..., min_length=1, description="Firebase project ID")
    FIREBASE_PRIVATE_KEY_ID: str = Field(..., min_length=1)
    FIREBASE_PRIVATE_KEY: str = Field(..., min_length=1)
    FIREBASE_CLIENT_EMAIL: EmailStr
    FIREBASE_CLIENT_ID: str = Field(..., min_length=1)
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_CERT_URL: str = Field(..., min_length=1)

    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    # Gemini AI Configuration
    GEMINI_API_KEY: str = Field(..., min_length=1, description="Google Gemini API key")

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = Field(..., min_length=1)
    CLOUDINARY_API_KEY: str = Field(..., min_length=1)
    CLOUDINARY_API_SECRET: str = Field(..., min_length=1)
    CLOUDINARY_UPLOAD_PRESET: str = "unifind_products"

    # Email Configuration
    GMAIL_USER: EmailStr
    GMAIL_APP_PASSWORD: str = Field(..., min_length=1)

    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        pattern="^(development|staging|production|test)$",
        description="Application environment",
    )

    # Observability & Monitoring
    SENTRY_DSN: Optional[str] = Field(
        default=None, description="Sentry DSN for error tracking (required in production)"
    )

    class Config:
        env_file = _env_path
        case_sensitive = True
        extra = "ignore"

    @field_validator("FIREBASE_PRIVATE_KEY")
    @classmethod
    def validate_private_key(cls, v: str) -> str:
        """Validate Firebase private key format."""
        if not v.startswith("-----BEGIN PRIVATE KEY-----"):
            raise ValueError("Invalid Firebase private key format")
        return v

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS origins."""
        if not v or v.strip() == "":
            raise ValueError("CORS_ORIGINS cannot be empty")
        return v

    @field_validator("SENTRY_DSN")
    @classmethod
    def validate_sentry_in_production(cls, v: Optional[str], info) -> Optional[str]:
        """Validate Sentry DSN is configured in production."""
        # Get environment from validation context
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and not v:
            raise ValueError(
                "SENTRY_DSN is required in production environment for error tracking. "
                "Get your DSN from https://sentry.io/settings/projects/"
            )
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.ENVIRONMENT == "test"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Validates all required environment variables on first call.
    """
    try:
        settings = Settings()
    except Exception as e:
        raise ValueError(
            f"Configuration error: {str(e)}\n"
            "Please check your .env file and ensure all required variables are set."
        ) from e

    # Additional production validations
    if settings.is_production:
        if "*" in settings.CORS_ORIGINS:
            raise ValueError(
                "CORS wildcard (*) is not allowed in production. " "Please specify exact origins."
            )

        # Warn about non-HTTPS origins in production
        for origin in settings.cors_origins_list:
            if not origin.startswith("https://") and not origin.startswith("http://localhost"):
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Non-HTTPS origin in production: {origin}. " "This may pose security risks."
                )

    return settings


# Global settings instance
settings = get_settings()
