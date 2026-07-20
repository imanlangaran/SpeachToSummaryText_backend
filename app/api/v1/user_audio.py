"""User audio routes — upload, transcribe, summarize."""

from fastapi import APIRouter, Depends, File, UploadFile, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.response import success_response, error_response
from app.core.exceptions import AppException, ValidationError
from app.services.audio_service import AudioService

router = APIRouter(prefix="/user/audio", tags=["user"])


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    prompt: str = Query(""),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("audio/"):
        return error_response("VALIDATION_ERROR", "Only audio files are accepted")
    try:
        svc = AudioService(db)
        file_bytes = await file.read()
        result = await svc.upload_and_transcribe(file_bytes, file.filename or "audio.mp3", current_user.id, prompt)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.post("/upload_summarize")
async def upload_and_summarize(
    file: UploadFile = File(...),
    transcribePrompt: str = Query(""),
    summaryPromptId: int = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("audio/"):
        return error_response("VALIDATION_ERROR", "Only audio files are accepted")
    try:
        svc = AudioService(db)
        file_bytes = await file.read()
        result = await svc.upload_transcribe_and_summarize(
            file_bytes, file.filename or "audio.mp3",
            current_user.id, transcribePrompt, summaryPromptId,
        )
        return success_response(result["data"])
    except AppException as e:
        return error_response(e.code, e.message)


@router.get("/")
async def list_audio(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = AudioService(db)
    result = svc.get_user_transcriptions(current_user.id)
    return success_response(result)


@router.get("/{audio_id}")
async def get_audio_summaries(
    audio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = AudioService(db)
    result = svc.get_transcription_summaries(audio_id, current_user.id)
    return success_response(result)


@router.post("/summarize")
async def summarize_audio(
    audioId: int = Query(...),
    summaryPromptId: int = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        svc = AudioService(db)
        result = await svc.summarize_existing(audioId, summaryPromptId, current_user.id)
        return success_response(result["data"])
    except AppException as e:
        return error_response(e.code, e.message)
