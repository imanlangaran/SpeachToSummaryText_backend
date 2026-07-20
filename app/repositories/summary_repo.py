"""Summary repository."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.summary import Summary
from app.repositories.base import BaseRepository


class SummaryRepository(BaseRepository[Summary]):
    def __init__(self, db: Session):
        super().__init__(db, Summary)

    def list_by_transcription(self, transcription_id: int, user_id: int) -> list[Summary]:
        return self.db.query(Summary).filter(
            and_(
                Summary.transcription_id == transcription_id,
                Summary.user_id == user_id,
            )
        ).all()

    def find_existing(self, user_id: int, transcription_id: int, prompt_id: int) -> Optional[Summary]:
        return self.db.query(Summary).filter(
            and_(
                Summary.user_id == user_id,
                Summary.transcription_id == transcription_id,
                Summary.prompt_id == prompt_id,
            )
        ).first()
