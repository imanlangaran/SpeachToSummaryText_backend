from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.auth.dependencies import admin_required

from app.services.prompt import *


router = APIRouter(prefix="/prompt" , tags=['admin'])


@router.post("/")
def create(
    title: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    return create_prompt(title=title, content=content, db=db)


@router.get("/")
def list(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    return list_prompts(include_deleted=include_deleted, db=db)


@router.put("/{prompt_id}")
def update(
    prompt_id: int,
    title: str,
    content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    return update_prompt(prompt_id=prompt_id, title=title, content=content, db=db)


@router.patch("/{prompt_id}/delete")
def soft_delete(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    return soft_delete_prompt(prompt_id=prompt_id, db=db)


@router.patch("/{prompt_id}/restore")
def restore(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    return restore_prompt(prompt_id=prompt_id, db=db)
