"""Tests for WordTutorService."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import ExternalServiceError, NotFoundError, ValidationError
from app.models import ChatRole, SessionStatus
from app.models.schemas.word_tutor import TutorMessageRequest
from app.services.word_tutor_service import WordTutorService
from tests.factories.profile_factory import ProfileFactory
from tests.factories.study_session_factory import StudySessionFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory
from tests.factories.word_tutor_factory import WordTutorMessageFactory, WordTutorThreadFactory


class TestWordTutorValidation:
    """Tests for validation methods."""

    async def test_validate_session_and_card_success(self, db_session):
        """Test successful validation of session and card."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        # Should not raise
        await WordTutorService._validate_session_and_card(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

    async def test_validate_session_not_found(self, db_session):
        """Test validation with non-existent session."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(NotFoundError):
            await WordTutorService._validate_session_and_card(
                db_session,
                user_id=profile.id,
                session_id=uuid4(),
                card_id=1,
            )

    async def test_validate_session_wrong_user(self, db_session):
        """Test validation when session belongs to different user."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_ids=[card.id],
        )

        with pytest.raises(ValidationError):
            await WordTutorService._validate_session_and_card(
                db_session,
                user_id=profile2.id,
                session_id=session.id,
                card_id=card.id,
            )

    async def test_validate_card_not_in_session(self, db_session):
        """Test validation when card is not in session."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        other_card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
        )

        with pytest.raises(ValidationError):
            await WordTutorService._validate_session_and_card(
                db_session,
                user_id=profile.id,
                session_id=session.id,
                card_id=other_card.id,
            )


class TestGetOrCreateThread:
    """Tests for thread creation/retrieval."""

    async def test_create_new_thread(self, db_session):
        """Test creating a new thread."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        thread = await WordTutorService._get_or_create_thread(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        assert thread is not None
        assert thread.user_id == profile.id
        assert thread.session_id == session.id
        assert thread.card_id == card.id

    async def test_get_existing_thread(self, db_session):
        """Test retrieving existing thread."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        # Create thread first
        existing_thread = await WordTutorThreadFactory.create_async(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        # Should return existing thread
        thread = await WordTutorService._get_or_create_thread(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        assert thread.id == existing_thread.id


class TestGetMessages:
    """Tests for message retrieval."""

    async def test_get_messages(self, db_session):
        """Test getting messages for a thread."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        thread = await WordTutorThreadFactory.create_async(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        # Create messages
        for i in range(3):
            await WordTutorMessageFactory.create_async(
                db_session,
                thread_id=thread.id,
                role=ChatRole.USER if i % 2 == 0 else ChatRole.ASSISTANT,
                content=f"Message {i}",
            )

        messages = await WordTutorService._get_messages(db_session, thread_id=thread.id)

        assert len(messages) == 3

    async def test_get_messages_with_limit(self, db_session):
        """Test message retrieval with limit."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        thread = await WordTutorThreadFactory.create_async(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        # Create 10 messages
        for i in range(10):
            await WordTutorMessageFactory.create_async(
                db_session,
                thread_id=thread.id,
                content=f"Message {i}",
            )

        messages = await WordTutorService._get_messages(db_session, thread_id=thread.id, limit=5)

        assert len(messages) == 5


class TestStartTutor:
    """Tests for starting tutor session."""

    async def test_start_tutor_no_api_key(self, db_session, mocker):
        """Test start fails without API key."""
        mocker.patch("app.services.word_tutor_service.settings.openai_api_key", None)

        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        with pytest.raises(ExternalServiceError):
            await WordTutorService.start(
                db_session,
                user_id=profile.id,
                session_id=session.id,
                card_id=card.id,
            )

    async def test_start_tutor_success(self, db_session, mocker):
        """Test successful tutor start with mocked graph."""
        mocker.patch("app.services.word_tutor_service.settings.openai_api_key", "test_key")

        # Mock the START_GRAPH
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "starter_questions": [
                "이 단어의 어원은 무엇인가요?",
                "비슷한 의미의 단어는?",
            ]
        }
        mocker.patch("app.services.word_tutor_service.START_GRAPH", mock_graph)

        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        result = await WordTutorService.start(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        assert result.thread_id is not None
        assert len(result.starter_questions) == 2


class TestSendMessage:
    """Tests for sending messages."""

    async def test_send_message_success(self, db_session, mocker):
        """Test successful message send with mocked graph."""
        mocker.patch("app.services.word_tutor_service.settings.openai_api_key", "test_key")

        # Mock the MESSAGE_GRAPH
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "assistant_answer": "이 단어는 라틴어에서 유래했습니다.",
            "follow_up_questions": ["더 알고 싶은 것이 있나요?"],
        }
        mocker.patch("app.services.word_tutor_service.MESSAGE_GRAPH", mock_graph)

        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        request = TutorMessageRequest(message="이 단어의 어원은 무엇인가요?")

        result = await WordTutorService.send_message(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            request=request,
        )

        assert result.thread_id is not None
        assert "라틴어" in result.assistant_message
        assert len(result.follow_up_questions) == 1


class TestHistory:
    """Tests for retrieving conversation history."""

    async def test_get_history(self, db_session):
        """Test getting conversation history."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(
            db_session, user_id=profile.id, card_ids=[card.id]
        )

        # Create thread with messages
        thread = await WordTutorThreadFactory.create_async(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        await WordTutorMessageFactory.create_async(
            db_session,
            thread_id=thread.id,
            role=ChatRole.USER,
            content="질문입니다",
        )
        await WordTutorMessageFactory.create_async(
            db_session,
            thread_id=thread.id,
            role=ChatRole.ASSISTANT,
            content="답변입니다",
        )

        result = await WordTutorService.history(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
        )

        assert result.thread_id == thread.id
        assert len(result.messages) == 2
