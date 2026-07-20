"""Tests for PromptRepository."""

from app.repositories.prompt_repo import PromptRepository
from app.models.prompt import Prompt


class TestPromptRepository:
    def test_create(self, db_session):
        repo = PromptRepository(db_session)
        p = repo.create(title="Test", content="Summarize this")
        db_session.commit()
        assert p.id is not None
        assert p.title == "Test"
        assert p.is_deleted is False

    def test_list_active_excludes_deleted(self, db_session):
        repo = PromptRepository(db_session)
        repo.create(title="Active 1", content="a")
        repo.create(title="Active 2", content="b")
        deleted = repo.create(title="Deleted", content="c", is_deleted=True)
        db_session.commit()
        active = repo.list_active()
        assert len(active) == 2
        assert deleted not in active

    def test_list_all_includes_deleted(self, db_session):
        repo = PromptRepository(db_session)
        repo.create(title="A", content="a")
        repo.create(title="B", content="b", is_deleted=True)
        db_session.commit()
        all_p = repo.list_all(include_deleted=True)
        assert len(all_p) == 2

    def test_list_all_excludes_deleted(self, db_session):
        repo = PromptRepository(db_session)
        repo.create(title="A", content="a")
        repo.create(title="B", content="b", is_deleted=True)
        db_session.commit()
        active = repo.list_all(include_deleted=False)
        assert len(active) == 1

    def test_update(self, db_session):
        repo = PromptRepository(db_session)
        p = repo.create(title="Original", content="orig")
        db_session.commit()
        repo.update(p.id, title="Updated")
        db_session.commit()
        found = repo.get(p.id)
        assert found.title == "Updated"
