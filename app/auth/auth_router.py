from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.schemas import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.auth.auth_utils import hash_password, verify_password, get_user_by_email
from app.auth.jwt_handler import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from app.auth.dependencies import get_current_user_email

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if get_user_by_email(db, user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = hash_password(user.password)
        new_user = User(email=user.email, hashed_password=hashed)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/loginSwagger")
def login(
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    db_user = get_user_by_email(db, username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def read_me(user_email: str = Depends(get_current_user_email)):
    return {"email": user_email}