"""Tests for UserRepository."""

from app.repositories.user_repo import UserRepository
from app.core.exceptions import NotFoundError


class TestUserRepository:
    def test_create(self, db_session):
        repo = UserRepository(db_session)
        user = repo.create(email="new@test.com", hashed_password="hash123")
        assert user.id is not None
        assert user.email == "new@test.com"

    def test_get_by_email_found(self, db_session, test_user):
        repo = UserRepository(db_session)
        found = repo.get_by_email("user@test.com")
        assert found is not None
        assert found.id == test_user.id

    def test_get_by_email_not_found(self, db_session):
        repo = UserRepository(db_session)
        assert repo.get_by_email("nope@test.com") is None

    def test_get_or_404_found(self, db_session, test_user):
        repo = UserRepository(db_session)
        user = repo.get_or_404(test_user.id, "User")
        assert user.id == test_user.id

    def test_get_or_404_not_found(self, db_session):
        repo = UserRepository(db_session)
        import pytest
        with pytest.raises(NotFoundError):
            repo.get_or_404(99999, "User")

    def test_list(self, db_session, test_user):
        repo = UserRepository(db_session)
        users = repo.list()
        assert len(users) >= 1
        assert test_user in users
