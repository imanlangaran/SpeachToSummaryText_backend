from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User

from app.auth.dependencies import get_current_user

from app.services.prompt import list_prompts

router = APIRouter(prefix='/prompt',tags=['user'])

@router.get("/")
def list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_prompts(include_deleted=False, db=db)
