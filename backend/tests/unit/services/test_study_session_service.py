"""Tests for StudySessionService."""

from uuid import uuid4

import pytest
from freezegun import freeze_time

from app.core.exceptions import NotFoundError, ValidationError
from app.models import QuizType, SessionStatus
from app.services.study_session_service import StudySessionService
from tests.factories.deck_factory import DeckFactory
from tests.factories.profile_factory import ProfileFactory
from tests.factories.study_session_factory import StudySessionFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory


class TestPreviewSession:
    """Tests for session preview functionality."""

    async def test_preview_session_basic(self, db_session):
        """Test basic session preview."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        # Create new cards
        for _ in range(10):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        result = await StudySessionService.preview_session(
            db_session, profile.id, total_cards=5, review_ratio=0.5
        )

        assert result.available.new_cards == 10
        assert result.allocation.total > 0

    async def test_preview_session_validation_total_cards(self, db_session):
        """Test validation for total_cards parameter."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(ValidationError):
            await StudySessionService.preview_session(
                db_session, profile.id, total_cards=0, review_ratio=0.5
            )

        with pytest.raises(ValidationError):
            await StudySessionService.preview_session(
                db_session, profile.id, total_cards=200, review_ratio=0.5
            )

    async def test_preview_session_validation_review_ratio(self, db_session):
        """Test validation for review_ratio parameter."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(ValidationError):
            await StudySessionService.preview_session(
                db_session, profile.id, total_cards=10, review_ratio=-0.1
            )

        with pytest.raises(ValidationError):
            await StudySessionService.preview_session(
                db_session, profile.id, total_cards=10, review_ratio=1.5
            )

    async def test_preview_session_no_profile(self, db_session):
        """Test preview with non-existent profile."""
        result = await StudySessionService.preview_session(
            db_session, uuid4(), total_cards=10, review_ratio=0.5
        )

        assert result.available.new_cards == 0
        assert "프로필을 찾을 수 없습니다" in result.message

    async def test_preview_session_no_cards_available(self, db_session):
        """Test preview when no cards are available."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        # No cards created

        result = await StudySessionService.preview_session(
            db_session, profile.id, total_cards=10, review_ratio=0.5
        )

        assert result.available.new_cards == 0
        assert result.available.review_cards == 0
        assert "학습 가능한 카드가 없습니다" in result.message

    async def test_preview_session_with_selected_decks(self, db_session):
        """Test preview with specific selected decks (not all decks)."""
        from tests.factories.user_selected_deck_factory import UserSelectedDeckFactory

        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)
        deck1 = await DeckFactory.create_async(db_session, is_public=True)
        deck2 = await DeckFactory.create_async(db_session, is_public=True)

        # Create cards in both decks
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck1.id)
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck2.id)

        # Only select deck1
        await UserSelectedDeckFactory.create_async(db_session, user_id=profile.id, deck_id=deck1.id)

        result = await StudySessionService.preview_session(
            db_session, profile.id, total_cards=10, review_ratio=0.5
        )

        # Should only see cards from selected deck (5 cards, not 10)
        assert result.available.new_cards == 5


class TestStartSession:
    """Tests for session start functionality."""

    async def test_start_session(self, db_session, seeded_random):
        """Test starting a new session."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        # Create cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        result = await StudySessionService.start_session(
            db_session, profile.id, use_profile_ratio=True
        )

        assert result.session_id is not None
        assert result.total_cards > 0
        assert result.started_at is not None

    async def test_start_session_with_custom_limits(self, db_session, seeded_random):
        """Test starting session with custom card limits."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        # Create cards
        for _ in range(10):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        result = await StudySessionService.start_session(
            db_session,
            profile.id,
            new_cards_limit=3,
            review_cards_limit=5,
            use_profile_ratio=False,
        )

        assert result.session_id is not None
        # new_cards_limit should be respected
        assert result.new_cards_count <= 3

    async def test_start_session_with_cards(self, db_session, seeded_random):
        """Test starting session with specific card IDs."""
        profile = await ProfileFactory.create_async(db_session)

        # Create cards
        card_ids = []
        for _ in range(5):
            card = await VocabularyCardFactory.create_async(db_session)
            card_ids.append(card.id)

        result = await StudySessionService.start_session_with_cards(
            db_session, profile.id, card_ids
        )

        assert result.session_id is not None
        assert result.total_cards == 5
        assert result.new_cards_count == 0
        assert result.review_cards_count == 5


