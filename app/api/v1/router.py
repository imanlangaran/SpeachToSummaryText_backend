"""Aggregates all v1 API routes."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.user_audio import router as user_audio_router
from app.api.v1.user_prompt import router as user_prompt_router
from app.api.v1.admin_prompt import router as admin_prompt_router

v1_router = APIRouter()

v1_router.include_router(auth_router)
v1_router.include_router(health_router)
v1_router.include_router(user_audio_router)
v1_router.include_router(user_prompt_router)
v1_router.include_router(admin_prompt_router)
