"""Tests for PromptService."""

import pytest
from app.services.prompt_service import PromptService
from app.core.exceptions import NotFoundError


class TestPromptService:
    def test_create(self, db_session):
        svc = PromptService(db_session)
        result = svc.create("My Prompt", "Summarize this text")
        assert result["title"] == "My Prompt"
        assert result["content"] == "Summarize this text"
        assert result["is_deleted"] is False
        assert result["id"] is not None

    def test_create_with_assistant_id(self, db_session):
        svc = PromptService(db_session)
        result = svc.create("Assistant Prompt", "Content", assistant_id="asst_abc123")
        assert result["assistant_id"] == "asst_abc123"

    def test_list_all(self, db_session):
        svc = PromptService(db_session)
        svc.create("A", "Content A")
        svc.create("B", "Content B")
        prompts = svc.list_all(include_deleted=False)
        assert len(prompts) >= 2

    def test_update(self, db_session):
        svc = PromptService(db_session)
        created = svc.create("Original", "Original content")
        updated = svc.update(created["id"], "Updated", "Updated content")
        assert updated["title"] == "Updated"
        assert updated["content"] == "Updated content"

    def test_soft_delete_and_restore(self, db_session):
        svc = PromptService(db_session)
        created = svc.create("To Delete", "Content")
        svc.soft_delete(created["id"])
        active = svc.list_all(include_deleted=False)
        assert created["id"] not in [p["id"] for p in active]
        svc.restore(created["id"])
        active_after = svc.list_all(include_deleted=False)
        assert created["id"] in [p["id"] for p in active_after]

    def test_update_nonexistent_raises(self, db_session):
        svc = PromptService(db_session)
        with pytest.raises(NotFoundError):
            svc.update(99999, "X", "Y")
