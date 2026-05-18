"""Base repository with common CRUD operations."""

import uuid
from abc import ABC
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository with CRUD operations."""

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: Any) -> T | None:
        """Get entity by ID."""
        if isinstance(id, uuid.UUID):
            id = str(id)
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Get all entities with pagination."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, id: Any, entity: T) -> T | None:
        """Update an existing entity."""
        existing = await self.get_by_id(id)
        if existing is None:
            return None
        for key, value in entity.dict().items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def delete(self, id: Any) -> bool:
        """Delete an entity by ID."""
        entity = await self.get_by_id(id)
        if entity is None:
            return False
        await self.session.delete(entity)
        await self.session.flush()
        return True

    async def save(self, entity: T) -> T:
        """Save an entity (create or update)."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
