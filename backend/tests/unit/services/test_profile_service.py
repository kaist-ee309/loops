"""Tests for ProfileService."""

from datetime import date, datetime
from uuid import uuid4

from freezegun import freeze_time

from app.models import CardState, ProfileUpdate
from app.services.profile_service import ProfileService
from tests.factories.profile_factory import ProfileFactory
from tests.factories.user_card_progress_factory import UserCardProgressFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory


class TestProfileServiceCRUD:
    """Tests for Profile CRUD operations."""

    async def test_create_profile(self, db_session):
        """Test creating a new profile."""
        profile_id = uuid4()

        profile = await ProfileService.create_profile(db_session, profile_id)

        assert profile is not None
        assert profile.id == profile_id
        assert profile.daily_goal == 20
        assert profile.current_streak == 0
        assert profile.select_all_decks is True

    async def test_get_profile_by_id(self, db_session):
        """Test getting a profile by ID."""
        # Create profile
        profile = await ProfileFactory.create_async(db_session)

        # Retrieve profile
        retrieved = await ProfileService.get_profile(db_session, profile.id)

        assert retrieved is not None
        assert retrieved.id == profile.id

    async def test_get_profile_not_found(self, db_session):
        """Test getting a non-existent profile returns None."""
        non_existent_id = uuid4()

        result = await ProfileService.get_profile(db_session, non_existent_id)

        assert result is None

    async def test_update_profile(self, db_session):
        """Test updating a profile."""
        profile = await ProfileFactory.create_async(db_session)
        update_data = ProfileUpdate(daily_goal=30, theme="dark")

        updated = await ProfileService.update_profile(db_session, profile.id, update_data)

        assert updated is not None
        assert updated.daily_goal == 30
        assert updated.theme == "dark"
        # Unchanged fields should remain
        assert updated.timezone == "UTC"

    async def test_update_profile_not_found(self, db_session):
        """Test updating a non-existent profile returns None."""
        non_existent_id = uuid4()
        update_data = ProfileUpdate(daily_goal=30)

        result = await ProfileService.update_profile(db_session, non_existent_id, update_data)

        assert result is None

    async def test_delete_profile(self, db_session):
        """Test deleting a profile."""
        profile = await ProfileFactory.create_async(db_session)
        profile_id = profile.id

        result = await ProfileService.delete_profile(db_session, profile_id)

        assert result is True
        # Verify deletion
        deleted = await ProfileService.get_profile(db_session, profile_id)
        assert deleted is None

    async def test_delete_profile_not_found(self, db_session):
        """Test deleting a non-existent profile returns False."""
        non_existent_id = uuid4()

        result = await ProfileService.delete_profile(db_session, non_existent_id)

        assert result is False


class TestProfileStreak:
    """Tests for streak calculation logic."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_calculate_streak_first_study(self, db_session):
        """Test streak calculation for first-time study."""
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=0,
            longest_streak=0,
            last_study_date=None,
        )

        result = await ProfileService.update_profile_streak(db_session, profile.id)

        assert result is not None
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 1
        assert result["is_new_record"] is True
        assert result["streak_status"] == "started"

    @freeze_time("2024-01-15 12:00:00")
    async def test_calculate_streak_consecutive_days(self, db_session):
        """Test streak continues when studying consecutive days."""
        yesterday = date(2024, 1, 14)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=5,
            longest_streak=10,
            last_study_date=yesterday,
        )

        result = await ProfileService.update_profile_streak(db_session, profile.id)

        assert result is not None
        assert result["current_streak"] == 6
        assert result["streak_status"] == "continued"

    @freeze_time("2024-01-15 12:00:00")
    async def test_calculate_streak_broken(self, db_session):
        """Test streak resets when gap > 1 day."""
        two_days_ago = date(2024, 1, 13)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=5,
            longest_streak=10,
            last_study_date=two_days_ago,
        )

        result = await ProfileService.update_profile_streak(db_session, profile.id)

        assert result is not None
        assert result["current_streak"] == 1
        assert result["streak_status"] == "broken"
        # Longest should remain unchanged
        assert result["longest_streak"] == 10

    @freeze_time("2024-01-15 12:00:00")
    async def test_calculate_streak_same_day(self, db_session):
        """Test multiple sessions on same day don't increase streak."""
        today = date(2024, 1, 15)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=5,
            longest_streak=10,
            last_study_date=today,
        )

        result = await ProfileService.update_profile_streak(db_session, profile.id)

        assert result is not None
        assert result["current_streak"] == 5  # No change
        assert result["streak_status"] == "continued"
        assert result["is_new_record"] is False

    @freeze_time("2024-01-15 12:00:00")
    async def test_calculate_streak_new_record(self, db_session):
        """Test new record is detected when current_streak exceeds longest."""
        yesterday = date(2024, 1, 14)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=10,
            longest_streak=10,
            last_study_date=yesterday,
        )

        result = await ProfileService.update_profile_streak(db_session, profile.id)

        assert result is not None
        assert result["current_streak"] == 11
        assert result["longest_streak"] == 11
        assert result["is_new_record"] is True

    async def test_update_profile_streak_not_found(self, db_session):
        """Test streak update for non-existent profile."""
        non_existent_id = uuid4()

        result = await ProfileService.update_profile_streak(db_session, non_existent_id)

        assert result is None


