"""Service layer for Test Execution management.

This module provides business logic for managing test execution and results.
"""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from morado.models.test_execution import ExecutionResult, ExecutionStatus, TestExecution
from morado.repositories.test_execution import TestExecutionRepository


class TestExecutionService:
    """Service for managing test execution.

    Provides business logic for creating, updating, and tracking test execution.

    Example:
        >>> service = TestExecutionService()
        >>> execution = service.create_execution(
        ...     session,
        ...     test_case_id=1,
        ...     environment="test"
        ... )
    """

    def __init__(self):
        """Initialize TestExecution service."""
        self.repository = TestExecutionRepository()

    def create_execution(
        self,
        session: Session,
        test_case_id: int | None = None,
        test_suite_id: int | None = None,
        environment: str = "test",
        executor: str | None = None,
        execution_parameters: dict | None = None,
        created_by: int | None = None,
        **kwargs: Any
    ) -> TestExecution:
        """Create a new test execution.

        Args:
            session: Database session
            test_case_id: Test case ID (for single case execution)
            test_suite_id: Test suite ID (for suite execution)
            environment: Execution environment
            executor: Executor name (e.g., "jenkins", "manual")
            execution_parameters: Execution parameters
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created TestExecution instance

        Raises:
            ValueError: If neither test_case_id nor test_suite_id is provided
        """
        if not test_case_id and not test_suite_id:
            raise ValueError("Either test_case_id or test_suite_id must be provided")

        execution = self.repository.create(
            session,
            test_case_id=test_case_id,
            test_suite_id=test_suite_id,
            status=ExecutionStatus.PENDING,
            environment=environment,
            executor=executor,
            execution_parameters=execution_parameters,
            created_by=created_by,
            **kwargs
        )

        session.commit()
        return execution

    def get_execution(
        self,
        session: Session,
        execution_id: int,
        with_results: bool = False
    ) -> TestExecution | None:
        """Get execution by ID.

        Args:
            session: Database session
            execution_id: Execution ID
            with_results: Whether to load execution results

        Returns:
            TestExecution instance or None if not found
        """
        if with_results:
            return self.repository.get_with_results(session, execution_id)
        else:
            return self.repository.get_by_id(session, execution_id)

    def get_execution_by_uuid(
        self,
        session: Session,
        uuid: str
    ) -> TestExecution | None:
        """Get execution by UUID.

        Args:
            session: Database session
            uuid: Execution UUID

        Returns:
            TestExecution instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_executions(
        self,
        session: Session,
        test_case_id: int | None = None,
        test_suite_id: int | None = None,
        status: ExecutionStatus | None = None,
        environment: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[TestExecution]:
        """List executions with optional filtering.

        Args:
            session: Database session
            test_case_id: Filter by test case ID
            test_suite_id: Filter by test suite ID
            status: Filter by status
            environment: Filter by environment
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestExecution instances
        """
        if test_case_id:
            return self.repository.get_by_test_case(
                session, test_case_id, skip, limit
            )
        elif test_suite_id:
            return self.repository.get_by_test_suite(
                session, test_suite_id, skip, limit
            )
        elif status:
            return self.repository.get_by_status(session, status, skip, limit)
        else:
            filters = {}
            if environment:
                filters['environment'] = environment
            return self.repository.get_all(session, skip, limit, filters)

    def start_execution(
        self,
        session: Session,
        execution_id: int
    ) -> TestExecution | None:
        """Start execution.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Updated TestExecution instance or None if not found
        """
        execution = self.repository.get_by_id(session, execution_id)
        if not execution:
            return None

        updated = self.repository.update(
            session,
            execution,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )

        session.commit()
        return updated

    def complete_execution(
        self,
        session: Session,
        execution_id: int,
        status: ExecutionStatus,
        error_message: str | None = None,
        stack_trace: str | None = None
    ) -> TestExecution | None:
        """Complete execution.

        Args:
            session: Database session
            execution_id: Execution ID
            status: Final status (passed/failed/error)
            error_message: Error message if failed
            stack_trace: Stack trace if error

        Returns:
            Updated TestExecution instance or None if not found
        """
        execution = self.repository.get_by_id(session, execution_id)
        if not execution:
            return None

        end_time = datetime.now()
        duration = None

        if execution.start_time:
            duration = (end_time - execution.start_time).total_seconds()

        updated = self.repository.update(
            session,
            execution,
            status=status,
            end_time=end_time,
            duration=duration,
            error_message=error_message,
            stack_trace=stack_trace
        )

        session.commit()
        return updated

    def cancel_execution(
        self,
        session: Session,
        execution_id: int
    ) -> TestExecution | None:
        """Cancel execution.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Updated TestExecution instance or None if not found
        """
        return self.complete_execution(
            session,
            execution_id,
            ExecutionStatus.CANCELLED
        )

    def update_execution_stats(
        self,
        session: Session,
        execution_id: int,
        total_count: int | None = None,
        passed_count: int | None = None,
        failed_count: int | None = None,
        error_count: int | None = None,
        skipped_count: int | None = None
    ) -> TestExecution | None:
        """Update execution statistics.

        Args:
            session: Database session
            execution_id: Execution ID
            total_count: Total count
            passed_count: Passed count
            failed_count: Failed count
            error_count: Error count
            skipped_count: Skipped count

        Returns:
            Updated TestExecution instance or None if not found
        """
        execution = self.repository.get_by_id(session, execution_id)
        if not execution:
            return None

        updates = {}
        if total_count is not None:
            updates['total_count'] = total_count
        if passed_count is not None:
            updates['passed_count'] = passed_count
        if failed_count is not None:
            updates['failed_count'] = failed_count
        if error_count is not None:
            updates['error_count'] = error_count
        if skipped_count is not None:
            updates['skipped_count'] = skipped_count

        updated = self.repository.update(session, execution, **updates)
        session.commit()
        return updated

    def add_execution_result(  # noqa: PLR0913
        self,
        session: Session,
        execution_id: int,
        script_id: int | None = None,
        component_id: int | None = None,
        status: ExecutionStatus = ExecutionStatus.PENDING,
        request_data: dict | None = None,
        response_data: dict | None = None,
        assertions: list | None = None,
        error_message: str | None = None,
        stack_trace: str | None = None,
        logs: str | None = None,
        screenshots: list | None = None
    ) -> ExecutionResult:
        """Add execution result.

        Args:
            session: Database session
            execution_id: Execution ID
            script_id: Script ID
            component_id: Component ID
            status: Execution status
            request_data: Request data
            response_data: Response data
            assertions: Assertion results
            error_message: Error message
            stack_trace: Stack trace
            logs: Logs
            screenshots: Screenshots

        Returns:
            Created ExecutionResult instance
        """
        result = ExecutionResult(
            execution_id=execution_id,
            script_id=script_id,
            component_id=component_id,
            status=status,
            request_data=request_data,
            response_data=response_data,
            assertions=assertions,
            error_message=error_message,
            stack_trace=stack_trace,
            logs=logs,
            screenshots=screenshots
        )

        session.add(result)
        session.commit()
        session.refresh(result)

        return result

    def update_execution_result(
        self,
        session: Session,
        result_id: int,
        **kwargs: Any
    ) -> ExecutionResult | None:
        """Update execution result.

        Args:
            session: Database session
            result_id: ExecutionResult ID
            **kwargs: Fields to update

        Returns:
            Updated ExecutionResult instance or None if not found
        """
        result = session.get(ExecutionResult, result_id)
        if not result:
            return None

        for key, value in kwargs.items():
            if hasattr(result, key):
                setattr(result, key, value)

        session.commit()
        session.refresh(result)
        return result

    def get_execution_results(
        self,
        session: Session,
        execution_id: int
    ) -> list[ExecutionResult]:
        """Get execution results.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            List of ExecutionResult instances
        """
        execution = self.repository.get_with_results(session, execution_id)
        if not execution:
            return []

        return execution.execution_results

    def get_execution_summary(
        self,
        session: Session,
        execution_id: int
    ) -> dict[str, Any] | None:
        """Get execution summary.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Dictionary with execution summary or None if not found
        """
        execution = self.repository.get_with_results(session, execution_id)
        if not execution:
            return None

        return {
            'execution': {
                'id': execution.id,
                'uuid': execution.uuid,
                'status': execution.status,
                'start_time': execution.start_time.isoformat() if execution.start_time else None,
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'duration': execution.duration,
                'environment': execution.environment,
                'executor': execution.executor
            },
            'statistics': {
                'total': execution.total_count,
                'passed': execution.passed_count,
                'failed': execution.failed_count,
                'error': execution.error_count,
                'skipped': execution.skipped_count
            },
            'results': [
                {
                    'id': result.id,
                    'script_id': result.script_id,
                    'component_id': result.component_id,
                    'status': result.status,
                    'duration': result.duration,
                    'error_message': result.error_message
                }
                for result in execution.execution_results
            ]
        }

    def get_recent_executions(
        self,
        session: Session,
        test_case_id: int | None = None,
        test_suite_id: int | None = None,
        limit: int = 10
    ) -> list[TestExecution]:
        """Get recent executions.

        Args:
            session: Database session
            test_case_id: Filter by test case ID
            test_suite_id: Filter by test suite ID
            limit: Maximum number of records to return

        Returns:
            List of recent TestExecution instances
        """
        if test_case_id:
            return self.repository.get_by_test_case(session, test_case_id, 0, limit)
        elif test_suite_id:
            return self.repository.get_by_test_suite(session, test_suite_id, 0, limit)
        else:
            return self.repository.get_all(session, 0, limit)
