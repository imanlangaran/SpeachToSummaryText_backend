"""Pydantic schemas for audio/transcription operations."""

from pydantic import BaseModel
from datetime import datetime


class TranscriptionResponse(BaseModel):
    id: int
    filename: str | None = None
    transcript: str | None = None

    model_config = {"from_attributes": True}


class AudioUploadResponse(BaseModel):
    filename: str
    transcript: str
    id: int


class SummaryItem(BaseModel):
    id: int
    summary: str | None = None
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AudioSummaryResponse(BaseModel):
    success: bool = True
    data: list[SummaryItem]


class SummarizeResponse(BaseModel):
    summarise_text: str


class UploadSummarizeResponse(BaseModel):
    summarise_text: str
    audioId: int


class AudioListResponse(BaseModel):
    success: bool = True
    data: list
