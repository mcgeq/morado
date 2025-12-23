"""Tracing interceptor for HTTP client.

This module provides a request interceptor that integrates with the execution context
to propagate tracing information (request_id, user_id) across HTTP requests.

The tracing interceptor automatically:
- Retrieves request_id and user_id from the current execution context
- Adds X-Request-ID header to outgoing HTTP requests
- Supports custom trace header names via configuration
"""

from typing import Any

from morado.common.http.interceptor import RequestInterceptor
from morado.common.logger.context import get_context_data, get_request_id


class TracingInterceptor(RequestInterceptor):
    """Request interceptor for distributed tracing.

    This interceptor integrates with the execution context to propagate
    tracing information across HTTP requests. It automatically adds
    tracing headers to outgoing requests based on the current context.

    The interceptor retrieves:
    - request_id: From the context variable (set by middleware or execution engine)
    - user_id: From the context data (set by authentication or execution engine)

    And adds them as HTTP headers:
    - X-Request-ID: The request ID for distributed tracing
    - X-User-ID: The user ID (optional, only if present in context)

    Example:
        >>> from morado.common.http.client import HttpClient
        >>> from morado.common.http.tracing_interceptor import TracingInterceptor
        >>> from morado.common.logger.context import set_request_id, set_context_data
        >>>
        >>> # Set up context
        >>> set_request_id("REQ-12345")
        >>> set_context_data("user_id", 42)
        >>>
        >>> # Create client with tracing
        >>> client = HttpClient()
        >>> client.interceptor_manager.add_request_interceptor(TracingInterceptor())
        >>>
        >>> # Make request - headers will be added automatically
        >>> response = client.get("https://api.example.com/users")
        >>> # Request will include:
        >>> # X-Request-ID: REQ-12345
        >>> # X-User-ID: 42
    """

    def __init__(
        self,
        trace_header_name: str = "X-Request-ID",
        user_header_name: str = "X-User-ID",
        include_user_id: bool = True,
    ):
        """Initialize the tracing interceptor.

        Args:
            trace_header_name: Name of the header for request ID (default: X-Request-ID)
            user_header_name: Name of the header for user ID (default: X-User-ID)
            include_user_id: Whether to include user ID in headers (default: True)

        Example:
            >>> # Use default header names
            >>> interceptor = TracingInterceptor()
            >>>
            >>> # Use custom header names
            >>> interceptor = TracingInterceptor(
            ...     trace_header_name="X-Trace-ID",
            ...     user_header_name="X-User"
            ... )
            >>>
            >>> # Disable user ID propagation
            >>> interceptor = TracingInterceptor(include_user_id=False)
        """
        self.trace_header_name = trace_header_name
        self.user_header_name = user_header_name
        self.include_user_id = include_user_id

    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Add tracing headers to the request before it is sent.

        This method is called before each HTTP request. It retrieves the
        request_id and user_id from the current execution context and adds
        them as headers to the outgoing request.

        If the headers already contain tracing information, they are not
        overwritten (existing headers take precedence).

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers dictionary
            **kwargs: Additional request parameters

        Returns:
            A tuple of (method, url, headers, kwargs) with tracing headers added.

        Example:
            >>> from morado.common.logger.context import set_request_id
            >>> set_request_id("REQ-abc123")
            >>>
            >>> interceptor = TracingInterceptor()
            >>> method, url, headers, kwargs = interceptor.before_request(
            ...     "GET",
            ...     "https://api.example.com",
            ...     {},
            ...     params={"key": "value"}
            ... )
            >>> headers["X-Request-ID"]
            'REQ-abc123'
        """
        # Create a copy of headers to avoid modifying the original
        modified_headers = headers.copy()

        # Get request ID from context
        request_id = get_request_id()
        if request_id and self.trace_header_name not in modified_headers:
            modified_headers[self.trace_header_name] = request_id

        # Get user ID from context data (if enabled)
        if self.include_user_id:
            user_id = get_context_data("user_id")
            if user_id is not None and self.user_header_name not in modified_headers:
                # Convert user_id to string for header value
                modified_headers[self.user_header_name] = str(user_id)

        return method, url, modified_headers, kwargs
