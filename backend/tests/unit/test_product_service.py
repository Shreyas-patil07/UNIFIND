"""
Unit tests for ProductService.
"""

from unittest.mock import MagicMock

import pytest

from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService


@pytest.mark.unit
@pytest.mark.asyncio
class TestProductService:
    """Test ProductService business logic."""

    @pytest.fixture
    def product_service(self, mock_db):
        """Create ProductService instance with mocked dependencies."""
        return ProductService(mock_db)

    async def test_create_product_success(self, product_service, mock_db, sample_product):
        """Test creating a new product."""
        product_data = ProductCreate(
            title=sample_product["title"],
            description=sample_product["description"],
            price=sample_product["price"],
            category=sample_product["category"],
            subcategory=sample_product["subcategory"],
            condition=sample_product["condition"],
            images=sample_product["images"],
        )

        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "new-product-id"
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        result = await product_service.create_product(product_data, "seller-123")

        assert result is not None
        assert "id" in result
        mock_doc_ref.set.assert_called_once()

    async def test_create_product_invalid_price(self, product_service):
        """Test creating product with negative price."""
        with pytest.raises(ValueError):
            product_data = ProductCreate(
                title="Test Product",
                description="Description",
                price=-10.0,  # Invalid
                category="Electronics",
                subcategory="Laptops",
                condition="New",
                images=[],
            )

    async def test_get_product_by_id_success(self, product_service, mock_db, sample_product):
        """Test getting product by ID."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.id = sample_product["id"]
        mock_doc.to_dict.return_value = sample_product

        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        result = await product_service.get_product_by_id(sample_product["id"])

        assert result is not None
        assert result["id"] == sample_product["id"]

    async def test_get_product_by_id_not_found(self, product_service, mock_db):
        """Test getting non-existent product."""
        mock_doc = MagicMock()
        mock_doc.exists = False

        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        result = await product_service.get_product_by_id("nonexistent-id")

        assert result is None

    async def test_update_product_success(self, product_service, mock_db, sample_product):
        """Test updating product by owner."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.id = sample_product["id"]
        mock_doc.to_dict.return_value = sample_product

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc

        update_data = ProductUpdate(title="Updated Title")

        result = await product_service.update_product(
            sample_product["id"], update_data, sample_product["seller_id"]
        )

        assert result is not None
        mock_doc_ref.update.assert_called_once()

    async def test_update_product_unauthorized(self, product_service, mock_db, sample_product):
        """Test updating product by non-owner."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_product

        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        update_data = ProductUpdate(title="Hacked Title")

        result = await product_service.update_product(
            sample_product["id"], update_data, "different-user-id"  # Not the owner
        )

        assert result is None

    async def test_delete_product_success(self, product_service, mock_db, sample_product):
        """Test deleting product by owner."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_product

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc

        result = await product_service.delete_product(
            sample_product["id"], sample_product["seller_id"]
        )

        assert result is True
        mock_doc_ref.delete.assert_called_once()

    async def test_delete_product_unauthorized(self, product_service, mock_db, sample_product):
        """Test deleting product by non-owner."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_product

        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        result = await product_service.delete_product(sample_product["id"], "different-user-id")

        assert result is False

    async def test_mark_as_sold_success(self, product_service, mock_db, sample_product):
        """Test marking product as sold."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = sample_product

        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc

        result = await product_service.mark_as_sold(
            sample_product["id"], sample_product["seller_id"], "buyer-123"
        )

        assert result is True
        mock_doc_ref.update.assert_called_once()
