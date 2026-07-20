"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Any
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def get(self, id: int) -> ModelT | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, id: int, entity_name: str = "Entity") -> ModelT:
        obj = self.get(id)
        if not obj:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(entity_name, id)
        return obj

    def list(self, **filters) -> list[ModelT]:
        query = self.db.query(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.filter(getattr(self.model, field) == value)
        return query.all()

    def create(self, **data) -> ModelT:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, id: int, **data) -> ModelT:
        obj = self.get_or_404(id, self.model.__name__)
        for key, value in data.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        self.db.flush()
        return obj

    def delete(self, id: int) -> None:
        obj = self.get_or_404(id, self.model.__name__)
        self.db.delete(obj)
        self.db.flush()
