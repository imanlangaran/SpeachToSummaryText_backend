"""Tests for AudioService."""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from app.services.audio_service import AudioService
from app.core.exceptions import ServiceError, NotFoundError


@pytest.fixture
def mock_provider():
    """Patch the create_provider function to return a mock."""
    provider = AsyncMock()
    provider.transcribe = AsyncMock(return_value="متن تست شده")
    provider.summarize = AsyncMock(return_value="خلاصه تست")
    provider.summarize_with_assistant = AsyncMock(return_value="خلاصه از دستیار")
    with patch("app.services.audio_service.create_provider", return_value=provider):
        yield provider


class TestAudioService:
    @pytest.mark.asyncio
    async def test_upload_and_transcribe(self, db_session, test_user, mock_provider):
        svc = AudioService(db_session)
        result = await svc.upload_and_transcribe(
            file_bytes=b"fake audio bytes",
            filename="test.mp3",
            user_id=test_user.id,
        )
        assert result["filename"] == "test.mp3"
        assert "متن تست شده" in result["transcript"]
        assert result["id"] is not None
        mock_provider.transcribe.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_upload_transcribe_and_summarize(self, db_session, test_user, test_prompt, mock_provider):
        svc = AudioService(db_session)
        result = await svc.upload_transcribe_and_summarize(
            file_bytes=b"fake audio",
            filename="audio.mp3",
            user_id=test_user.id,
            transcribe_prompt="",
            summary_prompt_id=test_prompt.id,
        )
        assert result["success"] is True
        assert result["data"]["summarise_text"] == "خلاصه تست"
        assert result["data"]["audioId"] is not None

    @pytest.mark.asyncio
    async def test_summarize_existing(self, db_session, test_user, test_prompt, mock_provider):
        # First create a transcription
        from app.repositories.transcription_repo import TranscriptionRepository
        repo = TranscriptionRepository(db_session)
        t = repo.create(user_id=test_user.id, file_path="/tmp/test.mp3", status="done", result="Original text")
        db_session.commit()

        svc = AudioService(db_session)
        result = await svc.summarize_existing(
            audio_id=t.id,
            summary_prompt_id=test_prompt.id,
            user_id=test_user.id,
        )
        assert result["success"] is True
        assert "خلاصه تست" in result["data"]["summarise_text"]

    @pytest.mark.asyncio
    async def test_summarize_nonexistent_audio(self, db_session, test_user, test_prompt, mock_provider):
        svc = AudioService(db_session)
        with pytest.raises(NotFoundError):
            await svc.summarize_existing(
                audio_id=99999,
                summary_prompt_id=test_prompt.id,
                user_id=test_user.id,
            )

    @pytest.mark.asyncio
    async def test_summarize_nonexistent_prompt(self, db_session, test_user, mock_provider):
        svc = AudioService(db_session)
        with pytest.raises(ServiceError, match="Transcription/Summarization failed"):
            await svc.upload_transcribe_and_summarize(
                file_bytes=b"data", filename="a.mp3",
                user_id=test_user.id, transcribe_prompt="",
                summary_prompt_id=99999,
            )

    def test_get_user_transcriptions(self, db_session, test_user):
        svc = AudioService(db_session)
        # No transcriptions yet
        assert svc.get_user_transcriptions(test_user.id) == []

    def test_get_transcription_summaries(self, db_session, test_user):
        svc = AudioService(db_session)
        assert svc.get_transcription_summaries(1, test_user.id) == []