class TestGetNextCard:
    """Tests for getting next card in session."""

    async def test_get_next_card(self, db_session):
        """Test getting next card from session."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            current_index=0,
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.get_next_card(
            db_session, profile.id, session.id, QuizType.WORD_TO_MEANING
        )

        assert result.card is not None
        assert result.card.id == card.id

    async def test_get_next_card_session_complete(self, db_session):
        """Test getting card when all cards completed."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            current_index=1,  # Already at the end
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.get_next_card(
            db_session, profile.id, session.id, QuizType.WORD_TO_MEANING
        )

        assert result.card is None
        assert result.cards_remaining == 0

    async def test_get_next_card_session_not_found(self, db_session):
        """Test error when session not found."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(NotFoundError):
            await StudySessionService.get_next_card(
                db_session, profile.id, uuid4(), QuizType.WORD_TO_MEANING
            )

    async def test_get_next_card_wrong_user(self, db_session):
        """Test error when session belongs to different user."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_ids=[card.id],
        )

        with pytest.raises(ValidationError):
            await StudySessionService.get_next_card(
                db_session, profile2.id, session.id, QuizType.WORD_TO_MEANING
            )

    async def test_get_next_card_inactive_session(self, db_session):
        """Test error when session is not active."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.COMPLETED,
        )

        with pytest.raises(ValidationError):
            await StudySessionService.get_next_card(
                db_session, profile.id, session.id, QuizType.WORD_TO_MEANING
            )


class TestSubmitAnswer:
    """Tests for answer submission."""

    async def test_submit_answer_correct(self, db_session):
        """Test submitting a correct answer."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="사과",
            quiz_type=QuizType.WORD_TO_MEANING.value,
        )

        assert result.is_correct is True
        assert result.score == 100
        assert result.hint_penalty == 0

    async def test_submit_answer_wrong(self, db_session):
        """Test submitting an incorrect answer."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="바나나",
            quiz_type=QuizType.WORD_TO_MEANING.value,
        )

        assert result.is_correct is False
        assert result.score == 0

    async def test_submit_answer_with_hints(self, db_session):
        """Test answer with hint penalty."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="사과",
            hint_count=2,
            quiz_type=QuizType.WORD_TO_MEANING.value,
        )

        assert result.is_correct is True
        assert result.hint_penalty == 40  # 2 hints * 20 penalty
        assert result.score == 60  # 100 - 40

    async def test_submit_answer_revealed(self, db_session):
        """Test answer when reveal button was used."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="사과",
            revealed_answer=True,
            quiz_type=QuizType.WORD_TO_MEANING.value,
        )

        # Even though answer matches, revealed=True means score is 0
        assert result.score == 0


class TestCompleteSession:
    """Tests for session completion."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_complete_session(self, db_session):
        """Test completing a session."""
        profile = await ProfileFactory.create_async(
            db_session,
            daily_goal=10,
            current_streak=0,
            last_study_date=None,
        )
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
            correct_count=5,
            wrong_count=2,
        )

        result = await StudySessionService.complete_session(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            duration_seconds=300,
        )

        assert result.session_summary.total_cards == 7
        assert result.session_summary.correct == 5
        assert result.session_summary.wrong == 2
        assert result.session_summary.duration_seconds == 300

        # Check streak started
        assert result.streak.current_streak == 1
        assert result.streak.streak_status == "started"

        # Check XP
        assert result.xp.base_xp == 50  # 5 correct * 10
        # 5/7 = 71.4% accuracy, no bonus
        assert result.xp.bonus_xp == 0

    async def test_complete_session_with_bonus(self, db_session):
        """Test completing session with accuracy bonus."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
            correct_count=9,
            wrong_count=1,
        )

        result = await StudySessionService.complete_session(
            db_session,
            user_id=profile.id,
            session_id=session.id,
        )

        # 90% accuracy = bonus
        assert result.xp.bonus_xp == 50

    async def test_complete_session_not_found(self, db_session):
        """Test completing non-existent session."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(NotFoundError):
            await StudySessionService.complete_session(db_session, profile.id, uuid4())

    async def test_complete_session_already_completed(self, db_session):
        """Test completing an already completed session."""
        profile = await ProfileFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            status=SessionStatus.COMPLETED,
        )

        with pytest.raises(ValidationError):
            await StudySessionService.complete_session(db_session, profile.id, session.id)


