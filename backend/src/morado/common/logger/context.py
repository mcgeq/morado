"""Request context management for distributed tracing.

This module provides context management for tracking requests across
the entire call chain, from HTTP entry point through services to database.
"""

import contextvars
from typing import Any

# Context variable to store request ID across async calls
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

# Context variable to store additional context data
# Note: ContextVar doesn't support default_factory, so we use None as default
context_data_var: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    "context_data", default=None
)


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context.

    This should be called by the middleware when a request enters the system.

    Args:
        request_id: The request ID to set

    Example:
        >>> set_request_id("REQ-abc123")
    """
    request_id_var.set(request_id)


def get_request_id() -> str | None:
    """Get the request ID from the current context.

    Returns:
        The request ID if set, None otherwise

    Example:
        >>> request_id = get_request_id()
        >>> if request_id:
        ...     logger.info("Processing", extra={"request_id": request_id})
    """
    return request_id_var.get()


def set_context_data(key: str, value: Any) -> None:
    """Set additional context data for the current request.

    Args:
        key: The context key
        value: The context value

    Example:
        >>> set_context_data("user_id", 123)
        >>> set_context_data("operation", "create_order")
    """
    data = context_data_var.get()
    if data is None:
        data = {}
    data[key] = value
    context_data_var.set(data)


def get_context_data(key: str | None = None) -> Any:
    """Get context data for the current request.

    Args:
        key: The context key to retrieve. If None, returns all context data.

    Returns:
        The context value if key is provided, or all context data if key is None

    Example:
        >>> user_id = get_context_data("user_id")
        >>> all_data = get_context_data()
    """
    data = context_data_var.get()
    if data is None:
        return {} if key is None else None
    if key is None:
        return data
    return data.get(key)


def clear_context() -> None:
    """Clear all context data.

    This is typically called at the end of a request.

    Example:
        >>> clear_context()
    """
    request_id_var.set(None)
    context_data_var.set(None)


def get_log_context() -> dict[str, Any]:
    """Get all context data for logging.

    Returns a dictionary containing the request ID and all context data,
    suitable for use in log extra fields.

    Returns:
        Dictionary with request_id and all context data

    Example:
        >>> logger.info("Operation completed", extra=get_log_context())
    """
    context = {}

    request_id = get_request_id()
    if request_id:
        context["request_id"] = request_id

    context_data = get_context_data()
    if context_data:
        context.update(context_data)

    return context
