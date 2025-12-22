"""Test Suite management API endpoints.

This module provides REST API endpoints for managing test suites.
"""

from typing import Annotated, Any

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.schemas.test_suite import (
    TestSuiteCaseCreate,
    TestSuiteCaseResponse,
    TestSuiteCreate,
    TestSuiteListResponse,
    TestSuiteResponse,
    TestSuiteUpdate,
)
from morado.services.test_suite import TestSuiteService
from sqlalchemy.orm import Session


def provide_test_suite_service() -> TestSuiteService:
    """Provide TestSuiteService instance."""
    return TestSuiteService()


class TestSuiteController(Controller):
    """Controller for Test Suite management endpoints."""

    path = "/test-suites"
    tags = ["Test Suites"]
    dependencies = {"test_suite_service": Provide(provide_test_suite_service)}

    @post("/")
    async def create_test_suite(
        self,
        data: TestSuiteCreate,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> TestSuiteResponse:
        """Create a new test suite.

        Args:
            data: Test suite creation data
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Created test suite

        Example:
            ```json
            {
                "name": "Regression Test Suite",
                "execution_order": "sequential",
                "parallel_execution": false,
                "environment": "test"
            }
            ```
        """
        suite = test_suite_service.create_test_suite(
            db_session,
            **data.model_dump()
        )
        return TestSuiteResponse.model_validate(suite)

    @get("/")
    async def list_test_suites(
        self,
        test_suite_service: TestSuiteService,
        db_session: Session,
        environment: Annotated[str | None, Parameter(query="environment")] = None,
        scheduled_only: Annotated[bool, Parameter(query="scheduled_only")] = False,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestSuiteListResponse:
        """List test suites with optional filtering.

        Args:
            test_suite_service: Test suite service instance
            db_session: Database session
            environment: Filter by environment
            scheduled_only: Whether to return only scheduled suites
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of test suites with pagination info
        """
        suites = test_suite_service.list_test_suites(
            db_session,
            environment=environment,
            scheduled_only=scheduled_only,
            skip=skip,
            limit=limit
        )

        return TestSuiteListResponse(
            items=[TestSuiteResponse.model_validate(s) for s in suites],
            total=len(suites),
            skip=skip,
            limit=limit
        )

    @get("/{suite_id:int}")
    async def get_test_suite(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
        with_test_cases: Annotated[bool, Parameter(query="with_test_cases")] = False,
    ) -> TestSuiteResponse:
        """Get test suite by ID.

        Args:
            suite_id: Suite ID
            test_suite_service: Test suite service instance
            db_session: Database session
            with_test_cases: Whether to load associated test cases

        Returns:
            Test suite details

        Raises:
            NotFoundException: If test suite not found
        """
        suite = test_suite_service.get_test_suite(
            db_session,
            suite_id,
            with_test_cases=with_test_cases
        )
        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return TestSuiteResponse.model_validate(suite)

    @get("/{suite_id:int}/execution-plan")
    async def get_suite_execution_plan(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get complete suite execution plan.

        This endpoint returns all information needed to execute a test suite,
        including all test cases in execution order.

        Args:
            suite_id: Suite ID
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Complete execution plan

        Raises:
            NotFoundException: If test suite not found
        """
        plan = test_suite_service.get_suite_execution_plan(db_session, suite_id)
        if not plan:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return plan

    @get("/uuid/{uuid:str}")
    async def get_test_suite_by_uuid(
        self,
        uuid: str,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> TestSuiteResponse:
        """Get test suite by UUID.

        Args:
            uuid: Suite UUID
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Test suite details

        Raises:
            NotFoundException: If test suite not found
        """
        suite = test_suite_service.get_test_suite_by_uuid(db_session, uuid)
        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with UUID {uuid} not found")

        return TestSuiteResponse.model_validate(suite)

    @patch("/{suite_id:int}")
    async def update_test_suite(
        self,
        suite_id: int,
        data: TestSuiteUpdate,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> TestSuiteResponse:
        """Update test suite.

        Args:
            suite_id: Suite ID
            data: Test suite update data
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Updated test suite

        Raises:
            NotFoundException: If test suite not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        suite = test_suite_service.update_test_suite(
            db_session,
            suite_id,
            **update_data
        )

        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return TestSuiteResponse.model_validate(suite)

    @delete("/{suite_id:int}", status_code=200)
    async def delete_test_suite(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete test suite.

        Args:
            suite_id: Suite ID
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If test suite not found
        """
        success = test_suite_service.delete_test_suite(db_session, suite_id)

        if not success:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return {"message": "Test suite deleted successfully"}

    @post("/{suite_id:int}/clone")
    async def clone_test_suite(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
        new_name: Annotated[str, Parameter(query="new_name", min_length=1)],
    ) -> TestSuiteResponse:
        """Clone a test suite.

        Args:
            suite_id: Suite ID to clone
            test_suite_service: Test suite service instance
            db_session: Database session
            new_name: Name for the cloned suite

        Returns:
            Cloned test suite

        Raises:
            NotFoundException: If test suite not found
        """
        cloned = test_suite_service.clone_test_suite(
            db_session,
            suite_id,
            new_name
        )

        if not cloned:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return TestSuiteResponse.model_validate(cloned)

    @post("/{suite_id:int}/schedule/enable")
    async def enable_scheduling(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
        schedule_config: dict,
    ) -> TestSuiteResponse:
        """Enable scheduling for test suite.

        Args:
            suite_id: Suite ID
            test_suite_service: Test suite service instance
            db_session: Database session
            schedule_config: Schedule configuration (cron expression, etc.)

        Returns:
            Updated test suite

        Raises:
            NotFoundException: If test suite not found

        Example:
            ```json
            {
                "cron": "0 0 * * *",
                "timezone": "UTC"
            }
            ```
        """
        suite = test_suite_service.enable_scheduling(
            db_session,
            suite_id,
            schedule_config
        )

        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return TestSuiteResponse.model_validate(suite)

    @post("/{suite_id:int}/schedule/disable")
    async def disable_scheduling(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> TestSuiteResponse:
        """Disable scheduling for test suite.

        Args:
            suite_id: Suite ID
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Updated test suite

        Raises:
            NotFoundException: If test suite not found
        """
        suite = test_suite_service.disable_scheduling(db_session, suite_id)

        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        return TestSuiteResponse.model_validate(suite)

    # Test case management endpoints

    @post("/{suite_id:int}/test-cases")
    async def add_test_case_to_suite(
        self,
        suite_id: int,
        data: TestSuiteCaseCreate,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> TestSuiteCaseResponse:
        """Add test case to suite.

        Args:
            suite_id: Suite ID
            data: Suite-test case association data
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            Created suite-test case association

        Raises:
            NotFoundException: If test suite not found
        """
        # Verify suite exists
        suite = test_suite_service.get_test_suite(db_session, suite_id)
        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        suite_case = test_suite_service.add_test_case_to_suite(
            db_session,
            suite_id=suite_id,
            **data.model_dump(exclude={"test_suite_id"})
        )

        return TestSuiteCaseResponse.model_validate(suite_case)

    @get("/{suite_id:int}/test-cases")
    async def get_suite_test_cases(
        self,
        suite_id: int,
        test_suite_service: TestSuiteService,
        db_session: Session,
    ) -> list[TestSuiteCaseResponse]:
        """Get test cases in suite.

        Args:
            suite_id: Suite ID
            test_suite_service: Test suite service instance
            db_session: Database session

        Returns:
            List of suite-test case associations

        Raises:
            NotFoundException: If test suite not found
        """
        # Verify suite exists
        suite = test_suite_service.get_test_suite(db_session, suite_id)
        if not suite:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Test suite with ID {suite_id} not found")

        suite_cases = test_suite_service.get_suite_test_cases(
            db_session,
            suite_id
        )

        return [TestSuiteCaseResponse.model_validate(sc) for sc in suite_cases]