class TestSessionStatus:
    """Tests for session status retrieval."""

    async def test_get_session_status(self, db_session):
        """Test getting session status."""
        profile = await ProfileFactory.create_async(db_session, daily_goal=10)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
            current_index=1,
            correct_count=1,
            wrong_count=0,
        )

        result = await StudySessionService.get_session_status(db_session, profile.id, session.id)

        assert result.session_id == session.id
        assert result.status == SessionStatus.ACTIVE.value
        assert result.completed_cards == 1
        assert result.total_cards == 1

    async def test_get_session_status_not_found(self, db_session):
        """Test getting status of non-existent session."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(NotFoundError):
            await StudySessionService.get_session_status(db_session, profile.id, uuid4())


class TestCalculateScore:
    """Tests for score calculation."""

    def test_calculate_score_perfect(self):
        """Test perfect score calculation."""
        score, penalty = StudySessionService._calculate_score(
            is_correct=True, hint_count=0, revealed_answer=False
        )

        assert score == 100
        assert penalty == 0

    def test_calculate_score_with_hints(self):
        """Test score with hint penalty."""
        score, penalty = StudySessionService._calculate_score(
            is_correct=True, hint_count=3, revealed_answer=False
        )

        assert penalty == 60
        assert score == 40

    def test_calculate_score_max_penalty(self):
        """Test score with max hint penalty."""
        score, penalty = StudySessionService._calculate_score(
            is_correct=True, hint_count=10, revealed_answer=False
        )

        assert penalty == 100  # Capped at base_score
        assert score == 0

    def test_calculate_score_wrong_answer(self):
        """Test score for incorrect answer."""
        score, penalty = StudySessionService._calculate_score(
            is_correct=False, hint_count=0, revealed_answer=False
        )

        assert score == 0
        assert penalty == 0

    def test_calculate_score_revealed(self):
        """Test score when answer revealed."""
        score, penalty = StudySessionService._calculate_score(
            is_correct=True, hint_count=0, revealed_answer=True
        )

        assert score == 0
        assert penalty == 0


class TestAbandonSession:
    """Tests for session abandonment."""

    async def test_abandon_session_success(self, db_session):
        """Test successfully abandoning a session."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
            correct_count=2,
            wrong_count=1,
        )

        result = await StudySessionService.abandon_session(
            db_session, profile.id, session.id, save_progress=True
        )

        assert result.session_id == session.id
        assert result.status == "abandoned"
        assert result.summary.completed_cards == 3
        assert result.progress_saved is True
        assert "저장" in result.message

    async def test_abandon_session_not_found(self, db_session):
        """Test abandoning non-existent session."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(NotFoundError):
            await StudySessionService.abandon_session(db_session, profile.id, uuid4())

    async def test_abandon_session_wrong_user(self, db_session):
        """Test abandoning session belonging to another user."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        with pytest.raises(ValidationError):
            await StudySessionService.abandon_session(db_session, profile2.id, session.id)

    async def test_abandon_session_already_completed(self, db_session):
        """Test abandoning already completed session."""
        profile = await ProfileFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            status=SessionStatus.COMPLETED,
        )

        with pytest.raises(ValidationError):
            await StudySessionService.abandon_session(db_session, profile.id, session.id)

    async def test_abandon_session_no_progress_saved(self, db_session):
        """Test abandoning session without saving progress."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.abandon_session(
            db_session, profile.id, session.id, save_progress=False
        )

        assert result.progress_saved is False
        assert "종료" in result.message


class TestGetNewCards:
    """Tests for _get_new_cards helper method."""

    async def test_get_new_cards_select_all_decks(self, db_session):
        """Test getting new cards when select_all_decks is True."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        # Create new cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        result = await StudySessionService._get_new_cards(db_session, profile.id, limit=10)

        assert len(result) == 5

    async def test_get_new_cards_with_selected_decks(self, db_session):
        """Test getting new cards with specific selected decks."""
        from tests.factories.user_selected_deck_factory import UserSelectedDeckFactory

        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)
        deck1 = await DeckFactory.create_async(db_session, is_public=True)
        deck2 = await DeckFactory.create_async(db_session, is_public=True)

        # Create cards in both decks
        for _ in range(3):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck1.id)
        for _ in range(3):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck2.id)

        # Only select deck1
        await UserSelectedDeckFactory.create_async(db_session, user_id=profile.id, deck_id=deck1.id)

        result = await StudySessionService._get_new_cards(db_session, profile.id, limit=10)

        # Should only get cards from deck1
        assert len(result) == 3

    async def test_get_new_cards_no_profile(self, db_session):
        """Test getting new cards with non-existent profile."""
        result = await StudySessionService._get_new_cards(db_session, uuid4(), limit=10)

        assert result == []


