"""Tests for GeminiImageService."""

from unittest.mock import MagicMock

import pytest

from app.services.gemini_image_service import GeminiImageService, GeneratedImage


class TestGeminiImageService:
    """Tests for Gemini image generation service."""

    def test_generate_image_success(self, mocker):
        """Test successful image generation with mocked client."""
        # Mock settings
        mocker.patch("app.services.gemini_image_service.settings.gemini_api_key", "test_key")
        mocker.patch(
            "app.services.gemini_image_service.settings.gemini_image_model",
            "gemini-3-pro-image-preview",
        )

        # Create mock response structure
        mock_inline_data = MagicMock()
        mock_inline_data.mime_type = "image/png"
        mock_inline_data.data = b"fake_image_bytes"

        mock_part = MagicMock()
        mock_part.inline_data = mock_inline_data

        mock_response = MagicMock()
        mock_response.parts = [mock_part]

        # Mock the client
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        mocker.patch("google.genai.Client", return_value=mock_client)

        result = GeminiImageService.generate_image("A cute cat")

        assert isinstance(result, GeneratedImage)
        assert result.bytes == b"fake_image_bytes"
        assert result.mime_type == "image/png"

    def test_generate_image_returns_bytes(self, mocker):
        """Test that generate_image returns bytes data."""
        mocker.patch("app.services.gemini_image_service.settings.gemini_api_key", "test_key")
        mocker.patch(
            "app.services.gemini_image_service.settings.gemini_image_model",
            "gemini-3-pro-image-preview",
        )

        # Create mock with JPEG response
        mock_inline_data = MagicMock()
        mock_inline_data.mime_type = "image/jpeg"
        mock_inline_data.data = b"\xff\xd8\xff\xe0"  # JPEG header bytes

        mock_part = MagicMock()
        mock_part.inline_data = mock_inline_data

        mock_response = MagicMock()
        mock_response.parts = [mock_part]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        mocker.patch("google.genai.Client", return_value=mock_client)

        result = GeminiImageService.generate_image("A dog")

        assert isinstance(result.bytes, bytes)
        assert len(result.bytes) > 0
        assert result.mime_type == "image/jpeg"

    def test_generate_image_missing_api_key(self, mocker):
        """Test error when API key is missing."""
        mocker.patch("app.services.gemini_image_service.settings.gemini_api_key", None)

        with pytest.raises(RuntimeError, match="Missing GEMINI_API_KEY"):
            GeminiImageService.generate_image("A prompt")

    def test_generate_image_no_image_data(self, mocker):
        """Test error when response contains no image data."""
        mocker.patch("app.services.gemini_image_service.settings.gemini_api_key", "test_key")
        mocker.patch(
            "app.services.gemini_image_service.settings.gemini_image_model",
            "gemini-3-pro-image-preview",
        )

        # Create mock response with no inline data
        mock_part = MagicMock()
        mock_part.inline_data = None

        mock_response = MagicMock()
        mock_response.parts = [mock_part]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        mocker.patch("google.genai.Client", return_value=mock_client)

        with pytest.raises(RuntimeError, match="returned no inline image data"):
            GeminiImageService.generate_image("A prompt")

    def test_generate_image_custom_model(self, mocker):
        """Test using custom model ID."""
        mocker.patch("app.services.gemini_image_service.settings.gemini_api_key", "test_key")
        mocker.patch(
            "app.services.gemini_image_service.settings.gemini_image_model",
            "default-model",
        )

        mock_inline_data = MagicMock()
        mock_inline_data.mime_type = "image/png"
        mock_inline_data.data = b"image_data"

        mock_part = MagicMock()
        mock_part.inline_data = mock_inline_data

        mock_response = MagicMock()
        mock_response.parts = [mock_part]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        mocker.patch("google.genai.Client", return_value=mock_client)

        GeminiImageService.generate_image("A prompt", model="custom-model")

        # Verify custom model was used
        call_args = mock_client.models.generate_content.call_args
        assert call_args.kwargs["model"] == "custom-model"

    def test_generate_image_empty_data(self, mocker):
        """Test error when response has empty data."""
        mocker.patch("app.services.gemini_image_service.settings.gemini_api_key", "test_key")
        mocker.patch(
            "app.services.gemini_image_service.settings.gemini_image_model",
            "gemini-3-pro-image-preview",
        )

        # Create mock response with empty data
        mock_inline_data = MagicMock()
        mock_inline_data.mime_type = "image/png"
        mock_inline_data.data = None  # Empty data

        mock_part = MagicMock()
        mock_part.inline_data = mock_inline_data

        mock_response = MagicMock()
        mock_response.parts = [mock_part]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)

        mocker.patch("google.genai.Client", return_value=mock_client)

        with pytest.raises(RuntimeError, match="returned no inline image data"):
            GeminiImageService.generate_image("A prompt")
