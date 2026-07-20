"""Admin prompt routes — CRUD with soft-delete/restore."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, admin_required
from app.core.response import success_response, error_response
from app.core.exceptions import AppException
from app.services.prompt_service import PromptService

router = APIRouter(prefix="/admin/prompt", tags=["admin"])


@router.post("/")
async def create_prompt(
    title: str = Query(...),
    content: str = Query(...),
    assistant_id: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(admin_required),
):
    try:
        svc = PromptService(db)
        result = svc.create(title, content, assistant_id)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.get("/")
async def list_prompts(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    _admin=Depends(admin_required),
):
    svc = PromptService(db)
    result = svc.list_all(include_deleted=include_deleted)
    return success_response(result)


@router.put("/{prompt_id}")
async def update_prompt(
    prompt_id: int,
    title: str = Query(...),
    content: str = Query(...),
    assistant_id: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(admin_required),
):
    try:
        svc = PromptService(db)
        result = svc.update(prompt_id, title, content, assistant_id)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.patch("/{prompt_id}/delete")
async def soft_delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(admin_required),
):
    try:
        svc = PromptService(db)
        result = svc.soft_delete(prompt_id)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.patch("/{prompt_id}/restore")
async def restore_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(admin_required),
):
    try:
        svc = PromptService(db)
        result = svc.restore(prompt_id)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)
