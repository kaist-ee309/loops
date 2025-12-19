"""
Pytest configuration and fixtures for Loops API tests.

This module provides:
- Database fixtures with transaction rollback for test isolation
- Factory fixtures for creating test data
- Mock fixtures for external services (OpenAI, Gemini, Supabase)
- Utility fixtures (frozen time, seeded random)
- API test fixtures with FastAPI TestClient
"""

import os
import random
import sys

# Add src and tests directories to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Set test environment before importing app modules
os.environ.setdefault("TESTING", "1")
# Default to sqlite for unit tests so CI doesn't require Postgres.
_TEST_DB_DIR = Path(__file__).resolve().parents[1] / ".tmp"
_TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
_DEFAULT_TEST_DB_URL = f"sqlite+aiosqlite:///{(_TEST_DB_DIR / f'loops_test_{uuid4().hex}.db')}"
os.environ.setdefault("DATABASE_URL", _DEFAULT_TEST_DB_URL)
os.environ.setdefault("TEST_DATABASE_URL", _DEFAULT_TEST_DB_URL)
os.environ.setdefault("DB_SSL_NO_VERIFY", "1")  # Skip SSL verification in tests
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "test_key")
os.environ.setdefault("SUPABASE_SECRET_KEY", "test_secret")
os.environ.setdefault("OPENAI_API_KEY", "test_openai_key")
os.environ.setdefault("GEMINI_API_KEY", "test_gemini_key")


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="function")
async def test_engine():
    """
    Create a test database engine.

    Uses the loops_test database for isolation from development data.
    """
    test_db_url = os.environ["TEST_DATABASE_URL"]

    engine_kwargs: dict = {
        "echo": False,
        "future": True,
        "pool_pre_ping": True,
    }
    if test_db_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    engine = create_async_engine(test_db_url, **engine_kwargs)

    # Import models to ensure they're registered

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup: drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session.

    Each test runs with a clean database since tables are dropped/recreated per test.
    """
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.commit()


# =============================================================================
# Time Fixtures
# =============================================================================


@pytest.fixture
def frozen_datetime():
    """
    Return a fixed datetime for testing time-dependent logic.

    Use with freezegun in tests:
        with freeze_time(frozen_datetime):
            # datetime.utcnow() returns frozen_datetime
    """
    return datetime(2024, 1, 15, 12, 0, 0)


@pytest.fixture
def freeze_time_fixture(frozen_datetime):
    """
    Automatically freeze time for the duration of a test.

    Usage:
        def test_something(freeze_time_fixture):
            # Time is frozen to 2024-01-15 12:00:00
            assert datetime.utcnow() == datetime(2024, 1, 15, 12, 0, 0)
    """
    with freeze_time(frozen_datetime):
        yield frozen_datetime


# =============================================================================
# Random Fixtures
# =============================================================================


@pytest.fixture
def seeded_random():
    """
    Seed random for deterministic test results.

    Resets random state after test to avoid affecting other tests.
    """
    original_state = random.getstate()
    random.seed(42)
    yield
    random.setstate(original_state)


# =============================================================================
# External Service Mocks (E2E-extensible)
# =============================================================================


@pytest.fixture
def mock_openai_client(request, mocker):
    """
    Mock OpenAI client for unit tests.

    For E2E tests marked with @pytest.mark.e2e, returns None to allow
    the service to use the real client.

    Usage in tests:
        def test_tutor(mock_openai_client):
            mock_openai_client.chat.completions.create.return_value = ...
    """
    if request.node.get_closest_marker("e2e"):
        yield None
        return

    mock_client = MagicMock()

    # Mock chat completions
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Test response"))]
    mock_completion.id = "test_response_id"
    mock_completion.model = "gpt-4o-mini"
    mock_completion.usage = MagicMock(prompt_tokens=10, completion_tokens=20, total_tokens=30)

    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    # Patch the OpenAI client in the word tutor service
    mocker.patch("langchain_openai.ChatOpenAI", return_value=mock_client)

    yield mock_client


@pytest.fixture
def mock_gemini_client(request, mocker):
    """
    Mock Gemini client for unit tests.

    For E2E tests marked with @pytest.mark.e2e, returns None to allow
    the service to use the real client.
    """
    if request.node.get_closest_marker("e2e"):
        yield None
        return

    mock_client = MagicMock()

    # Mock image generation response
    mock_image = MagicMock()
    mock_image.data = b"fake_image_bytes"
    mock_image.mime_type = "image/png"

    mock_response = MagicMock()
    mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_image]))]

    mock_model = MagicMock()
    mock_model.generate_content = MagicMock(return_value=mock_response)
    mock_client.models.generate_content = mock_model.generate_content

    mocker.patch("google.genai.Client", return_value=mock_client)

    yield mock_client


@pytest.fixture
def mock_supabase_storage(request, mocker):
    """
    Mock Supabase storage client for unit tests.

    For E2E tests marked with @pytest.mark.e2e, returns None to allow
    the service to use the real client.
    """
    if request.node.get_closest_marker("e2e"):
        yield None
        return

    mock_client = MagicMock()

    # Mock storage upload
    mock_storage = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.upload = MagicMock(return_value=None)
    mock_storage.from_ = MagicMock(return_value=mock_bucket)
    mock_client.storage = mock_storage

    mocker.patch(
        "app.services.supabase_storage_service.get_supabase_admin_client",
        return_value=mock_client,
    )

    yield mock_client


@pytest.fixture
def mock_supabase_auth(mocker):
    """Mock Supabase auth client for tests that don't need real auth."""
    mock_client = MagicMock()
    mock_auth = MagicMock()
    mock_auth.get_user = AsyncMock(return_value=MagicMock(user=MagicMock(id="test-user-id")))
    mock_client.auth = mock_auth

    mocker.patch("app.core.security.get_supabase_client", return_value=mock_client)

    yield mock_client


