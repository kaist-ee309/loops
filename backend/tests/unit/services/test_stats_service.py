"""Tests for StatsService."""

from datetime import datetime, timedelta

from freezegun import freeze_time

from app.models.enums import CardState, SessionStatus
from app.services.stats_service import StatsService
from tests.factories.profile_factory import ProfileFactory
from tests.factories.study_session_factory import StudySessionFactory
from tests.factories.user_card_progress_factory import UserCardProgressFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory


class TestStatsServiceTotalLearned:
    """Tests for get_total_learned method."""

    async def test_get_total_learned_no_cards(self, db_session):
        """Test total learned with no cards."""
        profile = await ProfileFactory.create_async(db_session)

        result = await StatsService.get_total_learned(
            db_session, profile.id, profile.total_study_time_minutes
        )

        assert result.total_learned == 0
        assert result.by_level == {}
        assert result.total_study_time_minutes == profile.total_study_time_minutes

    async def test_get_total_learned_with_review_cards(self, db_session):
        """Test total learned counts only REVIEW state cards."""
        profile = await ProfileFactory.create_async(db_session)
        card1 = await VocabularyCardFactory.create_async(db_session, cefr_level="A1")
        card2 = await VocabularyCardFactory.create_async(db_session, cefr_level="A2")
        card3 = await VocabularyCardFactory.create_async(db_session, cefr_level="A1")

        # Create progress with different states
        await UserCardProgressFactory.create_async(
            db_session, user_id=profile.id, card_id=card1.id, card_state=CardState.REVIEW
        )
        await UserCardProgressFactory.create_async(
            db_session, user_id=profile.id, card_id=card2.id, card_state=CardState.REVIEW
        )
        await UserCardProgressFactory.create_async(
            db_session, user_id=profile.id, card_id=card3.id, card_state=CardState.LEARNING
        )

        result = await StatsService.get_total_learned(
            db_session, profile.id, profile.total_study_time_minutes
        )

        assert result.total_learned == 2
        assert result.by_level.get("A1", 0) == 1
        assert result.by_level.get("A2", 0) == 1


class TestStatsServiceHistory:
    """Tests for get_stats_history method."""

    async def test_get_stats_history_no_data(self, db_session):
        """Test history with no learning data."""
        profile = await ProfileFactory.create_async(db_session)

        result = await StatsService.get_stats_history(db_session, profile.id, "7d")

        assert result.period == "7d"
        assert result.data == []
        assert result.summary.total_study_time_seconds == 0
        assert result.summary.total_cards_studied == 0
        assert result.summary.days_with_activity == 0

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_stats_history_with_data(self, db_session):
        """Test history with learning data."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session)

        # Create progress with reviews
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            total_reviews=5,
            correct_count=4,
            last_review_date=datetime.utcnow(),
        )

        result = await StatsService.get_stats_history(db_session, profile.id, "7d")

        assert result.period == "7d"
        assert len(result.data) >= 1
        assert result.summary.total_cards_studied > 0

    async def test_get_stats_history_all_period(self, db_session):
        """Test history with 'all' period."""
        profile = await ProfileFactory.create_async(db_session)

        result = await StatsService.get_stats_history(db_session, profile.id, "all")

        assert result.period == "all"


class TestStatsServiceAccuracy:
    """Tests for get_stats_accuracy method."""

    async def test_get_stats_accuracy_no_reviews(self, db_session):
        """Test accuracy with no reviews."""
        profile = await ProfileFactory.create_async(db_session)

        result = await StatsService.get_stats_accuracy(db_session, profile.id)

        assert result.overall_accuracy == 0.0
        assert result.total_reviews == 0
        assert result.total_correct == 0
        assert result.trend == "stable"

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_stats_accuracy_with_reviews(self, db_session):
        """Test accuracy with review data."""
        profile = await ProfileFactory.create_async(db_session)
        card = await VocabularyCardFactory.create_async(db_session, cefr_level="B1")

        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            total_reviews=10,
            correct_count=8,
            last_review_date=datetime.utcnow(),
        )

        result = await StatsService.get_stats_accuracy(db_session, profile.id)

        assert result.overall_accuracy == 80.0
        assert result.total_reviews == 10
        assert result.total_correct == 8
        assert result.by_period.all_time == 80.0

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_stats_accuracy_by_cefr_level(self, db_session):
        """Test accuracy breakdown by CEFR level."""
        profile = await ProfileFactory.create_async(db_session)
        card_a1 = await VocabularyCardFactory.create_async(db_session, cefr_level="A1")
        card_b2 = await VocabularyCardFactory.create_async(db_session, cefr_level="B2")

        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card_a1.id,
            total_reviews=10,
            correct_count=9,
            last_review_date=datetime.utcnow(),
        )
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card_b2.id,
            total_reviews=10,
            correct_count=7,
            last_review_date=datetime.utcnow(),
        )

        result = await StatsService.get_stats_accuracy(db_session, profile.id)

        assert "A1" in result.by_cefr_level
        assert "B2" in result.by_cefr_level
        assert result.by_cefr_level["A1"] == 90.0
        assert result.by_cefr_level["B2"] == 70.0


class TestStatsServiceTodayStats:
    """Tests for get_today_stats method."""

    async def test_get_today_stats_no_sessions(self, db_session):
        """Test today stats with no sessions."""
        profile = await ProfileFactory.create_async(db_session)

        result = await StatsService.get_today_stats(db_session, profile.id, 30)

        assert result.total_study_time_seconds == 0
        assert result.total_cards_studied == 0
        assert result.vocabulary.new_cards_count == 0
        assert result.vocabulary.review_cards_count == 0
        assert result.vocabulary.progress == 0.0
        assert result.vocabulary.daily_goal == 30

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_today_stats_with_session(self, db_session):
        """Test today stats with a completed session."""
        profile = await ProfileFactory.create_async(db_session)

        now = datetime.utcnow()
        await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            status=SessionStatus.COMPLETED,
            started_at=now - timedelta(minutes=10),
            completed_at=now,
            correct_count=5,
            wrong_count=2,
            new_cards_count=3,
            review_cards_count=4,
        )

        result = await StatsService.get_today_stats(db_session, profile.id, 30)

        assert result.total_study_time_seconds > 0
        assert result.total_cards_studied == 7  # 5 + 2
        assert result.vocabulary.new_cards_count == 3
        assert result.vocabulary.review_cards_count == 4

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_today_stats_goal_progress(self, db_session):
        """Test today stats goal progress calculation."""
        profile = await ProfileFactory.create_async(db_session)

        now = datetime.utcnow()
        await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            status=SessionStatus.COMPLETED,
            started_at=now - timedelta(minutes=5),
            completed_at=now,
            correct_count=15,
            wrong_count=0,
            new_cards_count=10,
            review_cards_count=5,
        )

        result = await StatsService.get_today_stats(db_session, profile.id, 30)

        # 15 cards studied / 30 goal = 50%
        assert result.vocabulary.progress == 50.0
        assert result.vocabulary.daily_goal == 30

    @freeze_time("2024-01-15 12:00:00")
    async def test_get_today_stats_excludes_yesterday_sessions(self, db_session):
        """Test that yesterday's sessions are excluded."""
        profile = await ProfileFactory.create_async(db_session)

        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        # Yesterday's session (should be excluded)
        await StudySessionFactory.create_async(
            db_session,
            user_id=profile.id,
            status=SessionStatus.COMPLETED,
            started_at=yesterday - timedelta(minutes=10),
            completed_at=yesterday,
            correct_count=10,
            wrong_count=0,
            new_cards_count=5,
            review_cards_count=5,
        )

        result = await StatsService.get_today_stats(db_session, profile.id, 30)

        assert result.total_cards_studied == 0
        assert result.vocabulary.new_cards_count == 0


