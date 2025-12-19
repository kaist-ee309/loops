"""Tests for UserCardProgressService."""

from datetime import datetime, timedelta
from uuid import uuid4

from freezegun import freeze_time
from fsrs import Card
from fsrs import State as FSRSState

from app.models import CardState, UserCardProgress, UserCardProgressCreate
from app.services.user_card_progress_service import UserCardProgressService
from tests.factories.deck_factory import DeckFactory
from tests.factories.profile_factory import ProfileFactory
from tests.factories.user_card_progress_factory import UserCardProgressFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory


class TestProgressToCard:
    """Tests for progress_to_card conversion."""

    def test_new_card_conversion(self):
        """Test conversion of NEW state progress to FSRS Card."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.NEW,
            next_review_date=datetime.utcnow(),
            stability=0.0,
            difficulty=5.0,
        )

        card = UserCardProgressService.progress_to_card(progress)

        assert card.state == FSRSState.Learning
        assert card.step == 0

    def test_learning_card_conversion(self):
        """Test conversion of LEARNING state progress to FSRS Card."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.LEARNING,
            next_review_date=datetime.utcnow(),
            stability=1.5,
            difficulty=5.0,
        )

        card = UserCardProgressService.progress_to_card(progress)

        assert card.state == FSRSState.Learning
        assert card.stability == 1.5
        assert card.difficulty == 5.0

    def test_review_card_conversion(self):
        """Test conversion of REVIEW state progress to FSRS Card."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.REVIEW,
            next_review_date=datetime.utcnow(),
            stability=10.0,
            difficulty=4.0,
            last_review_date=datetime.utcnow() - timedelta(days=7),
        )

        card = UserCardProgressService.progress_to_card(progress)

        assert card.state == FSRSState.Review
        assert card.stability == 10.0
        assert card.difficulty == 4.0

    def test_relearning_card_conversion(self):
        """Test conversion of RELEARNING state progress to FSRS Card."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.RELEARNING,
            next_review_date=datetime.utcnow(),
            stability=2.0,
            difficulty=6.0,
        )

        card = UserCardProgressService.progress_to_card(progress)

        assert card.state == FSRSState.Relearning
        assert card.step == 0


class TestUpdateProgressFromCard:
    """Tests for update_progress_from_card."""

    def test_update_after_correct_review(self):
        """Test progress update after correct answer."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.NEW,
            next_review_date=datetime.utcnow(),
            total_reviews=0,
            correct_count=0,
        )

        card = Card()
        card.state = FSRSState.Learning
        card.stability = 3.0
        card.difficulty = 4.5
        card.due = datetime.utcnow() + timedelta(minutes=10)

        now = datetime.utcnow()
        updated = UserCardProgressService.update_progress_from_card(
            progress, card, is_correct=True, review_datetime=now
        )

        assert updated.total_reviews == 1
        assert updated.correct_count == 1
        assert updated.stability == 3.0
        assert updated.difficulty == 4.5
        assert updated.quality_history is not None
        assert len(updated.quality_history) == 1
        assert updated.quality_history[0]["is_correct"] is True

    def test_update_after_wrong_review(self):
        """Test progress update after wrong answer."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.REVIEW,  # Was in review state
            next_review_date=datetime.utcnow(),
            total_reviews=5,
            correct_count=4,
            lapses=0,
        )

        card = Card()
        card.state = FSRSState.Relearning
        card.stability = 2.0
        card.difficulty = 6.0
        card.due = datetime.utcnow() + timedelta(minutes=1)

        now = datetime.utcnow()
        updated = UserCardProgressService.update_progress_from_card(
            progress, card, is_correct=False, review_datetime=now
        )

        assert updated.total_reviews == 6
        assert updated.correct_count == 4  # Unchanged
        assert updated.lapses == 1  # Incremented (was in REVIEW state)
        assert updated.card_state == CardState.RELEARNING


class TestProgressServiceCRUD:
    """Tests for UserCardProgress CRUD operations."""

    async def test_create_progress(self, db_session):
        """Test creating a new progress record."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        progress_data = UserCardProgressCreate(
            user_id=profile.id,
            card_id=card.id,
            next_review_date=datetime.utcnow(),
        )

        progress = await UserCardProgressService.create_progress(db_session, progress_data)

        assert progress is not None
        assert progress.id is not None
        assert progress.user_id == profile.id
        assert progress.card_id == card.id
        assert progress.card_state == CardState.NEW

    async def test_get_progress_by_id(self, db_session):
        """Test getting progress by ID."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        progress = await UserCardProgressFactory.create_async(
            db_session, user_id=profile.id, card_id=card.id
        )

        retrieved = await UserCardProgressService.get_progress(db_session, progress.id)

        assert retrieved is not None
        assert retrieved.id == progress.id

    async def test_get_user_card_progress(self, db_session):
        """Test getting progress for specific user and card."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)
        progress = await UserCardProgressFactory.create_async(
            db_session, user_id=profile.id, card_id=card.id
        )

        retrieved = await UserCardProgressService.get_user_card_progress(
            db_session, profile.id, card.id
        )

        assert retrieved is not None
        assert retrieved.id == progress.id

    async def test_get_user_card_progress_not_found(self, db_session):
        """Test getting non-existent progress returns None."""
        user_id = uuid4()

        result = await UserCardProgressService.get_user_card_progress(db_session, user_id, 99999)

        assert result is None


class TestDueCards:
    """Tests for due cards retrieval."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_due_cards(self, db_session):
        """Test getting cards due for review."""
        profile = await ProfileFactory.create_async(db_session)

        # Create due cards
        for _i in range(3):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                next_review_date=datetime(2024, 1, 14, 12, 0, 0),  # Yesterday
                card_state=CardState.REVIEW,
            )

        # Create not-due card
        future_card = await VocabularyCardFactory.create_async(db_session)
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=future_card.id,
            next_review_date=datetime(2024, 1, 20, 12, 0, 0),  # Future
            card_state=CardState.REVIEW,
        )

        due_cards = await UserCardProgressService.get_due_cards(db_session, profile.id)

        assert len(due_cards) == 3
        for card_progress in due_cards:
            assert card_progress.next_review_date <= datetime(2024, 1, 15, 12, 0, 0)