class TestGetDueReviewCards:
    """Tests for _get_due_review_cards helper method."""

    async def test_get_due_cards_with_selected_decks_scope(self, db_session):
        """Test getting due cards with selected_decks_only review scope."""
        from datetime import datetime

        from tests.factories.user_card_progress_factory import UserCardProgressFactory
        from tests.factories.user_selected_deck_factory import UserSelectedDeckFactory

        profile = await ProfileFactory.create_async(
            db_session, select_all_decks=False, review_scope="selected_decks_only"
        )
        deck = await DeckFactory.create_async(db_session, is_public=True)
        card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        # Select the deck
        await UserSelectedDeckFactory.create_async(db_session, user_id=profile.id, deck_id=deck.id)

        # Create progress with past due date
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            next_review_date=datetime(2020, 1, 1),
        )

        result = await StudySessionService._get_due_review_cards(db_session, profile.id, limit=10)

        assert len(result) >= 1


class TestCalculateCardLimits:
    """Tests for _calculate_card_limits helper method."""

    def test_calculate_limits_normal_mode(self):
        """Test card limits calculation in normal mode."""
        from app.models import Profile

        profile = Profile(
            id=uuid4(),
            daily_goal=20,
            review_ratio_mode="normal",
            min_new_ratio=0.25,
        )

        new_limit, review_limit = StudySessionService._calculate_card_limits(profile)

        assert new_limit == 5  # 20 * 0.25
        assert review_limit == 15  # 20 * 0.75

    def test_calculate_limits_custom_mode(self):
        """Test card limits calculation in custom mode."""
        from app.models import Profile

        profile = Profile(
            id=uuid4(),
            daily_goal=20,
            review_ratio_mode="custom",
            custom_review_ratio=0.6,
        )

        new_limit, review_limit = StudySessionService._calculate_card_limits(profile)

        assert new_limit == 8  # 20 * 0.4
        assert review_limit == 12  # 20 * 0.6

    def test_calculate_limits_max_caps(self):
        """Test card limits are capped at maximum values."""
        from app.models import Profile

        profile = Profile(
            id=uuid4(),
            daily_goal=200,  # Very high daily goal
            review_ratio_mode="normal",
            min_new_ratio=0.5,
        )

        new_limit, review_limit = StudySessionService._calculate_card_limits(profile)

        assert new_limit <= 50  # Max new cards
        assert review_limit <= 100  # Max review cards


