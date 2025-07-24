from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.db.database import Base
from sqlalchemy import Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    telegram_id = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)  # ➕ Add this line
    created_at = Column(DateTime, default=datetime.now(timezone.utc))