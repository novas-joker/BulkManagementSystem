"""Base repository with common CRUD operations for SQLAlchemy models."""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository for basic database operations."""

    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: ModelType) -> ModelType:
        """Create and persist a new model instance."""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, entity_id: str) -> ModelType | None:
        """Fetch one record by primary key."""
        stmt = select(self.model).where(self.model.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> list[ModelType]:
        """Fetch all records for the model."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing model instance."""
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a model instance."""
        await self.session.delete(obj)
        await self.session.commit()

    async def count(self) -> int:
        """Count total number of rows for the model."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
