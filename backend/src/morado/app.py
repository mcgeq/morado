"""Litestar application instance for the Morado testing platform.

This module creates and configures the Litestar application with all
necessary middleware, exception handlers, and route handlers.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from litestar import Litestar
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig

from morado.common.logger import configure_logger, get_logger
from morado.common.logger.config import LoggerConfig
from morado.core.config import get_settings
from morado.core.database import close_database, get_db, init_database
from morado.middleware import (
    create_cors_config,
    create_exception_handlers,
    create_logging_middleware,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None]:
    """Application lifespan manager.

    This context manager handles application startup and shutdown tasks:
    - Initialize database connections
    - Configure logging
    - Clean up resources on shutdown

    Args:
        app: Litestar application instance

    Yields:
        None
    """
    settings = get_settings()

    # Configure logging
    log_config = LoggerConfig(
        level=settings.log_level,
        format=settings.log_format,
    )
    configure_logger(log_config)

    logger.info(
        "Starting Morado application",
        extra={
            "environment": settings.environment,
            "version": settings.version,
            "debug": settings.debug,
        },
    )

    # Initialize database
    try:
        init_database(settings.database_url)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.exception("Failed to initialize database", extra={"error": str(e)})
        raise

    # Application is ready
    yield

    # Shutdown tasks
    logger.info("Shutting down Morado application")

    try:
        await close_database()
        logger.info("Database connections closed")
    except Exception as e:
        logger.exception("Error closing database connections", extra={"error": str(e)})


def create_app() -> Litestar:
    """Create and configure the Litestar application.

    This function creates a Litestar application instance with:
    - All API route handlers
    - CORS configuration
    - Exception handlers
    - Logging middleware
    - Database session dependency
    - OpenAPI documentation

    Returns:
        Configured Litestar application instance

    Example:
        >>> app = create_app()
        >>> # Run with uvicorn
        >>> # uvicorn morado.app:app --reload
    """
    settings = get_settings()

    # Import all controller classes from API modules
    from morado.api.v1.api_definition import ApiDefinitionController
    from morado.api.v1.body import BodyController
    from morado.api.v1.component import TestComponentController
    from morado.api.v1.dashboard import DashboardController
    from morado.api.v1.header import HeaderController
    from morado.api.v1.report import ReportController
    from morado.api.v1.script import TestScriptController
    from morado.api.v1.test_case import TestCaseController
    from morado.api.v1.test_execution import TestExecutionController
    from morado.api.v1.test_suite import TestSuiteController

    # Create OpenAPI configuration
    openapi_config = OpenAPIConfig(
        title=settings.app_name,
        version=settings.version,
        description="Morado Testing Platform API - A four-layer architecture for API testing",
        path="/docs",
        use_handler_docstrings=True,
        tags=[
            {
                "name": "Headers",
                "description": "HTTP header component management (Layer 1)",
            },
            {
                "name": "Bodies",
                "description": "Request/response body component management (Layer 1)",
            },
            {
                "name": "API Definitions",
                "description": "API definition management (Layer 1)",
            },
            {
                "name": "Scripts",
                "description": "Test script management and execution (Layer 2)",
            },
            {
                "name": "Components",
                "description": "Test component management and execution (Layer 3)",
            },
            {"name": "Test Cases", "description": "Test case management (Layer 4)"},
            {"name": "Test Suites", "description": "Test suite management"},
            {"name": "Test Execution", "description": "Test execution and results"},
            {"name": "Reports", "description": "Test reports and analytics"},
            {"name": "Dashboard", "description": "Dashboard statistics and metrics"},
        ],  # type: ignore[arg-type]
    )

    # Create application
    app = Litestar(
        route_handlers=[
            HeaderController,
            BodyController,
            ApiDefinitionController,
            TestScriptController,
            TestComponentController,
            TestCaseController,
            TestSuiteController,
            TestExecutionController,
            ReportController,
            DashboardController,
        ],
        cors_config=create_cors_config(settings),
        exception_handlers=create_exception_handlers(),
        middleware=[create_logging_middleware()],
        dependencies={
            "db_session": Provide(get_db, sync_to_thread=True),
        },
        openapi_config=openapi_config,
        lifespan=[lifespan],
        debug=settings.debug,
    )

    logger.info(
        "Litestar application created",
        extra={
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )

    return app


# Create application instance
app = create_app()
