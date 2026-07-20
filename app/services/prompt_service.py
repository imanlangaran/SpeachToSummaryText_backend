"""Prompt service — CRUD with soft-delete."""

from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError
from app.repositories.prompt_repo import PromptRepository


class PromptService:
    def __init__(self, db: Session):
        self.repo = PromptRepository(db)

    def create(self, title: str, content: str, assistant_id: str | None = None) -> dict:
        prompt = self.repo.create(title=title, content=content, assistant_id=assistant_id)
        return self._to_dict(prompt)

    def list_all(self, include_deleted: bool = False) -> list[dict]:
        prompts = self.repo.list_all(include_deleted=include_deleted)
        return [{"id": p.id, "title": p.title, "is_deleted": p.is_deleted} for p in prompts]

    def update(self, prompt_id: int, title: str, content: str, assistant_id: str | None = None) -> dict:
        data = {"title": title, "content": content}
        if assistant_id is not None:
            data["assistant_id"] = assistant_id
        prompt = self.repo.update(prompt_id, **data)
        return self._to_dict(prompt)

    def soft_delete(self, prompt_id: int) -> dict:
        prompt = self.repo.update(prompt_id, is_deleted=True)
        return {"message": "Prompt deleted"}

    def restore(self, prompt_id: int) -> dict:
        prompt = self.repo.update(prompt_id, is_deleted=False)
        return {"message": "Prompt restored"}

    def _to_dict(self, prompt) -> dict:
        return {
            "id": prompt.id,
            "title": prompt.title,
            "content": prompt.content,
            "assistant_id": prompt.assistant_id,
            "is_deleted": prompt.is_deleted,
            "created_at": prompt.created_at,
            "updated_at": prompt.updated_at,
        }
