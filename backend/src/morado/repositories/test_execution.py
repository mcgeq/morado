"""Repository for Test Execution models.

This module provides data access methods for TestExecution and ExecutionResult models.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from morado.models.test_execution import ExecutionResult, ExecutionStatus, TestExecution
from morado.repositories.base import BaseRepository


class TestExecutionRepository(BaseRepository[TestExecution]):
    """Repository for TestExecution model.

    Provides data access methods for test executions with support for
    loading execution results.

    Example:
        >>> repo = TestExecutionRepository()
        >>> execution = repo.get_with_results(session, 1)
        >>> # execution.execution_results are loaded
    """

    def __init__(self):
        """Initialize TestExecution repository."""
        super().__init__(TestExecution)

    def get_with_results(
        self, session: Session, execution_id: int
    ) -> TestExecution | None:
        """Get test execution with execution results.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            TestExecution instance with results loaded, or None

        Example:
            >>> execution = repo.get_with_results(session, 1)
            >>> for result in execution.execution_results:
            ...     print(result.status)
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.id == execution_id)
            .options(joinedload(TestExecution.execution_results))
        )
        return session.execute(stmt).unique().scalar_one_or_none()

    def get_by_test_case(
        self, session: Session, test_case_id: int, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by test case.

        Args:
            session: Database session
            test_case_id: Test case ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances ordered by start_time desc

        Example:
            >>> executions = repo.get_by_test_case(session, 1)
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.test_case_id == test_case_id)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_test_suite(
        self, session: Session, test_suite_id: int, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by test suite.

        Args:
            session: Database session
            test_suite_id: Test suite ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances ordered by start_time desc

        Example:
            >>> executions = repo.get_by_test_suite(session, 1)
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.test_suite_id == test_suite_id)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_status(
        self, session: Session, status: ExecutionStatus, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by status.

        Args:
            session: Database session
            status: Execution status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances

        Example:
            >>> running = repo.get_by_status(session, ExecutionStatus.RUNNING)
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.status == status)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_environment(
        self, session: Session, environment: str, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by environment.

        Args:
            session: Database session
            environment: Execution environment
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances

        Example:
            >>> executions = repo.get_by_environment(session, "test")
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.environment == environment)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_with_results_async(
        self, session: AsyncSession, execution_id: int
    ) -> TestExecution | None:
        """Get test execution with results (async).

        Args:
            session: Async database session
            execution_id: Execution ID

        Returns:
            TestExecution instance with results loaded, or None
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.id == execution_id)
            .options(joinedload(TestExecution.execution_results))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_test_case_async(
        self, session: AsyncSession, test_case_id: int, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by test case (async).

        Args:
            session: Async database session
            test_case_id: Test case ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.test_case_id == test_case_id)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_test_suite_async(
        self, session: AsyncSession, test_suite_id: int, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by test suite (async).

        Args:
            session: Async database session
            test_suite_id: Test suite ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.test_suite_id == test_suite_id)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status_async(
        self,
        session: AsyncSession,
        status: ExecutionStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestExecution]:
        """Get executions by status (async).

        Args:
            session: Async database session
            status: Execution status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.status == status)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_environment_async(
        self, session: AsyncSession, environment: str, skip: int = 0, limit: int = 100
    ) -> list[TestExecution]:
        """Get executions by environment (async).

        Args:
            session: Async database session
            environment: Execution environment
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances
        """
        stmt = (
            select(TestExecution)
            .where(TestExecution.environment == environment)
            .order_by(TestExecution.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


class ExecutionResultRepository(BaseRepository[ExecutionResult]):
    """Repository for ExecutionResult model.

    Provides data access methods for execution results.

    Example:
        >>> repo = ExecutionResultRepository()
        >>> results = repo.get_by_execution(session, 1)
    """

    def __init__(self):
        """Initialize ExecutionResult repository."""
        super().__init__(ExecutionResult)

    def get_by_execution(
        self, session: Session, execution_id: int
    ) -> list[ExecutionResult]:
        """Get results for an execution.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            List of ExecutionResult instances

        Example:
            >>> results = repo.get_by_execution(session, 1)
            >>> for result in results:
            ...     print(f"{result.script_id}: {result.status}")
        """
        stmt = (
            select(ExecutionResult)
            .where(ExecutionResult.execution_id == execution_id)
            .order_by(ExecutionResult.start_time)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_script(
        self, session: Session, script_id: int, skip: int = 0, limit: int = 100
    ) -> list[ExecutionResult]:
        """Get results for a script.

        Args:
            session: Database session
            script_id: Script ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ExecutionResult instances

        Example:
            >>> results = repo.get_by_script(session, 1)
        """
        stmt = (
            select(ExecutionResult)
            .where(ExecutionResult.script_id == script_id)
            .order_by(ExecutionResult.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    def get_by_component(
        self, session: Session, component_id: int, skip: int = 0, limit: int = 100
    ) -> list[ExecutionResult]:
        """Get results for a component.

        Args:
            session: Database session
            component_id: Component ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ExecutionResult instances

        Example:
            >>> results = repo.get_by_component(session, 1)
        """
        stmt = (
            select(ExecutionResult)
            .where(ExecutionResult.component_id == component_id)
            .order_by(ExecutionResult.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.execute(stmt).scalars().all())

    # Async methods

    async def get_by_execution_async(
        self, session: AsyncSession, execution_id: int
    ) -> list[ExecutionResult]:
        """Get results for an execution (async).

        Args:
            session: Async database session
            execution_id: Execution ID

        Returns:
            List of ExecutionResult instances
        """
        stmt = (
            select(ExecutionResult)
            .where(ExecutionResult.execution_id == execution_id)
            .order_by(ExecutionResult.start_time)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_script_async(
        self, session: AsyncSession, script_id: int, skip: int = 0, limit: int = 100
    ) -> list[ExecutionResult]:
        """Get results for a script (async).

        Args:
            session: Async database session
            script_id: Script ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ExecutionResult instances
        """
        stmt = (
            select(ExecutionResult)
            .where(ExecutionResult.script_id == script_id)
            .order_by(ExecutionResult.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_component_async(
        self, session: AsyncSession, component_id: int, skip: int = 0, limit: int = 100
    ) -> list[ExecutionResult]:
        """Get results for a component (async).

        Args:
            session: Async database session
            component_id: Component ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ExecutionResult instances
        """
        stmt = (
            select(ExecutionResult)
            .where(ExecutionResult.component_id == component_id)
            .order_by(ExecutionResult.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
