"""Test Execution management API endpoints.

This module provides REST API endpoints for managing test execution and results.
"""

from typing import Annotated, Any

from litestar import Controller, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.models.test_execution import ExecutionStatus
from morado.schemas.test_execution import (
    ExecutionResultCreate,
    ExecutionResultResponse,
    TestExecutionCreate,
    TestExecutionListResponse,
    TestExecutionResponse,
    TestExecutionUpdate,
)
from morado.services.test_execution import TestExecutionService
from sqlalchemy.orm import Session


def provide_test_execution_service() -> TestExecutionService:
    """Provide TestExecutionService instance."""
    return TestExecutionService()


class TestExecutionController(Controller):
    """Controller for Test Execution management endpoints."""

    path = "/test-executions"
    tags = ["Test Executions"]
    dependencies = {"test_execution_service": Provide(provide_test_execution_service)}

    @post("/")
    async def create_execution(
        self,
        data: TestExecutionCreate,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> TestExecutionResponse:
        """Create a new test execution.

        Args:
            data: Test execution creation data
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Created test execution

        Raises:
            ValueError: If neither test_case_id nor test_suite_id is provided

        Example:
            ```json
            {
                "test_case_id": 1,
                "environment": "test",
                "executor": "jenkins"
            }
            ```
        """
        try:
            execution = test_execution_service.create_execution(
                db_session,
                **data.model_dump()
            )
            return TestExecutionResponse.model_validate(execution)
        except ValueError as e:
            from litestar.exceptions import ValidationException
            raise ValidationException(detail=str(e))

    @get("/")
    async def list_executions(
        self,
        test_execution_service: TestExecutionService,
        db_session: Session,
        test_case_id: Annotated[int | None, Parameter(query="test_case_id")] = None,
        test_suite_id: Annotated[int | None, Parameter(query="test_suite_id")] = None,
        status: Annotated[ExecutionStatus | None, Parameter(query="status")] = None,
        environment: Annotated[str | None, Parameter(query="environment")] = None,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestExecutionListResponse:
        """List executions with optional filtering.

        Args:
            test_execution_service: Test execution service instance
            db_session: Database session
            test_case_id: Filter by test case ID
            test_suite_id: Filter by test suite ID
            status: Filter by status
            environment: Filter by environment
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of executions with pagination info
        """
        executions = test_execution_service.list_executions(
            db_session,
            test_case_id=test_case_id,
            test_suite_id=test_suite_id,
            status=status,
            environment=environment,
            skip=skip,
            limit=limit
        )

        return TestExecutionListResponse(
            items=[TestExecutionResponse.model_validate(e) for e in executions],
            total=len(executions),
            skip=skip,
            limit=limit
        )

    @get("/{execution_id:int}")
    async def get_execution(
        self,
        execution_id: int,
        test_execution_service: TestExecutionService,
        db_session: Session,
        with_results: Annotated[bool, Parameter(query="with_results")] = False,
    ) -> TestExecutionResponse:
        """Get execution by ID.

        Args:
            execution_id: Execution ID
            test_execution_service: Test execution service instance
            db_session: Database session
            with_results: Whether to load execution results

        Returns:
            Execution details

        Raises:
            NotFoundException: If execution not found
        """
        execution = test_execution_service.get_execution(
            db_session,
            execution_id,
            with_results=with_results
        )
        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        return TestExecutionResponse.model_validate(execution)

    @get("/{execution_id:int}/summary")
    async def get_execution_summary(
        self,
        execution_id: int,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get execution summary.

        This endpoint returns a summary of the execution including statistics
        and all execution results.

        Args:
            execution_id: Execution ID
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Execution summary

        Raises:
            NotFoundException: If execution not found
        """
        summary = test_execution_service.get_execution_summary(db_session, execution_id)
        if not summary:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        return summary

    @get("/uuid/{uuid:str}")
    async def get_execution_by_uuid(
        self,
        uuid: str,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> TestExecutionResponse:
        """Get execution by UUID.

        Args:
            uuid: Execution UUID
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Execution details

        Raises:
            NotFoundException: If execution not found
        """
        execution = test_execution_service.get_execution_by_uuid(db_session, uuid)
        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with UUID {uuid} not found")

        return TestExecutionResponse.model_validate(execution)

    @patch("/{execution_id:int}")
    async def update_execution(
        self,
        execution_id: int,
        data: TestExecutionUpdate,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> TestExecutionResponse:
        """Update execution.

        Args:
            execution_id: Execution ID
            data: Execution update data
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Updated execution

        Raises:
            NotFoundException: If execution not found
        """
        # Get existing execution
        execution = test_execution_service.get_execution(db_session, execution_id)
        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        # Update using repository directly
        from morado.repositories.test_execution import TestExecutionRepository
        repo = TestExecutionRepository()
        updated = repo.update(db_session, execution, **update_data)
        db_session.commit()

        return TestExecutionResponse.model_validate(updated)

    @post("/{execution_id:int}/start")
    async def start_execution(
        self,
        execution_id: int,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> TestExecutionResponse:
        """Start execution.

        Args:
            execution_id: Execution ID
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Updated execution

        Raises:
            NotFoundException: If execution not found
        """
        execution = test_execution_service.start_execution(db_session, execution_id)

        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        return TestExecutionResponse.model_validate(execution)

    @post("/{execution_id:int}/complete")
    async def complete_execution(
        self,
        execution_id: int,
        test_execution_service: TestExecutionService,
        db_session: Session,
        status: Annotated[ExecutionStatus, Parameter(query="status")],
        error_message: Annotated[str | None, Parameter(query="error_message")] = None,
    ) -> TestExecutionResponse:
        """Complete execution.

        Args:
            execution_id: Execution ID
            test_execution_service: Test execution service instance
            db_session: Database session
            status: Final status (passed/failed/error)
            error_message: Error message if failed

        Returns:
            Updated execution

        Raises:
            NotFoundException: If execution not found
        """
        execution = test_execution_service.complete_execution(
            db_session,
            execution_id,
            status,
            error_message=error_message
        )

        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        return TestExecutionResponse.model_validate(execution)

    @post("/{execution_id:int}/cancel")
    async def cancel_execution(
        self,
        execution_id: int,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> TestExecutionResponse:
        """Cancel execution.

        Args:
            execution_id: Execution ID
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Updated execution

        Raises:
            NotFoundException: If execution not found
        """
        execution = test_execution_service.cancel_execution(db_session, execution_id)

        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        return TestExecutionResponse.model_validate(execution)

    # Execution result endpoints

    @post("/{execution_id:int}/results")
    async def add_execution_result(
        self,
        execution_id: int,
        data: ExecutionResultCreate,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> ExecutionResultResponse:
        """Add execution result.

        Args:
            execution_id: Execution ID
            data: Execution result data
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            Created execution result

        Raises:
            NotFoundException: If execution not found
        """
        # Verify execution exists
        execution = test_execution_service.get_execution(db_session, execution_id)
        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        result = test_execution_service.add_execution_result(
            db_session,
            execution_id=execution_id,
            **data.model_dump(exclude={"execution_id"})
        )

        return ExecutionResultResponse.model_validate(result)

    @get("/{execution_id:int}/results")
    async def get_execution_results(
        self,
        execution_id: int,
        test_execution_service: TestExecutionService,
        db_session: Session,
    ) -> list[ExecutionResultResponse]:
        """Get execution results.

        Args:
            execution_id: Execution ID
            test_execution_service: Test execution service instance
            db_session: Database session

        Returns:
            List of execution results

        Raises:
            NotFoundException: If execution not found
        """
        # Verify execution exists
        execution = test_execution_service.get_execution(db_session, execution_id)
        if not execution:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Execution with ID {execution_id} not found")

        results = test_execution_service.get_execution_results(
            db_session,
            execution_id
        )

        return [ExecutionResultResponse.model_validate(r) for r in results]

    @get("/recent")
    async def get_recent_executions(
        self,
        test_execution_service: TestExecutionService,
        db_session: Session,
        test_case_id: Annotated[int | None, Parameter(query="test_case_id")] = None,
        test_suite_id: Annotated[int | None, Parameter(query="test_suite_id")] = None,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 10,
    ) -> TestExecutionListResponse:
        """Get recent executions.

        Args:
            test_execution_service: Test execution service instance
            db_session: Database session
            test_case_id: Filter by test case ID
            test_suite_id: Filter by test suite ID
            limit: Maximum number of records to return

        Returns:
            List of recent executions
        """
        executions = test_execution_service.get_recent_executions(
            db_session,
            test_case_id=test_case_id,
            test_suite_id=test_suite_id,
            limit=limit
        )

        return TestExecutionListResponse(
            items=[TestExecutionResponse.model_validate(e) for e in executions],
            total=len(executions),
            skip=0,
            limit=limit
        )
