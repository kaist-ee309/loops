"""Tests for dependencies module."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.dependencies import get_current_active_profile, get_current_profile


class TestGetCurrentProfile:
    """Tests for get_current_profile dependency."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_profile(self, mocker):
        """Test that valid token returns the user profile."""
        from app.models import Profile

        user_id = uuid4()
        mock_profile = Profile(id=user_id, daily_goal=20)

        # Mock credentials
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"

        # Mock session
        mock_session = AsyncMock()

        # Mock verify_supabase_token
        mocker.patch(
            "app.core.dependencies.verify_supabase_token",
            return_value=str(user_id),
        )

        # Mock ProfileService.get_profile
        mocker.patch(
            "app.core.dependencies.ProfileService.get_profile",
            new_callable=AsyncMock,
            return_value=mock_profile,
        )

        result = await get_current_profile(mock_credentials, mock_session)

        assert result.id == user_id

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, mocker):
        """Test that invalid token raises 401 HTTPException."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid_token"
        mock_session = AsyncMock()

        # Mock verify_supabase_token to return None
        mocker.patch(
            "app.core.dependencies.verify_supabase_token",
            return_value=None,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_profile(mock_credentials, mock_session)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_profile_not_found_raises_401(self, mocker):
        """Test that missing profile raises 401 HTTPException."""
        user_id = uuid4()
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid_token"
        mock_session = AsyncMock()

        # Mock verify_supabase_token
        mocker.patch(
            "app.core.dependencies.verify_supabase_token",
            return_value=str(user_id),
        )

        # Mock ProfileService.get_profile to return None
        mocker.patch(
            "app.core.dependencies.ProfileService.get_profile",
            new_callable=AsyncMock,
            return_value=None,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_profile(mock_credentials, mock_session)

        assert exc_info.value.status_code == 401


class TestGetCurrentActiveProfile:
    """Tests for get_current_active_profile dependency."""

    @pytest.mark.asyncio
    async def test_returns_profile_as_is(self):
        """Test that get_current_active_profile returns profile unchanged."""
        from app.models import Profile

        mock_profile = Profile(id=uuid4(), daily_goal=20)

        result = await get_current_active_profile(mock_profile)

        assert result is mock_profile
