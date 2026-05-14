"""
Pytest configuration and shared fixtures for UNIFIND backend tests.
Production-grade test infrastructure with proper mocking and isolation.
"""

import os
import sys
from datetime import datetime
from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

# Set test environment BEFORE any app imports
os.environ["ENVIRONMENT"] = "test"
os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ["FIREBASE_PRIVATE_KEY_ID"] = "test-key-id"
os.environ["FIREBASE_PRIVATE_KEY"] = (
    "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC\n-----END PRIVATE KEY-----\n"
)
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


# ==================== FIREBASE MOCKING ====================


class MockFirestoreDocument:
    """Mock Firestore document with realistic behavior."""

    def __init__(self, doc_id: str, data: Dict[str, Any] = None, exists: bool = True):
        self.id = doc_id
        self._data = data or {}
        self.exists = exists
        self.reference = MagicMock()
        self.reference.id = doc_id
        self.create_time = datetime.now()
        self.update_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Return document data."""
        return self._data.copy()

    def get(self, field: str = None):
        """Get field value."""
        if field:
            return self._data.get(field)
        return self._data


class MockFirestoreQuery:
    """Mock Firestore query with chainable methods."""

    def __init__(self, collection_name: str, db_state: Dict[str, Dict[str, Any]]):
        self.collection_name = collection_name
        self.db_state = db_state
        self._filters = []
        self._order_by_field = None
        self._limit_count = None
        self._offset_count = 0

    def where(self, field: str, op: str, value: Any):
        """Add filter condition."""
        self._filters.append((field, op, value))
        return self

    def order_by(self, field: str, direction: str = "ASCENDING"):
        """Add ordering."""
        self._order_by_field = (field, direction)
        return self

    def limit(self, count: int):
        """Limit results."""
        self._limit_count = count
        return self

    def offset(self, count: int):
        """Offset results."""
        self._offset_count = count
        return self

    def _apply_filters(self, docs: list) -> list:
        """Apply filters to documents."""
        filtered = []
        for doc in docs:
            data = doc.to_dict()
            matches = True

            for field, op, value in self._filters:
                field_value = data.get(field)

                if op == "==":
                    if field_value != value:
                        matches = False
                elif op == "!=":
                    if field_value == value:
                        matches = False
                elif op == ">":
                    if not (field_value and field_value > value):
                        matches = False
                elif op == ">=":
                    if not (field_value and field_value >= value):
                        matches = False
                elif op == "<":
                    if not (field_value and field_value < value):
                        matches = False
                elif op == "<=":
                    if not (field_value and field_value <= value):
                        matches = False
                elif op == "in":
                    if field_value not in value:
                        matches = False
                elif op == "array-contains":
                    if not (isinstance(field_value, list) and value in field_value):
                        matches = False

                if not matches:
                    break

            if matches:
                filtered.append(doc)

        return filtered

    def get(self) -> list:
        """Execute query and return documents."""
        collection_data = self.db_state.get(self.collection_name, {})
        docs = [
            MockFirestoreDocument(doc_id, data, exists=True)
            for doc_id, data in collection_data.items()
        ]

        # Apply filters
        docs = self._apply_filters(docs)

        # Apply ordering
        if self._order_by_field:
            field, direction = self._order_by_field
            reverse = direction == "DESCENDING"
            docs.sort(key=lambda d: d.to_dict().get(field, ""), reverse=reverse)

        # Apply offset and limit
        if self._offset_count:
            docs = docs[self._offset_count :]
        if self._limit_count:
            docs = docs[: self._limit_count]

        return docs

    def stream(self):
        """Stream documents."""
        return iter(self.get())


class MockFirestoreCollection:
    """Mock Firestore collection with realistic behavior."""

    def __init__(self, collection_name: str, db_state: Dict[str, Dict[str, Any]]):
        self.collection_name = collection_name
        self.db_state = db_state

        # Ensure collection exists in state
        if collection_name not in self.db_state:
            self.db_state[collection_name] = {}

    def document(self, doc_id: str = None):
        """Get document reference."""
        if doc_id is None:
            # Generate random ID
            import uuid

            doc_id = str(uuid.uuid4())

        return MockFirestoreDocumentReference(doc_id, self.collection_name, self.db_state)

    def where(self, field: str, op: str, value: Any):
        """Create query with filter."""
        return MockFirestoreQuery(self.collection_name, self.db_state).where(field, op, value)

    def order_by(self, field: str, direction: str = "ASCENDING"):
        """Create query with ordering."""
        return MockFirestoreQuery(self.collection_name, self.db_state).order_by(field, direction)

    def limit(self, count: int):
        """Create query with limit."""
        return MockFirestoreQuery(self.collection_name, self.db_state).limit(count)

    def offset(self, count: int):
        """Create query with offset."""
        return MockFirestoreQuery(self.collection_name, self.db_state).offset(count)

    def get(self):
        """Get all documents."""
        return MockFirestoreQuery(self.collection_name, self.db_state).get()

    def stream(self):
        """Stream all documents."""
        return MockFirestoreQuery(self.collection_name, self.db_state).stream()

    def add(self, data: Dict[str, Any]):
        """Add document with auto-generated ID."""
        import uuid

        doc_id = str(uuid.uuid4())
        doc_ref = self.document(doc_id)
        doc_ref.set(data)
        return (None, doc_ref)


class MockFirestoreDocumentReference:
    """Mock Firestore document reference with realistic behavior."""

    def __init__(self, doc_id: str, collection_name: str, db_state: Dict[str, Dict[str, Any]]):
        self.id = doc_id
        self.collection_name = collection_name
        self.db_state = db_state

    def get(self):
        """Get document snapshot."""
        collection_data = self.db_state.get(self.collection_name, {})
        data = collection_data.get(self.id)

        if data is None:
            return MockFirestoreDocument(self.id, None, exists=False)

        return MockFirestoreDocument(self.id, data, exists=True)

    def set(self, data: Dict[str, Any], merge: bool = False):
        """Set document data."""
        if self.collection_name not in self.db_state:
            self.db_state[self.collection_name] = {}

        if merge and self.id in self.db_state[self.collection_name]:
            # Merge with existing data
            self.db_state[self.collection_name][self.id].update(data)
        else:
            # Overwrite
            self.db_state[self.collection_name][self.id] = data.copy()

    def update(self, data: Dict[str, Any]):
        """Update document fields."""
        if self.collection_name not in self.db_state:
            self.db_state[self.collection_name] = {}

        if self.id not in self.db_state[self.collection_name]:
            raise Exception(f"Document {self.id} does not exist")

        self.db_state[self.collection_name][self.id].update(data)

    def delete(self):
        """Delete document."""
        if self.collection_name in self.db_state:
            self.db_state[self.collection_name].pop(self.id, None)

    def collection(self, collection_name: str):
        """Get subcollection."""
        full_name = f"{self.collection_name}/{self.id}/{collection_name}"
        return MockFirestoreCollection(full_name, self.db_state)


class MockFirestoreClient:
    """Mock Firestore client with realistic behavior."""

    def __init__(self):
        self.db_state: Dict[str, Dict[str, Any]] = {}

    def collection(self, collection_name: str):
        """Get collection reference."""
        return MockFirestoreCollection(collection_name, self.db_state)

    def reset(self):
        """Reset database state."""
        self.db_state.clear()


@pytest.fixture(scope="session")
def mock_firestore_client():
    """Create mock Firestore client for session."""
    return MockFirestoreClient()


@pytest.fixture
def mock_db(mock_firestore_client):
    """Provide clean mock database for each test."""
    mock_firestore_client.reset()
    return mock_firestore_client


@pytest.fixture(scope="session", autouse=True)
def mock_firebase_admin():
    """Mock Firebase Admin SDK at session level."""
    # Create mock firebase_admin module
    mock_firebase = MagicMock()
    mock_auth = MagicMock()

    # Mock auth functions
    mock_auth.verify_id_token = MagicMock(return_value={"uid": "test-user-123"})
    mock_auth.ExpiredIdTokenError = type("ExpiredIdTokenError", (Exception,), {})
    mock_auth.RevokedIdTokenError = type("RevokedIdTokenError", (Exception,), {})
    mock_auth.InvalidIdTokenError = type("InvalidIdTokenError", (Exception,), {})

    # Inject mocks
    sys.modules["firebase_admin"] = mock_firebase
    sys.modules["firebase_admin.auth"] = mock_auth
    sys.modules["firebase_admin.credentials"] = MagicMock()
    sys.modules["firebase_admin.firestore"] = MagicMock()

    mock_firebase.auth = mock_auth

    yield mock_firebase

    # Cleanup
    for module in [
        "firebase_admin",
        "firebase_admin.auth",
        "firebase_admin.credentials",
        "firebase_admin.firestore",
    ]:
        sys.modules.pop(module, None)


# ==================== APP AND CLIENT FIXTURES ====================


@pytest.fixture(scope="session")
def app(mock_firebase_admin) -> FastAPI:
    """Create FastAPI test application."""
    # Patch database to use mock
    with patch("app.core.database.FirebaseManager") as mock_manager:
        mock_instance = MagicMock()
        mock_instance.get_client.return_value = MockFirestoreClient()
        mock_manager.get_instance.return_value = mock_instance

        from app.main import app

        return app


@pytest.fixture
async def client(app: FastAPI, mock_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    # Override get_db dependency to use mock
    from app.core.database import get_db

    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()


# ==================== DATA FIXTURES ====================


@pytest.fixture
def sample_user() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "firebase_uid": "firebase-uid-123",
        "email": "test@example.com",
        "name": "Test User",
        "university": "Test University",
        "created_at": datetime.now().isoformat(),
        "email_verified": True,
        "profile_picture": "https://example.com/pic.jpg",
        "bio": "Test bio",
        "phone": "+1234567890",
    }


@pytest.fixture
def sample_product() -> Dict[str, Any]:
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
        "created_at": datetime.now().isoformat(),
        "views": 0,
        "location": "Test Location",
    }


@pytest.fixture
def sample_transaction() -> Dict[str, Any]:
    """Sample transaction data for testing."""
    return {
        "id": "test-transaction-123",
        "product_id": "test-product-123",
        "seller_id": "test-user-123",
        "buyer_id": "test-buyer-456",
        "amount": 99.99,
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_review() -> Dict[str, Any]:
    """Sample review data for testing."""
    return {
        "id": "test-review-123",
        "reviewer_id": "test-user-123",
        "reviewed_user_id": "test-user-456",
        "product_id": "test-product-123",
        "rating": 5,
        "comment": "Great seller!",
        "created_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_chat_room() -> Dict[str, Any]:
    """Sample chat room data for testing."""
    return {
        "id": "user1_user2",
        "participants": ["user1", "user2"],
        "last_message": "Hello",
        "last_message_time": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_message() -> Dict[str, Any]:
    """Sample message data for testing."""
    return {
        "id": "test-message-123",
        "chat_room_id": "user1_user2",
        "sender_id": "user1",
        "content": "Hello",
        "is_read": False,
        "created_at": datetime.now().isoformat(),
    }


# ==================== AUTH FIXTURES ====================


@pytest.fixture
def auth_headers(sample_user) -> Dict[str, str]:
    """Mock authentication headers."""
    return {"Authorization": f"Bearer mock-token-{sample_user['id']}"}


@pytest.fixture
def mock_current_user(sample_user):
    """Mock get_current_user dependency."""

    async def _get_current_user():
        return sample_user["firebase_uid"]

    return _get_current_user


@pytest.fixture
def authenticated_client(client, mock_current_user, app):
    """Client with mocked authentication."""
    from app.api.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = mock_current_user
    return client


# ==================== EXTERNAL SERVICE MOCKS ====================


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini AI client."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = (
        '{"intent": "buy", "keywords": ["laptop", "electronics"], "category": "Electronics"}'
    )
    mock_client.generate_content.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_cloudinary():
    """Mock Cloudinary upload."""
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {
            "secure_url": "https://cloudinary.com/test-image.jpg",
            "public_id": "test-public-id",
            "width": 800,
            "height": 600,
        }
        yield mock_upload


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    with patch("aiosmtplib.send") as mock_send:
        mock_send.return_value = None
        yield mock_send


# ==================== PYTEST CONFIGURATION ====================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_firebase: mark test as requiring real Firebase")
    config.addinivalue_line(
        "markers", "requires_external: mark test as requiring external services"
    )


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    from app.core.database import FirebaseManager

    FirebaseManager._instance = None
    yield
    FirebaseManager._instance = None


# ==================== TEST HELPERS ====================


@pytest.fixture
def create_test_user(mock_db):
    """Factory fixture to create test users."""

    def _create_user(**kwargs):
        user_data = {
            "id": kwargs.get("id", "test-user-123"),
            "firebase_uid": kwargs.get("firebase_uid", "firebase-uid-123"),
            "email": kwargs.get("email", "test@example.com"),
            "name": kwargs.get("name", "Test User"),
            "university": kwargs.get("university", "Test University"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
            "email_verified": kwargs.get("email_verified", True),
        }

        mock_db.collection("users").document(user_data["id"]).set(user_data)
        return user_data

    return _create_user


@pytest.fixture
def create_test_product(mock_db):
    """Factory fixture to create test products."""

    def _create_product(**kwargs):
        product_data = {
            "id": kwargs.get("id", "test-product-123"),
            "title": kwargs.get("title", "Test Product"),
            "description": kwargs.get("description", "Test description"),
            "price": kwargs.get("price", 99.99),
            "category": kwargs.get("category", "Electronics"),
            "seller_id": kwargs.get("seller_id", "test-user-123"),
            "status": kwargs.get("status", "active"),
            "created_at": kwargs.get("created_at", datetime.now().isoformat()),
        }

        mock_db.collection("products").document(product_data["id"]).set(product_data)
        return product_data

    return _create_product
