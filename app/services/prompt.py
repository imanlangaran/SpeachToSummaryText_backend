# app/routes/prompt_router.py

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.prompt import Prompt
from app.models.user import User
from app.auth.dependencies import admin_required


def create_prompt(
    title: str,
    content: str,
    db: Session = Depends(get_db)
):
    prompt = Prompt(title=title, content=content)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def list_prompts(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db)
):
    query = db.query(Prompt)
    if not include_deleted:
        query = query.filter(Prompt.is_deleted == False)
    return query.order_by(Prompt.updated_at.desc()).all()


def update_prompt(
    prompt_id: int,
    title: str,
    content: str,
    db: Session = Depends(get_db)
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.title = title
    prompt.content = content
    db.commit()
    return prompt


def soft_delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.is_deleted = True
    db.commit()
    return {"message": "Prompt deleted"}


def restore_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.is_deleted = False
    db.commit()
    return {"message": "Prompt restored"}
