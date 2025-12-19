"""Tests for main application module."""

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import LoopsAPIException, NotFoundError
from app.main import app


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_api_info(self):
        """Test that root endpoint returns API info."""
        with TestClient(app) as client:
            response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome to Loops API" in data["message"]
        assert "version" in data
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_returns_status(self):
        """Test health check endpoint returns status information."""
        with TestClient(app) as client:
            response = client.get("/health")

        # Should return either 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "database" in data


class TestExceptionHandlers:
    """Tests for exception handlers."""

    def test_validation_error_returns_400(self, api_client):
        """Test that validation errors return 400."""
        # Send invalid JSON type (api_client has auth mocked)
        response = api_client.post("/api/v1/study/session/preview", json={"total_cards": "invalid"})

        # Custom handler returns 400 for validation errors
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "validation_error"

    def test_loops_api_exception_handler(self):
        """Test custom LoopsAPIException handler."""
        # Create a test app with an endpoint that raises LoopsAPIException
        test_app = FastAPI()

        @test_app.get("/test-error")
        async def test_error_endpoint():
            raise NotFoundError(message="Test resource not found", resource="test")

        # Import and add the exception handler
        from app.main import loops_api_exception_handler

        test_app.add_exception_handler(LoopsAPIException, loops_api_exception_handler)

        with TestClient(test_app) as client:
            response = client.get("/test-error")

        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "not_found"
        assert data["message"] == "Test resource not found"
        assert data["resource"] == "test"

    def test_generic_exception_handler_debug_mode(self):
        """Test generic exception handler in debug mode."""
        test_app = FastAPI()

        @test_app.get("/test-generic-error")
        async def test_generic_error():
            raise RuntimeError("Unexpected error")

        from app.main import generic_exception_handler

        test_app.add_exception_handler(Exception, generic_exception_handler)

        with patch("app.main.settings") as mock_settings:
            mock_settings.debug = True
            with TestClient(test_app, raise_server_exceptions=False) as client:
                response = client.get("/test-generic-error")

        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "internal_server_error"
        assert "Unexpected error" in data["message"]
        assert "traceback" in data

    def test_generic_exception_handler_production_mode(self):
        """Test generic exception handler in production mode."""
        test_app = FastAPI()

        @test_app.get("/test-prod-error")
        async def test_prod_error():
            raise RuntimeError("Secret error details")

        from app.main import generic_exception_handler

        test_app.add_exception_handler(Exception, generic_exception_handler)

        with patch("app.main.settings") as mock_settings:
            mock_settings.debug = False
            with TestClient(test_app, raise_server_exceptions=False) as client:
                response = client.get("/test-prod-error")

        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "internal_server_error"
        # Should not expose internal error details
        assert "Secret error details" not in data["message"]
        assert "traceback" not in data


class TestMiddleware:
    """Tests for middleware."""

    def test_request_id_middleware(self):
        """Test that request ID is added to responses."""
        with TestClient(app) as client:
            response = client.get("/")

        # Check that X-Request-ID header is present
        assert "x-request-id" in response.headers

    def test_request_id_is_uuid_format(self):
        """Test that request ID is in UUID format."""
        import uuid

        with TestClient(app) as client:
            response = client.get("/")

        request_id = response.headers.get("x-request-id")
        # Should be a valid UUID
        try:
            uuid.UUID(request_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False

        assert is_valid_uuid


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers(self):
        """Test that CORS headers are properly set."""
        with TestClient(app) as client:
            response = client.options(
                "/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )

        # CORS should allow the origin
        assert response.status_code == 200
