"""Context management for request-scoped logging.

This module provides thread-safe and async-safe context variable management
for tracking request_id, user_id, trace_id, and other contextual information
across the logging system.
"""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from morado.common.utils.uuid import UUIDConfig


# Context variables for request-scoped data
_request_id_var: ContextVar[str | None] = ContextVar('request_id', default=None)
_user_id_var: ContextVar[int | None] = ContextVar('user_id', default=None)
_trace_id_var: ContextVar[str | None] = ContextVar('trace_id', default=None)


@dataclass
class RequestContext:
    """Request context data for logging.

    Contains standard context fields (request_id, user_id, trace_id) and
    supports additional custom fields.
    """
    request_id: str | None = None
    user_id: int | None = None
    trace_id: str | None = None
    additional: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for logging.

        Returns:
            Dictionary containing all non-None context values
        """
        result = {}

        if self.request_id is not None:
            result['request_id'] = self.request_id
        if self.user_id is not None:
            result['user_id'] = self.user_id
        if self.trace_id is not None:
            result['trace_id'] = self.trace_id

        # Add additional fields
        result.update(self.additional)

        return result


class ContextManager:
    """Manages logging context variables.

    Provides thread-safe and async-safe access to context variables
    using Python's contextvars module.
    """

    @staticmethod
    def get_request_id() -> str | None:
        """Get current request ID from context.

        Returns:
            Current request ID or None if not set
        """
        return _request_id_var.get()

    @staticmethod
    def set_request_id(request_id: str) -> Token:
        """Set current request ID in context.

        Args:
            request_id: Request ID to set

        Returns:
            Token that can be used to reset the value
        """
        return _request_id_var.set(request_id)

    @staticmethod
    def get_user_id() -> int | None:
        """Get current user ID from context.

        Returns:
            Current user ID or None if not set
        """
        return _user_id_var.get()

    @staticmethod
    def set_user_id(user_id: int) -> Token:
        """Set current user ID in context.

        Args:
            user_id: User ID to set

        Returns:
            Token that can be used to reset the value
        """
        return _user_id_var.set(user_id)

    @staticmethod
    def get_trace_id() -> str | None:
        """Get current trace ID from context.

        Returns:
            Current trace ID or None if not set
        """
        return _trace_id_var.get()

    @staticmethod
    def set_trace_id(trace_id: str) -> Token:
        """Set current trace ID in context.

        Args:
            trace_id: Trace ID to set

        Returns:
            Token that can be used to reset the value
        """
        return _trace_id_var.set(trace_id)

    @staticmethod
    def get_all_context() -> dict[str, Any]:
        """Get all context variables as dictionary.

        Returns:
            Dictionary containing all non-None context values
        """
        result = {}

        request_id = _request_id_var.get()
        if request_id is not None:
            result['request_id'] = request_id

        user_id = _user_id_var.get()
        if user_id is not None:
            result['user_id'] = user_id

        trace_id = _trace_id_var.get()
        if trace_id is not None:
            result['trace_id'] = trace_id

        return result

    @staticmethod
    def clear_context() -> None:
        """Clear all context variables.

        Sets all context variables back to None.
        """
        _request_id_var.set(None)
        _user_id_var.set(None)
        _trace_id_var.set(None)


@contextmanager
def request_scope(
    request_id: str | None = None,
    user_id: int | None = None,
    trace_id: str | None = None,
    request_id_config: Optional['UUIDConfig'] = None,
    **additional_context: Any
) -> Generator[dict[str, Any]]:
    """Context manager for request-scoped logging.

    Sets context variables for the duration of the context and restores
    previous values on exit. Auto-generates request_id if not provided.

    Args:
        request_id: Optional request ID (auto-generated if None)
        user_id: Optional user ID
        trace_id: Optional trace ID
        request_id_config: Optional UUID configuration for auto-generation
        **additional_context: Additional context fields (for future use)

    Yields:
        Dictionary containing all context values

    Example:
        with request_scope(request_id="REQ123", user_id=42) as ctx:
            logger.info("Processing request", ctx=ctx)
    """
    # Store previous values
    prev_request_id = _request_id_var.get()
    prev_user_id = _user_id_var.get()
    prev_trace_id = _trace_id_var.get()

    # Auto-generate request_id if not provided
    if request_id is None:
        # Import here to avoid circular dependency
        from morado.common.utils.uuid import UUIDConfig, UUIDGenerator

        # Use provided config or default to alphanumeric with length 38
        if request_id_config is None:
            request_id_config = UUIDConfig(format="alphanumeric", length=38)

        request_id = UUIDGenerator.generate(request_id_config)

    # Set new values
    tokens = []
    if request_id is not None:
        tokens.append(_request_id_var.set(request_id))
    if user_id is not None:
        tokens.append(_user_id_var.set(user_id))
    if trace_id is not None:
        tokens.append(_trace_id_var.set(trace_id))

    # Build context dict
    context = RequestContext(
        request_id=request_id,
        user_id=user_id,
        trace_id=trace_id,
        additional=additional_context
    )

    try:
        yield context.to_dict()
    finally:
        # Restore previous values
        _request_id_var.set(prev_request_id)
        _user_id_var.set(prev_user_id)
        _trace_id_var.set(prev_trace_id)


@asynccontextmanager
async def async_request_scope(
    request_id: str | None = None,
    user_id: int | None = None,
    trace_id: str | None = None,
    request_id_config: Optional['UUIDConfig'] = None,
    **additional_context: Any
) -> AsyncGenerator[dict[str, Any]]:
    """Async context manager for request-scoped logging.

    Async version of request_scope. Sets context variables for the duration
    of the context and restores previous values on exit. Auto-generates
    request_id if not provided.

    Args:
        request_id: Optional request ID (auto-generated if None)
        user_id: Optional user ID
        trace_id: Optional trace ID
        request_id_config: Optional UUID configuration for auto-generation
        **additional_context: Additional context fields (for future use)

    Yields:
        Dictionary containing all context values

    Example:
        async with async_request_scope(request_id="REQ123", user_id=42) as ctx:
            logger.info("Processing async request", ctx=ctx)
    """
    # Store previous values
    prev_request_id = _request_id_var.get()
    prev_user_id = _user_id_var.get()
    prev_trace_id = _trace_id_var.get()

    # Auto-generate request_id if not provided
    if request_id is None:
        # Import here to avoid circular dependency
        from morado.common.utils.uuid import UUIDConfig, UUIDGenerator

        # Use provided config or default to alphanumeric with length 38
        if request_id_config is None:
            request_id_config = UUIDConfig(format="alphanumeric", length=38)

        request_id = UUIDGenerator.generate(request_id_config)

    # Set new values
    tokens = []
    if request_id is not None:
        tokens.append(_request_id_var.set(request_id))
    if user_id is not None:
        tokens.append(_user_id_var.set(user_id))
    if trace_id is not None:
        tokens.append(_trace_id_var.set(trace_id))

    # Build context dict
    context = RequestContext(
        request_id=request_id,
        user_id=user_id,
        trace_id=trace_id,
        additional=additional_context
    )

    try:
        yield context.to_dict()
    finally:
        # Restore previous values
        _request_id_var.set(prev_request_id)
        _user_id_var.set(prev_user_id)
        _trace_id_var.set(prev_trace_id)