class TestGenerateStreakMessage:
    """Tests for _generate_streak_message helper method."""

    def test_streak_message_new_record(self):
        """Test streak message when new record is achieved."""
        result = {"is_new_record": True, "longest_streak": 10}
        message = StudySessionService._generate_streak_message(result)

        assert "최고 기록" in message
        assert "10" in message

    def test_streak_message_continued(self):
        """Test streak message for continued streak."""
        result = {
            "is_new_record": False,
            "streak_status": "continued",
            "current_streak": 5,
        }
        message = StudySessionService._generate_streak_message(result)

        assert "연속" in message
        assert "5" in message

    def test_streak_message_started(self):
        """Test streak message for started streak."""
        result = {"is_new_record": False, "streak_status": "started"}
        message = StudySessionService._generate_streak_message(result)

        assert "시작" in message

    def test_streak_message_broken(self):
        """Test streak message for broken streak."""
        result = {"is_new_record": False, "streak_status": "broken"}
        message = StudySessionService._generate_streak_message(result)

        assert "다시" in message


class TestGetOverview:
    """Tests for get_overview method."""

    async def test_get_overview(self, db_session):
        """Test getting study overview."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        # Create new cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        result = await StudySessionService.get_overview(db_session, profile.id)

        assert result.new_cards_count == 5
        assert result.review_cards_count == 0
        assert result.total_available == 5

    async def test_get_overview_with_review_cards(self, db_session):
        """Test overview with cards due for review."""
        from datetime import datetime

        from tests.factories.user_card_progress_factory import UserCardProgressFactory

        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)
        deck = await DeckFactory.create_async(db_session, is_public=True)
        card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        # Create progress with past due date
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            next_review_date=datetime(2020, 1, 1),
        )

        result = await StudySessionService.get_overview(db_session, profile.id)

        assert result.review_cards_count >= 1
        assert len(result.due_cards) >= 1


class TestGenerateClozeQuestion:
    """Tests for _generate_cloze_question helper method."""

    def test_cloze_from_cloze_sentences(self):
        """Test cloze generation from pre-generated cloze_sentences."""
        from app.models import VocabularyCard

        card = VocabularyCard(
            id=1,
            english_word="apple",
            korean_meaning="사과",
            cloze_sentences=[
                {
                    "sentence_with_blank": "I like ______.",
                    "hint": "과일",
                    "answer": "apple",
                    "blank_position": 7,
                }
            ],
        )

        result = StudySessionService._generate_cloze_question(card)

        assert result is not None
        assert result.sentence == "I like ______."
        assert result.answer == "apple"

    def test_cloze_from_example_sentences(self):
        """Test cloze generation from example_sentences."""
        from app.models import VocabularyCard

        card = VocabularyCard(
            id=1,
            english_word="apple",
            korean_meaning="사과",
            cloze_sentences=None,
            example_sentences=[{"en": "I like apple very much."}],
            part_of_speech="noun",
        )

        result = StudySessionService._generate_cloze_question(card)

        assert result is not None
        assert "______" in result.sentence
        assert result.answer == "apple"

    def test_cloze_no_data(self):
        """Test cloze generation with no cloze data."""
        from app.models import VocabularyCard

        card = VocabularyCard(
            id=1,
            english_word="apple",
            korean_meaning="사과",
            cloze_sentences=None,
            example_sentences=None,
        )

        result = StudySessionService._generate_cloze_question(card)

        assert result is None


class TestGetNextCardErrors:
    """Additional tests for get_next_card error paths."""

    async def test_get_next_card_card_not_found(self, db_session):
        """Test get_next_card when card doesn't exist in DB."""
        profile = await ProfileFactory.create_async(db_session)

        # Create session with non-existent card_id
        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[99999],  # Non-existent card
            status=SessionStatus.ACTIVE,
            current_index=0,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await StudySessionService.get_next_card(
                db_session, profile.id, session.id, QuizType.WORD_TO_MEANING
            )
        assert "Card" in str(exc_info.value.message)


