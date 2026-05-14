"""
Firebase Firestore database initialization and connection management.
Refactored for lazy initialization, thread safety, and testability.
"""

import logging
import threading
from contextlib import contextmanager
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

from app.core.config import settings

logger = logging.getLogger(__name__)


class FirebaseManager:
    """
    Thread-safe Firebase manager with lazy initialization.
    Supports testing with mock instances and proper cleanup.
    """

    _instance: Optional["FirebaseManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._db_client: Optional[firestore.Client] = None
        self._app: Optional[firebase_admin.App] = None
        self._initialized = False
        self._init_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "FirebaseManager":
        """Get singleton instance of FirebaseManager (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance.
        ONLY use this in tests for cleanup between test runs.
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.cleanup()
                cls._instance = None

    def initialize(self, force: bool = False) -> firestore.Client:
        """
        Initialize Firebase Admin SDK and return Firestore client.
        Thread-safe lazy initialization.

        Args:
            force: If True, reinitialize even if already initialized

        Returns:
            firestore.Client: Initialized Firestore client

        Raises:
            Exception: If Firebase initialization fails
        """
        if self._initialized and not force:
            return self._db_client

        with self._init_lock:
            # Double-check after acquiring lock
            if self._initialized and not force:
                return self._db_client

            try:
                # Clean up existing instance if forcing reinitialization
                if force and self._initialized:
                    self.cleanup()

                # Try to load from JSON file first (RECOMMENDED)
                from pathlib import Path
                json_path = Path(__file__).parent.parent.parent / "firebase-service-account.json"
                
                if json_path.exists():
                    logger.info(f"Loading Firebase credentials from JSON file: {json_path}")
                    cred = credentials.Certificate(str(json_path))
                else:
                    # Fall back to environment variables
                    logger.info("Loading Firebase credentials from environment variables")
                    firebase_config = {
                        "type": settings.FIREBASE_TYPE,
                        "project_id": settings.FIREBASE_PROJECT_ID,
                        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                        "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                        "client_email": settings.FIREBASE_CLIENT_EMAIL,
                        "client_id": settings.FIREBASE_CLIENT_ID,
                        "auth_uri": settings.FIREBASE_AUTH_URI,
                        "token_uri": settings.FIREBASE_TOKEN_URI,
                        "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_CERT_URL,
                        "client_x509_cert_url": settings.FIREBASE_CLIENT_CERT_URL,
                    }
                    cred = credentials.Certificate(firebase_config)

                # Check if default app already exists
                try:
                    self._app = firebase_admin.get_app()
                    logger.info("Using existing Firebase app")
                except ValueError:
                    # No default app exists, create one
                    self._app = firebase_admin.initialize_app(cred)
                    logger.info("Firebase app initialized")

                self._db_client = firestore.client()
                self._initialized = True
                logger.info("Firebase Firestore client initialized successfully")

                return self._db_client

            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}", exc_info=True)
                self._initialized = False
                self._db_client = None
                self._app = None
                raise

    def get_client(self) -> firestore.Client:
        """
        Get Firestore client, initializing if necessary.

        Returns:
            firestore.Client: Firestore client instance

        Raises:
            RuntimeError: If initialization fails
        """
        if not self._initialized or self._db_client is None:
            return self.initialize()
        return self._db_client

    def is_initialized(self) -> bool:
        """Check if Firebase is initialized."""
        return self._initialized and self._db_client is not None

    def cleanup(self) -> None:
        """
        Clean up Firebase resources.
        Use this in tests or during shutdown.
        """
        try:
            if self._app is not None:
                firebase_admin.delete_app(self._app)
                logger.info("Firebase app deleted")
        except Exception as e:
            logger.warning(f"Error during Firebase cleanup: {e}")
        finally:
            self._db_client = None
            self._app = None
            self._initialized = False

    def set_mock_client(self, mock_client: firestore.Client) -> None:
        """
        Set a mock Firestore client for testing.

        Args:
            mock_client: Mock Firestore client instance
        """
        self._db_client = mock_client
        self._initialized = True
        logger.info("Mock Firestore client set for testing")


# ==================== PUBLIC API ====================


def init_firebase() -> firestore.Client:
    """
    Initialize Firebase Admin SDK and return Firestore client.
    This should be called once during application startup.

    Returns:
        firestore.Client: Initialized Firestore client

    Raises:
        Exception: If Firebase initialization fails
    """
    manager = FirebaseManager.get_instance()
    return manager.initialize()


def get_db() -> firestore.Client:
    """
    Get Firestore database instance with lazy initialization.
    Thread-safe and suitable for use in FastAPI dependencies.

    Returns:
        firestore.Client: Firestore client instance

    Raises:
        RuntimeError: If initialization fails
    """
    manager = FirebaseManager.get_instance()
    return manager.get_client()


def cleanup_firebase() -> None:
    """
    Clean up Firebase resources.
    Use this during application shutdown or in test teardown.
    """
    manager = FirebaseManager.get_instance()
    manager.cleanup()


@contextmanager
def firebase_test_context(mock_client: Optional[firestore.Client] = None):
    """
    Context manager for testing with Firebase.
    Automatically cleans up after the test.

    Usage:
        with firebase_test_context(mock_client):
            # Your test code here
            db = get_db()

    Args:
        mock_client: Optional mock Firestore client
    """
    manager = FirebaseManager.get_instance()

    if mock_client:
        manager.set_mock_client(mock_client)

    try:
        yield manager
    finally:
        FirebaseManager.reset_instance()