# =============================================================================
# Factory Fixtures
# =============================================================================


@pytest.fixture
def profile_factory(db_session):
    """Factory fixture for creating Profile instances."""
    from tests.factories.profile_factory import ProfileFactory

    ProfileFactory._meta.sqlalchemy_session = db_session
    return ProfileFactory


@pytest.fixture
def vocabulary_card_factory(db_session):
    """Factory fixture for creating VocabularyCard instances."""
    from tests.factories.vocabulary_card_factory import VocabularyCardFactory

    VocabularyCardFactory._meta.sqlalchemy_session = db_session
    return VocabularyCardFactory


@pytest.fixture
def user_card_progress_factory(db_session):
    """Factory fixture for creating UserCardProgress instances."""
    from tests.factories.user_card_progress_factory import UserCardProgressFactory

    UserCardProgressFactory._meta.sqlalchemy_session = db_session
    return UserCardProgressFactory


@pytest.fixture
def deck_factory(db_session):
    """Factory fixture for creating Deck instances."""
    from tests.factories.deck_factory import DeckFactory

    DeckFactory._meta.sqlalchemy_session = db_session
    return DeckFactory


@pytest.fixture
def study_session_factory(db_session):
    """Factory fixture for creating StudySession instances."""
    from tests.factories.study_session_factory import StudySessionFactory

    StudySessionFactory._meta.sqlalchemy_session = db_session
    return StudySessionFactory


@pytest.fixture
def wrong_answer_factory(db_session):
    """Factory fixture for creating WrongAnswer instances."""
    from tests.factories.wrong_answer_factory import WrongAnswerFactory

    WrongAnswerFactory._meta.sqlalchemy_session = db_session
    return WrongAnswerFactory


@pytest.fixture
def word_tutor_thread_factory(db_session):
    """Factory fixture for creating WordTutorThread instances."""
    from tests.factories.word_tutor_factory import WordTutorThreadFactory

    WordTutorThreadFactory._meta.sqlalchemy_session = db_session
    return WordTutorThreadFactory


@pytest.fixture
def word_tutor_message_factory(db_session):
    """Factory fixture for creating WordTutorMessage instances."""
    from tests.factories.word_tutor_factory import WordTutorMessageFactory

    WordTutorMessageFactory._meta.sqlalchemy_session = db_session
    return WordTutorMessageFactory


# =============================================================================
# API Test Fixtures
# =============================================================================


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


@pytest.fixture
def api_client(mock_profile, db_session):
    """
    Create a FastAPI TestClient with mocked authentication.

    This fixture overrides:
    - CurrentActiveProfile dependency to return mock_profile
    - get_session dependency to return the test db_session
    """
    from app.core.dependencies import get_current_active_profile
    from app.database import get_session
    from app.main import app

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
def unauthenticated_client(db_session):
    """Create a FastAPI TestClient without authentication mocking."""
    from app.database import get_session
    from app.main import app

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides.clear()
