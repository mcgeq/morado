"""Service layer for Test Suite management.

This module provides business logic for managing test suites.
"""

from typing import Any

from sqlalchemy.orm import Session

from morado.models.test_suite import TestSuite, TestSuiteCase
from morado.repositories.test_suite import TestSuiteRepository


class TestSuiteService:
    """Service for managing test suites.

    Provides business logic for creating, updating, and managing test suites
    that group multiple test cases.

    Example:
        >>> service = TestSuiteService()
        >>> suite = service.create_test_suite(
        ...     session,
        ...     name="Regression Test Suite",
        ...     parallel_execution=True
        ... )
    """

    def __init__(self):
        """Initialize TestSuite service."""
        self.repository = TestSuiteRepository()

    def create_test_suite(  # noqa: PLR0913
        self,
        session: Session,
        name: str,
        description: str | None = None,
        execution_order: str = "sequential",
        parallel_execution: bool = False,
        continue_on_failure: bool = True,
        schedule_config: dict | None = None,
        is_scheduled: bool = False,
        environment: str = "test",
        global_variables: dict | None = None,
        tags: list[str] | None = None,
        created_by: int | None = None,
        **kwargs: Any,
    ) -> TestSuite:
        """Create a new test suite.

        Args:
            session: Database session
            name: Suite name
            description: Suite description
            execution_order: Execution order (sequential/parallel)
            parallel_execution: Whether to execute in parallel
            continue_on_failure: Whether to continue on failure
            schedule_config: Schedule configuration (cron, etc.)
            is_scheduled: Whether scheduling is enabled
            environment: Execution environment
            global_variables: Global variables for all test cases
            tags: Tags for categorization
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created TestSuite instance
        """
        suite = self.repository.create(
            session,
            name=name,
            description=description,
            execution_order=execution_order,
            parallel_execution=parallel_execution,
            continue_on_failure=continue_on_failure,
            schedule_config=schedule_config,
            is_scheduled=is_scheduled,
            environment=environment,
            global_variables=global_variables,
            tags=tags,
            created_by=created_by,
            **kwargs,
        )

        session.commit()
        return suite

    def get_test_suite(
        self,
        session: Session,
        suite_id: int,
        with_test_cases: bool = False,  # noqa: ARG002
    ) -> TestSuite | None:
        """Get test suite by ID.

        Args:
            session: Database session
            suite_id: Suite ID
            with_test_cases: Whether to load associated test cases

        Returns:
            TestSuite instance or None if not found
        """
        # Note: Repository doesn't have get_with_test_cases yet
        # For now, just get the suite and let relationships load lazily
        return self.repository.get_by_id(session, suite_id)

    def get_test_suite_by_uuid(self, session: Session, uuid: str) -> TestSuite | None:
        """Get test suite by UUID.

        Args:
            session: Database session
            uuid: Suite UUID

        Returns:
            TestSuite instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_test_suites(
        self,
        session: Session,
        environment: str | None = None,
        scheduled_only: bool = False,
        tags: list[str] | None = None,  # noqa: ARG002
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestSuite]:
        """List test suites with optional filtering.

        Args:
            session: Database session
            environment: Filter by environment
            scheduled_only: Whether to return only scheduled suites
            tags: Filter by tags
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestSuite instances
        """
        filters = {}

        if environment:
            filters["environment"] = environment

        if scheduled_only:
            filters["is_scheduled"] = True

        return self.repository.get_all(session, skip, limit, filters)

    def update_test_suite(
        self, session: Session, suite_id: int, **kwargs: Any
    ) -> TestSuite | None:
        """Update test suite.

        Args:
            session: Database session
            suite_id: Suite ID
            **kwargs: Fields to update

        Returns:
            Updated TestSuite instance or None if not found
        """
        suite = self.repository.get_by_id(session, suite_id)
        if not suite:
            return None

        updated_suite = self.repository.update(session, suite, **kwargs)
        session.commit()
        return updated_suite

    def delete_test_suite(self, session: Session, suite_id: int) -> bool:
        """Delete test suite.

        Args:
            session: Database session
            suite_id: Suite ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, suite_id)
        if result:
            session.commit()
        return result

    def add_test_case_to_suite(
        self,
        session: Session,
        suite_id: int,
        test_case_id: int,
        execution_order: int = 0,
        is_enabled: bool = True,
        case_parameters: dict | None = None,
        description: str | None = None,
    ) -> TestSuiteCase:
        """Add test case to suite.

        Args:
            session: Database session
            suite_id: Suite ID
            test_case_id: Test case ID
            execution_order: Execution order
            is_enabled: Whether test case is enabled
            case_parameters: Test case parameter overrides
            description: Description

        Returns:
            Created TestSuiteCase instance
        """
        # Create the association directly using SQLAlchemy
        suite_case = TestSuiteCase(
            test_suite_id=suite_id,
            test_case_id=test_case_id,
            execution_order=execution_order,
            is_enabled=is_enabled,
            case_parameters=case_parameters,
            description=description,
        )

        session.add(suite_case)
        session.commit()
        session.refresh(suite_case)

        return suite_case

    def get_suite_test_cases(
        self, session: Session, suite_id: int
    ) -> list[TestSuiteCase]:
        """Get test cases in suite.

        Args:
            session: Database session
            suite_id: Suite ID

        Returns:
            List of TestSuiteCase instances ordered by execution_order
        """
        suite = self.repository.get_by_id(session, suite_id)
        if not suite:
            return []

        return sorted(suite.test_suite_cases, key=lambda x: x.execution_order)

    def update_suite_test_case(
        self, session: Session, suite_case_id: int, **kwargs: Any
    ) -> TestSuiteCase | None:
        """Update suite-test case association.

        Args:
            session: Database session
            suite_case_id: TestSuiteCase ID
            **kwargs: Fields to update

        Returns:
            Updated TestSuiteCase instance or None if not found
        """
        suite_case = session.get(TestSuiteCase, suite_case_id)
        if not suite_case:
            return None

        for key, value in kwargs.items():
            if hasattr(suite_case, key):
                setattr(suite_case, key, value)

        session.commit()
        session.refresh(suite_case)
        return suite_case

    def remove_test_case_from_suite(self, session: Session, suite_case_id: int) -> bool:
        """Remove test case from suite.

        Args:
            session: Database session
            suite_case_id: TestSuiteCase ID

        Returns:
            True if removed, False if not found
        """
        suite_case = session.get(TestSuiteCase, suite_case_id)
        if not suite_case:
            return False

        session.delete(suite_case)
        session.commit()
        return True

    def enable_scheduling(
        self, session: Session, suite_id: int, schedule_config: dict
    ) -> TestSuite | None:
        """Enable scheduling for test suite.

        Args:
            session: Database session
            suite_id: Suite ID
            schedule_config: Schedule configuration (cron expression, etc.)

        Returns:
            Updated TestSuite instance or None if not found
        """
        return self.update_test_suite(
            session, suite_id, is_scheduled=True, schedule_config=schedule_config
        )

    def disable_scheduling(self, session: Session, suite_id: int) -> TestSuite | None:
        """Disable scheduling for test suite.

        Args:
            session: Database session
            suite_id: Suite ID

        Returns:
            Updated TestSuite instance or None if not found
        """
        return self.update_test_suite(session, suite_id, is_scheduled=False)

    def get_suite_execution_plan(
        self, session: Session, suite_id: int
    ) -> dict[str, Any] | None:
        """Get complete suite execution plan.

        This method returns all information needed to execute a test suite,
        including all test cases in execution order.

        Args:
            session: Database session
            suite_id: Suite ID

        Returns:
            Dictionary with complete execution plan or None if not found
        """
        suite = self.repository.get_by_id(session, suite_id)
        if not suite:
            return None

        # Get test cases in execution order
        test_cases = []
        for tsc in sorted(suite.test_suite_cases, key=lambda x: x.execution_order):
            if tsc.is_enabled:
                test_cases.append(
                    {
                        "order": tsc.execution_order,
                        "test_case_id": tsc.test_case_id,
                        "test_case_name": tsc.test_case.name,
                        "parameters": tsc.case_parameters,
                        "description": tsc.description,
                    }
                )

        return {
            "suite": {
                "id": suite.id,
                "uuid": suite.uuid,
                "name": suite.name,
                "description": suite.description,
                "execution_order": suite.execution_order,
                "parallel_execution": suite.parallel_execution,
                "continue_on_failure": suite.continue_on_failure,
                "environment": suite.environment,
                "global_variables": suite.global_variables,
            },
            "test_cases": test_cases,
        }

    def clone_test_suite(
        self, session: Session, suite_id: int, new_name: str
    ) -> TestSuite | None:
        """Clone a test suite.

        Args:
            session: Database session
            suite_id: Suite ID to clone
            new_name: Name for the cloned suite

        Returns:
            Cloned TestSuite instance or None if source not found
        """
        source = self.repository.get_by_id(session, suite_id)
        if not source:
            return None

        # Create new suite
        cloned = self.repository.create(
            session,
            name=new_name,
            description=f"Cloned from: {source.name}",
            execution_order=source.execution_order,
            parallel_execution=source.parallel_execution,
            continue_on_failure=source.continue_on_failure,
            schedule_config=source.schedule_config,
            is_scheduled=False,  # Don't enable scheduling for clones
            environment=source.environment,
            global_variables=source.global_variables,
            tags=source.tags,
            created_by=source.created_by,
        )

        # Clone test case associations
        for tsc in source.test_suite_cases:
            suite_case = TestSuiteCase(
                test_suite_id=cloned.id,
                test_case_id=tsc.test_case_id,
                execution_order=tsc.execution_order,
                is_enabled=tsc.is_enabled,
                case_parameters=tsc.case_parameters,
                description=tsc.description,
            )
            session.add(suite_case)

        session.commit()
        return cloned
