"""Tests for SupabaseStorageService."""

from unittest.mock import MagicMock

from app.services.supabase_storage_service import SupabaseStorageService


class TestPublicUrl:
    """Tests for public URL generation."""

    def test_public_url_basic(self, mocker):
        """Test basic URL generation."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        url = SupabaseStorageService.public_url(
            bucket="card-images",
            path="images/test.png",
        )

        assert (
            url == "https://test.supabase.co/storage/v1/object/public/card-images/images/test.png"
        )

    def test_public_url_encoding(self, mocker):
        """Test URL encoding for special characters."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        # Path with spaces and special characters
        url = SupabaseStorageService.public_url(
            bucket="card-images",
            path="images/test file (1).png",
        )

        # Spaces should be encoded as %20
        assert "%20" in url or "+" in url
        # Parentheses should be encoded
        assert "test%20file%20%281%29.png" in url or "test+file" in url

    def test_public_url_preserves_slashes(self, mocker):
        """Test that slashes in path are preserved."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        url = SupabaseStorageService.public_url(
            bucket="card-images",
            path="folder/subfolder/image.png",
        )

        assert "folder/subfolder/image.png" in url

    def test_public_url_different_bucket(self, mocker):
        """Test URL with different bucket name."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        url = SupabaseStorageService.public_url(
            bucket="user-uploads",
            path="file.txt",
        )

        assert "user-uploads" in url
        assert "file.txt" in url


class TestUploadBytes:
    """Tests for file upload functionality."""

    def test_upload_bytes_success(self, mocker):
        """Test successful file upload with mocked client."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        # Mock Supabase client
        mock_bucket = MagicMock()
        mock_bucket.upload.return_value = None

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket

        mock_client = MagicMock()
        mock_client.storage = mock_storage

        mocker.patch(
            "app.services.supabase_storage_service.get_supabase_admin_client",
            return_value=mock_client,
        )

        url = SupabaseStorageService.upload_bytes(
            bucket="card-images",
            path="test/image.png",
            data=b"fake_image_data",
            mime_type="image/png",
        )

        # Verify upload was called
        mock_storage.from_.assert_called_once_with("card-images")
        mock_bucket.upload.assert_called_once()

        # Verify return URL
        assert "test.supabase.co" in url
        assert "card-images" in url
        assert "test/image.png" in url

    def test_upload_bytes_returns_url(self, mocker):
        """Test that upload returns proper public URL."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://project.supabase.co",
        )

        mock_bucket = MagicMock()
        mock_bucket.upload.return_value = None

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket

        mock_client = MagicMock()
        mock_client.storage = mock_storage

        mocker.patch(
            "app.services.supabase_storage_service.get_supabase_admin_client",
            return_value=mock_client,
        )

        url = SupabaseStorageService.upload_bytes(
            bucket="my-bucket",
            path="folder/file.jpg",
            data=b"data",
            mime_type="image/jpeg",
        )

        expected_url = (
            "https://project.supabase.co/storage/v1/object/public/my-bucket/folder/file.jpg"
        )
        assert url == expected_url

    def test_upload_bytes_upsert_behavior(self, mocker):
        """Test that upload uses upsert option."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        mock_bucket = MagicMock()
        mock_bucket.upload.return_value = None

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket

        mock_client = MagicMock()
        mock_client.storage = mock_storage

        mocker.patch(
            "app.services.supabase_storage_service.get_supabase_admin_client",
            return_value=mock_client,
        )

        SupabaseStorageService.upload_bytes(
            bucket="test-bucket",
            path="file.png",
            data=b"data",
            mime_type="image/png",
        )

        # Verify file_options includes upsert
        call_kwargs = mock_bucket.upload.call_args.kwargs
        assert call_kwargs["file_options"]["upsert"] is True
        assert call_kwargs["file_options"]["content-type"] == "image/png"

    def test_upload_bytes_correct_arguments(self, mocker):
        """Test that upload passes correct arguments."""
        mocker.patch(
            "app.services.supabase_storage_service.settings.supabase_url",
            "https://test.supabase.co",
        )

        mock_bucket = MagicMock()
        mock_bucket.upload.return_value = None

        mock_storage = MagicMock()
        mock_storage.from_.return_value = mock_bucket

        mock_client = MagicMock()
        mock_client.storage = mock_storage

        mocker.patch(
            "app.services.supabase_storage_service.get_supabase_admin_client",
            return_value=mock_client,
        )

        test_data = b"test_binary_content"

        SupabaseStorageService.upload_bytes(
            bucket="uploads",
            path="path/to/file.bin",
            data=test_data,
            mime_type="application/octet-stream",
        )

        call_kwargs = mock_bucket.upload.call_args.kwargs
        assert call_kwargs["path"] == "path/to/file.bin"
        assert call_kwargs["file"] == test_data
