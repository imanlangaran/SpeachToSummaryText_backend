"""OpenAI and Groq provider implementations."""

import os
import tempfile
from typing import BinaryIO
from pydub import AudioSegment

from app.core.config import get_settings
from app.providers.base import AIProvider
from app.core.exceptions import ServiceError

settings = get_settings()

MAX_DURATION_MS = settings.max_audio_duration_ms
MAX_FILE_SIZE_MB = settings.max_file_size_mb


class OpenAICompatibleProvider(AIProvider):
    """Provider for any OpenAI-compatible API (OpenAI, Groq, Together, etc.)."""

    def __init__(self, api_key: str, base_url: str, transcription_model: str, chat_model: str):
        from openai import AsyncOpenAI
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.transcription_model = transcription_model
        self.chat_model = chat_model

    async def transcribe(
        self, audio_file: BinaryIO, filename: str = "audio.mp3", prompt: str | None = None
    ) -> str:
        try:
            transcript = await self._client.audio.transcriptions.create(
                model=self.transcription_model,
                file=(filename, audio_file.read()),
                language="fa",
                prompt=prompt,
            )
            return transcript.text.strip()
        except Exception as e:
            raise ServiceError(f"Transcription failed: {e}", code="TRANSCRIPTION_FAILED")

    async def summarize(self, text: str, system_prompt: str | None = None) -> str:
        try:
            messages = [
                {"role": "system", "content": system_prompt or "خلاصه‌کننده متن فارسی"},
                {"role": "user", "content": text},
            ]
            response = await self._client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise ServiceError(f"Summarization failed: {e}", code="SUMMARIZATION_FAILED")

    async def summarize_with_assistant(self, text: str, assistant_id: str) -> str:
        try:
            thread = await self._client.beta.threads.create(
                messages=[{"role": "user", "content": text}]
            )
            run = await self._client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant_id,
            )
            if run.status != "completed":
                raise ServiceError(
                    f"Assistant run failed with status: {run.status}",
                    code="ASSISTANT_FAILED",
                )
            messages = await self._client.beta.threads.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == "assistant":
                    return msg.content[0].text.value.strip()
            raise ServiceError("No response from assistant", code="ASSISTANT_NO_RESPONSE")
        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(f"Assistant summarization failed: {e}", code="ASSISTANT_FAILED")


def create_provider() -> AIProvider:
    """Factory: returns the right provider based on settings."""
    provider_name = settings.ai_provider.strip().lower()

    if provider_name == "groq":
        api_key = settings.groq_api_key
        if not api_key:
            raise ServiceError(
                "GROQ_API_KEY is required when AI_PROVIDER=groq",
                code="MISSING_API_KEY",
            )
        return OpenAICompatibleProvider(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            transcription_model="whisper-large-v3-turbo",
            chat_model="llama-3.3-70b-versatile",
        )

    # Default: OpenAI
    api_key = settings.openai_api_key
    if not api_key:
        raise ServiceError(
            "OPENAI_API_KEY is required. Set it or configure GROQ_API_KEY for free transcription.",
            code="MISSING_API_KEY",
        )
    return OpenAICompatibleProvider(
        api_key=api_key,
        base_url="https://api.openai.com/v1",
        transcription_model="whisper-1",
        chat_model="gpt-4.1",
    )
