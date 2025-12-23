"""Repository for Layer 2: Test Script models.

This module provides data access methods for TestScript and ScriptParameter models.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from morado.models.script import ScriptParameter, ScriptType, TestScript
from morado.repositories.base import BaseRepository


class TestScriptRepository(BaseRepository[TestScript]):
    """Repository for TestScript model.

    Provides data access methods for test scripts with support for
    eager loading of related API definitions and parameters.

    Example:
        >>> repo = TestScriptRepository()
        >>> script = repo.get_with_relations(session, 1)
        >>> # script.api_definition and script.parameters are loaded
    """

    def __init__(self):
        """Initialize TestScript repository."""
        super().__init__(TestScript)

    def get_with_relations(self, session: Session, script_id: int) -> TestScript | None:
        """Get test script with related API definition and parameters.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            TestScript instance with relations loaded, or None

        Example:
            >>> script = repo.get_with_relations(session, 1)
            >>> print(script.api_definition.name)
            >>> print(len(script.parameters))
        """
        stmt = (
            select(TestScript)
            .where(TestScript.id == script_id)
            .options(
                joinedload(TestScript.api_definition), joinedload(TestScript.parameters)
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_by_api_definition(
        self, session: Session, api_definition_id: int, skip: int = 0, limit: int = 100
    ) -> list[TestScript]:
        """Get scripts by API definition.

        Args:
            session: Database session
            api_definition_id: API definition ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances

        Example:
            >>> scripts = repo.get_by_api_definition(session, 1)
        """
        stmt = (
            select(TestScript)
            .where(TestScript.api_definition_id == api_definition_id)
            .where(TestScript.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_type(
        self, session: Session, script_type: ScriptType, skip: int = 0, limit: int = 100
    ) -> list[TestScript]:
        """Get scripts by type.

        Args:
            session: Database session
            script_type: Script type (setup/main/teardown/utility)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances

        Example:
            >>> setup_scripts = repo.get_by_type(session, ScriptType.SETUP)
        """
        stmt = (
            select(TestScript)
            .where(TestScript.script_type == script_type)
            .where(TestScript.is_active)
            .order_by(TestScript.execution_order)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def search_by_name(
        self, session: Session, name: str, skip: int = 0, limit: int = 100
    ) -> list[TestScript]:
        """Search scripts by name (case-insensitive).

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances

        Example:
            >>> scripts = repo.search_by_name(session, "login")
        """
        stmt = (
            select(TestScript)
            .where(TestScript.name.ilike(f"%{name}%"))
            .where(TestScript.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_tags(
        self, session: Session, tags: list[str], skip: int = 0, limit: int = 100
    ) -> list[TestScript]:
        """Get scripts by tags.

        Args:
            session: Database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances

        Example:
            >>> scripts = repo.get_by_tags(session, ["auth", "api"])
        """
        stmt = (
            select(TestScript)
            .where(TestScript.tags.contains(tags))
            .where(TestScript.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_with_relations_async(
        self, session: AsyncSession, script_id: int
    ) -> TestScript | None:
        """Get test script with relations (async).

        Args:
            session: Async database session
            script_id: Script ID

        Returns:
            TestScript instance with relations loaded, or None
        """
        stmt = (
            select(TestScript)
            .where(TestScript.id == script_id)
            .options(
                joinedload(TestScript.api_definition), joinedload(TestScript.parameters)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_api_definition_async(
        self,
        session: AsyncSession,
        api_definition_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestScript]:
        """Get scripts by API definition (async).

        Args:
            session: Async database session
            api_definition_id: API definition ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances
        """
        stmt = (
            select(TestScript)
            .where(TestScript.api_definition_id == api_definition_id)
            .where(TestScript.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type_async(
        self,
        session: AsyncSession,
        script_type: ScriptType,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestScript]:
        """Get scripts by type (async).

        Args:
            session: Async database session
            script_type: Script type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances
        """
        stmt = (
            select(TestScript)
            .where(TestScript.script_type == script_type)
            .where(TestScript.is_active)
            .order_by(TestScript.execution_order)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name_async(
        self, session: AsyncSession, name: str, skip: int = 0, limit: int = 100
    ) -> list[TestScript]:
        """Search scripts by name (async).

        Args:
            session: Async database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances
        """
        stmt = (
            select(TestScript)
            .where(TestScript.name.ilike(f"%{name}%"))
            .where(TestScript.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_tags_async(
        self, session: AsyncSession, tags: list[str], skip: int = 0, limit: int = 100
    ) -> list[TestScript]:
        """Get scripts by tags (async).

        Args:
            session: Async database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestScript instances
        """
        stmt = (
            select(TestScript)
            .where(TestScript.tags.contains(tags))
            .where(TestScript.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class ScriptParameterRepository(BaseRepository[ScriptParameter]):
    """Repository for ScriptParameter model.

    Provides data access methods for script parameters.

    Example:
        >>> repo = ScriptParameterRepository()
        >>> params = repo.get_by_script(session, 1)
    """

    def __init__(self):
        """Initialize ScriptParameter repository."""
        super().__init__(ScriptParameter)

    def get_by_script(self, session: Session, script_id: int) -> list[ScriptParameter]:
        """Get parameters for a specific script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            List of ScriptParameter instances ordered by order field

        Example:
            >>> params = repo.get_by_script(session, 1)
            >>> for param in params:
            ...     print(f"{param.name}: {param.parameter_type}")
        """
        stmt = (
            select(ScriptParameter)
            .where(ScriptParameter.script_id == script_id)
            .order_by(ScriptParameter.order)
        )
        return list(session.execute(stmt).scalars().all())

    def get_required_parameters(
        self, session: Session, script_id: int
    ) -> list[ScriptParameter]:
        """Get required parameters for a script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            List of required ScriptParameter instances

        Example:
            >>> required = repo.get_required_parameters(session, 1)
        """
        stmt = (
            select(ScriptParameter)
            .where(ScriptParameter.script_id == script_id)
            .where(ScriptParameter.is_required)
            .order_by(ScriptParameter.order)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_group(
        self, session: Session, script_id: int, group: str
    ) -> list[ScriptParameter]:
        """Get parameters by group.

        Args:
            session: Database session
            script_id: Script ID
            group: Parameter group name

        Returns:
            List of ScriptParameter instances in the group

        Example:
            >>> auth_params = repo.get_by_group(session, 1, "authentication")
        """
        stmt = (
            select(ScriptParameter)
            .where(ScriptParameter.script_id == script_id)
            .where(ScriptParameter.group == group)
            .order_by(ScriptParameter.order)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_script_async(
        self, session: AsyncSession, script_id: int
    ) -> list[ScriptParameter]:
        """Get parameters for a script (async).

        Args:
            session: Async database session
            script_id: Script ID

        Returns:
            List of ScriptParameter instances
        """
        stmt = (
            select(ScriptParameter)
            .where(ScriptParameter.script_id == script_id)
            .order_by(ScriptParameter.order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_required_parameters_async(
        self, session: AsyncSession, script_id: int
    ) -> list[ScriptParameter]:
        """Get required parameters for a script (async).

        Args:
            session: Async database session
            script_id: Script ID

        Returns:
            List of required ScriptParameter instances
        """
        stmt = (
            select(ScriptParameter)
            .where(ScriptParameter.script_id == script_id)
            .where(ScriptParameter.is_required)
            .order_by(ScriptParameter.order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_group_async(
        self, session: AsyncSession, script_id: int, group: str
    ) -> list[ScriptParameter]:
        """Get parameters by group (async).

        Args:
            session: Async database session
            script_id: Script ID
            group: Parameter group name

        Returns:
            List of ScriptParameter instances
        """
        stmt = (
            select(ScriptParameter)
            .where(ScriptParameter.script_id == script_id)
            .where(ScriptParameter.group == group)
            .order_by(ScriptParameter.order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