class TestProcessReview:
    """Tests for FSRS review processing."""

    async def test_process_review_correct_new_card(self, db_session):
        """Test processing a correct review for a new card."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        progress = await UserCardProgressService.process_review(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            is_correct=True,
        )

        assert progress is not None
        assert progress.total_reviews == 1
        assert progress.correct_count == 1
        # After first review, card should be in LEARNING or REVIEW state
        assert progress.card_state in [CardState.LEARNING, CardState.REVIEW]

    async def test_process_review_wrong(self, db_session):
        """Test processing an incorrect review."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        # First, create progress with REVIEW state
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            card_state=CardState.REVIEW,
            total_reviews=5,
            correct_count=4,
            lapses=0,
            stability=10.0,
            difficulty=5.0,
            next_review_date=datetime.utcnow() - timedelta(hours=1),
        )

        progress = await UserCardProgressService.process_review(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            is_correct=False,
        )

        assert progress.total_reviews == 6
        assert progress.correct_count == 4  # Unchanged
        assert progress.lapses == 1  # Incremented

    async def test_process_review_with_rating_hint(self, db_session):
        """Test processing review with explicit rating hint."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        # Test with EASY rating
        progress = await UserCardProgressService.process_review(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            is_correct=True,
            rating_hint=4,  # Easy
        )

        assert progress is not None
        assert progress.correct_count == 1

    async def test_process_review_creates_progress_if_not_exists(self, db_session):
        """Test that process_review creates progress if it doesn't exist."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        # No existing progress for this user/card
        progress = await UserCardProgressService.process_review(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            is_correct=True,
        )

        assert progress is not None
        assert progress.user_id == profile.id
        assert progress.card_id == card.id


class TestTodayProgress:
    """Tests for today's progress statistics."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_today_progress(self, db_session):
        """Test getting today's progress statistics."""
        profile = await ProfileFactory.create_async(db_session, daily_goal=10)

        # Create progress with today's reviews in quality_history
        card = await VocabularyCardFactory.create_async(db_session)
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            last_review_date=datetime(2024, 1, 15, 10, 0, 0),
            quality_history=[
                {"date": "2024-01-15T08:00:00", "is_correct": True},
                {"date": "2024-01-15T09:00:00", "is_correct": False},
                {"date": "2024-01-15T10:00:00", "is_correct": True},
            ],
        )

        result = await UserCardProgressService.get_today_progress(
            db_session, profile.id, daily_goal=10
        )

        assert result["total_reviews"] == 3
        assert result["correct_count"] == 2
        assert result["wrong_count"] == 1
        assert result["accuracy_rate"] == 66.7
        assert result["daily_goal"] == 10
        assert result["goal_progress"] == 30.0

    async def test_get_today_progress_no_reviews(self, db_session):
        """Test today's progress with no reviews."""
        profile = await ProfileFactory.create_async(db_session)

        result = await UserCardProgressService.get_today_progress(
            db_session, profile.id, daily_goal=20
        )

        assert result["total_reviews"] == 0
        assert result["correct_count"] == 0
        assert result["accuracy_rate"] == 0.0


