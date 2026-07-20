"""Common/shared Pydantic schemas."""

from pydantic import BaseModel
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class StandardResponse(BaseModel):
    success: bool
    data: Any = None
    error: ErrorDetail | None = None
