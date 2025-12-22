"""Repository for Layer 4: Test Case models.

This module provides data access methods for TestCase, TestCaseScript,
and TestCaseComponent models.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from morado.models.test_case import (
    TestCase,
    TestCaseComponent,
    TestCasePriority,
    TestCaseScript,
    TestCaseStatus,
)
from morado.repositories.base import BaseRepository


class TestCaseRepository(BaseRepository[TestCase]):
    """Repository for TestCase model.

    Provides data access methods for test cases with support for
    loading associated scripts and components.

    Example:
        >>> repo = TestCaseRepository()
        >>> test_case = repo.get_with_relations(session, 1)
        >>> # test_case.test_case_scripts and test_case_components are loaded
    """

    def __init__(self):
        """Initialize TestCase repository."""
        super().__init__(TestCase)

    def get_with_scripts(
        self,
        session: Session,
        id: int
    ) -> TestCase | None:
        """Get test case with associated scripts.

        Args:
            session: Database session
            id: Test case ID

        Returns:
            TestCase instance with scripts loaded, or None

        Example:
            >>> test_case = repo.get_with_scripts(session, 1)
            >>> for tcs in test_case.test_case_scripts:
            ...     print(tcs.script.name)
        """
        stmt = (
            select(TestCase)
            .where(TestCase.id == id)
            .options(
                joinedload(TestCase.test_case_scripts)
                .joinedload(TestCaseScript.script)
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_with_components(
        self,
        session: Session,
        id: int
    ) -> TestCase | None:
        """Get test case with associated components.

        Args:
            session: Database session
            id: Test case ID

        Returns:
            TestCase instance with components loaded, or None

        Example:
            >>> test_case = repo.get_with_components(session, 1)
            >>> for tcc in test_case.test_case_components:
            ...     print(tcc.component.name)
        """
        stmt = (
            select(TestCase)
            .where(TestCase.id == id)
            .options(
                joinedload(TestCase.test_case_components)
                .joinedload(TestCaseComponent.component)
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_with_relations(
        self,
        session: Session,
        id: int
    ) -> TestCase | None:
        """Get test case with all relations (scripts and components).

        Args:
            session: Database session
            id: Test case ID

        Returns:
            TestCase instance with all relations loaded, or None

        Example:
            >>> test_case = repo.get_with_relations(session, 1)
            >>> print(len(test_case.test_case_scripts))
            >>> print(len(test_case.test_case_components))
        """
        stmt = (
            select(TestCase)
            .where(TestCase.id == id)
            .options(
                joinedload(TestCase.test_case_scripts)
                .joinedload(TestCaseScript.script),
                joinedload(TestCase.test_case_components)
                .joinedload(TestCaseComponent.component)
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_by_status(
        self,
        session: Session,
        status: TestCaseStatus,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get test cases by status.

        Args:
            session: Database session
            status: Test case status (draft/active/deprecated/archived)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances

        Example:
            >>> active_cases = repo.get_by_status(session, TestCaseStatus.ACTIVE)
        """
        stmt = (
            select(TestCase)
            .where(TestCase.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_priority(
        self,
        session: Session,
        priority: TestCasePriority,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get test cases by priority.

        Args:
            session: Database session
            priority: Test case priority (low/medium/high/critical)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances

        Example:
            >>> critical_cases = repo.get_by_priority(session, TestCasePriority.CRITICAL)
        """
        stmt = (
            select(TestCase)
            .where(TestCase.priority == priority)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_category(
        self,
        session: Session,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get test cases by category.

        Args:
            session: Database session
            category: Test case category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances

        Example:
            >>> user_cases = repo.get_by_category(session, "用户管理")
        """
        stmt = (
            select(TestCase)
            .where(TestCase.category == category)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_environment(
        self,
        session: Session,
        environment: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get test cases by environment.

        Args:
            session: Database session
            environment: Execution environment (dev/test/prod)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances

        Example:
            >>> test_cases = repo.get_by_environment(session, "test")
        """
        stmt = (
            select(TestCase)
            .where(TestCase.environment == environment)
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
    ) -> list[TestCase]:
        """Search test cases by name (case-insensitive).

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances

        Example:
            >>> cases = repo.search_by_name(session, "login")
        """
        stmt = (
            select(TestCase)
            .where(TestCase.name.ilike(f"%{name}%"))
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
    ) -> list[TestCase]:
        """Get test cases by tags.

        Args:
            session: Database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances

        Example:
            >>> cases = repo.get_by_tags(session, ["auth", "api"])
        """
        stmt = (
            select(TestCase)
            .where(TestCase.tags.contains(tags))
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_automated_cases(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get automated test cases.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of automated TestCase instances

        Example:
            >>> automated = repo.get_automated_cases(session)
        """
        stmt = (
            select(TestCase)
            .where(TestCase.is_automated == True)
            .where(TestCase.status == TestCaseStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_with_scripts_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestCase | None:
        """Get test case with scripts (async).

        Args:
            session: Async database session
            id: Test case ID

        Returns:
            TestCase instance with scripts loaded, or None
        """
        stmt = (
            select(TestCase)
            .where(TestCase.id == id)
            .options(
                joinedload(TestCase.test_case_scripts)
                .joinedload(TestCaseScript.script)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_components_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestCase | None:
        """Get test case with components (async).

        Args:
            session: Async database session
            id: Test case ID

        Returns:
            TestCase instance with components loaded, or None
        """
        stmt = (
            select(TestCase)
            .where(TestCase.id == id)
            .options(
                joinedload(TestCase.test_case_components)
                .joinedload(TestCaseComponent.component)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_relations_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestCase | None:
        """Get test case with all relations (async).

        Args:
            session: Async database session
            id: Test case ID

        Returns:
            TestCase instance with all relations loaded, or None
        """
        stmt = (
            select(TestCase)
            .where(TestCase.id == id)
            .options(
                joinedload(TestCase.test_case_scripts)
                .joinedload(TestCaseScript.script),
                joinedload(TestCase.test_case_components)
                .joinedload(TestCaseComponent.component)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status_async(
        self,
        session: AsyncSession,
        status: TestCaseStatus,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get test cases by status (async).

        Args:
            session: Async database session
            status: Test case status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances
        """
        stmt = (
            select(TestCase)
            .where(TestCase.status == status)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_priority_async(
        self,
        session: AsyncSession,
        priority: TestCasePriority,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get test cases by priority (async).

        Args:
            session: Async database session
            priority: Test case priority
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances
        """
        stmt = (
            select(TestCase)
            .where(TestCase.priority == priority)
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
    ) -> list[TestCase]:
        """Search test cases by name (async).

        Args:
            session: Async database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances
        """
        stmt = (
            select(TestCase)
            .where(TestCase.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_automated_cases_async(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestCase]:
        """Get automated test cases (async).

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of automated TestCase instances
        """
        stmt = (
            select(TestCase)
            .where(TestCase.is_automated == True)
            .where(TestCase.status == TestCaseStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class TestCaseScriptRepository(BaseRepository[TestCaseScript]):
    """Repository for TestCaseScript association model.

    Provides data access methods for test case-script associations.

    Example:
        >>> repo = TestCaseScriptRepository()
        >>> associations = repo.get_by_test_case(session, 1)
    """

    def __init__(self):
        """Initialize TestCaseScript repository."""
        super().__init__(TestCaseScript)

    def get_by_test_case(
        self,
        session: Session,
        test_case_id: int
    ) -> list[TestCaseScript]:
        """Get script associations for a test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            List of TestCaseScript instances ordered by execution_order

        Example:
            >>> associations = repo.get_by_test_case(session, 1)
            >>> for assoc in associations:
            ...     print(f"{assoc.execution_order}: {assoc.script.name}")
        """
        stmt = (
            select(TestCaseScript)
            .where(TestCaseScript.test_case_id == test_case_id)
            .where(TestCaseScript.is_enabled == True)
            .options(joinedload(TestCaseScript.script))
            .order_by(TestCaseScript.execution_order)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_script(
        self,
        session: Session,
        script_id: int
    ) -> list[TestCaseScript]:
        """Get test case associations for a script.

        Args:
            session: Database session
            script_id: Script ID

        Returns:
            List of TestCaseScript instances

        Example:
            >>> associations = repo.get_by_script(session, 1)
            >>> for assoc in associations:
            ...     print(assoc.test_case.name)
        """
        stmt = (
            select(TestCaseScript)
            .where(TestCaseScript.script_id == script_id)
            .options(joinedload(TestCaseScript.test_case))
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_test_case_async(
        self,
        session: AsyncSession,
        test_case_id: int
    ) -> list[TestCaseScript]:
        """Get script associations for a test case (async).

        Args:
            session: Async database session
            test_case_id: Test case ID

        Returns:
            List of TestCaseScript instances
        """
        stmt = (
            select(TestCaseScript)
            .where(TestCaseScript.test_case_id == test_case_id)
            .where(TestCaseScript.is_enabled == True)
            .options(joinedload(TestCaseScript.script))
            .order_by(TestCaseScript.execution_order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_script_async(
        self,
        session: AsyncSession,
        script_id: int
    ) -> list[TestCaseScript]:
        """Get test case associations for a script (async).

        Args:
            session: Async database session
            script_id: Script ID

        Returns:
            List of TestCaseScript instances
        """
        stmt = (
            select(TestCaseScript)
            .where(TestCaseScript.script_id == script_id)
            .options(joinedload(TestCaseScript.test_case))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class TestCaseComponentRepository(BaseRepository[TestCaseComponent]):
    """Repository for TestCaseComponent association model.

    Provides data access methods for test case-component associations.

    Example:
        >>> repo = TestCaseComponentRepository()
        >>> associations = repo.get_by_test_case(session, 1)
    """

    def __init__(self):
        """Initialize TestCaseComponent repository."""
        super().__init__(TestCaseComponent)

    def get_by_test_case(
        self,
        session: Session,
        test_case_id: int
    ) -> list[TestCaseComponent]:
        """Get component associations for a test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            List of TestCaseComponent instances ordered by execution_order

        Example:
            >>> associations = repo.get_by_test_case(session, 1)
            >>> for assoc in associations:
            ...     print(f"{assoc.execution_order}: {assoc.component.name}")
        """
        stmt = (
            select(TestCaseComponent)
            .where(TestCaseComponent.test_case_id == test_case_id)
            .where(TestCaseComponent.is_enabled == True)
            .options(joinedload(TestCaseComponent.component))
            .order_by(TestCaseComponent.execution_order)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_component(
        self,
        session: Session,
        component_id: int
    ) -> list[TestCaseComponent]:
        """Get test case associations for a component.

        Args:
            session: Database session
            component_id: Component ID

        Returns:
            List of TestCaseComponent instances

        Example:
            >>> associations = repo.get_by_component(session, 1)
            >>> for assoc in associations:
            ...     print(assoc.test_case.name)
        """
        stmt = (
            select(TestCaseComponent)
            .where(TestCaseComponent.component_id == component_id)
            .options(joinedload(TestCaseComponent.test_case))
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_test_case_async(
        self,
        session: AsyncSession,
        test_case_id: int
    ) -> list[TestCaseComponent]:
        """Get component associations for a test case (async).

        Args:
            session: Async database session
            test_case_id: Test case ID

        Returns:
            List of TestCaseComponent instances
        """
        stmt = (
            select(TestCaseComponent)
            .where(TestCaseComponent.test_case_id == test_case_id)
            .where(TestCaseComponent.is_enabled == True)
            .options(joinedload(TestCaseComponent.component))
            .order_by(TestCaseComponent.execution_order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_component_async(
        self,
        session: AsyncSession,
        component_id: int
    ) -> list[TestCaseComponent]:
        """Get test case associations for a component (async).

        Args:
            session: Async database session
            component_id: Component ID

        Returns:
            List of TestCaseComponent instances
        """
        stmt = (
            select(TestCaseComponent)
            .where(TestCaseComponent.component_id == component_id)
            .options(joinedload(TestCaseComponent.test_case))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