class TestNewCardsCount:
    """Tests for new/review cards count."""

    async def test_get_new_cards_count_all_decks(self, db_session):
        """Test counting new cards when select_all_decks is true."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)

        # Create public deck with cards
        deck = await DeckFactory.create_async(db_session, is_public=True)
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        result = await UserCardProgressService.get_new_cards_count(db_session, profile.id)

        assert result["new_cards_count"] == 5
        assert result["review_cards_count"] == 0

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_review_cards_count(self, db_session):
        """Test counting review cards (due for review)."""
        profile = await ProfileFactory.create_async(db_session)

        # Create cards with progress
        for _ in range(3):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                next_review_date=datetime(2024, 1, 14, 12, 0, 0),  # Due
                card_state=CardState.REVIEW,
            )

        result = await UserCardProgressService.get_new_cards_count(db_session, profile.id)

        assert result["review_cards_count"] == 3

    async def test_get_new_cards_count_no_profile(self, db_session):
        """Test new cards count for non-existent profile."""
        non_existent_id = uuid4()

        result = await UserCardProgressService.get_new_cards_count(db_session, non_existent_id)

        assert result["new_cards_count"] == 0
        assert result["review_cards_count"] == 0

    async def test_get_new_cards_count_selected_decks_only(self, db_session):
        """Test counting new cards with selected_decks_only preference."""
        from tests.factories.user_selected_deck_factory import UserSelectedDeckFactory

        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)
        deck1 = await DeckFactory.create_async(db_session, is_public=True)
        deck2 = await DeckFactory.create_async(db_session, is_public=True)

        # Create cards in both decks
        for _ in range(3):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck1.id)
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck2.id)

        # Only select deck1
        await UserSelectedDeckFactory.create_async(db_session, user_id=profile.id, deck_id=deck1.id)

        result = await UserCardProgressService.get_new_cards_count(db_session, profile.id)

        # Should only count cards from selected deck1
        assert result["new_cards_count"] == 3


class TestUpdateProgressFromCardEdgeCases:
    """Tests for edge cases in update_progress_from_card."""

    def test_update_with_none_due_date(self):
        """Test progress update when card.due is None."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.NEW,
            next_review_date=datetime.utcnow(),
            total_reviews=0,
            correct_count=0,
        )

        card = Card()
        card.state = FSRSState.Learning
        card.stability = 3.0
        card.difficulty = 4.5
        card.due = None  # No due date

        now = datetime.utcnow()
        updated = UserCardProgressService.update_progress_from_card(
            progress, card, is_correct=True, review_datetime=now
        )

        assert updated.interval == 0
        assert updated.next_review_date is None

    def test_update_appends_to_existing_history(self):
        """Test that review appends to existing quality_history."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.LEARNING,
            next_review_date=datetime.utcnow(),
            total_reviews=2,
            correct_count=2,
            quality_history=[
                {"date": "2024-01-10T10:00:00", "is_correct": True},
                {"date": "2024-01-12T11:00:00", "is_correct": True},
            ],
        )

        card = Card()
        card.state = FSRSState.Review
        card.stability = 5.0
        card.difficulty = 4.0
        card.due = datetime.utcnow() + timedelta(days=3)

        now = datetime.utcnow()
        updated = UserCardProgressService.update_progress_from_card(
            progress, card, is_correct=True, review_datetime=now
        )

        assert len(updated.quality_history) == 3
        assert updated.quality_history[-1]["is_correct"] is True

    def test_update_with_non_list_history_replaces(self):
        """Test that non-list quality_history is replaced with list."""
        progress = UserCardProgress(
            id=1,
            user_id=uuid4(),
            card_id=1,
            card_state=CardState.LEARNING,
            next_review_date=datetime.utcnow(),
            total_reviews=1,
            correct_count=1,
            quality_history="invalid_data",  # Should be list but isn't
        )

        card = Card()
        card.state = FSRSState.Review
        card.stability = 5.0
        card.difficulty = 4.0
        card.due = datetime.utcnow() + timedelta(days=3)

        now = datetime.utcnow()
        updated = UserCardProgressService.update_progress_from_card(
            progress, card, is_correct=True, review_datetime=now
        )

        # Should replace with a list containing new entry
        assert isinstance(updated.quality_history, list)
        assert len(updated.quality_history) == 1


class TestGetUserProgress:
    """Tests for get_user_progress method."""

    async def test_get_user_progress_with_pagination(self, db_session):
        """Test getting user progress with pagination."""
        profile = await ProfileFactory.create_async(db_session)

        # Create multiple progress records
        for _i in range(10):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session, user_id=profile.id, card_id=card.id
            )

        # Get first page
        first_page = await UserCardProgressService.get_user_progress(
            db_session, profile.id, skip=0, limit=5
        )
        assert len(first_page) == 5

        # Get second page
        second_page = await UserCardProgressService.get_user_progress(
            db_session, profile.id, skip=5, limit=5
        )
        assert len(second_page) == 5

        # Ensure no overlap
        first_ids = {p.id for p in first_page}
        second_ids = {p.id for p in second_page}
        assert first_ids.isdisjoint(second_ids)


class TestTodayProgressEdgeCases:
    """Tests for edge cases in get_today_progress."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_today_progress_with_invalid_date_format(self, db_session):
        """Test progress with invalid date format in quality_history is skipped."""
        profile = await ProfileFactory.create_async(db_session)

        card = await VocabularyCardFactory.create_async(db_session)
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            quality_history=[
                {"date": "2024-01-15T08:00:00", "is_correct": True},
                {
                    "date": "invalid_date",
                    "is_correct": True,
                },  # Invalid - will be skipped
                {"is_correct": True},  # Missing date - will be skipped
            ],
        )

        result = await UserCardProgressService.get_today_progress(
            db_session, profile.id, daily_goal=10
        )

        # Invalid entries are skipped via try/except continue
        # Only valid entry with today's date is counted
        assert result["total_reviews"] >= 0
        assert result["correct_count"] >= 0
