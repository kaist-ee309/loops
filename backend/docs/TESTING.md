# Testing Guide

This document describes the testing setup and patterns used in the Loops API project.

## Quick Start

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src/app --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/api/test_auth_api.py

# Run specific test class
uv run pytest tests/unit/api/test_auth_api.py::TestLogin

# Run tests with verbose output
uv run pytest -v
```

## Test Structure

```text
tests/
├── conftest.py              # Shared fixtures (DB, factories, API clients)
├── factories.py             # Model factories for test data
├── unit/
│   ├── api/                 # API route handler tests
│   │   ├── test_auth_api.py
│   │   ├── test_cards_api.py
│   │   ├── test_decks_api.py
│   │   ├── test_profiles_api.py
│   │   ├── test_stats_api.py
│   │   └── test_study_api.py
│   └── services/            # Service layer tests
│       ├── test_deck_service.py
│       ├── test_profile_service.py
│       ├── test_stats_service.py
│       └── test_study_session_service.py
└── integration/             # Integration tests (future)
```

## Key Fixtures

### Database Session (`conftest.py`)

```python
@pytest.fixture
async def db_session():
    """Create an isolated database session for each test."""
    async with async_session_maker() as session:
        yield session
        await session.rollback()
```

### Mock Profile (`conftest.py`)

```python
@pytest.fixture
def mock_profile():
    """Create a mock Profile for API tests."""
    from app.models import Profile
    return Profile(
        id=uuid4(),
        select_all_decks=True,
        daily_goal=20,
        review_ratio_mode="normal",
        custom_review_ratio=0.75,
        min_new_ratio=0.25,
        review_scope="selected_decks_only",
        timezone="UTC",
        theme="auto",
        notification_enabled=True,
        highlight_color="#4CAF50",
        current_streak=5,
        longest_streak=10,
        last_study_date=None,
        total_study_time_minutes=120,
    )
```

### API Clients (`conftest.py`)

```python
@pytest.fixture
def api_client(mock_profile, db_session):
    """Authenticated API client for testing endpoints."""
    from app.main import app
    from app.core.dependencies import get_current_active_profile
    from app.database import get_session

    async def override_get_current_active_profile():
        return mock_profile

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_current_active_profile] = override_get_current_active_profile
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def unauthenticated_client():
    """Unauthenticated API client for testing 403 responses."""
    from app.main import app
    with TestClient(app) as client:
        yield client
```

## Testing Patterns

### API Endpoint Tests

```python
class TestEndpointName:
    """Tests for METHOD /path endpoint."""

    def test_success_case(self, api_client, mocker):
        """Test successful operation."""
        # Mock the service layer
        mock_response = SomeResponse(...)
        mocker.patch(
            "app.api.module.ServiceClass.method_name",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        # Make the request
        response = api_client.get("/api/v1/path")

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert data["field"] == expected_value

    def test_not_found(self, api_client, mocker):
        """Test 404 when resource not found."""
        mocker.patch(
            "app.api.module.ServiceClass.method_name",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.get("/api/v1/path/999")
        assert response.status_code == 404

    def test_requires_auth(self, unauthenticated_client):
        """Test that endpoint requires authentication."""
        response = unauthenticated_client.get("/api/v1/path")
        assert response.status_code == 403
```

### Service Layer Tests

```python
@pytest.mark.asyncio
async def test_service_method(db_session, mocker):
    """Test service method."""
    # Create test data using factories
    profile = await ProfileFactory.create_async(session=db_session)

    # Call the service method
    result = await SomeService.some_method(db_session, profile.id)

    # Assert the result
    assert result.field == expected_value
```

### Using Factories

```python
# Create a profile
profile = await ProfileFactory.create_async(session=db_session)

# Create with specific attributes
deck = await DeckFactory.create_async(
    session=db_session,
    name="Custom Deck",
    is_public=True,
)

# Create multiple records
cards = await VocabularyCardFactory.create_batch_async(
    session=db_session,
    size=10,
    deck_id=deck.id,
)
```

### Mocking External Services

```python
# Mock Supabase auth client
mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)

# Mock async service methods
mocker.patch(
    "app.api.study.StudySessionService.start_session",
    new_callable=AsyncMock,
    return_value=mock_response,
)

# Mock sync service methods
mocker.patch(
    "app.api.study.PronunciationService.evaluate_pronunciation",
    return_value=mock_response,
)
```

### Time-Dependent Tests

```python
from freezegun import freeze_time

@freeze_time("2024-01-15 10:00:00")
def test_with_frozen_time(api_client):
    """Test with frozen time."""
    response = api_client.get("/api/v1/endpoint")
    assert response.json()["date"] == "2024-01-15"
```

## Coverage Requirements

The project requires **80% minimum** test coverage. Current coverage: **85%+**

```bash
# Check coverage locally
uv run pytest --cov=src/app --cov-fail-under=80

# Generate HTML coverage report
uv run pytest --cov=src/app --cov-report=html
# Open htmlcov/index.html in browser
```

## Common Issues

### 1. Import Errors in Tests

Make sure to import models and services from `app.models` and `app.services`, not from internal modules:

```python
# Good
from app.models import Profile, Deck

# Avoid
from app.models.tables.profile import Profile
```

### 2. Async Test Functions

Use `pytest.mark.asyncio` for async test functions:

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result is not None
```

### 3. Database Isolation

Each test gets an isolated database session that is rolled back after the test. Don't commit changes in tests:

```python
# Don't do this in tests
await session.commit()

# The fixture handles cleanup via rollback
```

### 4. Route Ordering in FastAPI

When adding new routes with path parameters like `/{id}`, place them **after** static routes to avoid conflicts:

```python
# Correct order
@router.get("/selected-decks")    # Static route first
@router.get("/categories")        # Static route first
@router.get("/{deck_id}")         # Dynamic route last
```

## Running Tests in CI

Tests are run automatically on PR creation and push. The CI configuration:

1. Sets up Python and uv
2. Installs dependencies
3. Runs pytest with coverage
4. Fails if coverage < 80%

## Adding New Tests

1. Create test file in appropriate directory (`tests/unit/api/` or `tests/unit/services/`)
2. Follow naming convention: `test_<module>_<type>.py`
3. Use existing fixtures from `conftest.py`
4. Mock external dependencies (Supabase, OpenAI, etc.)
5. Test success, error, and authentication cases
6. Ensure tests are deterministic (use factories, freeze time)
