"""Pydantic schemas for prompt operations."""

from pydantic import BaseModel
from datetime import datetime


class PromptCreateRequest(BaseModel):
    title: str
    content: str
    assistant_id: str | None = None


class PromptUpdateRequest(BaseModel):
    title: str
    content: str
    assistant_id: str | None = None


class PromptResponse(BaseModel):
    id: int
    title: str
    content: str | None = None
    assistant_id: str | None = None
    is_deleted: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PromptListItem(BaseModel):
    id: int
    title: str
    is_deleted: bool

    model_config = {"from_attributes": True}
