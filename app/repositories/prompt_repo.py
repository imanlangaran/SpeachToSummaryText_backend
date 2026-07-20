"""Prompt repository."""

from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.repositories.base import BaseRepository


class PromptRepository(BaseRepository[Prompt]):
    def __init__(self, db: Session):
        super().__init__(db, Prompt)

    def list_active(self) -> list[Prompt]:
        return self.db.query(Prompt).filter(Prompt.is_deleted == False).order_by(Prompt.updated_at.desc()).all()

    def list_all(self, include_deleted: bool = False) -> list[Prompt]:
        query = self.db.query(Prompt)
        if not include_deleted:
            query = query.filter(Prompt.is_deleted == False)
        return query.order_by(Prompt.updated_at.desc()).all()