class TestSubmitAnswerErrors:
    """Additional tests for submit_answer error paths."""

    async def test_submit_answer_session_not_found(self, db_session):
        """Test submit_answer with non-existent session."""
        profile = await ProfileFactory.create_async(db_session)

        with pytest.raises(NotFoundError) as exc_info:
            await StudySessionService.submit_answer(
                db_session,
                user_id=profile.id,
                session_id=uuid4(),
                card_id=1,
                user_answer="test",
            )
        assert "Session" in str(exc_info.value.message)

    async def test_submit_answer_wrong_user(self, db_session):
        """Test submit_answer with session belonging to different user."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        with pytest.raises(ValidationError) as exc_info:
            await StudySessionService.submit_answer(
                db_session,
                user_id=profile2.id,
                session_id=session.id,
                card_id=card.id,
                user_answer="test",
            )
        assert "does not belong" in str(exc_info.value.message)

    async def test_submit_answer_session_not_active(self, db_session):
        """Test submit_answer with completed session."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.COMPLETED,
        )

        with pytest.raises(ValidationError) as exc_info:
            await StudySessionService.submit_answer(
                db_session,
                user_id=profile.id,
                session_id=session.id,
                card_id=card.id,
                user_answer="test",
            )
        assert "not active" in str(exc_info.value.message)

    async def test_submit_answer_card_not_in_session(self, db_session):
        """Test submit_answer with card not in session."""
        profile = await ProfileFactory.create_async(db_session)
        card1 = await VocabularyCardFactory.create_async(db_session)
        card2 = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card1.id],  # Only card1 in session
            status=SessionStatus.ACTIVE,
        )

        with pytest.raises(ValidationError) as exc_info:
            await StudySessionService.submit_answer(
                db_session,
                user_id=profile.id,
                session_id=session.id,
                card_id=card2.id,  # card2 not in session
                user_answer="test",
            )
        assert "not in this session" in str(exc_info.value.message)

    async def test_submit_answer_card_not_found(self, db_session):
        """Test submit_answer with non-existent card."""
        profile = await ProfileFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[99999],  # Non-existent card ID
            status=SessionStatus.ACTIVE,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await StudySessionService.submit_answer(
                db_session,
                user_id=profile.id,
                session_id=session.id,
                card_id=99999,
                user_answer="test",
            )
        assert "Card" in str(exc_info.value.message)


class TestFormatCard:
    """Tests for _format_card method."""

    async def test_format_card_meaning_to_word(self, db_session):
        """Test formatting card for MEANING_TO_WORD quiz."""
        # Create cards with same difficulty
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
            part_of_speech="noun",
            difficulty_level="beginner",
        )
        # Create distractor cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(
                db_session, difficulty_level="beginner", part_of_speech="noun"
            )

        result = await StudySessionService._format_card(
            db_session, card, QuizType.MEANING_TO_WORD, is_new=True
        )

        assert result.quiz_type == QuizType.MEANING_TO_WORD
        assert "(noun)" in result.question
        assert result.options is not None
        assert "apple" in result.options

    async def test_format_card_cloze_fallback(self, db_session):
        """Test cloze format falls back to word_to_meaning when no cloze data."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
            cloze_sentences=None,
            example_sentences=None,
        )
        # Create distractor cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session)

        result = await StudySessionService._format_card(
            db_session, card, QuizType.CLOZE, is_new=True
        )

        # Should fallback to word_to_meaning style
        assert result.question == "apple"
        assert result.options is not None

    async def test_format_card_listening(self, db_session):
        """Test formatting card for LISTENING quiz."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )
        # Create distractor cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session)

        result = await StudySessionService._format_card(
            db_session, card, QuizType.LISTENING, is_new=False
        )

        assert result.quiz_type == QuizType.LISTENING
        assert "🔊" in result.question
        assert result.options is not None

    async def test_format_card_image_to_word_no_image(self, db_session):
        """Test IMAGE_TO_WORD quiz fails without image."""
        from app.core.exceptions import UnprocessableEntityError

        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
            image_url=None,
        )

        with pytest.raises(UnprocessableEntityError):
            await StudySessionService._format_card(
                db_session, card, QuizType.IMAGE_TO_WORD, is_new=True
            )

    async def test_format_card_image_to_word_with_image(self, db_session):
        """Test IMAGE_TO_WORD quiz with image."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
            image_url="https://example.com/apple.jpg",
        )
        # Create distractor cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session)

        result = await StudySessionService._format_card(
            db_session, card, QuizType.IMAGE_TO_WORD, is_new=True
        )

        assert result.quiz_type == QuizType.IMAGE_TO_WORD
        assert "🖼️" in result.question
        assert result.options is not None


class TestGenerateOptions:
    """Tests for _generate_options helper method."""

    async def test_generate_options_fallback(self, db_session):
        """Test option generation with fallback when not enough matching candidates."""
        # Create only a few cards (not enough for exact match)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="unique_word",
            korean_meaning="고유한 단어",
            difficulty_level="advanced",
            part_of_speech="noun",
        )
        # Create one card with different difficulty
        await VocabularyCardFactory.create_async(
            db_session,
            difficulty_level="beginner",
            part_of_speech="verb",
        )

        options = await StudySessionService._generate_options(
            db_session,
            correct_answer="고유한 단어",
            quiz_type=QuizType.WORD_TO_MEANING,
            card=card,
            count=4,
        )

        assert "고유한 단어" in options
        # May have less than 4 if not enough cards in DB
        assert len(options) >= 1


class TestCompleteSessionEdgeCases:
    """Tests for edge cases in complete_session."""

    async def test_complete_session_wrong_user(self, db_session):
        """Test completing session belonging to different user."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        with pytest.raises(ValidationError) as exc_info:
            await StudySessionService.complete_session(db_session, profile2.id, session.id)
        assert "does not belong" in str(exc_info.value.message)

    async def test_complete_session_profile_not_found(self, db_session):
        """Test completing session when profile doesn't exist."""
        # This is tricky - we need a session that exists but profile deleted
        # Create profile, create session, then use different user_id that matches session
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        # Delete the profile to simulate profile not found
        await db_session.delete(profile)
        await db_session.commit()

        with pytest.raises(NotFoundError) as exc_info:
            await StudySessionService.complete_session(db_session, profile.id, session.id)
        assert "Profile" in str(exc_info.value.message)


