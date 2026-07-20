"""Abstract AI provider interface.

All AI providers (OpenAI, Groq, etc.) implement this interface.
Adding a new provider = creating a new class that inherits from AIProvider.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class AIProvider(ABC):
    """Abstract interface for AI transcription and summarization."""

    @abstractmethod
    async def transcribe(
        self, audio_file: BinaryIO, filename: str = "audio.mp3", prompt: str | None = None
    ) -> str:
        """Transcribe an audio file to text."""
        ...

    @abstractmethod
    async def summarize(self, text: str, system_prompt: str | None = None) -> str:
        """Summarize text using an LLM."""
        ...

    @abstractmethod
    async def summarize_with_assistant(self, text: str, assistant_id: str) -> str:
        """Summarize text using an OpenAI Assistant (thread-based)."""
        ...
