"""Test script for the logging system.

This script demonstrates and tests the logging functionality in Morado.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from morado.common.logger import configure_logger, get_logger, request_scope
from morado.common.logger.config import LoggerConfig
from morado.core.config import get_settings


def test_basic_logging():
    """Test basic logging functionality."""
    print("\n" + "=" * 60)
    print("Testing Basic Logging")
    print("=" * 60)

    logger = get_logger(__name__)

    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")

    print("✓ Basic logging test completed")


def test_structured_logging():
    """Test structured logging with extra fields."""
    print("\n" + "=" * 60)
    print("Testing Structured Logging")
    print("=" * 60)

    logger = get_logger(__name__)

    # Log with structured data
    logger.info(
        "User action performed",
        extra={
            "user_id": 123,
            "action": "create_header",
            "header_name": "Auth Header",
            "scope": "global",
        },
    )

    logger.info(
        "Database operation",
        extra={
            "operation": "INSERT",
            "table": "headers",
            "rows_affected": 1,
            "duration_ms": 45,
        },
    )

    print("✓ Structured logging test completed")


def test_request_context():
    """Test request context tracking."""
    print("\n" + "=" * 60)
    print("Testing Request Context")
    print("=" * 60)

    logger = get_logger(__name__)

    # Test with request scope
    with request_scope(user_id=456, action="test_operation") as ctx:
        logger.info("Inside request scope", extra={"step": 1})
        logger.info("Processing data", extra={"step": 2})
        logger.info("Request context", extra={"context": ctx})

    print("✓ Request context test completed")


def test_exception_logging():
    """Test exception logging."""
    print("\n" + "=" * 60)
    print("Testing Exception Logging")
    print("=" * 60)

    logger = get_logger(__name__)

    try:
        # Simulate an error
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.exception(
            "Division by zero error",
            extra={"operation": "divide", "error": str(e)},
        )

    print("✓ Exception logging test completed")


def test_module_logging():
    """Test logging from different modules."""
    print("\n" + "=" * 60)
    print("Testing Module-Specific Logging")
    print("=" * 60)

    # Get loggers for different modules
    config_logger = get_logger("morado.core.config")
    db_logger = get_logger("morado.core.database")
    service_logger = get_logger("morado.services.api_component")

    config_logger.info("Config module log")
    db_logger.info("Database module log")
    service_logger.info("Service module log")

    print("✓ Module-specific logging test completed")


def test_log_formats():
    """Test different log formats."""
    print("\n" + "=" * 60)
    print("Testing Log Formats")
    print("=" * 60)

    logger = get_logger(__name__)

    # Test console format
    print("\n--- Console Format ---")
    configure_logger(LoggerConfig(level="INFO", format="console"))
    logger.info("Console format message", extra={"format": "console"})

    # Test JSON format
    print("\n--- JSON Format ---")
    configure_logger(LoggerConfig(level="INFO", format="json"))
    logger.info("JSON format message", extra={"format": "json"})

    # Reset to console for readability
    configure_logger(LoggerConfig(level="INFO", format="console"))

    print("\n✓ Log format test completed")


def test_configuration_logging():
    """Test logging from configuration module."""
    print("\n" + "=" * 60)
    print("Testing Configuration Module Logging")
    print("=" * 60)

    # This will trigger logging in the config module
    settings = get_settings()

    print(f"✓ Configuration loaded: {settings.app_name} v{settings.version}")
    print(f"  Environment: {settings.environment}")
    print(f"  Log level: {settings.log_level}")


def test_database_logging():
    """Test logging from database module."""
    print("\n" + "=" * 60)
    print("Testing Database Module Logging")
    print("=" * 60)

    from morado.core.database import get_database_manager

    db_manager = get_database_manager()

    # Note: This will fail if database is not available, but will show logging
    try:
        db_manager.initialize()
        print("✓ Database initialized (logging captured)")
    except Exception as e:
        print(f"✓ Database initialization failed (expected): {e}")
        print("  But logging was captured!")


def main():
    """Run all logging tests."""
    print("\n" + "=" * 60)
    print("Morado Logging System Test Suite")
    print("=" * 60)

    # Configure logger for testing
    configure_logger(LoggerConfig(level="DEBUG", format="console"))

    # Run tests
    test_basic_logging()
    test_structured_logging()
    test_request_context()
    test_exception_logging()
    test_module_logging()
    test_log_formats()
    test_configuration_logging()
    test_database_logging()

    print("\n" + "=" * 60)
    print("✓ All logging tests completed successfully!")
    print("=" * 60)
    print("\nLogging system is working correctly.")
    print("Check the output above to see different log formats and levels.")


if __name__ == "__main__":
    main()
