"""Tests for security module."""

from unittest.mock import MagicMock

from app.core.security import (
    get_supabase_admin_client,
    get_supabase_client,
    verify_supabase_token,
)


class TestGetSupabaseClient:
    """Tests for get_supabase_client function."""

    def test_get_supabase_client_creates_client(self, mocker):
        """Test that get_supabase_client creates and caches client."""
        import app.core.security as security_module

        # Reset global state
        security_module._supabase_client = None

        mock_client = MagicMock()
        mock_create = mocker.patch("app.core.security.create_client", return_value=mock_client)

        client = get_supabase_client()

        assert client is mock_client
        mock_create.assert_called_once()

    def test_get_supabase_client_returns_cached(self, mocker):
        """Test that get_supabase_client returns cached client."""
        import app.core.security as security_module

        mock_client = MagicMock()
        security_module._supabase_client = mock_client

        client = get_supabase_client()

        assert client is mock_client


class TestGetSupabaseAdminClient:
    """Tests for get_supabase_admin_client function."""

    def test_get_admin_client_creates_client(self, mocker):
        """Test that get_supabase_admin_client creates and caches client."""
        import app.core.security as security_module

        # Reset global state
        security_module._supabase_admin_client = None

        mock_client = MagicMock()
        mock_create = mocker.patch("app.core.security.create_client", return_value=mock_client)

        # Ensure secret key is set
        mocker.patch("app.core.security.settings.supabase_secret_key", "test_secret")

        client = get_supabase_admin_client()

        assert client is mock_client
        mock_create.assert_called_once()

    def test_get_admin_client_returns_cached(self, mocker):
        """Test that get_supabase_admin_client returns cached client."""
        import app.core.security as security_module

        mock_client = MagicMock()
        security_module._supabase_admin_client = mock_client

        client = get_supabase_admin_client()

        assert client is mock_client


class TestVerifySupabaseToken:
    """Tests for verify_supabase_token function."""

    def test_verify_valid_token(self, mocker):
        """Test verifying a valid token."""
        mock_user = MagicMock()
        mock_user.id = "test-user-id"

        mock_response = MagicMock()
        mock_response.user = mock_user

        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = mock_response

        mocker.patch("app.core.security.get_supabase_client", return_value=mock_client)

        result = verify_supabase_token("valid_token")

        assert result == "test-user-id"
        mock_client.auth.get_user.assert_called_once_with("valid_token")

    def test_verify_invalid_token(self, mocker):
        """Test verifying an invalid token returns None."""
        mock_response = MagicMock()
        mock_response.user = None

        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = mock_response

        mocker.patch("app.core.security.get_supabase_client", return_value=mock_client)

        result = verify_supabase_token("invalid_token")

        assert result is None

    def test_verify_token_exception(self, mocker):
        """Test that exceptions during verification return None."""
        mock_client = MagicMock()
        mock_client.auth.get_user.side_effect = Exception("Network error")

        mocker.patch("app.core.security.get_supabase_client", return_value=mock_client)

        result = verify_supabase_token("any_token")

        assert result is None

    def test_verify_token_no_response(self, mocker):
        """Test verifying token when response is None."""
        mock_client = MagicMock()
        mock_client.auth.get_user.return_value = None

        mocker.patch("app.core.security.get_supabase_client", return_value=mock_client)

        result = verify_supabase_token("some_token")

        assert result is None
