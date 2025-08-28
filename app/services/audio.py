from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os
import tempfile

from app.services.transcription_service import transcribe_audio
from app.services.summarise_service import summarise_text_assistant

from app.models import Transcription, User, Prompt, Summary


async def upload_audio(
    file: UploadFile,
    prompt: str,
    current_user: User,
    db: Session,
):
    # 1. Validate audio file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are accepted")

    # 2. Save to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        transcription = Transcription(
            user_id=current_user.id,
            file_path=tmp_path,
            prompt=prompt,
            status="processing",
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)

        # 3. Transcribe using Whisper
        transcript_text = transcribe_audio(tmp_path, prompt=prompt)

        transcription.status = "done"
        transcription.result = transcript_text.strip()
        db.commit()

        # 4. Return transcript
        return {
            "filename": file.filename,
            "transcript": transcript_text,
            "id": transcription.id,
        }

    except Exception as e:
        transcription.status = "failed"
        transcription.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def upload_summerize(
    file: UploadFile,
    transcribePrompt: str,
    summaryPromptId: int,
    current_user: User,
    db: Session,
):
    # 1. Validate audio file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Only audio files are accepted")

    prompt = db.query(Prompt).filter(Prompt.id == summaryPromptId).first()
    if summaryPromptId == -1 or not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # 2. Save to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        transcription = Transcription(
            user_id=current_user.id,
            file_path=tmp_path,
            prompt=transcribePrompt,
            status="processing",
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)

        # 3. Transcribe using Whisper
        transcript_text = transcribe_audio(tmp_path, prompt=prompt)

        transcript_text = transcript_text.strip()
        transcription.status = "done"
        transcription.result = transcript_text
        db.commit()

        summary = Summary(
            user_id=current_user.id, status="pending", prompt_id=summaryPromptId
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

        summarised_text = summarise_text_assistant(transcript_text, prompt.assistant_id)

        summary.status = "success"
        summary.summary = summarised_text
        db.commit()

        return {"sucess": "true", "data": {"summarise_text": summarised_text}}

    except Exception as e:
        transcription.status = "failed"
        transcription.error_message = str(e)

        # if summary is not None:
        #     summary.status = 'error'
        #     summary.result = str(e)

        db.commit()
        raise HTTPException(
            status_code=500, detail=f"Transcription/Summarization failed: {str(e)}"
        )

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def summarize(audioId: int, summaryPromptId: int, currentUser: User, db: Session):
    # 1. Validate audio file type

    prompt = db.query(Prompt).filter(Prompt.id == summaryPromptId).first()
    if summaryPromptId == -1 or not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    transcription = db.query(Transcription).filter(Transcription.id == audioId).first()
    if transcription == -1 or not transcription:
        raise HTTPException(status_code=404, detail="Audio not found")

    # 2. Save to a temporary location
    try:

        summary = Summary(
            user_id=currentUser.id, status="pending", prompt_id=summaryPromptId
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)

        # summarised_text = summarise_text(transcription.result, prompt)
        summarised_text = summarise_text_assistant(transcription.result, prompt.assistant_id)
        

        summary.status = "success"
        summary.summary = summarised_text
        db.commit()

        return {"sucess": "true", "data": {"summarise_text": summarised_text}}

    except Exception as e:

        if summary is not None:
            summary.status = "error"
            summary.result = str(e)

        db.commit()
        raise HTTPException(
            status_code=500, detail=f"Transcription/Summarization failed: {str(e)}"
        )


def get_all_user_audio(currentUser: User, db: Session):
    try:
        audio_records = (
            db.query(Transcription)
            .filter(Transcription.user_id == currentUser.id)
            .all()
        )
        if not audio_records:
            raise HTTPException(
                status_code=404, detail="No audio files found for this user."
            )
        return {"success": "true", "data": audio_records}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving audio files: {str(e)}"
        )


def get_user_audio_summaries(audio_id: int, currentUser: User, db: Session):
    if audio_id == -1:
        raise HTTPException(
            status_code=404, detail="No audio files found for this user."
        )
    try:
        audio_record = (
            db.query(Summary)
            .filter(
                and_(
                    Summary.user_id == currentUser.id,
                    Summary.transcription_id == audio_id,
                )
            )
            .all()
        )
        if not audio_record or audio_id == -1:
            raise HTTPException(
                status_code=404, detail="No audio files found for this user."
            )
        return {"success": "true", "data": audio_record}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving audio files: {str(e)}"
        )
