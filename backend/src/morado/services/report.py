"""Service layer for Test Report generation.

This module provides business logic for generating test reports and analytics.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from morado.models.test_execution import ExecutionStatus, TestExecution
from morado.repositories.test_execution import TestExecutionRepository


class ReportService:
    """Service for generating test reports and analytics.

    Provides business logic for generating various test reports,
    statistics, and analytics.

    Example:
        >>> service = ReportService()
        >>> summary = service.get_execution_summary_report(
        ...     session,
        ...     start_date=datetime.now() - timedelta(days=7)
        ... )
    """

    def __init__(self):
        """Initialize Report service."""
        self.execution_repository = TestExecutionRepository()

    def get_execution_summary_report(
        self,
        session: Session,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        environment: str | None = None,
        test_case_id: int | None = None,
        test_suite_id: int | None = None,
    ) -> dict[str, Any]:
        """Get execution summary report.

        Args:
            session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            environment: Filter by environment
            test_case_id: Filter by test case ID
            test_suite_id: Filter by test suite ID

        Returns:
            Dictionary with execution summary statistics
        """
        # Build query
        query = session.query(TestExecution)

        if start_date:
            query = query.filter(TestExecution.start_time >= start_date)

        if end_date:
            query = query.filter(TestExecution.start_time <= end_date)

        if environment:
            query = query.filter(TestExecution.environment == environment)

        if test_case_id:
            query = query.filter(TestExecution.test_case_id == test_case_id)

        if test_suite_id:
            query = query.filter(TestExecution.test_suite_id == test_suite_id)

        # Get all executions
        executions = query.all()

        # Calculate statistics
        total_executions = len(executions)
        status_counts = {
            "passed": 0,
            "failed": 0,
            "error": 0,
            "skipped": 0,
            "cancelled": 0,
            "running": 0,
            "pending": 0,
        }

        total_duration = 0.0
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0

        for execution in executions:
            # Count by status
            status_key = (
                execution.status.value
                if hasattr(execution.status, "value")
                else str(execution.status)
            )
            if status_key in status_counts:
                status_counts[status_key] += 1

            # Sum durations
            if execution.duration:
                total_duration += execution.duration

            # Sum test counts
            total_tests += execution.total_count
            total_passed += execution.passed_count
            total_failed += execution.failed_count
            total_errors += execution.error_count
            total_skipped += execution.skipped_count

        # Calculate averages
        avg_duration = total_duration / total_executions if total_executions > 0 else 0

        # Calculate pass rate
        completed_tests = total_passed + total_failed + total_errors
        pass_rate = (total_passed / completed_tests * 100) if completed_tests > 0 else 0

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "filters": {
                "environment": environment,
                "test_case_id": test_case_id,
                "test_suite_id": test_suite_id,
            },
            "summary": {
                "total_executions": total_executions,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_errors": total_errors,
                "total_skipped": total_skipped,
                "pass_rate": round(pass_rate, 2),
                "total_duration": round(total_duration, 2),
                "avg_duration": round(avg_duration, 2),
            },
            "status_breakdown": status_counts,
        }

    def get_test_case_report(
        self, session: Session, test_case_id: int, limit: int = 10
    ) -> dict[str, Any]:
        """Get test case execution report.

        Args:
            session: Database session
            test_case_id: Test case ID
            limit: Number of recent executions to include

        Returns:
            Dictionary with test case execution history and statistics
        """
        # Get recent executions
        executions = self.execution_repository.get_by_test_case(
            session, test_case_id, 0, limit
        )

        if not executions:
            return {
                "test_case_id": test_case_id,
                "total_executions": 0,
                "recent_executions": [],
            }

        # Calculate statistics
        total_executions = len(executions)
        passed_count = sum(1 for e in executions if e.status == ExecutionStatus.PASSED)
        failed_count = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)
        error_count = sum(1 for e in executions if e.status == ExecutionStatus.ERROR)

        # Get last execution
        last_execution = executions[0] if executions else None

        # Calculate success rate
        completed = passed_count + failed_count + error_count
        success_rate = (passed_count / completed * 100) if completed > 0 else 0

        # Calculate average duration
        durations = [e.duration for e in executions if e.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "test_case_id": test_case_id,
            "total_executions": total_executions,
            "statistics": {
                "passed": passed_count,
                "failed": failed_count,
                "error": error_count,
                "success_rate": round(success_rate, 2),
                "avg_duration": round(avg_duration, 2),
            },
            "last_execution": {
                "id": last_execution.id,
                "status": last_execution.status,
                "start_time": last_execution.start_time.isoformat()
                if last_execution.start_time
                else None,
                "duration": last_execution.duration,
            }
            if last_execution
            else None,
            "recent_executions": [
                {
                    "id": e.id,
                    "uuid": e.uuid,
                    "status": e.status,
                    "start_time": e.start_time.isoformat() if e.start_time else None,
                    "duration": e.duration,
                    "environment": e.environment,
                }
                for e in executions
            ],
        }

    def get_test_suite_report(
        self, session: Session, test_suite_id: int, limit: int = 10
    ) -> dict[str, Any]:
        """Get test suite execution report.

        Args:
            session: Database session
            test_suite_id: Test suite ID
            limit: Number of recent executions to include

        Returns:
            Dictionary with test suite execution history and statistics
        """
        # Get recent executions
        executions = self.execution_repository.get_by_test_suite(
            session, test_suite_id, 0, limit
        )

        if not executions:
            return {
                "test_suite_id": test_suite_id,
                "total_executions": 0,
                "recent_executions": [],
            }

        # Calculate statistics
        total_executions = len(executions)
        passed_count = sum(1 for e in executions if e.status == ExecutionStatus.PASSED)
        failed_count = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)
        error_count = sum(1 for e in executions if e.status == ExecutionStatus.ERROR)

        # Get last execution
        last_execution = executions[0] if executions else None

        # Calculate success rate
        completed = passed_count + failed_count + error_count
        success_rate = (passed_count / completed * 100) if completed > 0 else 0

        # Calculate average duration
        durations = [e.duration for e in executions if e.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Calculate average test counts
        total_tests = sum(e.total_count for e in executions)
        avg_tests = total_tests / total_executions if total_executions > 0 else 0

        return {
            "test_suite_id": test_suite_id,
            "total_executions": total_executions,
            "statistics": {
                "passed": passed_count,
                "failed": failed_count,
                "error": error_count,
                "success_rate": round(success_rate, 2),
                "avg_duration": round(avg_duration, 2),
                "avg_tests_per_execution": round(avg_tests, 2),
            },
            "last_execution": {
                "id": last_execution.id,
                "status": last_execution.status,
                "start_time": last_execution.start_time.isoformat()
                if last_execution.start_time
                else None,
                "duration": last_execution.duration,
                "total_count": last_execution.total_count,
                "passed_count": last_execution.passed_count,
                "failed_count": last_execution.failed_count,
            }
            if last_execution
            else None,
            "recent_executions": [
                {
                    "id": e.id,
                    "uuid": e.uuid,
                    "status": e.status,
                    "start_time": e.start_time.isoformat() if e.start_time else None,
                    "duration": e.duration,
                    "total_count": e.total_count,
                    "passed_count": e.passed_count,
                    "failed_count": e.failed_count,
                    "environment": e.environment,
                }
                for e in executions
            ],
        }

    def get_trend_report(
        self, session: Session, days: int = 30, environment: str | None = None
    ) -> dict[str, Any]:
        """Get execution trend report.

        Args:
            session: Database session
            days: Number of days to include in trend
            environment: Filter by environment

        Returns:
            Dictionary with daily execution trends
        """
        start_date = datetime.now() - timedelta(days=days)

        # Build query
        query = session.query(
            func.date(TestExecution.start_time).label("date"),
            func.count(TestExecution.id).label("total"),
            func.sum(
                func.case((TestExecution.status == ExecutionStatus.PASSED, 1), else_=0)
            ).label("passed"),
            func.sum(
                func.case((TestExecution.status == ExecutionStatus.FAILED, 1), else_=0)
            ).label("failed"),
            func.sum(
                func.case((TestExecution.status == ExecutionStatus.ERROR, 1), else_=0)
            ).label("error"),
        ).filter(TestExecution.start_time >= start_date)

        if environment:
            query = query.filter(TestExecution.environment == environment)

        query = query.group_by(func.date(TestExecution.start_time))
        query = query.order_by(func.date(TestExecution.start_time))

        results = query.all()

        # Format results
        daily_data = []
        for row in results:
            date_str = row.date.isoformat() if row.date else None
            total = row.total or 0
            passed = row.passed or 0
            failed = row.failed or 0
            error = row.error or 0

            pass_rate = (passed / total * 100) if total > 0 else 0

            daily_data.append(
                {
                    "date": date_str,
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "error": error,
                    "pass_rate": round(pass_rate, 2),
                }
            )

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "days": days,
            },
            "environment": environment,
            "daily_data": daily_data,
        }

    def get_environment_comparison_report(
        self,
        session: Session,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Get environment comparison report.

        Args:
            session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Dictionary with statistics by environment
        """
        # Build query
        query = session.query(
            TestExecution.environment,
            func.count(TestExecution.id).label("total"),
            func.sum(
                func.case((TestExecution.status == ExecutionStatus.PASSED, 1), else_=0)
            ).label("passed"),
            func.sum(
                func.case((TestExecution.status == ExecutionStatus.FAILED, 1), else_=0)
            ).label("failed"),
            func.sum(
                func.case((TestExecution.status == ExecutionStatus.ERROR, 1), else_=0)
            ).label("error"),
            func.avg(TestExecution.duration).label("avg_duration"),
        )

        if start_date:
            query = query.filter(TestExecution.start_time >= start_date)

        if end_date:
            query = query.filter(TestExecution.start_time <= end_date)

        query = query.group_by(TestExecution.environment)

        results = query.all()

        # Format results
        environments = []
        for row in results:
            total = row.total or 0
            passed = row.passed or 0
            failed = row.failed or 0
            error = row.error or 0
            avg_duration = row.avg_duration or 0

            pass_rate = (passed / total * 100) if total > 0 else 0

            environments.append(
                {
                    "environment": row.environment,
                    "total_executions": total,
                    "passed": passed,
                    "failed": failed,
                    "error": error,
                    "pass_rate": round(pass_rate, 2),
                    "avg_duration": round(avg_duration, 2),
                }
            )

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "environments": environments,
        }

    def get_failure_analysis_report(
        self,
        session: Session,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get failure analysis report.

        Args:
            session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Number of top failures to include

        Returns:
            Dictionary with failure analysis
        """
        # Build query for failed executions
        query = session.query(TestExecution).filter(
            TestExecution.status.in_([ExecutionStatus.FAILED, ExecutionStatus.ERROR])
        )

        if start_date:
            query = query.filter(TestExecution.start_time >= start_date)

        if end_date:
            query = query.filter(TestExecution.start_time <= end_date)

        query = query.order_by(TestExecution.start_time.desc()).limit(limit)

        failed_executions = query.all()

        # Format results
        failures = []
        for execution in failed_executions:
            failures.append(
                {
                    "id": execution.id,
                    "uuid": execution.uuid,
                    "test_case_id": execution.test_case_id,
                    "test_suite_id": execution.test_suite_id,
                    "status": execution.status,
                    "start_time": execution.start_time.isoformat()
                    if execution.start_time
                    else None,
                    "duration": execution.duration,
                    "environment": execution.environment,
                    "error_message": execution.error_message,
                    "failed_count": execution.failed_count,
                    "error_count": execution.error_count,
                }
            )

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "total_failures": len(failures),
            "recent_failures": failures,
        }
