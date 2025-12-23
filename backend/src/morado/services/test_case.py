"""Service layer for Layer 4: Test Case management.

This module provides business logic for managing test cases.
"""

from typing import Any

from sqlalchemy.orm import Session

from morado.models.test_case import (
    TestCase,
    TestCaseComponent,
    TestCasePriority,
    TestCaseScript,
    TestCaseStatus,
)
from morado.repositories.test_case import (
    TestCaseComponentRepository,
    TestCaseRepository,
    TestCaseScriptRepository,
)


class TestCaseService:
    """Service for managing test cases.

    Provides business logic for creating, updating, and managing test cases
    that reference scripts and components.

    Example:
        >>> service = TestCaseService()
        >>> test_case = service.create_test_case(
        ...     session,
        ...     name="User Registration Flow",
        ...     priority=TestCasePriority.HIGH
        ... )
    """

    def __init__(self):
        """Initialize TestCase service."""
        self.repository = TestCaseRepository()
        self.script_repository = TestCaseScriptRepository()
        self.component_repository = TestCaseComponentRepository()

    def create_test_case(  # noqa: PLR0913
        self,
        session: Session,
        name: str,
        description: str | None = None,
        priority: TestCasePriority = TestCasePriority.MEDIUM,
        status: TestCaseStatus = TestCaseStatus.DRAFT,
        category: str | None = None,
        tags: list[str] | None = None,
        preconditions: str | None = None,
        postconditions: str | None = None,
        execution_order: str = "sequential",
        timeout: int = 300,
        retry_count: int = 0,
        continue_on_failure: bool = False,
        test_data: dict | None = None,
        environment: str = "test",
        is_automated: bool = True,
        created_by: int | None = None,
        **kwargs: Any,
    ) -> TestCase:
        """Create a new test case.

        Args:
            session: Database session
            name: Test case name
            description: Test case description
            priority: Priority level (low/medium/high/critical)
            status: Status (draft/active/deprecated/archived)
            category: Category
            tags: Tags for categorization
            preconditions: Preconditions
            postconditions: Postconditions
            execution_order: Execution order (sequential/parallel)
            timeout: Timeout in seconds
            retry_count: Number of retries
            continue_on_failure: Whether to continue on failure
            test_data: Test data
            environment: Execution environment
            is_automated: Whether test is automated
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created TestCase instance
        """
        test_case = self.repository.create(
            session,
            name=name,
            description=description,
            priority=priority,
            status=status,
            category=category,
            tags=tags,
            preconditions=preconditions,
            postconditions=postconditions,
            execution_order=execution_order,
            timeout=timeout,
            retry_count=retry_count,
            continue_on_failure=continue_on_failure,
            test_data=test_data,
            environment=environment,
            is_automated=is_automated,
            created_by=created_by,
            **kwargs,
        )

        session.commit()
        return test_case

    def get_test_case(
        self,
        session: Session,
        test_case_id: int,
        load_scripts: bool = False,
        load_components: bool = False,
        load_all: bool = False,
    ) -> TestCase | None:
        """Get test case by ID.

        Args:
            session: Database session
            test_case_id: Test case ID
            load_scripts: Whether to load associated scripts
            load_components: Whether to load associated components
            load_all: Whether to load all relations

        Returns:
            TestCase instance or None if not found
        """
        if load_all:
            return self.repository.get_with_relations(session, test_case_id)
        elif load_scripts:
            return self.repository.get_with_scripts(session, test_case_id)
        elif load_components:
            return self.repository.get_with_components(session, test_case_id)
        else:
            return self.repository.get_by_id(session, test_case_id)

    def get_test_case_by_uuid(self, session: Session, uuid: str) -> TestCase | None:
        """Get test case by UUID.

        Args:
            session: Database session
            uuid: Test case UUID

        Returns:
            TestCase instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_test_cases(
        self,
        session: Session,
        status: TestCaseStatus | None = None,
        priority: TestCasePriority | None = None,
        category: str | None = None,
        environment: str | None = None,
        automated_only: bool = False,
        tags: list[str] | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestCase]:
        """List test cases with optional filtering.

        Args:
            session: Database session
            status: Filter by status
            priority: Filter by priority
            category: Filter by category
            environment: Filter by environment
            automated_only: Whether to return only automated test cases
            tags: Filter by tags
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances
        """
        if automated_only:
            return self.repository.get_automated_cases(session, skip, limit)
        elif status:
            return self.repository.get_by_status(session, status, skip, limit)
        elif priority:
            return self.repository.get_by_priority(session, priority, skip, limit)
        elif category:
            return self.repository.get_by_category(session, category, skip, limit)
        elif environment:
            return self.repository.get_by_environment(session, environment, skip, limit)
        elif tags:
            return self.repository.get_by_tags(session, tags, skip, limit)
        else:
            return self.repository.get_all(session, skip, limit)

    def search_test_cases(
        self, session: Session, name: str, skip: int = 0, limit: int = 100
    ) -> list[TestCase]:
        """Search test cases by name.

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestCase instances
        """
        return self.repository.search_by_name(session, name, skip, limit)

    def update_test_case(
        self, session: Session, test_case_id: int, **kwargs: Any
    ) -> TestCase | None:
        """Update test case.

        Args:
            session: Database session
            test_case_id: Test case ID
            **kwargs: Fields to update

        Returns:
            Updated TestCase instance or None if not found
        """
        test_case = self.repository.get_by_id(session, test_case_id)
        if not test_case:
            return None

        updated_test_case = self.repository.update(session, test_case, **kwargs)
        session.commit()
        return updated_test_case

    def delete_test_case(self, session: Session, test_case_id: int) -> bool:
        """Delete test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, test_case_id)
        if result:
            session.commit()
        return result

    def add_script_to_test_case(
        self,
        session: Session,
        test_case_id: int,
        script_id: int,
        execution_order: int = 0,
        is_enabled: bool = True,
        script_parameters: dict | None = None,
        description: str | None = None,
    ) -> TestCaseScript:
        """Add script to test case.

        Args:
            session: Database session
            test_case_id: Test case ID
            script_id: Script ID
            execution_order: Execution order
            is_enabled: Whether script is enabled
            script_parameters: Script parameter overrides
            description: Description

        Returns:
            Created TestCaseScript instance
        """
        test_case_script = self.script_repository.create(
            session,
            test_case_id=test_case_id,
            script_id=script_id,
            execution_order=execution_order,
            is_enabled=is_enabled,
            script_parameters=script_parameters,
            description=description,
        )

        session.commit()
        return test_case_script

    def add_component_to_test_case(
        self,
        session: Session,
        test_case_id: int,
        component_id: int,
        execution_order: int = 0,
        is_enabled: bool = True,
        component_parameters: dict | None = None,
        description: str | None = None,
    ) -> TestCaseComponent:
        """Add component to test case.

        Args:
            session: Database session
            test_case_id: Test case ID
            component_id: Component ID
            execution_order: Execution order
            is_enabled: Whether component is enabled
            component_parameters: Component parameter overrides
            description: Description

        Returns:
            Created TestCaseComponent instance
        """
        test_case_component = self.component_repository.create(
            session,
            test_case_id=test_case_id,
            component_id=component_id,
            execution_order=execution_order,
            is_enabled=is_enabled,
            component_parameters=component_parameters,
            description=description,
        )

        session.commit()
        return test_case_component

    def get_test_case_scripts(
        self, session: Session, test_case_id: int
    ) -> list[TestCaseScript]:
        """Get scripts associated with test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            List of TestCaseScript instances ordered by execution_order
        """
        return self.script_repository.get_by_test_case(session, test_case_id)

    def get_test_case_components(
        self, session: Session, test_case_id: int
    ) -> list[TestCaseComponent]:
        """Get components associated with test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            List of TestCaseComponent instances ordered by execution_order
        """
        return self.component_repository.get_by_test_case(session, test_case_id)

    def update_test_case_script(
        self, session: Session, test_case_script_id: int, **kwargs: Any
    ) -> TestCaseScript | None:
        """Update test case-script association.

        Args:
            session: Database session
            test_case_script_id: TestCaseScript ID
            **kwargs: Fields to update

        Returns:
            Updated TestCaseScript instance or None if not found
        """
        test_case_script = self.script_repository.get_by_id(
            session, test_case_script_id
        )
        if not test_case_script:
            return None

        updated = self.script_repository.update(session, test_case_script, **kwargs)
        session.commit()
        return updated

    def update_test_case_component(
        self, session: Session, test_case_component_id: int, **kwargs: Any
    ) -> TestCaseComponent | None:
        """Update test case-component association.

        Args:
            session: Database session
            test_case_component_id: TestCaseComponent ID
            **kwargs: Fields to update

        Returns:
            Updated TestCaseComponent instance or None if not found
        """
        test_case_component = self.component_repository.get_by_id(
            session, test_case_component_id
        )
        if not test_case_component:
            return None

        updated = self.component_repository.update(
            session, test_case_component, **kwargs
        )
        session.commit()
        return updated

    def remove_script_from_test_case(
        self, session: Session, test_case_script_id: int
    ) -> bool:
        """Remove script from test case.

        Args:
            session: Database session
            test_case_script_id: TestCaseScript ID

        Returns:
            True if removed, False if not found
        """
        result = self.script_repository.delete_by_id(session, test_case_script_id)
        if result:
            session.commit()
        return result

    def remove_component_from_test_case(
        self, session: Session, test_case_component_id: int
    ) -> bool:
        """Remove component from test case.

        Args:
            session: Database session
            test_case_component_id: TestCaseComponent ID

        Returns:
            True if removed, False if not found
        """
        result = self.component_repository.delete_by_id(session, test_case_component_id)
        if result:
            session.commit()
        return result

    def activate_test_case(
        self, session: Session, test_case_id: int
    ) -> TestCase | None:
        """Activate test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            Updated TestCase instance or None if not found
        """
        return self.update_test_case(
            session, test_case_id, status=TestCaseStatus.ACTIVE
        )

    def archive_test_case(self, session: Session, test_case_id: int) -> TestCase | None:
        """Archive test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            Updated TestCase instance or None if not found
        """
        return self.update_test_case(
            session, test_case_id, status=TestCaseStatus.ARCHIVED
        )

    def deprecate_test_case(
        self, session: Session, test_case_id: int
    ) -> TestCase | None:
        """Deprecate test case.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            Updated TestCase instance or None if not found
        """
        return self.update_test_case(
            session, test_case_id, status=TestCaseStatus.DEPRECATED
        )

    def get_test_case_execution_plan(
        self, session: Session, test_case_id: int
    ) -> dict[str, Any] | None:
        """Get complete test case execution plan.

        This method returns all information needed to execute a test case,
        including all scripts and components in execution order.

        Args:
            session: Database session
            test_case_id: Test case ID

        Returns:
            Dictionary with complete execution plan or None if not found
        """
        test_case = self.repository.get_with_relations(session, test_case_id)
        if not test_case:
            return None

        # Build execution plan
        execution_items = []

        # Add scripts
        for tcs in test_case.test_case_scripts:
            if tcs.is_enabled:
                execution_items.append(
                    {
                        "type": "script",
                        "order": tcs.execution_order,
                        "id": tcs.script_id,
                        "name": tcs.script.name,
                        "parameters": tcs.script_parameters,
                        "description": tcs.description,
                    }
                )

        # Add components
        for tcc in test_case.test_case_components:
            if tcc.is_enabled:
                execution_items.append(
                    {
                        "type": "component",
                        "order": tcc.execution_order,
                        "id": tcc.component_id,
                        "name": tcc.component.name,
                        "parameters": tcc.component_parameters,
                        "description": tcc.description,
                    }
                )

        # Sort by execution order
        execution_items.sort(key=lambda x: x["order"])

        return {
            "test_case": {
                "id": test_case.id,
                "uuid": test_case.uuid,
                "name": test_case.name,
                "description": test_case.description,
                "priority": test_case.priority,
                "status": test_case.status,
                "category": test_case.category,
                "execution_order": test_case.execution_order,
                "timeout": test_case.timeout,
                "retry_count": test_case.retry_count,
                "continue_on_failure": test_case.continue_on_failure,
                "test_data": test_case.test_data,
                "environment": test_case.environment,
            },
            "execution_items": execution_items,
        }

    def clone_test_case(
        self, session: Session, test_case_id: int, new_name: str
    ) -> TestCase | None:
        """Clone a test case.

        Args:
            session: Database session
            test_case_id: Test case ID to clone
            new_name: Name for the cloned test case

        Returns:
            Cloned TestCase instance or None if source not found
        """
        source = self.repository.get_with_relations(session, test_case_id)
        if not source:
            return None

        # Create new test case
        cloned = self.repository.create(
            session,
            name=new_name,
            description=f"Cloned from: {source.name}",
            priority=source.priority,
            status=TestCaseStatus.DRAFT,
            category=source.category,
            tags=source.tags,
            preconditions=source.preconditions,
            postconditions=source.postconditions,
            execution_order=source.execution_order,
            timeout=source.timeout,
            retry_count=source.retry_count,
            continue_on_failure=source.continue_on_failure,
            test_data=source.test_data,
            environment=source.environment,
            is_automated=source.is_automated,
            created_by=source.created_by,
        )

        # Clone scripts
        for tcs in source.test_case_scripts:
            self.script_repository.create(
                session,
                test_case_id=cloned.id,
                script_id=tcs.script_id,
                execution_order=tcs.execution_order,
                is_enabled=tcs.is_enabled,
                script_parameters=tcs.script_parameters,
                description=tcs.description,
            )

        # Clone components
        for tcc in source.test_case_components:
            self.component_repository.create(
                session,
                test_case_id=cloned.id,
                component_id=tcc.component_id,
                execution_order=tcc.execution_order,
                is_enabled=tcc.is_enabled,
                component_parameters=tcc.component_parameters,
                description=tcc.description,
            )

        session.commit()
        return cloned
