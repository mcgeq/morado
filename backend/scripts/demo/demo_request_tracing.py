"""Demonstration of full request tracing across the call chain.

This script demonstrates how a single request ID is tracked through
the entire application stack:
- HTTP Request (Middleware)
- Service Layer
- Repository Layer
- Database Layer

All logs will include the same request_id, making it easy to trace
a request through the entire system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from morado.common.logger import configure_logger, get_logger
from morado.common.logger.config import LoggerConfig
from morado.common.logger.context import (
    clear_context,
    get_log_context,
    set_context_data,
    set_request_id,
)


def simulate_http_request():
    """Simulate an HTTP request entering the system."""
    print("\n" + "=" * 70)
    print("SIMULATING HTTP REQUEST")
    print("=" * 70)

    # Generate a request ID (normally done by middleware)
    request_id = "REQ-demo-12345"
    set_request_id(request_id)

    # Set request context (normally done by middleware)
    set_context_data("method", "POST")
    set_context_data("path", "/v1/headers")
    set_context_data("client_ip", "192.168.1.100")

    logger = get_logger("morado.middleware.logging")
    logger.info("Request started", extra=get_log_context())

    # Call service layer
    simulate_service_layer()

    logger.info("Request completed", extra=get_log_context())

    # Clear context (normally done by middleware)
    clear_context()


def simulate_service_layer():
    """Simulate service layer processing."""
    print("\n" + "-" * 70)
    print("SERVICE LAYER")
    print("-" * 70)

    logger = get_logger("morado.services.api_component")

    # Add service-specific context
    set_context_data("service", "HeaderService")
    set_context_data("operation", "create_header")

    logger.info(
        "Creating header component",
        extra={
            **get_log_context(),
            "name": "Auth Header",
            "scope": "global",
        },
    )

    # Call repository layer
    simulate_repository_layer()

    logger.info(
        "Header component created successfully",
        extra={
            **get_log_context(),
            "header_id": 123,
            "name": "Auth Header",
        },
    )


def simulate_repository_layer():
    """Simulate repository layer processing."""
    print("\n" + "-" * 70)
    print("REPOSITORY LAYER")
    print("-" * 70)

    logger = get_logger("morado.repositories.api_component")

    # Add repository-specific context
    set_context_data("repository", "HeaderRepository")

    logger.debug(
        "Creating header in database",
        extra={
            **get_log_context(),
            "table": "headers",
        },
    )

    # Call database layer
    simulate_database_layer()

    logger.debug(
        "Header created in database",
        extra={
            **get_log_context(),
            "header_id": 123,
        },
    )


def simulate_database_layer():
    """Simulate database layer processing."""
    print("\n" + "-" * 70)
    print("DATABASE LAYER")
    print("-" * 70)

    logger = get_logger("morado.core.database")

    logger.debug(
        "Executing SQL INSERT",
        extra={
            **get_log_context(),
            "query": "INSERT INTO headers (name, scope) VALUES (?, ?)",
            "params": ["Auth Header", "global"],
        },
    )

    logger.debug(
        "SQL INSERT completed",
        extra={
            **get_log_context(),
            "rows_affected": 1,
            "duration_ms": 15,
        },
    )


def demonstrate_multiple_requests():
    """Demonstrate multiple requests with different request IDs."""
    print("\n\n" + "=" * 70)
    print("DEMONSTRATING MULTIPLE CONCURRENT REQUESTS")
    print("=" * 70)
    print("\nNotice how each request has its own request_id that is")
    print("tracked through the entire call chain.\n")

    # Request 1
    print("\n" + ">" * 70)
    print("REQUEST 1")
    print(">" * 70)
    set_request_id("REQ-user-login-001")
    set_context_data("method", "POST")
    set_context_data("path", "/v1/auth/login")
    set_context_data("user", "john@example.com")

    logger = get_logger("morado.services.auth")
    logger.info("User login attempt", extra=get_log_context())
    logger.info("Login successful", extra=get_log_context())
    clear_context()

    # Request 2
    print("\n" + ">" * 70)
    print("REQUEST 2")
    print(">" * 70)
    set_request_id("REQ-create-order-002")
    set_context_data("method", "POST")
    set_context_data("path", "/v1/orders")
    set_context_data("user_id", 123)

    logger = get_logger("morado.services.order")
    logger.info("Creating order", extra=get_log_context())
    logger.info("Order created", extra={**get_log_context(), "order_id": 456})
    clear_context()

    # Request 3
    print("\n" + ">" * 70)
    print("REQUEST 3")
    print(">" * 70)
    set_request_id("REQ-get-profile-003")
    set_context_data("method", "GET")
    set_context_data("path", "/v1/users/123/profile")

    logger = get_logger("morado.services.user")
    logger.info("Fetching user profile", extra=get_log_context())
    logger.info("Profile retrieved", extra={**get_log_context(), "user_id": 123})
    clear_context()


def demonstrate_error_tracing():
    """Demonstrate error tracing with request ID."""
    print("\n\n" + "=" * 70)
    print("DEMONSTRATING ERROR TRACING")
    print("=" * 70)
    print("\nNotice how errors include the full request context,")
    print("making it easy to trace which request caused the error.\n")

    set_request_id("REQ-error-demo-999")
    set_context_data("method", "POST")
    set_context_data("path", "/v1/headers")
    set_context_data("user_id", 789)

    logger = get_logger("morado.services.api_component")

    try:
        logger.info("Creating header component", extra=get_log_context())

        # Simulate an error
        raise ValueError("Invalid header format")

    except Exception as e:
        logger.exception(
            "Failed to create header component",
            extra={
                **get_log_context(),
                "error": str(e),
            },
        )

    clear_context()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("MORADO REQUEST TRACING DEMONSTRATION")
    print("=" * 70)
    print("\nThis demonstration shows how a single request_id is tracked")
    print("through the entire application stack, from HTTP request to database.")
    print("\nAll logs from the same request will have the same request_id,")
    print("making it easy to trace a request through the system.")

    # Configure logger
    configure_logger(LoggerConfig(level="DEBUG", format="console"))

    # Run demonstrations
    simulate_http_request()
    demonstrate_multiple_requests()
    demonstrate_error_tracing()

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("1. ✓ Each request has a unique request_id")
    print("2. ✓ The request_id is automatically included in all logs")
    print("3. ✓ Context data (method, path, user_id, etc.) is preserved")
    print("4. ✓ Easy to trace a request through the entire call chain")
    print("5. ✓ Errors include full context for debugging")
    print("\nIn production, you can grep logs by request_id:")
    print('  grep "REQ-demo-12345" logs/app.log')
    print("\nOr use jq for JSON logs:")
    print('  cat logs/app.log | jq \'select(.request_id == "REQ-demo-12345")\'')


if __name__ == "__main__":
    main()
