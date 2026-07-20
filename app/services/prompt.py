# app/routes/prompt_router.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.prompt import Prompt

def create_prompt(
    title: str,
    content: str,
    db: Session,
    assistant_id: str | None = None,
):
    prompt = Prompt(title=title, content=content, assistant_id=assistant_id)
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


def list_prompts(
    include_deleted: bool,
    db: Session
):
    query = db.query(
        Prompt.id,
        Prompt.title,
        Prompt.is_deleted
    )

    if not include_deleted:
        query = query.filter(Prompt.is_deleted == False)

    results = query.order_by(Prompt.updated_at.desc()).all()
    return [dict(row._mapping) for row in results]


def update_prompt(
    prompt_id: int,
    title: str,
    content: str,
    db: Session,
    assistant_id: str | None = None,
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.title = title
    prompt.content = content
    if assistant_id is not None:
        prompt.assistant_id = assistant_id
    db.commit()
    return prompt


def soft_delete_prompt(
    prompt_id: int,
    db: Session
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.is_deleted = True
    db.commit()
    return {"message": "Prompt deleted"}


def restore_prompt(
    prompt_id: int,
    db: Session
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.is_deleted = False
    db.commit()
    return {"message": "Prompt restored"}