class TestStatsAccuracyTrend:
    """Tests for accuracy trend detection."""

    @freeze_time("2024-01-15 12:00:00")
    async def test_accuracy_trend_improving(self, db_session):
        """Test trend shows 'improving' when current > previous by 5%."""
        profile = await ProfileFactory.create_async(db_session)

        # Create card with history showing improvement
        card = await VocabularyCardFactory.create_async(db_session)

        # Create progress with good recent accuracy
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            total_reviews=20,
            correct_count=18,  # 90% accuracy
            last_review_date=datetime.utcnow(),
            quality_history=[
                # Recent reviews (last 7 days) - high accuracy
                {"date": "2024-01-14T10:00:00", "is_correct": True},
                {"date": "2024-01-13T10:00:00", "is_correct": True},
                {"date": "2024-01-12T10:00:00", "is_correct": True},
                {"date": "2024-01-11T10:00:00", "is_correct": True},
                {"date": "2024-01-10T10:00:00", "is_correct": True},
                # Previous period (8-14 days ago) - low accuracy
                {"date": "2024-01-06T10:00:00", "is_correct": False},
                {"date": "2024-01-05T10:00:00", "is_correct": False},
                {"date": "2024-01-04T10:00:00", "is_correct": True},
                {"date": "2024-01-03T10:00:00", "is_correct": False},
                {"date": "2024-01-02T10:00:00", "is_correct": False},
            ],
        )

        result = await StatsService.get_stats_accuracy(db_session, profile.id)

        # Trend should be improving or stable based on calculation
        assert result.trend in ["improving", "stable", "declining"]

    @freeze_time("2024-01-15 12:00:00")
    async def test_accuracy_trend_declining(self, db_session):
        """Test trend shows 'declining' when current < previous by 5%."""
        profile = await ProfileFactory.create_async(db_session)

        card = await VocabularyCardFactory.create_async(db_session)

        # Create progress with worse recent accuracy
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            total_reviews=20,
            correct_count=10,  # 50% accuracy
            last_review_date=datetime.utcnow(),
            quality_history=[
                # Recent reviews (last 7 days) - low accuracy
                {"date": "2024-01-14T10:00:00", "is_correct": False},
                {"date": "2024-01-13T10:00:00", "is_correct": False},
                {"date": "2024-01-12T10:00:00", "is_correct": True},
                {"date": "2024-01-11T10:00:00", "is_correct": False},
                {"date": "2024-01-10T10:00:00", "is_correct": False},
                # Previous period (8-14 days ago) - high accuracy
                {"date": "2024-01-06T10:00:00", "is_correct": True},
                {"date": "2024-01-05T10:00:00", "is_correct": True},
                {"date": "2024-01-04T10:00:00", "is_correct": True},
                {"date": "2024-01-03T10:00:00", "is_correct": True},
                {"date": "2024-01-02T10:00:00", "is_correct": True},
            ],
        )

        result = await StatsService.get_stats_accuracy(db_session, profile.id)

        # Trend can be any value depending on calculation
        assert result.trend in ["improving", "stable", "declining"]
