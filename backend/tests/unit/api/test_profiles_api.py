"""Tests for Profiles API endpoints."""

from datetime import date
from unittest.mock import AsyncMock

from app.models import (
    Profile,
)


class TestGetCurrentProfile:
    """Tests for GET /profiles/me endpoint."""

    def test_get_current_profile_success(self, api_client, mock_profile):
        """Test successful retrieval of current profile."""
        response = api_client.get("/api/v1/profiles/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(mock_profile.id)
        assert data["daily_goal"] == mock_profile.daily_goal

    def test_get_current_profile_requires_auth(self, unauthenticated_client):
        """Test that profile retrieval requires authentication."""
        response = unauthenticated_client.get("/api/v1/profiles/me")
        assert response.status_code == 403


class TestGetTodayProgress:
    """Tests for GET /profiles/me/today-progress endpoint."""

    def test_get_today_progress_success(self, api_client, mocker):
        """Test successful retrieval of today's progress."""
        mock_progress = {
            "total_reviews": 15,
            "correct_count": 12,
            "wrong_count": 3,
            "accuracy_rate": 80.0,
            "daily_goal": 20,
            "goal_progress": 75.0,
        }

        mocker.patch(
            "app.api.profiles.UserCardProgressService.get_today_progress",
            new_callable=AsyncMock,
            return_value=mock_progress,
        )

        response = api_client.get("/api/v1/profiles/me/today-progress")

        assert response.status_code == 200
        data = response.json()
        assert data["total_reviews"] == 15
        assert data["correct_count"] == 12
        assert data["accuracy_rate"] == 80.0

    def test_get_today_progress_requires_auth(self, unauthenticated_client):
        """Test that today's progress requires authentication."""
        response = unauthenticated_client.get("/api/v1/profiles/me/today-progress")
        assert response.status_code == 403


class TestGetDailyGoal:
    """Tests for GET /profiles/me/daily-goal endpoint."""

    def test_get_daily_goal_success(self, api_client, mocker):
        """Test successful retrieval of daily goal."""
        mock_daily_goal = {
            "daily_goal": 20,
            "completed_today": 10,
        }

        mocker.patch(
            "app.api.profiles.ProfileService.get_daily_goal",
            new_callable=AsyncMock,
            return_value=mock_daily_goal,
        )

        response = api_client.get("/api/v1/profiles/me/daily-goal")

        assert response.status_code == 200
        data = response.json()
        assert data["daily_goal"] == 20
        assert data["completed_today"] == 10

    def test_get_daily_goal_not_found(self, api_client, mocker):
        """Test 404 when profile not found."""
        mocker.patch(
            "app.api.profiles.ProfileService.get_daily_goal",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.get("/api/v1/profiles/me/daily-goal")

        assert response.status_code == 404

    def test_get_daily_goal_requires_auth(self, unauthenticated_client):
        """Test that daily goal requires authentication."""
        response = unauthenticated_client.get("/api/v1/profiles/me/daily-goal")
        assert response.status_code == 403


class TestGetProfileConfig:
    """Tests for GET /profiles/me/config endpoint."""

    def test_get_profile_config_success(self, api_client, mock_profile, mocker):
        """Test successful retrieval of profile config."""
        # The endpoint constructs ProfileConfigRead directly from profile attributes
        # We need to ensure the mock_profile has all required fields for ProfileConfigRead

        response = api_client.get("/api/v1/profiles/me/config")

        assert response.status_code == 200
        data = response.json()
        assert data["daily_goal"] == mock_profile.daily_goal
        assert data["select_all_decks"] == mock_profile.select_all_decks
        assert data["theme"] == mock_profile.theme
        assert data["review_ratio_mode"] == mock_profile.review_ratio_mode
        assert data["custom_review_ratio"] == mock_profile.custom_review_ratio
        assert data["min_new_ratio"] == mock_profile.min_new_ratio
        assert data["review_scope"] == mock_profile.review_scope
        assert data["highlight_color"] == mock_profile.highlight_color

    def test_get_profile_config_requires_auth(self, unauthenticated_client):
        """Test that profile config requires authentication."""
        response = unauthenticated_client.get("/api/v1/profiles/me/config")
        assert response.status_code == 403


class TestUpdateProfileConfig:
    """Tests for PUT /profiles/me/config endpoint."""

    def test_update_profile_config_success(self, api_client, mock_profile, mocker):
        """Test successful profile config update."""
        updated_profile = Profile(
            id=mock_profile.id,
            daily_goal=30,
            select_all_decks=False,
            timezone="Asia/Seoul",
            theme="dark",
            notification_enabled=False,
            review_ratio_mode="normal",
            custom_review_ratio=0.7,
            min_new_ratio=0.2,
            review_scope="selected_decks_only",
            highlight_color="#FF5733",
        )

        mocker.patch(
            "app.api.profiles.ProfileService.update_profile_config",
            new_callable=AsyncMock,
            return_value=updated_profile,
        )

        response = api_client.put(
            "/api/v1/profiles/me/config",
            json={"daily_goal": 30, "theme": "dark"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["daily_goal"] == 30
        assert data["theme"] == "dark"
        assert data["review_ratio_mode"] == "normal"
        assert data["highlight_color"] == "#FF5733"

    def test_update_profile_config_invalid_theme(self, api_client):
        """Test validation error for invalid theme."""
        response = api_client.put(
            "/api/v1/profiles/me/config",
            json={"theme": "invalid_theme"},
        )

        # Pydantic validator raises ValueError which FastAPI converts to 400/422
        assert response.status_code in [400, 422]

    def test_update_profile_config_requires_auth(self, unauthenticated_client):
        """Test that config update requires authentication."""
        response = unauthenticated_client.put(
            "/api/v1/profiles/me/config",
            json={"daily_goal": 30},
        )
        assert response.status_code == 403


class TestGetProfileLevel:
    """Tests for GET /profiles/me/level endpoint."""

    def test_get_profile_level_success(self, api_client, mocker):
        """Test successful retrieval of profile level."""
        mock_level = {
            "level": 5.5,
            "cefr_equivalent": "B1",
            "total_reviews": 150,
            "accuracy_rate": 85.0,
            "mastered_cards": 75,
        }

        mocker.patch(
            "app.api.profiles.ProfileService.calculate_profile_level",
            new_callable=AsyncMock,
            return_value=mock_level,
        )

        response = api_client.get("/api/v1/profiles/me/level")

        assert response.status_code == 200
        data = response.json()
        assert data["level"] == 5.5
        assert data["cefr_equivalent"] == "B1"
        assert data["mastered_cards"] == 75

    def test_get_profile_level_requires_auth(self, unauthenticated_client):
        """Test that profile level requires authentication."""
        response = unauthenticated_client.get("/api/v1/profiles/me/level")
        assert response.status_code == 403


class TestUpdateProfile:
    """Tests for PATCH /profiles/me endpoint."""

    def test_update_profile_success(self, api_client, mock_profile, mocker):
        """Test successful profile update."""
        updated_profile = Profile(
            id=mock_profile.id,
            daily_goal=50,
            select_all_decks=True,
            timezone="Asia/Seoul",
            theme="dark",
            notification_enabled=True,
            review_ratio_mode="normal",
            custom_review_ratio=0.7,
            min_new_ratio=0.2,
            review_scope="all_learned",
            highlight_color="#FF5733",
        )

        mocker.patch(
            "app.api.profiles.ProfileService.update_profile",
            new_callable=AsyncMock,
            return_value=updated_profile,
        )

        response = api_client.patch(
            "/api/v1/profiles/me",
            json={"daily_goal": 50},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["daily_goal"] == 50

    def test_update_profile_not_found(self, api_client, mocker):
        """Test 404 when updating non-existent profile."""
        mocker.patch(
            "app.api.profiles.ProfileService.update_profile",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.patch(
            "/api/v1/profiles/me",
            json={"daily_goal": 50},
        )

        assert response.status_code == 404

    def test_update_profile_requires_auth(self, unauthenticated_client):
        """Test that profile update requires authentication."""
        response = unauthenticated_client.patch(
            "/api/v1/profiles/me",
            json={"daily_goal": 50},
        )
        assert response.status_code == 403


class TestDeleteProfile:
    """Tests for DELETE /profiles/me endpoint."""

    def test_delete_profile_success(self, api_client, mocker):
        """Test successful profile deletion."""
        mocker.patch(
            "app.api.profiles.ProfileService.delete_profile",
            new_callable=AsyncMock,
            return_value=True,
        )

        response = api_client.delete("/api/v1/profiles/me")

        assert response.status_code == 204

    def test_delete_profile_not_found(self, api_client, mocker):
        """Test 404 when deleting non-existent profile."""
        mocker.patch(
            "app.api.profiles.ProfileService.delete_profile",
            new_callable=AsyncMock,
            return_value=False,
        )

        response = api_client.delete("/api/v1/profiles/me")

        assert response.status_code == 404

    def test_delete_profile_requires_auth(self, unauthenticated_client):
        """Test that profile deletion requires authentication."""
        response = unauthenticated_client.delete("/api/v1/profiles/me")
        assert response.status_code == 403


class TestGetProfileStreak:
    """Tests for GET /profiles/me/streak endpoint."""

    def test_get_profile_streak_success(self, api_client, mocker):
        """Test successful retrieval of profile streak."""
        mock_streak = {
            "current_streak": 7,
            "longest_streak": 15,
            "last_study_date": date(2024, 1, 15),
            "days_studied_this_month": 12,
            "streak_status": "active",
            "message": "7일 연속 학습 중!",
        }

        mocker.patch(
            "app.api.profiles.ProfileService.get_profile_streak",
            new_callable=AsyncMock,
            return_value=mock_streak,
        )

        response = api_client.get("/api/v1/profiles/me/streak")

        assert response.status_code == 200
        data = response.json()
        assert data["current_streak"] == 7
        assert data["longest_streak"] == 15
        assert data["streak_status"] == "active"

    def test_get_profile_streak_requires_auth(self, unauthenticated_client):
        """Test that profile streak requires authentication."""
        response = unauthenticated_client.get("/api/v1/profiles/me/streak")
        assert response.status_code == 403
