"""
Pytest configuration and shared fixtures for UNIFIND backend tests.
"""
import pytest
import os
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, MagicMock, AsyncMock
from httpx import AsyncClient
from fastapi import FastAPI

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ["FIREBASE_PRIVATE_KEY_ID"] = "test-key-id"
os.environ["FIREBASE_PRIVATE_KEY"] = "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n"
os.environ["FIREBASE_CLIENT_EMAIL"] = "test@test.iam.gserviceaccount.com"
os.environ["FIREBASE_CLIENT_ID"] = "123456789"
os.environ["FIREBASE_CLIENT_CERT_URL"] = "https://test.com"
os.environ["GEMINI_API_KEY"] = "test-gemini-key"
os.environ["CLOUDINARY_CLOUD_NAME"] = "test-cloud"
os.environ["CLOUDINARY_API_KEY"] = "test-key"
os.environ["CLOUDINARY_API_SECRET"] = "test-secret"
os.environ["GMAIL_USER"] = "test@gmail.com"
os.environ["GMAIL_APP_PASSWORD"] = "test-password"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"


@pytest.fixture(scope="session")
def mock_firebase_db():
    """Mock Firestore database for all tests."""
    mock_db = MagicMock()
    
    # Mock collection and document methods
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_query = MagicMock()
    
    # Setup method chaining
    mock_db.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document
    mock_collection.where.return_value = mock_query
    mock_collection.order_by.return_value = mock_query
    mock_collection.limit.return_value = mock_query
    mock_collection.offset.return_value = mock_query
    mock_collection.stream.return_value = []
    mock_collection.get.return_value = []
    
    mock_query.where.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.stream.return_value = []
    mock_query.get.return_value = []
    
    # Mock document operations
    mock_document.get.return_value = MagicMock(exists=False)
    mock_document.set.return_value = None
    mock_document.update.return_value = None
    mock_document.delete.return_value = None
    
    return mock_db


@pytest.fixture(scope="session")
def mock_firebase_admin(mock_firebase_db):
    """Mock Firebase Admin SDK."""
    import sys
    from unittest.mock import MagicMock
    
    # Create mock firebase_admin module
    mock_firebase = MagicMock()
    mock_firebase.firestore.client.return_value = mock_firebase_db
    mock_firebase.initialize_app.return_value = None
    
    # Mock credentials
    mock_credentials = MagicMock()
    mock_firebase.credentials.Certificate.return_value = mock_credentials
    
    sys.modules['firebase_admin'] = mock_firebase
    sys.modules['firebase_admin.firestore'] = mock_firebase.firestore
    sys.modules['firebase_admin.credentials'] = mock_firebase.credentials
    
    return mock_firebase


@pytest.fixture(scope="session")
def app(mock_firebase_admin) -> FastAPI:
    """Create FastAPI test application."""
    from app.main import app
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db(mock_firebase_db):
    """Provide mock database for individual tests."""
    # Reset mocks for each test
    mock_firebase_db.reset_mock()
    return mock_firebase_db


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "firebase_uid": "firebase-uid-123",
        "email": "test@example.com",
        "name": "Test User",
        "university": "Test University",
        "created_at": "2024-01-01T00:00:00Z",
        "email_verified": True,
        "profile_picture": "https://example.com/pic.jpg"
    }


@pytest.fixture
def sample_product():
    """Sample product data for testing."""
    return {
        "id": "test-product-123",
        "title": "Test Product",
        "description": "Test description",
        "price": 99.99,
        "category": "Electronics",
        "subcategory": "Laptops",
        "condition": "Like New",
        "seller_id": "test-user-123",
        "images": ["https://example.com/image1.jpg"],
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "views": 0
    }


@pytest.fixture
def sample_transaction():
    """Sample transaction data for testing."""
    return {
        "id": "test-transaction-123",
        "product_id": "test-product-123",
        "seller_id": "test-user-123",
        "buyer_id": "test-buyer-456",
        "amount": 99.99,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def auth_headers(sample_user):
    """Mock authentication headers."""
    return {
        "Authorization": f"Bearer mock-token-{sample_user['id']}"
    }


@pytest.fixture
def mock_auth_dependency(sample_user, monkeypatch):
    """Mock authentication dependency to return test user."""
    async def mock_get_current_user():
        return sample_user["id"]
    
    from app.api.dependencies import auth
    monkeypatch.setattr(auth, "get_current_user", mock_get_current_user)
    
    return mock_get_current_user


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini AI client."""
    mock_client = AsyncMock()
    mock_client.generate_content.return_value = MagicMock(
        text='{"intent": "buy", "keywords": ["laptop", "electronics"]}'
    )
    return mock_client


@pytest.fixture
def mock_cloudinary():
    """Mock Cloudinary upload."""
    mock_upload = Mock()
    mock_upload.return_value = {
        "secure_url": "https://cloudinary.com/test-image.jpg",
        "public_id": "test-public-id"
    }
    return mock_upload


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
