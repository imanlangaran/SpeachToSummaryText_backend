from fastapi import APIRouter, File, Depends, Query

from app.auth.dependencies import get_current_user
from app.db.database import get_db

from app.services.audio import *

router = APIRouter(prefix="/audio", tags=["user"])


@router.post("/upload", response_model=None)
async def upload(
    file: UploadFile = File(...),
    prompt: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upload_audio(file=file, prompt=prompt, current_user=current_user, db=db)


@router.post("/upload_summarize", response_model=None)
async def upload_sm(
    file: UploadFile = File(...),
    transcribePrompt: str = "",
    summaryPromptId: int = -1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return await upload_summerize(
        file=file,
        transcribePrompt=transcribePrompt,
        summaryPromptId=summaryPromptId,
        current_user=current_user,
        db=db,
    )


@router.get("/", response_model=None)
def all_user_audio(
    currentUser: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return get_all_user_audio(currentUser=currentUser, db=db)


@router.post("/summarize", response_model=None)
async def sm(
    audioId: int = -1,
    summaryPromptId: int = -1,
    currentUser: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return summarize(
        audioId=audioId, summaryPromptId=summaryPromptId, currentUser=currentUser, db=db
    )
