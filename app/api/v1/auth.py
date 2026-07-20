"""Auth routes — register, login, profile."""

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.response import success_response, error_response
from app.core.exceptions import AppException
from app.schemas.auth import UserCreateRequest, UserLoginRequest, UserResponse, TokenResponse, MeResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(body: UserCreateRequest, db: Session = Depends(get_db)):
    try:
        svc = AuthService(db)
        result = svc.register(body.email, body.password)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.post("/login")
async def login(body: UserLoginRequest, db: Session = Depends(get_db)):
    try:
        svc = AuthService(db)
        result = svc.login(body.email, body.password)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.post("/loginSwagger")
async def login_swagger(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        svc = AuthService(db)
        result = svc.login(username, password)
        return success_response(result)
    except AppException as e:
        return error_response(e.code, e.message)


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return success_response({"email": current_user.email, "is_admin": current_user.is_admin})
