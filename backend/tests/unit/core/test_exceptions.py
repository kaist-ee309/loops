"""Tests for custom exception classes."""

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    LoopsAPIException,
    NotFoundError,
    UnprocessableEntityError,
    ValidationError,
)


class TestLoopsAPIException:
    """Tests for base LoopsAPIException."""

    def test_default_values(self):
        """Test exception with default values."""
        exc = LoopsAPIException(message="Test error")

        assert exc.message == "Test error"
        assert exc.error_type == "api_error"
        assert exc.status_code == 500
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_custom_values(self):
        """Test exception with custom values."""
        exc = LoopsAPIException(
            message="Custom error",
            error_type="custom_type",
            status_code=418,
            details={"foo": "bar"},
        )

        assert exc.message == "Custom error"
        assert exc.error_type == "custom_type"
        assert exc.status_code == 418
        assert exc.details == {"foo": "bar"}


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_defaults(self):
        """Test ValidationError default values."""
        exc = ValidationError(message="Invalid input")

        assert exc.message == "Invalid input"
        assert exc.error_type == "validation_error"
        assert exc.status_code == 400
        assert exc.details == {}

    def test_validation_error_with_details(self):
        """Test ValidationError with details."""
        exc = ValidationError(
            message="Invalid input",
            details={"field": "email", "reason": "invalid format"},
        )

        assert exc.details == {"field": "email", "reason": "invalid format"}


class TestUnprocessableEntityError:
    """Tests for UnprocessableEntityError."""

    def test_unprocessable_entity_error_defaults(self):
        """Test UnprocessableEntityError default values."""
        exc = UnprocessableEntityError(message="Cannot process request")

        assert exc.message == "Cannot process request"
        assert exc.error_type == "unprocessable_entity"
        assert exc.status_code == 422
        assert exc.details == {}

    def test_unprocessable_entity_error_with_details(self):
        """Test UnprocessableEntityError with details."""
        exc = UnprocessableEntityError(
            message="Cannot process",
            details={"reason": "conflicting values"},
        )

        assert exc.details == {"reason": "conflicting values"}


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_authentication_error_default_message(self):
        """Test AuthenticationError default message."""
        exc = AuthenticationError()

        assert exc.message == "Authentication failed"
        assert exc.error_type == "authentication_error"
        assert exc.status_code == 401

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError custom message."""
        exc = AuthenticationError(message="Invalid token")

        assert exc.message == "Invalid token"


class TestAuthorizationError:
    """Tests for AuthorizationError."""

    def test_authorization_error_default_message(self):
        """Test AuthorizationError default message."""
        exc = AuthorizationError()

        assert exc.message == "Permission denied"
        assert exc.error_type == "authorization_error"
        assert exc.status_code == 403

    def test_authorization_error_custom_message(self):
        """Test AuthorizationError custom message."""
        exc = AuthorizationError(message="Insufficient permissions")

        assert exc.message == "Insufficient permissions"


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_not_found_error_without_resource(self):
        """Test NotFoundError without resource."""
        exc = NotFoundError(message="Item not found")

        assert exc.message == "Item not found"
        assert exc.error_type == "not_found"
        assert exc.status_code == 404
        assert exc.details == {}

    def test_not_found_error_with_resource(self):
        """Test NotFoundError with resource."""
        exc = NotFoundError(message="Card not found", resource="card")

        assert exc.details == {"resource": "card"}


class TestConflictError:
    """Tests for ConflictError."""

    def test_conflict_error_defaults(self):
        """Test ConflictError default values."""
        exc = ConflictError(message="Resource already exists")

        assert exc.message == "Resource already exists"
        assert exc.error_type == "conflict"
        assert exc.status_code == 409
        assert exc.details == {}

    def test_conflict_error_with_details(self):
        """Test ConflictError with details."""
        exc = ConflictError(
            message="Duplicate entry",
            details={"field": "email", "value": "test@example.com"},
        )

        assert exc.details == {"field": "email", "value": "test@example.com"}


class TestDatabaseError:
    """Tests for DatabaseError."""

    def test_database_error_default_message(self):
        """Test DatabaseError default message."""
        exc = DatabaseError()

        assert exc.message == "Database operation failed"
        assert exc.error_type == "database_error"
        assert exc.status_code == 500

    def test_database_error_custom_message(self):
        """Test DatabaseError custom message."""
        exc = DatabaseError(message="Connection timeout")

        assert exc.message == "Connection timeout"


class TestExternalServiceError:
    """Tests for ExternalServiceError."""

    def test_external_service_error_without_service(self):
        """Test ExternalServiceError without service."""
        exc = ExternalServiceError(message="Service unavailable")

        assert exc.message == "Service unavailable"
        assert exc.error_type == "external_service_error"
        assert exc.status_code == 503
        assert exc.details == {}

    def test_external_service_error_with_service(self):
        """Test ExternalServiceError with service."""
        exc = ExternalServiceError(message="TTS failed", service="tts")

        assert exc.details == {"service": "tts"}
