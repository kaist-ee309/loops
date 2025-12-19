"""Tests for Stats API endpoints."""

import datetime
from unittest.mock import AsyncMock

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


class TestGetTotalLearned:
    """Tests for GET /stats/total-learned endpoint."""

    def test_get_total_learned_success(self, api_client, mocker):
        """Test successful retrieval of total learned stats."""
        mock_response = TotalLearnedRead(
            total_learned=150,
            by_level={"A1": 30, "A2": 40, "B1": 50, "B2": 20, "C1": 10, "C2": 0},
            total_study_time_minutes=120,
        )
        mocker.patch(
            "app.api.stats.StatsService.get_total_learned",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/stats/total-learned")

        assert response.status_code == 200
        data = response.json()
        assert data["total_learned"] == 150
        assert data["by_level"]["A1"] == 30
        assert data["total_study_time_minutes"] == 120


class TestGetStatsHistory:
    """Tests for GET /stats/history endpoint."""

    def test_get_stats_history_default_period(self, api_client, mocker):
        """Test stats history with default 30d period."""
        mock_response = StatsHistoryRead(
            period="30d",
            data=[
                StatsHistoryItem(
                    date=datetime.date(2024, 1, 15),
                    cards_studied=25,
                    correct_count=20,
                    accuracy_rate=80.0,
                    study_time_seconds=1800,
                )
            ],
            summary=StatsHistorySummary(
                total_study_time_seconds=1800,
                total_cards_studied=25,
                avg_daily_study_time_seconds=1800,
                avg_daily_cards_studied=25,
                days_with_activity=1,
            ),
        )
        mocker.patch(
            "app.api.stats.StatsService.get_stats_history",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/stats/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["cards_studied"] == 25
        assert data["summary"]["days_with_activity"] == 1

    def test_get_stats_history_with_period_7d(self, api_client, mocker):
        """Test stats history with 7d period parameter."""
        mock_response = StatsHistoryRead(
            period="7d",
            data=[],
            summary=StatsHistorySummary(
                total_study_time_seconds=0,
                total_cards_studied=0,
                avg_daily_study_time_seconds=0,
                avg_daily_cards_studied=0,
                days_with_activity=0,
            ),
        )
        mock_service = mocker.patch(
            "app.api.stats.StatsService.get_stats_history",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/stats/history?period=7d")

        assert response.status_code == 200
        # Verify the service was called with correct period
        mock_service.assert_called_once()
        call_args = mock_service.call_args
        assert call_args[0][2] == "7d"  # Third positional arg is period

    def test_get_stats_history_all_periods(self, api_client, mocker):
        """Test stats history with all period options."""
        mock_response = StatsHistoryRead(
            period="30d",
            data=[],
            summary=StatsHistorySummary(
                total_study_time_seconds=0,
                total_cards_studied=0,
                avg_daily_study_time_seconds=0,
                avg_daily_cards_studied=0,
                days_with_activity=0,
            ),
        )
        mocker.patch(
            "app.api.stats.StatsService.get_stats_history",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        for period in ["7d", "30d", "1y", "all"]:
            response = api_client.get(f"/api/v1/stats/history?period={period}")
            assert response.status_code == 200


class TestGetStatsAccuracy:
    """Tests for GET /stats/accuracy endpoint."""

    def test_get_stats_accuracy_success(self, api_client, mocker):
        """Test successful retrieval of accuracy stats."""
        mock_response = StatsAccuracyRead(
            overall_accuracy=85.5,
            total_reviews=500,
            total_correct=427,
            by_period=AccuracyByPeriod(
                all_time=85.5,
                last_7_days=88.0,
                last_30_days=86.0,
                last_90_days=85.0,
            ),
            by_cefr_level={
                "A1": 95.0,
                "A2": 90.0,
                "B1": 85.0,
                "B2": 80.0,
                "C1": 75.0,
                "C2": 70.0,
            },
            trend="improving",
        )
        mocker.patch(
            "app.api.stats.StatsService.get_stats_accuracy",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/stats/accuracy")

        assert response.status_code == 200
        data = response.json()
        assert data["overall_accuracy"] == 85.5
        assert data["total_reviews"] == 500
        assert data["trend"] == "improving"
        assert data["by_period"]["last_7_days"] == 88.0


class TestGetTodayStats:
    """Tests for GET /stats/today endpoint."""

    def test_get_today_stats_success(self, api_client, mocker):
        """Test successful retrieval of today's stats."""
        mock_response = TodayStatsRead(
            total_study_time_seconds=3600,
            total_cards_studied=50,
            vocabulary=TodayVocabularyStats(
                new_cards_count=10,
                review_cards_count=40,
                review_accuracy=87.5,
                progress=50,
                daily_goal=20,
            ),
        )
        mocker.patch(
            "app.api.stats.StatsService.get_today_stats",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/stats/today")

        assert response.status_code == 200
        data = response.json()
        assert data["total_study_time_seconds"] == 3600
        assert data["total_cards_studied"] == 50
        assert data["vocabulary"]["new_cards_count"] == 10
        assert data["vocabulary"]["review_accuracy"] == 87.5

    def test_get_today_stats_no_activity(self, api_client, mocker):
        """Test today stats when there's no activity."""
        mock_response = TodayStatsRead(
            total_study_time_seconds=0,
            total_cards_studied=0,
            vocabulary=TodayVocabularyStats(
                new_cards_count=0,
                review_cards_count=0,
                review_accuracy=None,
                progress=0,
                daily_goal=20,
            ),
        )
        mocker.patch(
            "app.api.stats.StatsService.get_today_stats",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/stats/today")

        assert response.status_code == 200
        data = response.json()
        assert data["total_cards_studied"] == 0
        assert data["vocabulary"]["review_accuracy"] is None


class TestStatsAPIAuth:
    """Tests for authentication requirements on stats endpoints."""

    def test_total_learned_requires_auth(self, unauthenticated_client):
        """Test that total-learned endpoint requires authentication."""
        response = unauthenticated_client.get("/api/v1/stats/total-learned")
        assert response.status_code == 403  # HTTPBearer returns 403 when no token

    def test_history_requires_auth(self, unauthenticated_client):
        """Test that history endpoint requires authentication."""
        response = unauthenticated_client.get("/api/v1/stats/history")
        assert response.status_code == 403

    def test_accuracy_requires_auth(self, unauthenticated_client):
        """Test that accuracy endpoint requires authentication."""
        response = unauthenticated_client.get("/api/v1/stats/accuracy")
        assert response.status_code == 403

    def test_today_requires_auth(self, unauthenticated_client):
        """Test that today endpoint requires authentication."""
        response = unauthenticated_client.get("/api/v1/stats/today")
        assert response.status_code == 403