class TestGetSessionStatusEdgeCases:
    """Tests for edge cases in get_session_status."""

    async def test_get_session_status_wrong_user(self, db_session):
        """Test getting session status for different user's session."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        with pytest.raises(ValidationError) as exc_info:
            await StudySessionService.get_session_status(db_session, profile2.id, session.id)
        assert "does not belong" in str(exc_info.value.message)

    async def test_get_session_status_profile_not_found(self, db_session):
        """Test getting session status when profile doesn't exist."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        # Delete profile
        await db_session.delete(profile)
        await db_session.commit()

        with pytest.raises(NotFoundError) as exc_info:
            await StudySessionService.get_session_status(db_session, profile.id, session.id)
        assert "Profile" in str(exc_info.value.message)


class TestFormatCardDefault:
    """Tests for default case in _format_card."""

    async def test_format_card_word_to_meaning(self, db_session):
        """Test _format_card with WORD_TO_MEANING quiz type."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="test",
            korean_meaning="테스트",
        )
        # Create distractor cards
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session)

        result = await StudySessionService._format_card(
            db_session, card, QuizType.WORD_TO_MEANING, is_new=True
        )

        assert result.question == "test"
        assert result.quiz_type == QuizType.WORD_TO_MEANING


class TestSubmitAnswerFeedback:
    """Tests for submit_answer feedback messages."""

    async def test_submit_answer_feedback_with_hint(self, db_session):
        """Test feedback message includes hint count."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="사과",
            hint_count=1,
        )

        assert result.is_correct is True
        assert "힌트" in result.feedback
        assert "1" in result.feedback

    async def test_submit_answer_feedback_revealed(self, db_session):
        """Test feedback message when answer was revealed."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="사과",
            revealed_answer=True,
        )

        assert "정답:" in result.feedback
        assert "사과" in result.feedback
        assert "apple" in result.feedback

    async def test_submit_answer_feedback_wrong(self, db_session):
        """Test feedback message for wrong answer."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="apple",
            korean_meaning="사과",
        )

        session = await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            card_ids=[card.id],
            status=SessionStatus.ACTIVE,
        )

        result = await StudySessionService.submit_answer(
            db_session,
            user_id=profile.id,
            session_id=session.id,
            card_id=card.id,
            user_answer="바나나",
        )

        assert result.is_correct is False
        assert "틀렸습니다" in result.feedback
        assert "정답:" in result.feedback
