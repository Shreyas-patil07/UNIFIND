#!/usr/bin/env python3
"""Test delete product endpoint"""

import sys
import os
sys.path.insert(0, 'backend')

# Set environment variables before importing
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'backend/unifind-firebase-key.json'
os.environ['GEMINI_API_KEY'] = 'test-key'
os.environ['CLOUDINARY_CLOUD_NAME'] = 'test'
os.environ['CLOUDINARY_API_KEY'] = 'test'
os.environ['CLOUDINARY_API_SECRET'] = 'test'

from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

# Mock Firebase auth
def mock_get_current_user():
    return "test-user-123"

# Mock Firestore
mock_doc = MagicMock()
mock_doc.exists = True
mock_doc.to_dict.return_value = {
    'seller_id': 'test-user-123',
    'title': 'Test Product',
    'images': []
}

mock_doc_ref = MagicMock()
mock_doc_ref.get.return_value = mock_doc
mock_doc_ref.delete.return_value = None

mock_collection = MagicMock()
mock_collection.document.return_value = mock_doc_ref

mock_db = MagicMock()
mock_db.collection.return_value = mock_collection

print("Testing DELETE /api/products/{product_id}")
print("=" * 60)

with patch('routes.products.get_current_user', return_value="test-user-123"):
    with patch('routes.products.get_db', return_value=mock_db):
        response = client.delete(
            "/api/products/test-product-123",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Delete endpoint works correctly!")
        else:
            print("❌ Delete endpoint failed!")
            sys.exit(1)

print("\nTesting unauthorized delete (different user)")
print("=" * 60)

mock_doc.to_dict.return_value = {
    'seller_id': 'different-user',
    'title': 'Test Product',
    'images': []
}

with patch('routes.products.get_current_user', return_value="test-user-123"):
    with patch('routes.products.get_db', return_value=mock_db):
        response = client.delete(
            "/api/products/test-product-123",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 403:
            print("✅ Authorization check works correctly!")
        else:
            print("❌ Authorization check failed!")
            sys.exit(1)

print("\n✅ All delete endpoint tests passed!")
