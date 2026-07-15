"""Base repository for SQLAlchemy models.

Implements the abstract repository pattern with generic CRUD operations.
"""

import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic base repository for all database models.
    
    Provides standard database methods without business logic.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[ModelType]:
        """Get a single record by its UUID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get a list of records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create a new record."""
        obj_in_data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an existing record."""
        obj_data = db_obj.__dict__
        update_data = obj_in.model_dump(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        """Delete a record by its UUID."""
        obj = await self.get_by_id(db=db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def exists(self, db: AsyncSession, id: uuid.UUID) -> bool:
        """Check if a record exists."""
        obj = await self.get_by_id(db=db, id=id)
        return obj is not None

    async def filter(
        self, db: AsyncSession, **kwargs: Any
    ) -> List[ModelType]:
        """Filter records by keyword arguments."""
        stmt = select(self.model).filter_by(**kwargs)
        result = await db.execute(stmt)
        return list(result.scalars().all())
