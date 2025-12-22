"""Logging middleware for the Morado application.

This module provides middleware for logging HTTP requests and responses,
including request IDs, timing information, and structured logging support.
"""

import time
from typing import TYPE_CHECKING

from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from morado.common.logger import get_logger
from morado.common.utils.uuid import generate_uuid

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class LoggingMiddleware:
    """Middleware for logging HTTP requests and responses.

    This middleware logs information about each HTTP request and response,
    including:
    - Request method and path
    - Request ID (generated or from header)
    - Response status code
    - Request duration
    - Client IP address

    The middleware uses structured logging to ensure logs are easily
    parseable and searchable.

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

        # Add request ID to scope for downstream handlers
        scope["state"] = scope.get("state", {})
        scope["state"]["request_id"] = request_id

        # Get client IP
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        # Start timing
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_ip,
            },
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
            # Log exception
            duration = time.time() - start_time
            logger.exception(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration": duration,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )
            raise
        else:
            # Log successful response
            duration = time.time() - start_time
            log_level = "info" if status_code and status_code < 400 else "warning"

            log_func = logger.info if log_level == "info" else logger.warning
            log_func(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration": duration,
                    "client_ip": client_ip,
                },
            )


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
