"""Test Case management API endpoints.

This module provides REST API endpoints for managing test cases (Layer 4).
"""

from typing import Annotated, Any

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.models.test_case import TestCasePriority, TestCaseStatus
from morado.schemas.test_case import (
    TestCaseComponentCreate,
    TestCaseComponentResponse,
    TestCaseCreate,
    TestCaseListResponse,
    TestCaseResponse,
    TestCaseScriptCreate,
    TestCaseScriptResponse,
    TestCaseUpdate,
)
from morado.services.test_case import TestCaseService
from sqlalchemy.orm import Session


def provide_test_case_service() -> TestCaseService:
    """Provide TestCaseService instance."""
    return TestCaseService()


class TestCaseController(Controller):
    """Controller for Test Case management endpoints."""

    path = "/test-cases"
    tags = ["Test Cases"]
    dependencies = {"test_case_service": Provide(provide_test_case_service)}

    @post("/")
    async def create_test_case(
        self,
        data: TestCaseCreate,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseResponse:
        """Create a new test case.

        Args:
            data: Test case creation data
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Created test case

        Example:
            ```json
            {
                "name": "User Registration Flow",
                "priority": "high",
                "status": "active",
                "category": "User Management"
            }
            ```
        """
        test_case = test_case_service.create_test_case(
            db_session,
            **data.model_dump()
        )
        return TestCaseResponse.model_validate(test_case)

    @get("/")
    async def list_test_cases(
        self,
        test_case_service: TestCaseService,
        db_session: Session,
        status: Annotated[TestCaseStatus | None, Parameter(query="status")] = None,
        priority: Annotated[TestCasePriority | None, Parameter(query="priority")] = None,
        category: Annotated[str | None, Parameter(query="category")] = None,
        environment: Annotated[str | None, Parameter(query="environment")] = None,
        automated_only: Annotated[bool, Parameter(query="automated_only")] = False,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestCaseListResponse:
        """List test cases with optional filtering.

        Args:
            test_case_service: Test case service instance
            db_session: Database session
            status: Filter by status
            priority: Filter by priority
            category: Filter by category
            environment: Filter by environment
            automated_only: Whether to return only automated test cases
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of test cases with pagination info
        """
        test_cases = test_case_service.list_test_cases(
            db_session,
            status=status,
            priority=priority,
            category=category,
            environment=environment,
            automated_only=automated_only,
            skip=skip,
            limit=limit
        )

        return TestCaseListResponse(
            items=[TestCaseResponse.model_validate(tc) for tc in test_cases],
            total=len(test_cases),
            skip=skip,
            limit=limit
        )

    @get("/search")
    async def search_test_cases(
        self,
        test_case_service: TestCaseService,
        db_session: Session,
        name: Annotated[str, Parameter(query="name", min_length=1)],
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestCaseListResponse:
        """Search test cases by name.

        Args:
            test_case_service: Test case service instance
            db_session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching test cases
        """
        test_cases = test_case_service.search_test_cases(
            db_session,
            name=name,
            skip=skip,
            limit=limit
        )

        return TestCaseListResponse(
            items=[TestCaseResponse.model_validate(tc) for tc in test_cases],
            total=len(test_cases),
            skip=skip,
            limit=limit
        )

    @get("/{test_case_id:int}")
    async def get_test_case(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
        load_scripts: Annotated[bool, Parameter(query="load_scripts")] = False,
        load_components: Annotated[bool, Parameter(query="load_components")] = False,
        load_all: Annotated[bool, Parameter(query="load_all")] = False,
    ) -> TestCaseResponse:
        """Get test case by ID.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session
            load_scripts: Whether to load associated scripts
            load_components: Whether to load associated components
            load_all: Whether to load all relations

        Returns:
            Test case details

        Raises:
            NotFoundException: If test case not found
        """
        test_case = test_case_service.get_test_case(
            db_session,
            test_case_id,
            load_scripts=load_scripts,
            load_components=load_components,
            load_all=load_all
        )
        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return TestCaseResponse.model_validate(test_case)

    @get("/{test_case_id:int}/execution-plan")
    async def get_test_case_execution_plan(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get complete test case execution plan.

        This endpoint returns all information needed to execute a test case,
        including all scripts and components in execution order.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Complete execution plan

        Raises:
            NotFoundException: If test case not found
        """
        plan = test_case_service.get_test_case_execution_plan(db_session, test_case_id)
        if not plan:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return plan

    @get("/uuid/{uuid:str}")
    async def get_test_case_by_uuid(
        self,
        uuid: str,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseResponse:
        """Get test case by UUID.

        Args:
            uuid: Test case UUID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Test case details

        Raises:
            NotFoundException: If test case not found
        """
        test_case = test_case_service.get_test_case_by_uuid(db_session, uuid)
        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with UUID {uuid} not found")

        return TestCaseResponse.model_validate(test_case)

    @patch("/{test_case_id:int}")
    async def update_test_case(
        self,
        test_case_id: int,
        data: TestCaseUpdate,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseResponse:
        """Update test case.

        Args:
            test_case_id: Test case ID
            data: Test case update data
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Updated test case

        Raises:
            NotFoundException: If test case not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        test_case = test_case_service.update_test_case(
            db_session,
            test_case_id,
            **update_data
        )

        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return TestCaseResponse.model_validate(test_case)

    @delete("/{test_case_id:int}", status_code=200)
    async def delete_test_case(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete test case.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If test case not found
        """
        success = test_case_service.delete_test_case(db_session, test_case_id)

        if not success:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return {"message": "Test case deleted successfully"}

    @post("/{test_case_id:int}/activate")
    async def activate_test_case(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseResponse:
        """Activate test case.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Updated test case

        Raises:
            NotFoundException: If test case not found
        """
        test_case = test_case_service.activate_test_case(db_session, test_case_id)

        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return TestCaseResponse.model_validate(test_case)

    @post("/{test_case_id:int}/archive")
    async def archive_test_case(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseResponse:
        """Archive test case.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Updated test case

        Raises:
            NotFoundException: If test case not found
        """
        test_case = test_case_service.archive_test_case(db_session, test_case_id)

        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return TestCaseResponse.model_validate(test_case)

    @post("/{test_case_id:int}/deprecate")
    async def deprecate_test_case(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseResponse:
        """Deprecate test case.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Updated test case

        Raises:
            NotFoundException: If test case not found
        """
        test_case = test_case_service.deprecate_test_case(db_session, test_case_id)

        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return TestCaseResponse.model_validate(test_case)

    @post("/{test_case_id:int}/clone")
    async def clone_test_case(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
        new_name: Annotated[str, Parameter(query="new_name", min_length=1)],
    ) -> TestCaseResponse:
        """Clone a test case.

        Args:
            test_case_id: Test case ID to clone
            test_case_service: Test case service instance
            db_session: Database session
            new_name: Name for the cloned test case

        Returns:
            Cloned test case

        Raises:
            NotFoundException: If test case not found
        """
        cloned = test_case_service.clone_test_case(
            db_session,
            test_case_id,
            new_name
        )

        if not cloned:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        return TestCaseResponse.model_validate(cloned)

    # Script management endpoints

    @post("/{test_case_id:int}/scripts")
    async def add_script_to_test_case(
        self,
        test_case_id: int,
        data: TestCaseScriptCreate,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseScriptResponse:
        """Add script to test case.

        Args:
            test_case_id: Test case ID
            data: Test case-script association data
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Created test case-script association

        Raises:
            NotFoundException: If test case not found
        """
        # Verify test case exists
        test_case = test_case_service.get_test_case(db_session, test_case_id)
        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        test_case_script = test_case_service.add_script_to_test_case(
            db_session,
            test_case_id=test_case_id,
            **data.model_dump(exclude={"test_case_id"})
        )

        return TestCaseScriptResponse.model_validate(test_case_script)

    @post("/{test_case_id:int}/components")
    async def add_component_to_test_case(
        self,
        test_case_id: int,
        data: TestCaseComponentCreate,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> TestCaseComponentResponse:
        """Add component to test case.

        Args:
            test_case_id: Test case ID
            data: Test case-component association data
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            Created test case-component association

        Raises:
            NotFoundException: If test case not found
        """
        # Verify test case exists
        test_case = test_case_service.get_test_case(db_session, test_case_id)
        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        test_case_component = test_case_service.add_component_to_test_case(
            db_session,
            test_case_id=test_case_id,
            **data.model_dump(exclude={"test_case_id"})
        )

        return TestCaseComponentResponse.model_validate(test_case_component)

    @get("/{test_case_id:int}/scripts")
    async def get_test_case_scripts(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> list[TestCaseScriptResponse]:
        """Get scripts associated with test case.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            List of test case-script associations

        Raises:
            NotFoundException: If test case not found
        """
        # Verify test case exists
        test_case = test_case_service.get_test_case(db_session, test_case_id)
        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        test_case_scripts = test_case_service.get_test_case_scripts(
            db_session,
            test_case_id
        )

        return [TestCaseScriptResponse.model_validate(tcs) for tcs in test_case_scripts]

    @get("/{test_case_id:int}/components")
    async def get_test_case_components(
        self,
        test_case_id: int,
        test_case_service: TestCaseService,
        db_session: Session,
    ) -> list[TestCaseComponentResponse]:
        """Get components associated with test case.

        Args:
            test_case_id: Test case ID
            test_case_service: Test case service instance
            db_session: Database session

        Returns:
            List of test case-component associations

        Raises:
            NotFoundException: If test case not found
        """
        # Verify test case exists
        test_case = test_case_service.get_test_case(db_session, test_case_id)
        if not test_case:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test case with ID {test_case_id} not found")

        test_case_components = test_case_service.get_test_case_components(
            db_session,
            test_case_id
        )

        return [TestCaseComponentResponse.model_validate(tcc) for tcc in test_case_components]
