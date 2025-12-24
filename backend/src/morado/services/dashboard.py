"""Service layer for Dashboard data.

This module provides business logic for generating dashboard statistics
and metrics for the home page.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from morado.models.api_component import ApiDefinition
from morado.models.component import TestComponent
from morado.models.script import TestScript
from morado.models.test_case import TestCase
from morado.models.test_execution import ExecutionStatus, TestExecution
from morado.models.user import User


class DashboardService:
    """Service for generating dashboard data.

    Provides business logic for generating dashboard statistics,
    user metrics, and trend data for the home page.

    Example:
        >>> service = DashboardService()
        >>> metrics = service.get_user_metrics(session, user_id=1)
    """

    def get_user_metrics(self, session: Session, user_id: int) -> dict[str, Any]:
        """Get user metrics for dashboard.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Dictionary with user information and metrics

        Example:
            >>> metrics = service.get_user_metrics(session, user_id=1)
            >>> print(metrics['total_executions'])
        """
        # Get user information
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            return {
                "user_id": user_id,
                "username": "Unknown",
                "avatar_url": None,
                "registration_date": None,
                "total_executions": 0,
                "passed_tests": 0,
                "failed_tests": 0,
            }

        # Get execution statistics for this user
        executions = (
            session.query(TestExecution)
            .filter(TestExecution.created_by == user_id)
            .all()
        )

        total_executions = len(executions)
        passed_tests = sum(e.passed_count for e in executions)
        failed_tests = sum(e.failed_count + e.error_count for e in executions)

        return {
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "registration_date": user.created_at.isoformat() if user.created_at else None,
            "total_executions": total_executions,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
        }

    def get_step_statistics(self, session: Session) -> dict[str, Any]:
        """Get step statistics for dashboard.

        This calculates statistics based on execution results.
        - Completed: Successful executions
        - SQL Failed: Executions with SQL-related errors
        - API Request: Total API requests made

        Args:
            session: Database session

        Returns:
            Dictionary with step statistics

        Example:
            >>> stats = service.get_step_statistics(session)
            >>> print(stats['completed'])
        """
        # Get all executions
        executions = session.query(TestExecution).all()

        # Calculate statistics
        completed = sum(e.passed_count for e in executions)
        
        # SQL failures - count executions with "SQL" or "sql" in error message
        sql_failed = 0
        for e in executions:
            if e.error_message and ("SQL" in e.error_message or "sql" in e.error_message):
                sql_failed += e.failed_count + e.error_count

        # API requests - count total test executions (each execution represents API calls)
        api_request = sum(e.total_count for e in executions)

        total = completed + sql_failed + api_request

        return {
            "completed": completed,
            "sql_failed": sql_failed,
            "api_request": api_request,
            "total": total,
        }

    def get_api_usage(self, session: Session) -> dict[str, Any]:
        """Get API usage statistics for dashboard.

        Args:
            session: Database session

        Returns:
            Dictionary with API usage statistics

        Example:
            >>> usage = service.get_api_usage(session)
            >>> print(usage['api_completion_rate'])
        """
        # Get total API definitions
        total_apis = session.query(func.count(ApiDefinition.id)).scalar() or 0

        # Get APIs that have been used in scripts
        completed_apis = (
            session.query(func.count(func.distinct(TestScript.api_definition_id)))
            .filter(TestScript.api_definition_id.isnot(None))
            .scalar()
            or 0
        )

        # Get APIs with tags (assuming tags indicate completion/validation)
        tagged_apis = (
            session.query(func.count(ApiDefinition.id))
            .filter(ApiDefinition.tags.isnot(None))
            .scalar()
            or 0
        )

        # Calculate API completion rate
        api_completion_rate = (
            (completed_apis / total_apis * 100) if total_apis > 0 else 0
        )

        # Get total test cases
        total_test_cases = session.query(func.count(TestCase.id)).scalar() or 0

        # Get test cases that have been executed
        passed_test_cases = (
            session.query(func.count(func.distinct(TestExecution.test_case_id)))
            .filter(
                TestExecution.test_case_id.isnot(None),
                TestExecution.status == ExecutionStatus.PASSED,
            )
            .scalar()
            or 0
        )

        # Get test cases with tags
        tagged_test_cases = (
            session.query(func.count(TestCase.id))
            .filter(TestCase.tags.isnot(None))
            .scalar()
            or 0
        )

        # Calculate test case completion rate
        test_case_completion_rate = (
            (passed_test_cases / total_test_cases * 100) if total_test_cases > 0 else 0
        )

        return {
            "api_completion_rate": round(api_completion_rate, 0),
            "total_apis": total_apis,
            "completed_apis": completed_apis,
            "tagged_apis": tagged_apis,
            "test_case_completion_rate": round(test_case_completion_rate, 0),
            "total_test_cases": total_test_cases,
            "passed_test_cases": passed_test_cases,
            "tagged_test_cases": tagged_test_cases,
        }

    def get_trends(self, session: Session, days: int = 7) -> dict[str, Any]:
        """Get trend data for dashboard.

        Args:
            session: Database session
            days: Number of days to include in trend (default: 7)

        Returns:
            Dictionary with trend data

        Example:
            >>> trends = service.get_trends(session, days=7)
            >>> print(trends['data'])
        """
        start_date = datetime.now() - timedelta(days=days)

        # Query for daily component and test case counts
        # We'll use creation dates as a proxy for activity
        
        # Get daily script counts (scheduled components)
        script_query = (
            session.query(
                func.date(TestScript.created_at).label("date"),
                func.count(TestScript.id).label("count"),
            )
            .filter(TestScript.created_at >= start_date)
            .group_by(func.date(TestScript.created_at))
            .all()
        )

        # Get daily test case counts
        test_case_query = (
            session.query(
                func.date(TestCase.created_at).label("date"),
                func.count(TestCase.id).label("count"),
            )
            .filter(TestCase.created_at >= start_date)
            .group_by(func.date(TestCase.created_at))
            .all()
        )

        # Get daily component counts
        component_query = (
            session.query(
                func.date(TestComponent.created_at).label("date"),
                func.count(TestComponent.id).label("count"),
            )
            .filter(TestComponent.created_at >= start_date)
            .group_by(func.date(TestComponent.created_at))
            .all()
        )

        # Get daily execution counts (detection components)
        execution_query = (
            session.query(
                func.date(TestExecution.start_time).label("date"),
                func.count(TestExecution.id).label("count"),
            )
            .filter(TestExecution.start_time >= start_date)
            .group_by(func.date(TestExecution.start_time))
            .all()
        )

        # Create a dictionary for each data series
        script_data = {row.date: row.count for row in script_query if row.date}
        test_case_data = {row.date: row.count for row in test_case_query if row.date}
        component_data = {row.date: row.count for row in component_query if row.date}
        execution_data = {row.date: row.count for row in execution_query if row.date}

        # Generate data for all days in the range
        data = []
        current_date = start_date.date()
        end_date = datetime.now().date()

        while current_date <= end_date:
            data.append(
                {
                    "date": current_date.isoformat(),
                    "scheduled_components": script_data.get(current_date, 0),
                    "test_case_components": test_case_data.get(current_date, 0),
                    "actual_components": component_data.get(current_date, 0),
                    "detection_components": execution_data.get(current_date, 0),
                }
            )
            current_date += timedelta(days=1)

        return {"data": data}
