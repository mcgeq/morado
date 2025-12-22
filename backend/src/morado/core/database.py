"""Database configuration and session management.

This module provides database connection management, session handling,
and initialization for the Morado application using SQLAlchemy.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from morado.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    All database models should inherit from this class.

    Example:
        >>> from morado.core.database import Base
        >>> from sqlalchemy import Column, Integer, String
        >>>
        >>> class User(Base):
        ...     __tablename__ = "users"
        ...     id = Column(Integer, primary_key=True)
        ...     username = Column(String(50), unique=True)
    """


class DatabaseManager:
    """Database connection and session manager.

    This class manages database engines and session factories for both
    synchronous and asynchronous database operations.

    Attributes:
        engine: Synchronous SQLAlchemy engine
        async_engine: Asynchronous SQLAlchemy engine
        session_factory: Synchronous session factory
        async_session_factory: Asynchronous session factory
    """

    def __init__(self):
        """Initialize database manager."""
        self.engine: create_engine | None = None
        self.async_engine: AsyncEngine | None = None
        self.session_factory: sessionmaker | None = None
        self.async_session_factory: async_sessionmaker | None = None
        self._initialized = False

    def initialize(self, database_url: str | None = None) -> None:
        """Initialize database engines and session factories.

        Args:
            database_url: Database connection URL. If None, uses settings.

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> # Database is now ready for use
        """
        if self._initialized:
            return

        settings = get_settings()
        db_url = database_url or settings.database_url

        # Convert postgresql:// to postgresql+asyncpg:// for async engine
        async_db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

        # Create synchronous engine
        self.engine = create_engine(
            db_url,
            pool_size=settings.database_pool_size,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.database_echo,
        )

        # Create asynchronous engine
        self.async_engine = create_async_engine(
            async_db_url,
            pool_size=settings.database_pool_size,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.database_echo,
        )

        # Create session factories
        self.session_factory = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
        )

        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self._initialized = True

    def create_tables(self) -> None:
        """Create all database tables.

        This method creates all tables defined in models that inherit
        from Base. Should be called during application initialization.

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> db_manager.create_tables()
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        Base.metadata.create_all(bind=self.engine)

    async def create_tables_async(self) -> None:
        """Create all database tables asynchronously.

        Async version of create_tables().

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> await db_manager.create_tables_async()
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def drop_tables(self) -> None:
        """Drop all database tables.

        WARNING: This will delete all data in the database!
        Should only be used in testing or development.

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> db_manager.drop_tables()  # Careful!
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        Base.metadata.drop_all(bind=self.engine)

    async def drop_tables_async(self) -> None:
        """Drop all database tables asynchronously.

        Async version of drop_tables().
        WARNING: This will delete all data in the database!

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> await db_manager.drop_tables_async()  # Careful!
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def get_session(self) -> Session:
        """Get a new synchronous database session.

        Returns:
            SQLAlchemy Session instance

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> session = db_manager.get_session()
            >>> try:
            ...     # Use session
            ...     session.commit()
            ... finally:
            ...     session.close()
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        return self.session_factory()

    def get_async_session(self) -> AsyncSession:
        """Get a new asynchronous database session.

        Returns:
            SQLAlchemy AsyncSession instance

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> async_session = db_manager.get_async_session()
            >>> async with async_session:
            ...     # Use session
            ...     await async_session.commit()
        """
        if not self._initialized:
            raise RuntimeError("Database manager not initialized")

        return self.async_session_factory()

    async def close(self) -> None:
        """Close database connections.

        Should be called during application shutdown.

        Example:
            >>> db_manager = DatabaseManager()
            >>> db_manager.initialize()
            >>> # ... use database ...
            >>> await db_manager.close()
        """
        if self.async_engine:
            await self.async_engine.dispose()

        if self.engine:
            self.engine.dispose()

        self._initialized = False


# Global database manager instance
_db_manager = DatabaseManager()


def init_database(database_url: str | None = None) -> None:
    """Initialize the global database manager.

    Args:
        database_url: Database connection URL. If None, uses settings.

    Example:
        >>> init_database()
        >>> # Database is now ready for use
    """
    _db_manager.initialize(database_url)


async def close_database() -> None:
    """Close the global database manager.

    Should be called during application shutdown.

    Example:
        >>> await close_database()
    """
    await _db_manager.close()


def get_db() -> Session:
    """Get a database session (synchronous).

    This function is designed to be used as a dependency in Litestar.
    The session is automatically closed after the request.

    Yields:
        SQLAlchemy Session instance

    Example:
        >>> from litestar import get
        >>> from litestar.di import Provide
        >>>
        >>> @get("/users")
        >>> def get_users(db: Session = Depends(get_db)) -> list:
        ...     return db.query(User).all()
    """
    session = _db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Get an async database session context manager.

    This function provides an async context manager for database sessions.
    The session is automatically committed on success and rolled back on error.

    Yields:
        SQLAlchemy AsyncSession instance

    Example:
        >>> async with get_db_session() as session:
        ...     user = await session.get(User, user_id)
        ...     user.name = "New Name"
        ...     # Session is automatically committed
    """
    session = _db_manager.get_async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance.

    Returns:
        DatabaseManager instance

    Example:
        >>> db_manager = get_database_manager()
        >>> db_manager.create_tables()
    """
    return _db_manager
