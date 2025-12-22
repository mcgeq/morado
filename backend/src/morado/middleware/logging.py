"""Logging middleware for the Morado application.

This module provides middleware for logging HTTP requests and responses,
including request IDs, timing information, and structured logging support.

The middleware automatically sets the request ID in the context, making it
available throughout the entire call chain (services, repositories, etc.).
"""

import time
from typing import TYPE_CHECKING

from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from morado.common.logger import get_logger
from morado.common.logger.context import (
    clear_context,
    get_log_context,
    set_context_data,
    set_request_id,
)
from morado.common.utils.uuid import generate_uuid

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class LoggingMiddleware:
    """Middleware for logging HTTP requests and responses with full context tracking.

    This middleware logs information about each HTTP request and response,
    including:
    - Request method and path
    - Request ID (generated or from header)
    - Response status code
    - Request duration
    - Client IP address

    The middleware automatically sets the request ID in a context variable,
    making it available throughout the entire call chain. All logs from
    services, repositories, and other components will automatically include
    the request ID.

    Example:
        >>> from litestar import Litestar
        >>> from morado.middleware.logging import LoggingMiddleware
        >>> app = Litestar(
        ...     route_handlers=[...],
        ...     middleware=[DefineMiddleware(LoggingMiddleware)]
        ... )
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the logging middleware.

        Args:
            app: The ASGI application to wrap.
        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request and log information.

        Args:
            scope: ASGI scope dictionary containing request information.
            receive: ASGI receive callable for reading request body.
            send: ASGI send callable for sending response.
        """
        # Only process HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request information
        method = scope.get("method", "")
        path = scope.get("path", "")

        # Get or generate request ID
        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", b"").decode("utf-8")
        if not request_id:
            request_id = generate_uuid()

        # Set request ID in context for the entire call chain
        # This makes it available to all services, repositories, etc.
        set_request_id(request_id)

        # Add request ID to scope for downstream handlers
        scope["state"] = scope.get("state", {})
        scope["state"]["request_id"] = request_id

        # Get client IP
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        # Store additional context that will be included in all logs
        set_context_data("method", method)
        set_context_data("path", path)
        set_context_data("client_ip", client_ip)

        # Start timing
        start_time = time.time()

        # Log request with full context
        logger.info(
            "Request started",
            extra=get_log_context(),
        )

        # Capture response status
        status_code = None

        async def send_wrapper(message: dict) -> None:  # type: ignore[type-arg]
            """Wrapper to capture response status code."""
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                # Add request ID to response headers
                headers_list = list(message.get("headers", []))
                headers_list.append((b"x-request-id", request_id.encode("utf-8")))
                message["headers"] = headers_list
            await send(message)  # type: ignore[arg-type]

        try:
            # Process request
            await self.app(scope, receive, send_wrapper)  # type: ignore[arg-type]
        except Exception as exc:
            # Log exception with full context
            duration = time.time() - start_time
            set_context_data("duration", duration)
            set_context_data("error", str(exc))
            set_context_data("error_type", type(exc).__name__)

            logger.exception(
                "Request failed with exception",
                extra=get_log_context(),
            )
            raise
        else:
            # Log successful response with full context
            duration = time.time() - start_time
            set_context_data("status_code", status_code)
            set_context_data("duration", duration)

            log_level = "info" if status_code and status_code < 400 else "warning"
            log_func = logger.info if log_level == "info" else logger.warning

            log_func(
                "Request completed",
                extra=get_log_context(),
            )
        finally:
            # Clear context after request completes
            clear_context()


def create_logging_middleware() -> DefineMiddleware:
    """Create a DefineMiddleware instance for logging.

    Returns:
        DefineMiddleware instance wrapping LoggingMiddleware.

    Example:
        >>> from litestar import Litestar
        >>> from morado.middleware.logging import create_logging_middleware
        >>> app = Litestar(
        ...     route_handlers=[...],
        ...     middleware=[create_logging_middleware()]
        ... )
    """
    return DefineMiddleware(LoggingMiddleware)
