"""Global test fixtures and configuration."""

import os
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import AsyncMock

# Set test environment BEFORE importing app modules
os.environ["AI_PROVIDER"] = "groq"
os.environ["GROQ_API_KEY"] = "test_gsk_mock_key_for_testing"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only_32_chars"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.db.database import Base
from app.main import app
from app.core.dependencies import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.prompt import Prompt


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine (SQLite for speed)."""
    e = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=e)
    yield e
    Base.metadata.drop_all(bind=e)
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    """Create a fresh session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, autocommit=False, autoflush=False)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden DB dependency."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a regular test user."""
    user = User(
        email="user@test.com",
        hashed_password=hash_password("password123"),
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_admin(db_session: Session) -> User:
    """Create an admin test user."""
    admin = User(
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def user_token(test_user: User) -> str:
    """JWT for regular user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """JWT for admin."""
    return create_access_token(data={"sub": test_admin.email})


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Authorization header for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Authorization header for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


# ---------------------------------------------------------------------------
# Data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_prompt(db_session: Session) -> Prompt:
    """Create a test prompt."""
    prompt = Prompt(
        title="Test Prompt",
        content="خلاصه کن این متن را",
        is_deleted=False,
    )
    db_session.add(prompt)
    db_session.commit()
    return prompt


@pytest.fixture
def mock_audio_bytes() -> bytes:
    """Return minimal valid MP3 bytes for testing."""
    # Minimal MP3 silence frame (works with pydub for basic tests)
    return b"\xff\xfb\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
