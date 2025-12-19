"""Tests for WrongAnswerService."""

from app.models import QuizType
from app.services.wrong_answer_service import WrongAnswerService
from tests.factories.profile_factory import ProfileFactory
from tests.factories.study_session_factory import StudySessionFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory
from tests.factories.wrong_answer_factory import WrongAnswerFactory


class TestCreateWrongAnswer:
    """Tests for creating wrong answer records."""

    async def test_create_wrong_answer(self, db_session):
        """Test creating a new wrong answer record."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        session = await StudySessionFactory.create_async(db_session, user_id=profile.id)

        wrong_answer = await WrongAnswerService.create_wrong_answer(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            session_id=session.id,
            user_answer="wrong",
            correct_answer="correct",
            quiz_type=QuizType.WORD_TO_MEANING.value,
        )

        assert wrong_answer is not None
        assert wrong_answer.id is not None
        assert wrong_answer.user_id == profile.id
        assert wrong_answer.card_id == card.id
        assert wrong_answer.user_answer == "wrong"
        assert wrong_answer.correct_answer == "correct"
        assert wrong_answer.reviewed is False

    async def test_create_wrong_answer_without_session(self, db_session):
        """Test creating wrong answer without session_id."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        wrong_answer = await WrongAnswerService.create_wrong_answer(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            session_id=None,
            user_answer="wrong",
            correct_answer="correct",
            quiz_type=QuizType.CLOZE.value,
        )

        assert wrong_answer is not None
        assert wrong_answer.session_id is None


class TestGetWrongAnswers:
    """Tests for retrieving wrong answers."""

    async def test_get_wrong_answers(self, db_session):
        """Test getting wrong answer list."""
        profile = await ProfileFactory.create_async(db_session)

        # Create cards and wrong answers
        for _i in range(5):
            card = await VocabularyCardFactory.create_async(db_session)
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
            )

        result = await WrongAnswerService.get_wrong_answers(db_session, user_id=profile.id)

        assert result.total == 5
        assert len(result.wrong_answers) == 5

    async def test_get_wrong_answers_pagination(self, db_session):
        """Test wrong answers pagination."""
        profile = await ProfileFactory.create_async(db_session)

        # Create 15 wrong answers
        for _i in range(15):
            card = await VocabularyCardFactory.create_async(db_session)
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
            )

        # Get first page
        first_page = await WrongAnswerService.get_wrong_answers(
            db_session, user_id=profile.id, limit=10, offset=0
        )
        assert len(first_page.wrong_answers) == 10
        assert first_page.total == 15

        # Get second page
        second_page = await WrongAnswerService.get_wrong_answers(
            db_session, user_id=profile.id, limit=10, offset=10
        )
        assert len(second_page.wrong_answers) == 5

    async def test_filter_by_reviewed(self, db_session):
        """Test filtering by reviewed status."""
        profile = await ProfileFactory.create_async(db_session)

        # Create reviewed and unreviewed answers
        for _i in range(3):
            card = await VocabularyCardFactory.create_async(db_session)
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                reviewed=True,
            )

        for _i in range(2):
            card = await VocabularyCardFactory.create_async(db_session)
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                reviewed=False,
            )

        # Get only unreviewed
        unreviewed = await WrongAnswerService.get_wrong_answers(
            db_session, user_id=profile.id, reviewed=False
        )
        assert unreviewed.total == 2
        assert unreviewed.unreviewed_count == 2

        # Get only reviewed
        reviewed = await WrongAnswerService.get_wrong_answers(
            db_session, user_id=profile.id, reviewed=True
        )
        assert reviewed.total == 3

    async def test_filter_by_quiz_type(self, db_session):
        """Test filtering by quiz type."""
        profile = await ProfileFactory.create_async(db_session)

        # Create answers with different quiz types
        card1 = await VocabularyCardFactory.create_async(db_session)
        await WrongAnswerFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card1.id,
            quiz_type=QuizType.CLOZE.value,
        )

        card2 = await VocabularyCardFactory.create_async(db_session)
        await WrongAnswerFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card2.id,
            quiz_type=QuizType.WORD_TO_MEANING.value,
        )

        # Filter by cloze
        cloze_results = await WrongAnswerService.get_wrong_answers(
            db_session, user_id=profile.id, quiz_type=QuizType.CLOZE.value
        )
        assert cloze_results.total == 1


