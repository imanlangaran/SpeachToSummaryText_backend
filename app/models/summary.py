# app/models/summary.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="summaries")

    result = Column(Text, nullable=True)  # Raw OpenAI response or JSON as string
    status = Column(String, default="pending")  # e.g. "pending", "success", "error"

    summary = Column(Text, nullable=True)  # Final cleaned/generated summary
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=True)
    prompt = relationship("Prompt", back_populates="summaries")
    
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=True)
    transcription = relationship("Transcription", back_populates="summaries")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
