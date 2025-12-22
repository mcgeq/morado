"""Repository for Layer 3: Test Component models.

This module provides data access methods for TestComponent and ComponentScript models.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from morado.models.component import ComponentScript, ComponentType, TestComponent
from morado.repositories.base import BaseRepository


class TestComponentRepository(BaseRepository[TestComponent]):
    """Repository for TestComponent model.

    Provides data access methods for test components with support for
    nested components and script associations.

    Example:
        >>> repo = TestComponentRepository()
        >>> component = repo.get_with_scripts(session, 1)
        >>> # component.component_scripts are loaded
    """

    def __init__(self):
        """Initialize TestComponent repository."""
        super().__init__(TestComponent)

    def get_with_scripts(
        self,
        session: Session,
        id: int
    ) -> TestComponent | None:
        """Get component with associated scripts.

        Args:
            session: Database session
            id: Component ID

        Returns:
            TestComponent instance with scripts loaded, or None

        Example:
            >>> component = repo.get_with_scripts(session, 1)
            >>> for cs in component.component_scripts:
            ...     print(cs.script.name)
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.id == id)
            .options(
                joinedload(TestComponent.component_scripts)
                .joinedload(ComponentScript.script)
            )
        )
        return session.execute(stmt).unique().scalar_one_or_none()

    def get_with_children(
        self,
        session: Session,
        id: int
    ) -> TestComponent | None:
        """Get component with child components.

        Args:
            session: Database session
            id: Component ID

        Returns:
            TestComponent instance with children loaded, or None

        Example:
            >>> component = repo.get_with_children(session, 1)
            >>> for child in component.child_components:
            ...     print(child.name)
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.id == id)
            .options(joinedload(TestComponent.child_components))
        )
        return session.execute(stmt).unique().scalar_one_or_none()

    def get_with_full_hierarchy(
        self,
        session: Session,
        id: int
    ) -> TestComponent | None:
        """Get component with scripts and child components.

        Args:
            session: Database session
            id: Component ID

        Returns:
            TestComponent instance with full hierarchy loaded, or None

        Example:
            >>> component = repo.get_with_full_hierarchy(session, 1)
            >>> print(len(component.component_scripts))
            >>> print(len(component.child_components))
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.id == id)
            .options(
                joinedload(TestComponent.component_scripts)
                .joinedload(ComponentScript.script),
                joinedload(TestComponent.child_components)
            )
        )
        return session.execute(stmt).unique().scalar_one_or_none()

    def get_by_type(
        self,
        session: Session,
        component_type: ComponentType,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get components by type.

        Args:
            session: Database session
            component_type: Component type (simple/composite/template)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances

        Example:
            >>> templates = repo.get_by_type(session, ComponentType.TEMPLATE)
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.component_type == component_type)
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_root_components(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get root components (components without parent).

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of root TestComponent instances

        Example:
            >>> roots = repo.get_root_components(session)
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.parent_component_id.is_(None))
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_children(
        self,
        session: Session,
        parent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get child components of a parent.

        Args:
            session: Database session
            parent_id: Parent component ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of child TestComponent instances

        Example:
            >>> children = repo.get_children(session, 1)
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.parent_component_id == parent_id)
            .where(TestComponent.is_active)
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
    ) -> list[TestComponent]:
        """Search components by name (case-insensitive).

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances

        Example:
            >>> components = repo.search_by_name(session, "login")
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.name.ilike(f"%{name}%"))
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_tags(
        self,
        session: Session,
        tags: list[str],
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get components by tags.

        Args:
            session: Database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances

        Example:
            >>> components = repo.get_by_tags(session, ["auth", "api"])
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.tags.contains(tags))
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_with_scripts_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestComponent | None:
        """Get component with scripts (async).

        Args:
            session: Async database session
            id: Component ID

        Returns:
            TestComponent instance with scripts loaded, or None
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.id == id)
            .options(
                joinedload(TestComponent.component_scripts)
                .joinedload(ComponentScript.script)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_children_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestComponent | None:
        """Get component with children (async).

        Args:
            session: Async database session
            id: Component ID

        Returns:
            TestComponent instance with children loaded, or None
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.id == id)
            .options(joinedload(TestComponent.child_components))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_full_hierarchy_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestComponent | None:
        """Get component with full hierarchy (async).

        Args:
            session: Async database session
            id: Component ID

        Returns:
            TestComponent instance with full hierarchy loaded, or None
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.id == id)
            .options(
                joinedload(TestComponent.component_scripts)
                .joinedload(ComponentScript.script),
                joinedload(TestComponent.child_components)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_type_async(
        self,
        session: AsyncSession,
        component_type: ComponentType,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get components by type (async).

        Args:
            session: Async database session
            component_type: Component type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.component_type == component_type)
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_root_components_async(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get root components (async).

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of root TestComponent instances
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.parent_component_id.is_(None))
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_children_async(
        self,
        session: AsyncSession,
        parent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get child components (async).

        Args:
            session: Async database session
            parent_id: Parent component ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of child TestComponent instances
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.parent_component_id == parent_id)
            .where(TestComponent.is_active)
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
    ) -> list[TestComponent]:
        """Search components by name (async).

        Args:
            session: Async database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.name.ilike(f"%{name}%"))
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_tags_async(
        self,
        session: AsyncSession,
        tags: list[str],
        skip: int = 0,
        limit: int = 100
    ) -> list[TestComponent]:
        """Get components by tags (async).

        Args:
            session: Async database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances
        """
        stmt = (
            select(TestComponent)
            .where(TestComponent.tags.contains(tags))
            .where(TestComponent.is_active)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class ComponentScriptRepository(BaseRepository[ComponentScript]):
    """Repository for ComponentScript association model.

    Provides data access methods for component-script associations.

    Example:
        >>> repo = ComponentScriptRepository()
        >>> associations = repo.get_by_component(session, 1)
    """

    def __init__(self):
        """Initialize ComponentScript repository."""
        super().__init__(ComponentScript)

    def get_by_component(
        self,
        session: Session,
        component_id: int
    ) -> list[ComponentScript]:
        """Get script associations for a component.

        Args:
            session: Database session
            component_id: Component ID

        Returns:
            List of ComponentScript instances ordered by execution_order

        Example:
            >>> associations = repo.get_by_component(session, 1)
            >>> for assoc in associations:
            ...     print(f"{assoc.execution_order}: {assoc.script.name}")
        """
        stmt = (
            select(ComponentScript)
            .where(ComponentScript.component_id == component_id)
            .where(ComponentScript.is_enabled)
            .options(joinedload(ComponentScript.script))
            .order_by(ComponentScript.execution_order)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_script(
        self,
        session: Session,
        script_id: int
    ) -> list[ComponentScript]:
        """Get component associations for a script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            List of ComponentScript instances

        Example:
            >>> associations = repo.get_by_script(session, 1)
            >>> for assoc in associations:
            ...     print(assoc.component.name)
        """
        stmt = (
            select(ComponentScript)
            .where(ComponentScript.script_id == script_id)
            .options(joinedload(ComponentScript.component))
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_component_async(
        self,
        session: AsyncSession,
        component_id: int
    ) -> list[ComponentScript]:
        """Get script associations for a component (async).

        Args:
            session: Async database session
            component_id: Component ID

        Returns:
            List of ComponentScript instances
        """
        stmt = (
            select(ComponentScript)
            .where(ComponentScript.component_id == component_id)
            .where(ComponentScript.is_enabled)
            .options(joinedload(ComponentScript.script))
            .order_by(ComponentScript.execution_order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_script_async(
        self,
        session: AsyncSession,
        script_id: int
    ) -> list[ComponentScript]:
        """Get component associations for a script (async).

        Args:
            session: Async database session
            script_id: Script ID

        Returns:
            List of ComponentScript instances
        """
        stmt = (
            select(ComponentScript)
            .where(ComponentScript.script_id == script_id)
            .options(joinedload(ComponentScript.component))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
