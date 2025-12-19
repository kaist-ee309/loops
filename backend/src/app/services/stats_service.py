"""Statistics service for learning analytics."""

from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserCardProgress, VocabularyCard
from app.models.enums import CardState
from app.models.schemas.stats import (
    AccuracyByPeriod,
    StatsAccuracyRead,
    StatsHistoryItem,
    StatsHistoryRead,
    StatsHistorySummary,
    TodayStatsRead,
    TodayVocabularyStats,
    TotalLearnedRead,
)
from app.models.tables.study_session import StudySession


class StatsService:
    """Service for statistics and analytics operations."""

    @staticmethod
    async def get_total_learned(
        session: AsyncSession,
        user_id: UUID,
        total_study_time_minutes: int,
    ) -> TotalLearnedRead:
        """
        Get total learned cards count and breakdown by CEFR level.

        Args:
            session: Database session
            user_id: User's profile ID
            total_study_time_minutes: Total study time from profile

        Returns:
            TotalLearnedRead with total count and by_level breakdown
        """
        # Count total REVIEW state cards
        total_learned_query = select(func.count(UserCardProgress.id)).where(
            UserCardProgress.user_id == user_id,
            UserCardProgress.card_state == CardState.REVIEW,
        )
        result = await session.exec(total_learned_query)
        total_learned = result.one()

        # Get breakdown by CEFR level
        by_level_query = (
            select(VocabularyCard.cefr_level, func.count(UserCardProgress.id))
            .select_from(UserCardProgress)
            .join(
                VocabularyCard,
                VocabularyCard.id == UserCardProgress.card_id,
            )
            .where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.card_state == CardState.REVIEW,
                VocabularyCard.cefr_level.isnot(None),
            )
            .group_by(VocabularyCard.cefr_level)
        )
        result = await session.exec(by_level_query)
        by_level_results = result.all()

        # Convert to dictionary
        by_level = dict(by_level_results)

        return TotalLearnedRead(
            total_learned=total_learned,
            by_level=by_level,
            total_study_time_minutes=total_study_time_minutes,
        )

    @staticmethod
    async def get_stats_history(
        session: AsyncSession,
        user_id: UUID,
        period: Literal["7d", "30d", "1y", "all"] = "30d",
    ) -> StatsHistoryRead:
        """
        Get learning history for charting.

        Args:
            session: Database session
            user_id: User's profile ID
            period: Time period (7d, 30d, 1y, all)

        Returns:
            StatsHistoryRead with daily stats and summary
        """
        # Calculate date range based on period
        now = datetime.utcnow()
        if period == "all":
            start_date = None
        else:
            period_days = {"7d": 7, "30d": 30, "1y": 365}
            days = period_days[period]
            start_date = now - timedelta(days=days)

        # Query for daily stats grouped by date from UserCardProgress
        history_query = select(
            func.date(UserCardProgress.last_review_date).label("review_date"),
            func.sum(UserCardProgress.total_reviews).label("cards_studied"),
            func.sum(UserCardProgress.correct_count).label("correct_count"),
        ).where(
            UserCardProgress.user_id == user_id,
            UserCardProgress.last_review_date.isnot(None),
        )

        if start_date:
            history_query = history_query.where(UserCardProgress.last_review_date >= start_date)

        history_query = history_query.group_by(
            func.date(UserCardProgress.last_review_date)
        ).order_by(func.date(UserCardProgress.last_review_date).asc())

        result = await session.exec(history_query)
        rows = result.all()

        # Query for daily study time from StudySession
        study_time_query = select(
            func.date(StudySession.started_at).label("session_date"),
            func.sum(
                func.extract(
                    "epoch",
                    StudySession.completed_at - StudySession.started_at,
                )
            ).label("total_seconds"),
        ).where(
            StudySession.user_id == user_id,
            StudySession.completed_at.isnot(None),
        )

        if start_date:
            study_time_query = study_time_query.where(StudySession.started_at >= start_date)

        study_time_query = study_time_query.group_by(func.date(StudySession.started_at)).order_by(
            func.date(StudySession.started_at).asc()
        )

        time_result = await session.exec(study_time_query)
        time_rows = time_result.all()

        # Build a map of date -> study_time_seconds
        study_time_map = {row[0]: int(row[1] or 0) for row in time_rows}

        # Build history items with study time
        history_data = []
        for row in rows:
            review_date, cards_studied, correct_count = row
            cards_studied = cards_studied or 0
            correct_count = correct_count or 0
            accuracy = (correct_count / cards_studied * 100) if cards_studied > 0 else 0.0
            study_time = study_time_map.get(review_date, 0)

            history_data.append(
                StatsHistoryItem(
                    date=review_date,
                    cards_studied=cards_studied,
                    correct_count=correct_count,
                    accuracy_rate=round(accuracy, 1),
                    study_time_seconds=study_time,
                )
            )

        # Calculate summary statistics
        total_study_time = sum(item.study_time_seconds for item in history_data)
        total_cards = sum(item.cards_studied for item in history_data)
        days_with_activity = len([item for item in history_data if item.cards_studied > 0])

        avg_study_time = int(total_study_time / days_with_activity) if days_with_activity > 0 else 0
        avg_cards = int(total_cards / days_with_activity) if days_with_activity > 0 else 0

        summary = StatsHistorySummary(
            total_study_time_seconds=total_study_time,
            total_cards_studied=total_cards,
            avg_daily_study_time_seconds=avg_study_time,
            avg_daily_cards_studied=avg_cards,
            days_with_activity=days_with_activity,
        )

        return StatsHistoryRead(period=period, summary=summary, data=history_data)

    @staticmethod
    async def get_stats_accuracy(
        session: AsyncSession,
        user_id: UUID,
    ) -> StatsAccuracyRead:
        """
        Get accuracy statistics.

        Args:
            session: Database session
            user_id: User's profile ID

        Returns:
            StatsAccuracyRead with overall, period-based, and CEFR-level accuracy
        """
        now = datetime.utcnow()

        # Helper function to calculate accuracy for a period
        async def get_accuracy_for_period(days: int | None) -> tuple[int, int]:
            """Returns (total_reviews, correct_count) for the given period."""
            query = select(
                func.sum(UserCardProgress.total_reviews),
                func.sum(UserCardProgress.correct_count),
            ).where(UserCardProgress.user_id == user_id)

            if days is not None:
                start_date = now - timedelta(days=days)
                query = query.where(UserCardProgress.last_review_date >= start_date)

            result = await session.exec(query)
            row = result.one()
            return (row[0] or 0, row[1] or 0)

        # Get all-time stats
        total_reviews, total_correct = await get_accuracy_for_period(None)
        overall_accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0.0

        # Get period-based stats
        reviews_7d, correct_7d = await get_accuracy_for_period(7)
        reviews_30d, correct_30d = await get_accuracy_for_period(30)
        reviews_90d, correct_90d = await get_accuracy_for_period(90)

        accuracy_7d = (correct_7d / reviews_7d * 100) if reviews_7d > 0 else None
        accuracy_30d = (correct_30d / reviews_30d * 100) if reviews_30d > 0 else None
        accuracy_90d = (correct_90d / reviews_90d * 100) if reviews_90d > 0 else None

        by_period = AccuracyByPeriod(
            all_time=round(overall_accuracy, 1),
            last_7_days=round(accuracy_7d, 1) if accuracy_7d is not None else None,
            last_30_days=round(accuracy_30d, 1) if accuracy_30d is not None else None,
            last_90_days=round(accuracy_90d, 1) if accuracy_90d is not None else None,
        )

        # Get accuracy by CEFR level
        by_level_query = (
            select(
                VocabularyCard.cefr_level,
                func.sum(UserCardProgress.total_reviews),
                func.sum(UserCardProgress.correct_count),
            )
            .select_from(UserCardProgress)
            .join(VocabularyCard, VocabularyCard.id == UserCardProgress.card_id)
            .where(
                UserCardProgress.user_id == user_id,
                VocabularyCard.cefr_level.isnot(None),
            )
            .group_by(VocabularyCard.cefr_level)
        )
        result = await session.exec(by_level_query)
        by_level_rows = result.all()

        by_cefr_level = {}
        for level, reviews, correct in by_level_rows:
            if reviews and reviews > 0:
                by_cefr_level[level] = round((correct or 0) / reviews * 100, 1)

        # Determine trend (comparing last 7 days vs previous 7 days)
        trend = "stable"
        if accuracy_7d is not None:
            # Get accuracy for 8-14 days ago
            prev_start = now - timedelta(days=14)
            prev_end = now - timedelta(days=7)
            prev_query = select(
                func.sum(UserCardProgress.total_reviews),
                func.sum(UserCardProgress.correct_count),
            ).where(
                UserCardProgress.user_id == user_id,
                UserCardProgress.last_review_date >= prev_start,
                UserCardProgress.last_review_date < prev_end,
            )
            result = await session.exec(prev_query)
            prev_row = result.one()
            prev_reviews, prev_correct = prev_row[0] or 0, prev_row[1] or 0

            if prev_reviews > 0:
                prev_accuracy = prev_correct / prev_reviews * 100
                diff = accuracy_7d - prev_accuracy
                if diff > 5:
                    trend = "improving"
                elif diff < -5:
                    trend = "declining"

        return StatsAccuracyRead(
            overall_accuracy=round(overall_accuracy, 1),
            total_reviews=total_reviews,
            total_correct=total_correct,
            by_period=by_period,
            by_cefr_level=by_cefr_level,
            trend=trend,
        )

    @staticmethod
    async def get_today_stats(
        session: AsyncSession,
        user_id: UUID,
        daily_goal: int,
    ) -> TodayStatsRead:
        """
        Get today's learning statistics.

        Args:
            session: Database session
            user_id: User's profile ID
            daily_goal: User's daily goal from profile

        Returns:
            TodayStatsRead with today's learning details
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Query today's completed study sessions
        sessions_query = select(StudySession).where(
            StudySession.user_id == user_id,
            StudySession.started_at >= today_start,
            StudySession.started_at <= today_end,
            StudySession.completed_at.isnot(None),
        )
        result = await session.exec(sessions_query)
        sessions = result.all()

        # Calculate totals
        total_study_time_seconds = 0
        total_cards_studied = 0
        new_cards_count = 0
        review_cards_count = 0
        review_correct_count = 0

        for study_session in sessions:
            # Calculate study time
            if study_session.completed_at and study_session.started_at:
                duration = (study_session.completed_at - study_session.started_at).total_seconds()
                total_study_time_seconds += int(duration)

            # Sum cards
            cards_in_session = study_session.correct_count + study_session.wrong_count
            total_cards_studied += cards_in_session
            new_cards_count += study_session.new_cards_count
            review_cards_count += study_session.review_cards_count

            # For review accuracy, approximate from session data
            if study_session.review_cards_count > 0:
                session_accuracy = (
                    study_session.correct_count / cards_in_session if cards_in_session > 0 else 0
                )
                review_correct_count += int(study_session.review_cards_count * session_accuracy)

        # Calculate review accuracy
        review_accuracy = None
        if review_cards_count > 0:
            review_accuracy = round((review_correct_count / review_cards_count) * 100, 1)

        # Use provided daily goal or default
        effective_daily_goal = daily_goal or 30

        # Calculate progress
        progress = (
            min((total_cards_studied / effective_daily_goal) * 100, 100.0)
            if effective_daily_goal > 0
            else 0.0
        )

        vocabulary_stats = TodayVocabularyStats(
            new_cards_count=new_cards_count,
            review_cards_count=review_cards_count,
            review_accuracy=review_accuracy,
            progress=round(progress, 1),
            daily_goal=effective_daily_goal,
        )

        return TodayStatsRead(
            total_study_time_seconds=total_study_time_seconds,
            total_cards_studied=total_cards_studied,
            vocabulary=vocabulary_stats,
        )
