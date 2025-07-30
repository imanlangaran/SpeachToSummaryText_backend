from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User

from app.auth.dependencies import get_current_user

router = APIRouter(prefix='/prompt',tags=['user'])

@router.get("/")
def list_prompts(
    include_deleted: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_prompts(include_deleted=include_deleted, db=db)
