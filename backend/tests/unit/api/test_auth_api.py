"""Tests for Auth API endpoints."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from app.models import Profile


def make_profile() -> Profile:
    """Create a Profile instance for testing."""
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
        created_at=datetime(2024, 1, 15),
        updated_at=None,
    )


class TestRegister:
    """Tests for POST /auth/register endpoint."""

    def test_register_success(self, api_client, mocker):
        """Test successful user registration."""
        mock_profile = make_profile()
        mock_user = MagicMock()
        mock_user.id = str(mock_profile.id)

        mock_session = MagicMock()
        mock_session.access_token = "test_access_token"
        mock_session.refresh_token = "test_refresh_token"

        mock_auth_response = MagicMock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase = MagicMock()
        mock_supabase.auth.sign_up.return_value = mock_auth_response

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)
        mocker.patch(
            "app.api.auth.ProfileService.create_profile",
            return_value=mock_profile,
        )

        response = api_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "securePassword123"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["refresh_token"] == "test_refresh_token"
        assert data["token_type"] == "bearer"

    def test_register_supabase_error(self, api_client, mocker):
        """Test registration failure when Supabase returns error."""
        mock_supabase = MagicMock()
        mock_supabase.auth.sign_up.side_effect = Exception("Email already registered")

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)

        response = api_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "securePassword123"},
        )

        assert response.status_code == 400

    def test_register_supabase_returns_none(self, api_client, mocker):
        """Test registration failure when Supabase returns None user/session."""
        mock_auth_response = MagicMock()
        mock_auth_response.user = None
        mock_auth_response.session = None

        mock_supabase = MagicMock()
        mock_supabase.auth.sign_up.return_value = mock_auth_response

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)

        response = api_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "securePassword123"},
        )

        assert response.status_code == 400

    def test_register_invalid_email(self, api_client):
        """Test registration with invalid email format."""
        response = api_client.post(
            "/api/v1/auth/register",
            json={"email": "invalid-email", "password": "securePassword123"},
        )

        # App returns 400 for validation errors
        assert response.status_code == 400

    def test_register_short_password(self, api_client):
        """Test registration with password too short."""
        response = api_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "short"},
        )

        # App returns 400 for validation errors
        assert response.status_code == 400


class TestLogin:
    """Tests for POST /auth/login endpoint."""

    def test_login_success(self, api_client, mocker):
        """Test successful login."""
        mock_profile = make_profile()
        mock_user = MagicMock()
        mock_user.id = str(mock_profile.id)

        mock_session = MagicMock()
        mock_session.access_token = "test_access_token"
        mock_session.refresh_token = "test_refresh_token"

        mock_auth_response = MagicMock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase = MagicMock()
        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)
        mocker.patch(
            "app.api.auth.ProfileService.get_profile",
            return_value=mock_profile,
        )

        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "securePassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, api_client, mocker):
        """Test login with invalid credentials."""
        mock_supabase = MagicMock()
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)

        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongPassword"},
        )

        assert response.status_code == 401

    def test_login_profile_not_found(self, api_client, mocker):
        """Test login when profile not found in local DB."""
        mock_user = MagicMock()
        mock_user.id = str(uuid4())

        mock_session = MagicMock()
        mock_session.access_token = "test_access_token"
        mock_session.refresh_token = "test_refresh_token"

        mock_auth_response = MagicMock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase = MagicMock()
        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)
        mocker.patch(
            "app.api.auth.ProfileService.get_profile",
            return_value=None,
        )

        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "securePassword123"},
        )

        assert response.status_code == 404


class TestRefreshToken:
    """Tests for POST /auth/refresh endpoint."""

    def test_refresh_token_success(self, api_client, mocker):
        """Test successful token refresh."""
        mock_profile = make_profile()
        mock_user = MagicMock()
        mock_user.id = str(mock_profile.id)

        mock_session = MagicMock()
        mock_session.access_token = "new_access_token"
        mock_session.refresh_token = "new_refresh_token"

        mock_auth_response = MagicMock()
        mock_auth_response.user = mock_user
        mock_auth_response.session = mock_session

        mock_supabase = MagicMock()
        mock_supabase.auth.refresh_session.return_value = mock_auth_response

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)
        mocker.patch(
            "app.api.auth.ProfileService.get_profile",
            return_value=mock_profile,
        )

        response = api_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "old_refresh_token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token"
        assert data["refresh_token"] == "new_refresh_token"

    def test_refresh_token_invalid(self, api_client, mocker):
        """Test token refresh with invalid refresh token."""
        mock_supabase = MagicMock()
        mock_supabase.auth.refresh_session.side_effect = Exception("Invalid token")

        mocker.patch("app.api.auth.get_supabase_client", return_value=mock_supabase)

        response = api_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /auth/logout endpoint."""

    def test_logout_success(self, api_client):
        """Test successful logout."""
        response = api_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_logout_requires_auth(self, unauthenticated_client):
        """Test that logout requires authentication."""
        response = unauthenticated_client.post("/api/v1/auth/logout")
        assert response.status_code == 403


class TestGetCurrentUser:
    """Tests for GET /auth/me endpoint."""

    def test_get_current_user_success(self, api_client, mock_profile):
        """Test successful retrieval of current user."""
        response = api_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(mock_profile.id)
        assert data["daily_goal"] == mock_profile.daily_goal

    def test_get_current_user_requires_auth(self, unauthenticated_client):
        """Test that getting current user requires authentication."""
        response = unauthenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 403
