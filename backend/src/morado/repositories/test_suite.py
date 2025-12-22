"""Repository for Test Suite models.

This module provides data access methods for TestSuite and TestSuiteCase models.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from morado.models.test_suite import TestSuite, TestSuiteCase
from morado.repositories.base import BaseRepository


class TestSuiteRepository(BaseRepository[TestSuite]):
    """Repository for TestSuite model.

    Provides data access methods for test suites with support for
    loading associated test cases.

    Example:
        >>> repo = TestSuiteRepository()
        >>> suite = repo.get_with_test_cases(session, 1)
        >>> # suite.test_suite_cases are loaded
    """

    def __init__(self):
        """Initialize TestSuite repository."""
        super().__init__(TestSuite)

    def get_with_test_cases(
        self,
        session: Session,
        id: int
    ) -> TestSuite | None:
        """Get test suite with associated test cases.

        Args:
            session: Database session
            id: Test suite ID

        Returns:
            TestSuite instance with test cases loaded, or None

        Example:
            >>> suite = repo.get_with_test_cases(session, 1)
            >>> for tsc in suite.test_suite_cases:
            ...     print(tsc.test_case.name)
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.id == id)
            .options(
                joinedload(TestSuite.test_suite_cases)
                .joinedload(TestSuiteCase.test_case)
            )
        )
        return session.execute(stmt).scalar_one_or_none()

    def get_by_environment(
        self,
        session: Session,
        environment: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestSuite]:
        """Get test suites by environment.

        Args:
            session: Database session
            environment: Execution environment (dev/test/prod)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances

        Example:
            >>> suites = repo.get_by_environment(session, "test")
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.environment == environment)
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_scheduled_suites(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestSuite]:
        """Get scheduled test suites.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of scheduled TestSuite instances

        Example:
            >>> scheduled = repo.get_scheduled_suites(session)
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.is_scheduled)
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
    ) -> list[TestSuite]:
        """Search test suites by name (case-insensitive).

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances

        Example:
            >>> suites = repo.search_by_name(session, "regression")
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.name.ilike(f"%{name}%"))
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
    ) -> list[TestSuite]:
        """Get test suites by tags.

        Args:
            session: Database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances

        Example:
            >>> suites = repo.get_by_tags(session, ["smoke", "critical"])
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.tags.contains(tags))
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_with_test_cases_async(
        self,
        session: AsyncSession,
        id: int
    ) -> TestSuite | None:
        """Get test suite with test cases (async).

        Args:
            session: Async database session
            id: Test suite ID

        Returns:
            TestSuite instance with test cases loaded, or None
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.id == id)
            .options(
                joinedload(TestSuite.test_suite_cases)
                .joinedload(TestSuiteCase.test_case)
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_environment_async(
        self,
        session: AsyncSession,
        environment: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestSuite]:
        """Get test suites by environment (async).

        Args:
            session: Async database session
            environment: Execution environment
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.environment == environment)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_scheduled_suites_async(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestSuite]:
        """Get scheduled test suites (async).

        Args:
            session: Async database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of scheduled TestSuite instances
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.is_scheduled)
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
    ) -> list[TestSuite]:
        """Search test suites by name (async).

        Args:
            session: Async database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.name.ilike(f"%{name}%"))
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
    ) -> list[TestSuite]:
        """Get test suites by tags (async).

        Args:
            session: Async database session
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances
        """
        stmt = (
            select(TestSuite)
            .where(TestSuite.tags.contains(tags))
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class TestSuiteCaseRepository(BaseRepository[TestSuiteCase]):
    """Repository for TestSuiteCase association model.

    Provides data access methods for test suite-case associations.

    Example:
        >>> repo = TestSuiteCaseRepository()
        >>> associations = repo.get_by_test_suite(session, 1)
    """

    def __init__(self):
        """Initialize TestSuiteCase repository."""
        super().__init__(TestSuiteCase)

    def get_by_test_suite(
        self,
        session: Session,
        test_suite_id: int
    ) -> list[TestSuiteCase]:
        """Get test case associations for a test suite.

        Args:
            session: Database session
            test_suite_id: Test suite ID

        Returns:
            List of TestSuiteCase instances ordered by execution_order

        Example:
            >>> associations = repo.get_by_test_suite(session, 1)
            >>> for assoc in associations:
            ...     print(f"{assoc.execution_order}: {assoc.test_case.name}")
        """
        stmt = (
            select(TestSuiteCase)
            .where(TestSuiteCase.test_suite_id == test_suite_id)
            .where(TestSuiteCase.is_enabled)
            .options(joinedload(TestSuiteCase.test_case))
            .order_by(TestSuiteCase.execution_order)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_test_case(
        self,
        session: Session,
        test_case_id: int
    ) -> list[TestSuiteCase]:
        """Get test suite associations for a test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            List of TestSuiteCase instances

        Example:
            >>> associations = repo.get_by_test_case(session, 1)
            >>> for assoc in associations:
            ...     print(assoc.test_suite.name)
        """
        stmt = (
            select(TestSuiteCase)
            .where(TestSuiteCase.test_case_id == test_case_id)
            .options(joinedload(TestSuiteCase.test_suite))
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_test_suite_async(
        self,
        session: AsyncSession,
        test_suite_id: int
    ) -> list[TestSuiteCase]:
        """Get test case associations for a test suite (async).

        Args:
            session: Async database session
            test_suite_id: Test suite ID

        Returns:
            List of TestSuiteCase instances
        """
        stmt = (
            select(TestSuiteCase)
            .where(TestSuiteCase.test_suite_id == test_suite_id)
            .where(TestSuiteCase.is_enabled)
            .options(joinedload(TestSuiteCase.test_case))
            .order_by(TestSuiteCase.execution_order)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_test_case_async(
        self,
        session: AsyncSession,
        test_case_id: int
    ) -> list[TestSuiteCase]:
        """Get test suite associations for a test case (async).

        Args:
            session: Async database session
            test_case_id: Test case ID

        Returns:
            List of TestSuiteCase instances
        """
        stmt = (
            select(TestSuiteCase)
            .where(TestSuiteCase.test_case_id == test_case_id)
            .options(joinedload(TestSuiteCase.test_suite))
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
