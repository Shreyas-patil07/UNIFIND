# UNIFIND Backend - Testing Guide

## Test Architecture

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests (isolated, fast)
│   ├── test_auth_service.py
│   └── test_product_service.py
├── integration/          # Integration tests (API endpoints)
│   ├── test_auth_routes.py
│   ├── test_product_routes.py
│   ├── test_user_routes.py
│   └── test_transaction_routes.py
└── fixtures/             # Test data and mocks
```

## Running Tests

### All Tests
```bash
pytest tests/
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Unit Tests Only
```bash
pytest tests/unit/ -m unit
```

### Integration Tests Only
```bash
pytest tests/integration/ -m integration
```

### Specific Test File
```bash
pytest tests/integration/test_auth_routes.py
```

### Specific Test Function
```bash
pytest tests/integration/test_auth_routes.py::TestAuthRoutes::test_send_verification_email_success
```

### Verbose Output
```bash
pytest tests/ -v
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Run Last Failed Tests
```bash
pytest tests/ --lf
```

## Test Fixtures

### Available Fixtures (from conftest.py)

- `client` - Async HTTP client for API testing
- `mock_db` - Mocked Firestore database
- `sample_user` - Sample user data
- `sample_product` - Sample product data
- `sample_transaction` - Sample transaction data
- `auth_headers` - Mock authentication headers
- `mock_gemini_client` - Mocked Gemini AI client
- `mock_cloudinary` - Mocked Cloudinary upload

### Using Fixtures

```python
@pytest.mark.asyncio
async def test_example(client, sample_user):
    """Test using fixtures."""
    response = await client.get(f"/api/users/{sample_user['id']}")
    assert response.status_code == 200
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import MagicMock
from app.services.product_service import ProductService

@pytest.mark.unit
@pytest.mark.asyncio
class TestProductService:
    """Test ProductService business logic."""
    
    @pytest.fixture
    def product_service(self, mock_db):
        return ProductService(mock_db)
    
    async def test_create_product(self, product_service):
        """Test creating a product."""
        # Arrange
        mock_db.collection.return_value.document.return_value.id = "new-id"
        
        # Act
        result = await product_service.create_product(...)
        
        # Assert
        assert result is not None
        assert "id" in result
```

### Integration Test Example

```python
import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.integration
@pytest.mark.asyncio
class TestProductRoutes:
    """Test product API endpoints."""
    
    async def test_get_products(self, client: AsyncClient):
        """Test getting products list."""
        response = await client.get("/api/products")
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
```

## Mocking

### Mocking Firebase

```python
from unittest.mock import MagicMock

def test_with_firebase_mock(mock_db):
    # Mock document
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"id": "123", "name": "Test"}
    
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
```

### Mocking Services

```python
from unittest.mock import patch

async def test_with_service_mock(client):
    with patch('app.services.product_service.ProductService.get_all_products') as mock:
        mock.return_value = {"products": [], "total": 0}
        
        response = await client.get("/api/products")
        assert response.status_code == 200
```

### Mocking Authentication

```python
from unittest.mock import patch

async def test_authenticated_endpoint(client):
    with patch('app.api.dependencies.auth.get_current_user') as mock_auth:
        mock_auth.return_value = "user-123"
        
        response = await client.get("/api/products/seller/me")
        assert response.status_code == 200
```

## Coverage

### Generate Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
```

View report: `open htmlcov/index.html`

### Coverage Requirements

- Minimum coverage: 60%
- Target coverage: 80%
- Critical paths: 90%+

### Excluded from Coverage

- Test files
- `__init__.py` files
- Abstract methods
- Type checking blocks

## Test Markers

### Available Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.asyncio` - Async tests

### Using Markers

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_example():
    pass
```

### Running by Marker

```bash
pytest tests/ -m unit
pytest tests/ -m "not slow"
```

## Best Practices

### 1. Test Naming
- Use descriptive names: `test_create_product_success`
- Follow pattern: `test_<what>_<condition>_<expected>`

### 2. Test Structure (AAA Pattern)
```python
async def test_example():
    # Arrange - Set up test data
    user_data = {"name": "Test"}
    
    # Act - Perform action
    result = await service.create_user(user_data)
    
    # Assert - Verify result
    assert result is not None
```

### 3. Test Independence
- Each test should be independent
- Don't rely on test execution order
- Clean up after tests

### 4. Mock External Services
- Always mock Firebase
- Mock AI services (Gemini)
- Mock email sending
- Mock file uploads

### 5. Test Edge Cases
- Empty inputs
- Invalid data
- Unauthorized access
- Not found scenarios
- Error conditions

### 6. Async Testing
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

## Continuous Integration

Tests run automatically on:
- Push to main/develop
- Pull requests
- Manual workflow dispatch

### CI Pipeline
1. Install dependencies
2. Run linters (ruff, black, isort)
3. Run tests with coverage
4. Upload coverage reports
5. Build Docker image

## Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=.
pytest tests/
```

### Async Warnings
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

### Firebase Mock Issues
- Check conftest.py for mock setup
- Ensure firebase_admin is mocked before import

### Coverage Not Working
```bash
# Install pytest-cov
pip install pytest-cov
```

## Performance

### Test Execution Time

- Unit tests: < 1s per test
- Integration tests: < 5s per test
- Full suite: < 2 minutes

### Slow Tests

Mark slow tests:
```python
@pytest.mark.slow
async def test_slow_operation():
    pass
```

Skip slow tests:
```bash
pytest tests/ -m "not slow"
```

## Future Improvements

- [ ] Add E2E tests with real Firebase emulator
- [ ] Add load testing with Locust
- [ ] Add mutation testing
- [ ] Increase coverage to 80%+
- [ ] Add performance benchmarks
- [ ] Add contract testing for API
