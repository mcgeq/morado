"""Dashboard API endpoints.

This module provides REST API endpoints for dashboard data including
user metrics, statistics, API usage, and trend analysis.
"""

from typing import Annotated, Any

from litestar import Controller, get
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy.orm import Session

from morado.services.dashboard import DashboardService


def provide_dashboard_service() -> DashboardService:
    """Provide DashboardService instance."""
    return DashboardService()


class DashboardController(Controller):
    """Controller for Dashboard endpoints."""

    path = "/dashboard"
    tags = ["Dashboard"]
    dependencies = {"dashboard_service": Provide(provide_dashboard_service)}

    @get("/user-metrics")
    async def get_user_metrics(
        self,
        dashboard_service: DashboardService,
        db_session: Session,
        user_id: Annotated[int, Parameter(query="user_id")] = 1,
    ) -> dict[str, Any]:
        """Get user metrics for dashboard.

        This endpoint provides user information and key testing metrics
        including total executions, passed tests, and failed tests.

        Args:
            dashboard_service: Dashboard service instance
            db_session: Database session
            user_id: User ID (default: 1)

        Returns:
            User metrics including:
            - user_id: User ID
            - username: Username
            - avatar_url: Avatar URL
            - registration_date: Registration date
            - total_executions: Total test executions
            - passed_tests: Total passed tests
            - failed_tests: Total failed tests

        Example:
            GET /dashboard/user-metrics?user_id=1
        """
        return dashboard_service.get_user_metrics(db_session, user_id)

    @get("/step-statistics")
    async def get_step_statistics(
        self,
        dashboard_service: DashboardService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get step statistics for dashboard.

        This endpoint provides statistics about test execution steps
        including completed steps, SQL failures, and API requests.

        Args:
            dashboard_service: Dashboard service instance
            db_session: Database session

        Returns:
            Step statistics including:
            - completed: Number of completed steps
            - sql_failed: Number of SQL execution failures
            - api_request: Number of API requests
            - total: Total number of steps

        Example:
            GET /dashboard/step-statistics
        """
        return dashboard_service.get_step_statistics(db_session)

    @get("/api-usage")
    async def get_api_usage(
        self,
        dashboard_service: DashboardService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get API usage statistics for dashboard.

        This endpoint provides statistics about API definitions and
        test case completion rates.

        Args:
            dashboard_service: Dashboard service instance
            db_session: Database session

        Returns:
            API usage statistics including:
            - api_completion_rate: API completion percentage
            - total_apis: Total number of API definitions
            - completed_apis: Number of completed APIs
            - tagged_apis: Number of tagged APIs
            - test_case_completion_rate: Test case completion percentage
            - total_test_cases: Total number of test cases
            - passed_test_cases: Number of passed test cases
            - tagged_test_cases: Number of tagged test cases

        Example:
            GET /dashboard/api-usage
        """
        return dashboard_service.get_api_usage(db_session)

    @get("/trends")
    async def get_trends(
        self,
        dashboard_service: DashboardService,
        db_session: Session,
        days: Annotated[int, Parameter(query="days", ge=1, le=365)] = 7,
    ) -> dict[str, Any]:
        """Get trend data for dashboard.

        This endpoint provides daily trend data for various components
        over a specified time period.

        Args:
            dashboard_service: Dashboard service instance
            db_session: Database session
            days: Number of days to include (default: 7, max: 365)

        Returns:
            Trend data including:
            - data: Array of daily data points with:
              - date: Date in YYYY-MM-DD format
              - scheduled_components: Number of scheduled components
              - test_case_components: Number of test case components
              - actual_components: Number of actual components
              - detection_components: Number of detection components

        Example:
            GET /dashboard/trends?days=30
        """
        return dashboard_service.get_trends(db_session, days)
