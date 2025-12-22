"""Repository for Layer 1: API Component models.

This module provides data access methods for Header, Body, and ApiDefinition models.
"""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from morado.models.api_component import ApiDefinition, Body, Header, HeaderScope
from morado.repositories.base import BaseRepository


class HeaderRepository(BaseRepository[Header]):
    """Repository for Header model.

    Provides data access methods for HTTP header components.

    Example:
        >>> repo = HeaderRepository()
        >>> header = repo.get_by_id(session, 1)
        >>> global_headers = repo.get_by_scope(session, HeaderScope.GLOBAL)
    """

    def __init__(self):
        """Initialize Header repository."""
        super().__init__(Header)

    def get_by_scope(
        self,
        session: Session,
        scope: HeaderScope,
        skip: int = 0,
        limit: int = 100
    ) -> list[Header]:
        """Get headers by scope.

        Args:
            session: Database session
            scope: Header scope (global/project/private)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances

        Example:
            >>> headers = repo.get_by_scope(session, HeaderScope.GLOBAL)
        """
        stmt = (
            select(Header)
            .where(Header.scope == scope)
            .where(Header.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_project(
        self,
        session: Session,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Header]:
        """Get headers by project ID.

        Args:
            session: Database session
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances

        Example:
            >>> headers = repo.get_by_project(session, 1)
        """
        stmt = (
            select(Header)
            .where(Header.project_id == project_id)
            .where(Header.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def search_by_name(
        self,
        session: Session,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Header]:
        """Search headers by name (case-insensitive).

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances

        Example:
            >>> headers = repo.search_by_name(session, "auth")
        """
        stmt = (
            select(Header)
            .where(Header.name.ilike(f"%{name}%"))
            .where(Header.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_scope_async(
        self,
        session: AsyncSession,
        scope: HeaderScope,
        skip: int = 0,
        limit: int = 100
    ) -> list[Header]:
        """Get headers by scope (async).

        Args:
            session: Async database session
            scope: Header scope
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances
        """
        stmt = (
            select(Header)
            .where(Header.scope == scope)
            .where(Header.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_project_async(
        self,
        session: AsyncSession,
        project_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[Header]:
        """Get headers by project ID (async).

        Args:
            session: Async database session
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances
        """
        stmt = (
            select(Header)
            .where(Header.project_id == project_id)
            .where(Header.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name_async(
        self,
        session: AsyncSession,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Header]:
        """Search headers by name (async).

        Args:
            session: Async database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances
        """
        stmt = (
            select(Header)
            .where(Header.name.ilike(f"%{name}%"))
            .where(Header.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class BodyRepository(BaseRepository[Body]):
    """Repository for Body model.

    Provides data access methods for request/response body components.

    Example:
        >>> repo = BodyRepository()
        >>> body = repo.get_by_id(session, 1)
        >>> request_bodies = repo.get_by_type(session, BodyType.REQUEST)
    """

    def __init__(self):
        """Initialize Body repository."""
        super().__init__(Body)

    def get_by_scope(
        self,
        session: Session,
        scope: HeaderScope,
        skip: int = 0,
        limit: int = 100
    ) -> list[Body]:
        """Get bodies by scope.

        Args:
            session: Database session
            scope: Body scope
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        stmt = (
            select(Body)
            .where(Body.scope == scope)
            .where(Body.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_type(
        self,
        session: Session,
        body_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Body]:
        """Get bodies by type.

        Args:
            session: Database session
            body_type: Body type (request/response/both)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        stmt = (
            select(Body)
            .where(Body.body_type == body_type)
            .where(Body.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def search_by_name(
        self,
        session: Session,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Body]:
        """Search bodies by name (case-insensitive).

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        stmt = (
            select(Body)
            .where(Body.name.ilike(f"%{name}%"))
            .where(Body.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_scope_async(
        self,
        session: AsyncSession,
        scope: HeaderScope,
        skip: int = 0,
        limit: int = 100
    ) -> list[Body]:
        """Get bodies by scope (async).

        Args:
            session: Async database session
            scope: Body scope
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        stmt = (
            select(Body)
            .where(Body.scope == scope)
            .where(Body.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type_async(
        self,
        session: AsyncSession,
        body_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Body]:
        """Get bodies by type (async).

        Args:
            session: Async database session
            body_type: Body type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        stmt = (
            select(Body)
            .where(Body.body_type == body_type)
            .where(Body.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name_async(
        self,
        session: AsyncSession,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Body]:
        """Search bodies by name (async).

        Args:
            session: Async database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        stmt = (
            select(Body)
            .where(Body.name.ilike(f"%{name}%"))
            .where(Body.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class ApiDefinitionRepository(BaseRepository[ApiDefinition]):
    """Repository for ApiDefinition model.

    Provides data access methods for API definitions with support for
    eager loading of related Header and Body components.

    Example:
        >>> repo = ApiDefinitionRepository()
        >>> api_def = repo.get_with_relations(session, 1)
        >>> # api_def.header and api_def.request_body are loaded
    """

    def __init__(self):
        """Initialize ApiDefinition repository."""
        super().__init__(ApiDefinition)

    def get_with_relations(
        self,
        session: Session,
        id: int
    ) -> ApiDefinition | None:
        """Get API definition with related Header and Body components.

        Args:
            session: Database session
            id: API definition ID

        Returns:
            ApiDefinition instance with relations loaded, or None

        Example:
            >>> api_def = repo.get_with_relations(session, 1)
            >>> print(api_def.header.name)
            >>> print(api_def.request_body.name)
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.id == id)
            .options(
                joinedload(ApiDefinition.header),
                joinedload(ApiDefinition.request_body),
                joinedload(ApiDefinition.response_body)
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_by_method(
        self,
        session: Session,
        method: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[ApiDefinition]:
        """Get API definitions by HTTP method.

        Args:
            session: Database session
            method: HTTP method (GET/POST/PUT/etc)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.method == method)
            .where(ApiDefinition.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def search_by_path(
        self,
        session: Session,
        path: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[ApiDefinition]:
        """Search API definitions by path (case-insensitive).

        Args:
            session: Database session
            path: Path to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.path.ilike(f"%{path}%"))
            .where(ApiDefinition.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_header(
        self,
        session: Session,
        header_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[ApiDefinition]:
        """Get API definitions that use a specific header.

        Args:
            session: Database session
            header_id: Header ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.header_id == header_id)
            .where(ApiDefinition.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_with_relations_async(
        self,
        session: AsyncSession,
        id: int
    ) -> ApiDefinition | None:
        """Get API definition with relations (async).

        Args:
            session: Async database session
            id: API definition ID

        Returns:
            ApiDefinition instance with relations loaded, or None
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.id == id)
            .options(
                joinedload(ApiDefinition.header),
                joinedload(ApiDefinition.request_body),
                joinedload(ApiDefinition.response_body)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_method_async(
        self,
        session: AsyncSession,
        method: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[ApiDefinition]:
        """Get API definitions by HTTP method (async).

        Args:
            session: Async database session
            method: HTTP method
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.method == method)
            .where(ApiDefinition.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_path_async(
        self,
        session: AsyncSession,
        path: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[ApiDefinition]:
        """Search API definitions by path (async).

        Args:
            session: Async database session
            path: Path to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.path.ilike(f"%{path}%"))
            .where(ApiDefinition.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_header_async(
        self,
        session: AsyncSession,
        header_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[ApiDefinition]:
        """Get API definitions by header (async).

        Args:
            session: Async database session
            header_id: Header ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        stmt = (
            select(ApiDefinition)
            .where(ApiDefinition.header_id == header_id)
            .where(ApiDefinition.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
