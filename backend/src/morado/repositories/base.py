"""Base repository class for data access layer.

This module provides the base repository class with common CRUD operations
that all specific repositories inherit from.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from morado.models.base import Base

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations.

    This class provides standard database operations that can be used
    by all specific repositories. It supports both synchronous and
    asynchronous operations.

    Attributes:
        model: The SQLAlchemy model class this repository manages

    Example:
        >>> class UserRepository(BaseRepository[User]):
        ...     def __init__(self):
        ...         super().__init__(User)
        >>>
        >>> repo = UserRepository()
        >>> user = repo.get_by_id(session, 1)
    """

    def __init__(self, model: type[ModelType]):
        """Initialize repository with model class.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    # Synchronous methods

    def get_by_id(self, session: Session, id: int) -> ModelType | None:
        """Get a record by ID.

        Args:
            session: Database session
            id: Record ID

        Returns:
            Model instance or None if not found

        Example:
            >>> user = repo.get_by_id(session, 1)
        """
        return session.get(self.model, id)

    def get_by_uuid(self, session: Session, uuid: str) -> ModelType | None:
        """Get a record by UUID.

        Args:
            session: Database session
            uuid: Record UUID

        Returns:
            Model instance or None if not found

        Example:
            >>> user = repo.get_by_uuid(session, "abc-123")
        """
        stmt = select(self.model).where(self.model.uuid == uuid)
        return session.execute(stmt).scalar_one_or_none()

    def get_all(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None
    ) -> list[ModelType]:
        """Get all records with optional filtering and pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field:value filters

        Returns:
            List of model instances

        Example:
            >>> users = repo.get_all(session, skip=0, limit=10)
            >>> active_users = repo.get_all(session, filters={"is_active": True})
        """
        stmt = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        stmt = stmt.offset(skip).limit(limit)
        return list(session.execute(stmt).scalars().all())

    def count(self, session: Session, filters: dict[str, Any] | None = None) -> int:
        """Count records with optional filtering.

        Args:
            session: Database session
            filters: Dictionary of field:value filters

        Returns:
            Number of records

        Example:
            >>> total = repo.count(session)
            >>> active_count = repo.count(session, filters={"is_active": True})
        """
        stmt = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        return session.execute(stmt).scalar()

    def create(self, session: Session, **kwargs: Any) -> ModelType:
        """Create a new record.

        Args:
            session: Database session
            **kwargs: Field values for the new record

        Returns:
            Created model instance

        Example:
            >>> user = repo.create(session, name="John", email="john@example.com")
        """
        instance = self.model(**kwargs)
        session.add(instance)
        session.flush()
        session.refresh(instance)
        return instance

    def update(
        self,
        session: Session,
        instance: ModelType,
        **kwargs: Any
    ) -> ModelType:
        """Update an existing record.

        Args:
            session: Database session
            instance: Model instance to update
            **kwargs: Field values to update

        Returns:
            Updated model instance

        Example:
            >>> user = repo.get_by_id(session, 1)
            >>> updated_user = repo.update(session, user, name="Jane")
        """
        for field, value in kwargs.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        session.flush()
        session.refresh(instance)
        return instance

    def delete(self, session: Session, instance: ModelType) -> None:
        """Delete a record.

        Args:
            session: Database session
            instance: Model instance to delete

        Example:
            >>> user = repo.get_by_id(session, 1)
            >>> repo.delete(session, user)
        """
        session.delete(instance)
        session.flush()

    def delete_by_id(self, session: Session, id: int) -> bool:
        """Delete a record by ID.

        Args:
            session: Database session
            id: Record ID

        Returns:
            True if deleted, False if not found

        Example:
            >>> success = repo.delete_by_id(session, 1)
        """
        instance = self.get_by_id(session, id)
        if instance:
            self.delete(session, instance)
            return True
        return False

    # Asynchronous methods

    async def get_by_id_async(
        self,
        session: AsyncSession,
        id: int
    ) -> ModelType | None:
        """Get a record by ID (async).

        Args:
            session: Async database session
            id: Record ID

        Returns:
            Model instance or None if not found

        Example:
            >>> user = await repo.get_by_id_async(session, 1)
        """
        return await session.get(self.model, id)

    async def get_by_uuid_async(
        self,
        session: AsyncSession,
        uuid: str
    ) -> ModelType | None:
        """Get a record by UUID (async).

        Args:
            session: Async database session
            uuid: Record UUID

        Returns:
            Model instance or None if not found

        Example:
            >>> user = await repo.get_by_uuid_async(session, "abc-123")
        """
        stmt = select(self.model).where(self.model.uuid == uuid)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_async(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None
    ) -> list[ModelType]:
        """Get all records with optional filtering and pagination (async).

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field:value filters

        Returns:
            List of model instances

        Example:
            >>> users = await repo.get_all_async(session, skip=0, limit=10)
        """
        stmt = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        stmt = stmt.offset(skip).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def count_async(
        self,
        session: AsyncSession,
        filters: dict[str, Any] | None = None
    ) -> int:
        """Count records with optional filtering (async).

        Args:
            session: Async database session
            filters: Dictionary of field:value filters

        Returns:
            Number of records

        Example:
            >>> total = await repo.count_async(session)
        """
        stmt = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)

        result = await session.execute(stmt)
        return result.scalar()

    async def create_async(
        self,
        session: AsyncSession,
        **kwargs: Any
    ) -> ModelType:
        """Create a new record (async).

        Args:
            session: Async database session
            **kwargs: Field values for the new record

        Returns:
            Created model instance

        Example:
            >>> user = await repo.create_async(session, name="John")
        """
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def update_async(
        self,
        session: AsyncSession,
        instance: ModelType,
        **kwargs: Any
    ) -> ModelType:
        """Update an existing record (async).

        Args:
            session: Async database session
            instance: Model instance to update
            **kwargs: Field values to update

        Returns:
            Updated model instance

        Example:
            >>> user = await repo.get_by_id_async(session, 1)
            >>> updated = await repo.update_async(session, user, name="Jane")
        """
        for field, value in kwargs.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        await session.flush()
        await session.refresh(instance)
        return instance

    async def delete_async(
        self,
        session: AsyncSession,
        instance: ModelType
    ) -> None:
        """Delete a record (async).

        Args:
            session: Async database session
            instance: Model instance to delete

        Example:
            >>> user = await repo.get_by_id_async(session, 1)
            >>> await repo.delete_async(session, user)
        """
        await session.delete(instance)
        await session.flush()

    async def delete_by_id_async(
        self,
        session: AsyncSession,
        id: int
    ) -> bool:
        """Delete a record by ID (async).

        Args:
            session: Async database session
            id: Record ID

        Returns:
            True if deleted, False if not found

        Example:
            >>> success = await repo.delete_by_id_async(session, 1)
        """
        instance = await self.get_by_id_async(session, id)
        if instance:
            await self.delete_async(session, instance)
            return True
        return False