class TestDailyGoal:
    """Tests for daily goal tracking."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_daily_goal(self, db_session):
        """Test getting daily goal with today's completion count."""
        profile = await ProfileFactory.create_async(db_session, daily_goal=20)

        # Create some cards and progress for today
        for _i in range(5):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                last_review_date=datetime(2024, 1, 15, 10, 0, 0),
                total_reviews=1,
            )

        result = await ProfileService.get_daily_goal(db_session, profile.id)

        assert result is not None
        assert result["daily_goal"] == 20
        assert result["completed_today"] == 5

    async def test_get_daily_goal_no_progress(self, db_session):
        """Test daily goal when no cards studied today."""
        profile = await ProfileFactory.create_async(db_session, daily_goal=15)

        result = await ProfileService.get_daily_goal(db_session, profile.id)

        assert result is not None
        assert result["daily_goal"] == 15
        assert result["completed_today"] == 0

    async def test_get_daily_goal_not_found(self, db_session):
        """Test daily goal for non-existent profile."""
        non_existent_id = uuid4()

        result = await ProfileService.get_daily_goal(db_session, non_existent_id)

        assert result is None


class TestProfileLevel:
    """Tests for profile level calculation."""

    async def test_calculate_level_no_reviews(self, db_session):
        """Test level calculation with no reviews."""
        profile = await ProfileFactory.create_async(db_session)

        result = await ProfileService.calculate_profile_level(db_session, profile.id)

        assert result is not None
        assert result["level"] == 1.0
        assert result["cefr_equivalent"] == "A1"
        assert result["total_reviews"] == 0
        assert result["mastered_cards"] == 0

    async def test_calculate_level_with_mastered_cards(self, db_session):
        """Test level calculation with mastered cards."""
        profile = await ProfileFactory.create_async(db_session)

        # Create cards and progress with REVIEW state (mastered)
        for _i in range(5):
            card = await VocabularyCardFactory.create_async(
                db_session,
                cefr_level="B1",
            )
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.REVIEW,
                difficulty=5.0,
                total_reviews=10,
                correct_count=8,
                last_review_date=datetime.utcnow(),
            )

        result = await ProfileService.calculate_profile_level(db_session, profile.id)

        assert result is not None
        assert result["total_reviews"] == 50  # 5 cards * 10 reviews
        assert result["accuracy_rate"] == 80.0  # 40/50 correct
        assert result["mastered_cards"] == 5

    async def test_calculate_level_mixed_states(self, db_session):
        """Test level calculation with mixed card states."""
        profile = await ProfileFactory.create_async(db_session)

        # Create mastered cards (REVIEW state)
        for _i in range(3):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.REVIEW,
                difficulty=6.0,
                total_reviews=5,
                correct_count=4,
                last_review_date=datetime.utcnow(),
            )

        # Create learning cards
        for _i in range(2):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.LEARNING,
                difficulty=4.0,
                total_reviews=2,
                correct_count=1,
                last_review_date=datetime.utcnow(),
            )

        result = await ProfileService.calculate_profile_level(db_session, profile.id)

        assert result is not None
        assert result["mastered_cards"] == 3
        # Total: 3*5 + 2*2 = 19 reviews
        assert result["total_reviews"] == 19

    async def test_calculate_level_no_mastered_uses_all_cards(self, db_session):
        """Test level calculation uses all cards when none are mastered."""
        profile = await ProfileFactory.create_async(db_session)

        # Create only learning cards (no mastered)
        for _i in range(3):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.LEARNING,
                difficulty=4.0,
                total_reviews=3,
                correct_count=2,
                last_review_date=datetime.utcnow(),
            )

        result = await ProfileService.calculate_profile_level(db_session, profile.id)

        assert result is not None
        assert result["mastered_cards"] == 0
        # Level should be calculated from learning cards
        assert result["level"] >= 1.0

    async def test_calculate_level_cefr_c2(self, db_session):
        """Test level calculation returns C2 for high difficulty."""
        profile = await ProfileFactory.create_async(db_session)

        # Create high difficulty mastered cards
        for _i in range(5):
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.REVIEW,
                difficulty=9.5,  # Very high difficulty
                total_reviews=10,
                correct_count=10,  # 100% accuracy
                last_review_date=datetime.utcnow(),
            )

        result = await ProfileService.calculate_profile_level(db_session, profile.id)

        assert result is not None
        assert result["cefr_equivalent"] == "C2"
        assert result["level"] >= 8.0


