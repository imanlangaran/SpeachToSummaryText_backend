"""Transcription repository."""

from sqlalchemy.orm import Session
from app.models.transcription import Transcription
from app.repositories.base import BaseRepository


class TranscriptionRepository(BaseRepository[Transcription]):
    def __init__(self, db: Session):
        super().__init__(db, Transcription)

    def list_by_user(self, user_id: int) -> list[Transcription]:
        return self.db.query(Transcription).filter(Transcription.user_id == user_id).all()
