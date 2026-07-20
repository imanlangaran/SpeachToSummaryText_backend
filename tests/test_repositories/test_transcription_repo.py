"""Tests for TranscriptionRepository."""

from app.repositories.transcription_repo import TranscriptionRepository
from app.models.transcription import Transcription


class TestTranscriptionRepository:
    def test_create(self, db_session, test_user):
        repo = TranscriptionRepository(db_session)
        t = repo.create(user_id=test_user.id, file_path="/tmp/test.mp3", status="pending")
        assert t.id is not None
        assert t.user_id == test_user.id

    def test_list_by_user(self, db_session, test_user):
        repo = TranscriptionRepository(db_session)
        repo.create(user_id=test_user.id, file_path="/tmp/a.mp3", status="done")
        repo.create(user_id=test_user.id, file_path="/tmp/b.mp3", status="done")
        results = repo.list_by_user(test_user.id)
        assert len(results) == 2

    def test_empty_list(self, db_session):
        repo = TranscriptionRepository(db_session)
        assert repo.list_by_user(999) == []

    def test_get(self, db_session, test_user):
        repo = TranscriptionRepository(db_session)
        t = repo.create(user_id=test_user.id, file_path="/tmp/x.mp3", status="pending")
        found = repo.get(t.id)
        assert found is not None
        assert found.file_path == "/tmp/x.mp3"
