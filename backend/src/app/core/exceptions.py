"""Custom exception classes for the application."""

from typing import Any


class LoopsAPIException(Exception):
    """Base exception for all Loops API custom exceptions."""

    def __init__(
        self,
        message: str,
        error_type: str = "api_error",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(LoopsAPIException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_type="validation_error",
            status_code=400,
            details=details,
        )


class UnprocessableEntityError(LoopsAPIException):
    """Raised when request is well-formed but cannot be processed (HTTP 422)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_type="unprocessable_entity",
            status_code=422,
            details=details,
        )


class AuthenticationError(LoopsAPIException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_type="authentication_error",
            status_code=401,
        )


class AuthorizationError(LoopsAPIException):
    """Raised when user doesn't have permission."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            error_type="authorization_error",
            status_code=403,
        )


class NotFoundError(LoopsAPIException):
    """Raised when a resource is not found."""

    def __init__(self, message: str, resource: str | None = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message=message,
            error_type="not_found",
            status_code=404,
            details=details,
        )


class ConflictError(LoopsAPIException):
    """Raised when there's a conflict (e.g., duplicate resource)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_type="conflict",
            status_code=409,
            details=details,
        )


class DatabaseError(LoopsAPIException):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            error_type="database_error",
            status_code=500,
        )


class ExternalServiceError(LoopsAPIException):
    """Raised when an external service (TTS, etc.) fails."""

    def __init__(self, message: str, service: str | None = None):
        details = {"service": service} if service else {}
        super().__init__(
            message=message,
            error_type="external_service_error",
            status_code=503,
            details=details,
        )
