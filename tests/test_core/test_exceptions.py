"""Tests for core/exceptions module."""

from app.core.exceptions import (
    AppException, NotFoundError, AuthError, ForbiddenError,
    DuplicateError, ValidationError, ServiceError,
)


class TestAppException:
    def test_defaults(self):
        exc = AppException("Something went wrong")
        assert exc.message == "Something went wrong"
        assert exc.code == "INTERNAL_ERROR"
        assert exc.status_code == 500

    def test_custom_values(self):
        exc = AppException("Custom error", code="CUSTOM", status_code=418)
        assert exc.message == "Custom error"
        assert exc.code == "CUSTOM"
        assert exc.status_code == 418


class TestNotFoundError:
    def test_with_id(self):
        exc = NotFoundError("User", 42)
        assert "User" in exc.message
        assert "42" in exc.message
        assert exc.code == "NOT_FOUND"
        assert exc.status_code == 404

    def test_without_id(self):
        exc = NotFoundError("Prompt")
        assert "Prompt" in exc.message
        assert exc.code == "NOT_FOUND"


class TestAuthError:
    def test_default_message(self):
        exc = AuthError()
        assert exc.message == "Invalid credentials"
        assert exc.status_code == 401

    def test_custom_message(self):
        exc = AuthError("Token expired")
        assert exc.message == "Token expired"


class TestForbiddenError:
    def test_defaults(self):
        exc = ForbiddenError()
        assert exc.status_code == 403
        assert exc.code == "FORBIDDEN"


class TestDuplicateError:
    def test_defaults(self):
        exc = DuplicateError("Email taken")
        assert exc.status_code == 409
        assert exc.code == "DUPLICATE"


class TestValidationError:
    def test_defaults(self):
        exc = ValidationError("Bad input")
        assert exc.status_code == 400
        assert exc.code == "VALIDATION_ERROR"


class TestServiceError:
    def test_defaults(self):
        exc = ServiceError("AI failed")
        assert exc.status_code == 502
        assert exc.code == "SERVICE_ERROR"