class TestMarkReviewed:
    """Tests for marking wrong answers as reviewed."""

    async def test_mark_as_reviewed(self, db_session):
        """Test marking a wrong answer as reviewed."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        wrong_answer = await WrongAnswerFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            reviewed=False,
        )

        result = await WrongAnswerService.mark_reviewed(
            db_session, user_id=profile.id, wrong_answer_id=wrong_answer.id
        )

        assert result is not None
        assert result.reviewed is True
        assert result.reviewed_at is not None

    async def test_mark_reviewed_not_found(self, db_session):
        """Test marking non-existent wrong answer."""
        profile = await ProfileFactory.create_async(db_session)

        result = await WrongAnswerService.mark_reviewed(
            db_session, user_id=profile.id, wrong_answer_id=99999
        )

        assert result is None

    async def test_mark_reviewed_wrong_user(self, db_session):
        """Test marking another user's wrong answer."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        # Create wrong answer for profile1
        wrong_answer = await WrongAnswerFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_id=card.id,
            reviewed=False,
        )

        # Try to mark as profile2
        result = await WrongAnswerService.mark_reviewed(
            db_session, user_id=profile2.id, wrong_answer_id=wrong_answer.id
        )

        assert result is None  # Should not be able to mark other user's answer


class TestGetUnreviewedCardIds:
    """Tests for getting unreviewed card IDs."""

    async def test_get_unreviewed_card_ids(self, db_session):
        """Test getting unique card IDs from unreviewed wrong answers."""
        profile = await ProfileFactory.create_async(db_session)

        # Create unreviewed wrong answers for different cards
        card_ids = []
        for _ in range(5):
            card = await VocabularyCardFactory.create_async(db_session)
            card_ids.append(card.id)
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                reviewed=False,
            )

        result = await WrongAnswerService.get_unreviewed_card_ids(db_session, user_id=profile.id)

        assert len(result) == 5
        for card_id in result:
            assert card_id in card_ids

    async def test_get_unreviewed_card_ids_excludes_reviewed(self, db_session):
        """Test that reviewed wrong answers are excluded."""
        profile = await ProfileFactory.create_async(db_session)

        # Create reviewed wrong answer
        card1 = await VocabularyCardFactory.create_async(db_session)
        await WrongAnswerFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card1.id,
            reviewed=True,
        )

        # Create unreviewed wrong answer
        card2 = await VocabularyCardFactory.create_async(db_session)
        await WrongAnswerFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card2.id,
            reviewed=False,
        )

        result = await WrongAnswerService.get_unreviewed_card_ids(db_session, user_id=profile.id)

        assert len(result) == 1
        assert result[0] == card2.id

    async def test_get_unreviewed_card_ids_distinct(self, db_session):
        """Test that card IDs are unique even with multiple wrong answers."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        # Create multiple wrong answers for the same card
        for _ in range(3):
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                reviewed=False,
            )

        result = await WrongAnswerService.get_unreviewed_card_ids(db_session, user_id=profile.id)

        # Should only return the card ID once
        assert len(result) == 1
        assert result[0] == card.id

    async def test_get_unreviewed_card_ids_limit(self, db_session):
        """Test limit on returned card IDs."""
        profile = await ProfileFactory.create_async(db_session)

        # Create 15 cards with wrong answers
        for _ in range(15):
            card = await VocabularyCardFactory.create_async(db_session)
            await WrongAnswerFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                reviewed=False,
            )

        result = await WrongAnswerService.get_unreviewed_card_ids(
            db_session, user_id=profile.id, limit=5
        )

        assert len(result) == 5