class TestProfileConfig:
    """Tests for profile configuration."""

    async def test_update_profile_config(self, db_session):
        """Test updating profile configuration."""
        profile = await ProfileFactory.create_async(db_session)

        config_data = {
            "daily_goal": 50,
            "theme": "dark",
            "notification_enabled": False,
        }

        result = await ProfileService.update_profile_config(db_session, profile, config_data)

        assert result is not None
        assert result.daily_goal == 50
        assert result.theme == "dark"
        assert result.notification_enabled is False


class TestGetProfileStreak:
    """Tests for get_profile_streak method."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_profile_streak_active(self, db_session):
        """Test getting streak info when streak is active."""
        today = date(2024, 1, 15)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=5,
            longest_streak=10,
            last_study_date=today,
        )

        result = await ProfileService.get_profile_streak(db_session, profile)

        assert result["current_streak"] == 5
        assert result["longest_streak"] == 10
        assert result["last_study_date"] == today
        assert result["streak_status"] == "active"
        assert "🔥" in result["message"]

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_profile_streak_active_yesterday(self, db_session):
        """Test getting streak info when last study was yesterday."""
        yesterday = date(2024, 1, 14)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=3,
            longest_streak=5,
            last_study_date=yesterday,
        )

        result = await ProfileService.get_profile_streak(db_session, profile)

        assert result["streak_status"] == "active"
        assert "🔥" in result["message"]

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_profile_streak_broken(self, db_session):
        """Test getting streak info when streak is broken."""
        three_days_ago = date(2024, 1, 12)
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=2,
            longest_streak=7,
            last_study_date=three_days_ago,
        )

        result = await ProfileService.get_profile_streak(db_session, profile)

        assert result["streak_status"] == "broken"
        assert "💪" in result["message"]
        assert "3일 전" in result["message"]

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_profile_streak_never_studied(self, db_session):
        """Test getting streak info when user never studied."""
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=0,
            longest_streak=0,
            last_study_date=None,
        )

        result = await ProfileService.get_profile_streak(db_session, profile)

        assert result["streak_status"] == "broken"
        assert result["last_study_date"] is None
        assert "첫 학습" in result["message"]

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_profile_streak_with_days_this_month(self, db_session):
        """Test days_studied_this_month calculation."""
        profile = await ProfileFactory.create_async(
            db_session,
            current_streak=3,
            longest_streak=3,
            last_study_date=date(2024, 1, 15),
        )

        # Create some progress records this month
        for day in [10, 12, 15]:
            card = await VocabularyCardFactory.create_async(db_session)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                last_review_date=datetime(2024, 1, day, 10, 0, 0),
                total_reviews=1,
            )

        result = await ProfileService.get_profile_streak(db_session, profile)

        assert result["days_studied_this_month"] == 3
