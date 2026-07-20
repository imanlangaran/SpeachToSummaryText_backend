"""Tests for AuthService."""

from unittest.mock import patch, MagicMock
import pytest
from app.services.auth_service import AuthService
from app.core.exceptions import DuplicateError, AuthError


class TestAuthService:
    def test_register_success(self, db_session):
        svc = AuthService(db_session)
        result = svc.register("new@test.com", "password123")
        assert result["email"] == "new@test.com"
        assert result["id"] is not None
        assert "hashed_password" not in result

    def test_register_duplicate_email(self, db_session, test_user):
        svc = AuthService(db_session)
        with pytest.raises(DuplicateError, match="Email already registered"):
            svc.register(test_user.email, "any")

    def test_login_success(self, db_session, test_user):
        svc = AuthService(db_session)
        result = svc.login("user@test.com", "password123")
        assert "access_token" in result
        assert result["token_type"] == "bearer"

    def test_login_wrong_password(self, db_session, test_user):
        svc = AuthService(db_session)
        with pytest.raises(AuthError, match="Invalid credentials"):
            svc.login("user@test.com", "wrongpassword")

    def test_login_nonexistent_user(self, db_session):
        svc = AuthService(db_session)
        with pytest.raises(AuthError, match="Invalid credentials"):
            svc.login("nobody@test.com", "any")
