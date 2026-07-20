"""Audio service — orchestrates upload, transcription, and summarization.

This service layer has NO knowledge of FastAPI/HTTP. It receives plain data
and returns plain dicts. Transactions are properly managed with rollback.
"""

import os
import tempfile
from typing import BinaryIO
from sqlalchemy.orm import Session
from pydub import AudioSegment

from app.core.config import get_settings
from app.core.exceptions import ServiceError, ValidationError, NotFoundError
from app.providers.factory import create_provider
from app.repositories.transcription_repo import TranscriptionRepository
from app.repositories.summary_repo import SummaryRepository
from app.repositories.prompt_repo import PromptRepository

settings = get_settings()


class AudioService:
    def __init__(self, db: Session):
        self.db = db
        self.provider = create_provider()
        self.transcription_repo = TranscriptionRepository(db)
        self.summary_repo = SummaryRepository(db)
        self.prompt_repo = PromptRepository(db)

    async def upload_and_transcribe(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: int,
        prompt: str = "",
    ) -> dict:
        """Upload audio, transcribe it, return transcription result."""
        tmp_path = None
        try:
            # Save to temp file
            tmp_path = self._save_temp(file_bytes, filename)

            # Create transcription record
            transcription = self.transcription_repo.create(
                user_id=user_id,
                file_path=tmp_path,
                prompt=prompt,
                status="processing",
            )
            self.db.flush()

            # Transcribe
            with open(tmp_path, "rb") as f:
                transcript_text = await self.provider.transcribe(f, filename, prompt)

            # Update record
            self.transcription_repo.update(
                transcription.id,
                status="done",
                result=transcript_text.strip(),
            )
            self.db.commit()

            return {
                "filename": filename,
                "transcript": transcript_text.strip(),
                "id": transcription.id,
            }

        except Exception as e:
            self.db.rollback()
            if transcription and transcription.id:
                self.transcription_repo.update(transcription.id, status="failed", error_message=str(e))
                self.db.commit()
            raise ServiceError(f"Transcription failed: {e}", code="TRANSCRIPTION_FAILED")

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def upload_transcribe_and_summarize(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: int,
        transcribe_prompt: str,
        summary_prompt_id: int,
    ) -> dict:
        """Upload audio, transcribe, and summarize in one go."""
        tmp_path = None
        transcription = None
        summary = None

        try:
            # Get the prompt
            prompt = self.prompt_repo.get(summary_prompt_id)
            if not prompt:
                raise NotFoundError("Prompt", summary_prompt_id)

            # Save temp file
            tmp_path = self._save_temp(file_bytes, filename)

            # Create transcription record
            transcription = self.transcription_repo.create(
                user_id=user_id,
                file_path=tmp_path,
                prompt=transcribe_prompt,
                status="processing",
            )
            self.db.flush()

            # Transcribe
            with open(tmp_path, "rb") as f:
                transcript_text = await self.provider.transcribe(f, filename, transcribe_prompt)
            transcript_text = transcript_text.strip()

            self.transcription_repo.update(
                transcription.id, status="done", result=transcript_text,
            )
            self.db.flush()

            # Create summary record
            summary = self.summary_repo.create(
                user_id=user_id,
                status="pending",
                prompt_id=summary_prompt_id,
                transcription_id=transcription.id,
            )
            self.db.flush()

            # Summarize
            summarised_text = await self._do_summarize(transcript_text, prompt)

            self.summary_repo.update(summary.id, status="success", summary=summarised_text)
            self.db.commit()

            return {"success": True, "data": {"summarise_text": summarised_text, "audioId": transcription.id}}

        except Exception as e:
            self.db.rollback()
            if transcription and transcription.id:
                self.transcription_repo.update(
                    transcription.id, status="failed", error_message=str(e),
                )
            if summary and summary.id:
                self.summary_repo.update(summary.id, status="error", result=str(e))
            self.db.commit()
            raise ServiceError(f"Transcription/Summarization failed: {e}")

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def summarize_existing(
        self,
        audio_id: int,
        summary_prompt_id: int,
        user_id: int,
    ) -> dict:
        """Summarize an existing transcription."""
        try:
            prompt = self.prompt_repo.get(summary_prompt_id)
            if not prompt:
                raise NotFoundError("Prompt", summary_prompt_id)

            transcription = self.transcription_repo.get(audio_id)
            if not transcription or transcription.user_id != user_id:
                raise NotFoundError("Transcription", audio_id)

            summary = self.summary_repo.create(
                user_id=user_id,
                status="pending",
                prompt_id=summary_prompt_id,
                transcription_id=audio_id,
            )
            self.db.flush()

            summarised_text = await self._do_summarize(transcription.result, prompt)

            self.summary_repo.update(summary.id, status="success", summary=summarised_text)
            self.db.commit()

            return {"success": True, "data": {"summarise_text": summarised_text}}

        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            if summary and summary.id:
                self.summary_repo.update(summary.id, status="error", result=str(e))
                self.db.commit()
            raise ServiceError(f"Summarization failed: {e}")

    def get_user_transcriptions(self, user_id: int) -> list:
        return self.transcription_repo.list_by_user(user_id)

    def get_transcription_summaries(self, audio_id: int, user_id: int) -> list:
        return self.summary_repo.list_by_transcription(audio_id, user_id)

    async def _do_summarize(self, text: str, prompt) -> str:
        """Helper: pick the right summarization path based on prompt config."""
        if prompt.assistant_id:
            return await self.provider.summarize_with_assistant(text, prompt.assistant_id)
        return await self.provider.summarize(text, prompt.content)

    def _save_temp(self, file_bytes: bytes, filename: str) -> str:
        """Save uploaded file to a temporary location."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1] or ".mp3")
        tmp.write(file_bytes)
        tmp.close()
        return tmp.name

    def _process_audio_chunks(self, file_path: str):
        """Split audio into chunks if it exceeds limits. Returns list of chunk paths."""
        audio = AudioSegment.from_file(file_path).set_frame_rate(16000).set_channels(1)
        duration_ms = len(audio)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        max_duration = settings.max_audio_duration_ms
        max_size = settings.max_file_size_mb

        if duration_ms <= max_duration and file_size_mb <= max_size:
            return [file_path]

        chunks = []
        for i in range(0, duration_ms, max_duration):
            chunk = audio[i : i + max_duration]
            chunk_path = file_path.replace(".", f"_chunk{i // max_duration}.")
            chunk.export(chunk_path, format="mp3")
            chunks.append(chunk_path)
        return chunks
