"""
Database dependencies for dependency injection.
"""
from google.cloud import firestore
from app.core.database import get_db


def get_database() -> firestore.Client:
    """
    Dependency to inject Firestore database client.
    
    Usage:
        @router.get("/items")
        async def get_items(db: firestore.Client = Depends(get_database)):
            items = db.collection('items').stream()
            return list(items)
    """
    return get_db()
