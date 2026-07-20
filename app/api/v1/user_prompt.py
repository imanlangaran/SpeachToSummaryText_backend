"""User prompt routes — list available prompts."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.response import success_response
from app.services.prompt_service import PromptService

router = APIRouter(prefix="/user/prompt", tags=["user"])


@router.get("/")
async def list_prompts(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    svc = PromptService(db)
    result = svc.list_all(include_deleted=False)
    return success_response(result)
