import os
from pydub import AudioSegment
import tempfile
from app.services.openai_client import get_openai_client

client = get_openai_client()

MAX_DURATION_MS = 2 * 60 * 1000  # 2 minutes in milliseconds
MAX_FILE_SIZE_MB = 25


def transcribe_audio(file_path: str, prompt: str | None = None) -> str:
    try:
        # Load and preprocess audio: set frame rate to 16000 and mono channel
        audio = AudioSegment.from_file(file_path).set_frame_rate(16000).set_channels(1)

        duration_ms = len(audio)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if duration_ms > MAX_DURATION_MS or file_size_mb > MAX_FILE_SIZE_MB:
            # Split into chunks of max 2 minutes
            chunks = [
                audio[i : i + MAX_DURATION_MS]
                for i in range(0, len(audio), MAX_DURATION_MS)
            ]
        else:
            chunks = [audio]

        full_transcript = ""

        for idx, chunk in enumerate(chunks):
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
                chunk.export(temp_file.name, format="mp3")
                with open(temp_file.name, "rb") as f:
                    transcript = client.audio.transcriptions.create(
                        model="gpt-4o-transcribe",
                        file=f,
                        language="fa",
                        prompt=prompt,
                    )
                    full_transcript += transcript.text.strip() + "\n"

        return full_transcript.strip()

    except Exception as error:
        raise RuntimeError(f"Whisper transcription failed: {error}")
