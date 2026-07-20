"""Auth service — registration, login, user management."""

from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import DuplicateError, AuthError, NotFoundError
from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, email: str, password: str) -> dict:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise DuplicateError("Email already registered")
        hashed = hash_password(password)
        user = self.user_repo.create(email=email, hashed_password=hashed)
        self.db.commit()
        return {"id": user.id, "email": user.email, "is_admin": user.is_admin, "created_at": user.created_at}

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid credentials")
        token = create_access_token(data={"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}

    def get_profile(self, email: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundError("User")
        return {"email": user.email, "is_admin": user.is_admin}
