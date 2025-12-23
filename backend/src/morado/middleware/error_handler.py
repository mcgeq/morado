"""Error handling middleware for the Morado application.

This module provides centralized error handling for the Litestar application,
converting exceptions into standardized JSON error responses with appropriate
HTTP status codes.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from litestar.exceptions import (
    HTTPException,
    InternalServerException,
    NotAuthorizedException,
    NotFoundException,
    PermissionDeniedException,
    ValidationException,
)
from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from pydantic import BaseModel, Field

from morado.common.logger import get_logger
from morado.core.config import get_settings

if TYPE_CHECKING:
    from litestar import Request, Response

logger = get_logger(__name__)


class ErrorDetail(BaseModel):
    """Detailed error information.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable error message.
        details: Additional error details (optional).
        timestamp: ISO 8601 timestamp when the error occurred.
        request_id: Request ID for tracing (optional).
        path: Request path where the error occurred (optional).
    """

    code: str
    message: str
    details: dict | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    request_id: str | None = None
    path: str | None = None


class ErrorResponse(BaseModel):
    """Standardized error response format.

    Attributes:
        error: Detailed error information.
    """

    error: ErrorDetail


def create_error_response(
    code: str,
    message: str,
    details: dict | None = None,
    request_id: str | None = None,
    path: str | None = None,
) -> ErrorResponse:
    """Create a standardized error response.

    Args:
        code: Machine-readable error code.
        message: Human-readable error message.
        details: Additional error details (optional).
        request_id: Request ID for tracing (optional).
        path: Request path where the error occurred (optional).

    Returns:
        ErrorResponse instance with error details.

    Example:
        >>> response = create_error_response(
        ...     code="NOT_FOUND",
        ...     message="Resource not found",
        ...     request_id="abc-123"
        ... )
        >>> print(response.error.code)
        NOT_FOUND
    """
    return ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details,
            request_id=request_id,
            path=path,
        )
    )


async def validation_exception_handler(
    request: "Request", exc: ValidationException
) -> "Response":
    """Handle validation exceptions.

    Args:
        request: The request that caused the exception.
        exc: The validation exception.

    Returns:
        Response with validation error details.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        "Validation error",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "errors": exc.extra,
        },
    )

    error_response = create_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"validation_errors": exc.extra} if exc.extra else None,
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=HTTP_400_BAD_REQUEST,
    )


async def not_found_exception_handler(
    request: "Request", exc: NotFoundException
) -> "Response":
    """Handle not found exceptions.

    Args:
        request: The request that caused the exception.
        exc: The not found exception.

    Returns:
        Response with not found error details.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        "Resource not found",
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
    )

    error_response = create_error_response(
        code="NOT_FOUND",
        message=exc.detail or "The requested resource was not found",
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=HTTP_404_NOT_FOUND,
    )


async def not_authorized_exception_handler(
    request: "Request", exc: NotAuthorizedException
) -> "Response":
    """Handle not authorized exceptions.

    Args:
        request: The request that caused the exception.
        exc: The not authorized exception.

    Returns:
        Response with authentication error details.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        "Authentication required",
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
    )

    error_response = create_error_response(
        code="NOT_AUTHORIZED",
        message=exc.detail or "Authentication is required to access this resource",
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=HTTP_401_UNAUTHORIZED,
    )


async def permission_denied_exception_handler(
    request: "Request", exc: PermissionDeniedException
) -> "Response":
    """Handle permission denied exceptions.

    Args:
        request: The request that caused the exception.
        exc: The permission denied exception.

    Returns:
        Response with permission error details.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        "Permission denied",
        extra={
            "request_id": request_id,
            "path": request.url.path,
        },
    )

    error_response = create_error_response(
        code="PERMISSION_DENIED",
        message=exc.detail or "You do not have permission to access this resource",
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=HTTP_403_FORBIDDEN,
    )


async def http_exception_handler(request: "Request", exc: HTTPException) -> "Response":
    """Handle generic HTTP exceptions.

    Args:
        request: The request that caused the exception.
        exc: The HTTP exception.

    Returns:
        Response with error details.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        "HTTP exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "status_code": exc.status_code,
        },
    )

    error_response = create_error_response(
        code="HTTP_ERROR",
        message=exc.detail or "An HTTP error occurred",
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=exc.status_code,
    )


async def internal_server_exception_handler(
    request: "Request", exc: InternalServerException
) -> "Response":
    """Handle internal server exceptions.

    Args:
        request: The request that caused the exception.
        exc: The internal server exception.

    Returns:
        Response with error details.
    """
    request_id = getattr(request.state, "request_id", None)
    settings = get_settings()

    logger.exception(
        "Internal server error",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "error": str(exc),
            "error_type": type(exc).__name__,
        },
    )

    # In production, hide detailed error information
    if settings.is_production:
        message = "An internal server error occurred"
        details = None
    else:
        message = exc.detail or "An internal server error occurred"
        details = {"error_type": type(exc).__name__, "error": str(exc)}

    error_response = create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message=message,
        details=details,
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def generic_exception_handler(request: "Request", exc: Exception) -> "Response":
    """Handle generic exceptions.

    This is the catch-all handler for any exceptions not caught by
    more specific handlers.

    Args:
        request: The request that caused the exception.
        exc: The exception.

    Returns:
        Response with error details.
    """
    request_id = getattr(request.state, "request_id", None)
    settings = get_settings()

    logger.exception(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "error": str(exc),
            "error_type": type(exc).__name__,
        },
    )

    # In production, hide detailed error information
    if settings.is_production:
        message = "An unexpected error occurred"
        details = None
    else:
        message = f"An unexpected error occurred: {exc!s}"
        details = {"error_type": type(exc).__name__, "error": str(exc)}

    error_response = create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message=message,
        details=details,
        request_id=request_id,
        path=request.url.path,
    )

    return Response(
        content=error_response.model_dump(),
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


def create_exception_handlers() -> dict:
    """Create exception handlers mapping for Litestar.

    Returns:
        Dictionary mapping exception types to handler functions.

    Example:
        >>> from litestar import Litestar
        >>> from morado.middleware.error_handler import create_exception_handlers
        >>> app = Litestar(
        ...     route_handlers=[...],
        ...     exception_handlers=create_exception_handlers()
        ... )
    """
    return {
        ValidationException: validation_exception_handler,
        NotFoundException: not_found_exception_handler,
        NotAuthorizedException: not_authorized_exception_handler,
        PermissionDeniedException: permission_denied_exception_handler,
        HTTPException: http_exception_handler,
        InternalServerException: internal_server_exception_handler,
        Exception: generic_exception_handler,
    }
