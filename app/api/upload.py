from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import tempfile

from app.services.transcription_service import transcribe_audio

from app.db.database import get_db
from app.models import Transcription, User
# from app.auth.dependencies import get_current_user_email
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/upload", response_model=None)
async def upload_audio(
    file: UploadFile = File(...),
    prompt: str = "",
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    # 1. Validate audio file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are accepted")

    # 2. Save to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 3. Transcribe using Whisper
        transcript_text = transcribe_audio(tmp_path, prompt=prompt)

        # 4. Return transcript
        return {
            "filename": file.filename,
            "transcript": transcript_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
