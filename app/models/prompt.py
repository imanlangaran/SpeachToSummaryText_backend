# app/models/prompt.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone
from app.db.database import Base
from sqlalchemy.orm import relationship

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)  # optional name for display
    content = Column(Text, nullable=True)       # actual prompt content
    
    assistant_id = Column(Text, nullable=False)

    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    summaries = relationship("Summary", back_populates="prompt", cascade="all, delete-orphan")
