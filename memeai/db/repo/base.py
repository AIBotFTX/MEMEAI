from typing import TypeVar, Generic, Optional, List, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from memeai.db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession) -> List[ModelType]:
        """Get all records."""
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def update(
        self, session: AsyncSession, id: int, **kwargs
    ) -> Optional[ModelType]:
        """Update a record by ID."""
        instance = await self.get_by_id(session, id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await session.commit()
            await session.refresh(instance)
        return instance

    async def delete(self, session: AsyncSession, id: int) -> bool:
        """Delete a record by ID."""
        instance = await self.get_by_id(session, id)
        if instance:
            await session.delete(instance)
            await session.commit()
            return True
        return False

    def _build_query(self) -> Select:
        """Build a base query for the model."""
        return select(self.model)
