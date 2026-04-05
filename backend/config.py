from pydantic_settings import BaseSettings
from typing import Optional
import os

_env_path = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    # Firebase Service Account Credentials
    FIREBASE_TYPE: str = "service_account"
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_AUTH_URI: str = "https://accounts.google.com/o/oauth2/auth"
    FIREBASE_TOKEN_URI: str = "https://oauth2.googleapis.com/token"
    FIREBASE_AUTH_PROVIDER_CERT_URL: str = "https://www.googleapis.com/oauth2/v1/certs"
    FIREBASE_CLIENT_CERT_URL: str
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str
    
    class Config:
        env_file = _env_path
        case_sensitive = True
        extra = "ignore"


settings = Settings()
