"""Test Report API endpoints.

This module provides REST API endpoints for generating test reports and analytics.
"""

from datetime import datetime
from typing import Annotated, Any

from litestar import Controller, get
from litestar.di import Provide
from litestar.params import Parameter
from morado.services.report import ReportService
from sqlalchemy.orm import Session


def provide_report_service() -> ReportService:
    """Provide ReportService instance."""
    return ReportService()


class ReportController(Controller):
    """Controller for Report generation endpoints."""

    path = "/reports"
    tags = ["Reports"]
    dependencies = {"report_service": Provide(provide_report_service)}

    @get("/execution-summary")
    async def get_execution_summary_report(
        self,
        report_service: ReportService,
        db_session: Session,
        start_date: Annotated[datetime | None, Parameter(query="start_date")] = None,
        end_date: Annotated[datetime | None, Parameter(query="end_date")] = None,
        environment: Annotated[str | None, Parameter(query="environment")] = None,
        test_case_id: Annotated[int | None, Parameter(query="test_case_id")] = None,
        test_suite_id: Annotated[int | None, Parameter(query="test_suite_id")] = None,
    ) -> dict[str, Any]:
        """Get execution summary report.

        This endpoint provides aggregated statistics about test executions
        within a specified time period.

        Args:
            report_service: Report service instance
            db_session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            environment: Filter by environment
            test_case_id: Filter by test case ID
            test_suite_id: Filter by test suite ID

        Returns:
            Execution summary statistics

        Example:
            GET /reports/execution-summary?start_date=2024-01-01&end_date=2024-01-31
        """
        return report_service.get_execution_summary_report(
            db_session,
            start_date=start_date,
            end_date=end_date,
            environment=environment,
            test_case_id=test_case_id,
            test_suite_id=test_suite_id
        )

    @get("/test-case/{test_case_id:int}")
    async def get_test_case_report(
        self,
        test_case_id: int,
        report_service: ReportService,
        db_session: Session,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 10,
    ) -> dict[str, Any]:
        """Get test case execution report.

        This endpoint provides execution history and statistics for a specific test case.

        Args:
            test_case_id: Test case ID
            report_service: Report service instance
            db_session: Database session
            limit: Number of recent executions to include

        Returns:
            Test case execution history and statistics
        """
        return report_service.get_test_case_report(
            db_session,
            test_case_id,
            limit=limit
        )

    @get("/test-suite/{test_suite_id:int}")
    async def get_test_suite_report(
        self,
        test_suite_id: int,
        report_service: ReportService,
        db_session: Session,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 10,
    ) -> dict[str, Any]:
        """Get test suite execution report.

        This endpoint provides execution history and statistics for a specific test suite.

        Args:
            test_suite_id: Test suite ID
            report_service: Report service instance
            db_session: Database session
            limit: Number of recent executions to include

        Returns:
            Test suite execution history and statistics
        """
        return report_service.get_test_suite_report(
            db_session,
            test_suite_id,
            limit=limit
        )

    @get("/trend")
    async def get_trend_report(
        self,
        report_service: ReportService,
        db_session: Session,
        days: Annotated[int, Parameter(query="days", ge=1, le=365)] = 30,
        environment: Annotated[str | None, Parameter(query="environment")] = None,
    ) -> dict[str, Any]:
        """Get execution trend report.

        This endpoint provides daily execution trends over a specified period.

        Args:
            report_service: Report service instance
            db_session: Database session
            days: Number of days to include in trend
            environment: Filter by environment

        Returns:
            Daily execution trends

        Example:
            GET /reports/trend?days=30&environment=test
        """
        return report_service.get_trend_report(
            db_session,
            days=days,
            environment=environment
        )

    @get("/environment-comparison")
    async def get_environment_comparison_report(
        self,
        report_service: ReportService,
        db_session: Session,
        start_date: Annotated[datetime | None, Parameter(query="start_date")] = None,
        end_date: Annotated[datetime | None, Parameter(query="end_date")] = None,
    ) -> dict[str, Any]:
        """Get environment comparison report.

        This endpoint provides statistics comparing test executions across
        different environments.

        Args:
            report_service: Report service instance
            db_session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Statistics by environment

        Example:
            GET /reports/environment-comparison?start_date=2024-01-01
        """
        return report_service.get_environment_comparison_report(
            db_session,
            start_date=start_date,
            end_date=end_date
        )

    @get("/failure-analysis")
    async def get_failure_analysis_report(
        self,
        report_service: ReportService,
        db_session: Session,
        start_date: Annotated[datetime | None, Parameter(query="start_date")] = None,
        end_date: Annotated[datetime | None, Parameter(query="end_date")] = None,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 10,
    ) -> dict[str, Any]:
        """Get failure analysis report.

        This endpoint provides analysis of failed test executions,
        including error messages and failure patterns.

        Args:
            report_service: Report service instance
            db_session: Database session
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Number of top failures to include

        Returns:
            Failure analysis

        Example:
            GET /reports/failure-analysis?limit=20
        """
        return report_service.get_failure_analysis_report(
            db_session,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
