"""Custom exceptions for HTTP client wrapper.

This module defines all custom exceptions used by the HTTP client wrapper.
"""



class HttpClientError(Exception):
    """Base exception for all HTTP client errors.

    All custom exceptions in the HTTP client wrapper inherit from this class.
    """



class HttpRequestError(HttpClientError):
    """Exception raised when an HTTP request fails.

    This exception is raised for HTTP errors (4xx, 5xx status codes).

    Attributes:
        status_code: The HTTP status code
        response: The response object (if available)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: any | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class HttpTimeoutError(HttpClientError):
    """Exception raised when an HTTP request times out.

    Attributes:
        timeout_type: Type of timeout ('connect' or 'read')
    """

    def __init__(self, message: str, timeout_type: str = "unknown"):
        super().__init__(message)
        self.timeout_type = timeout_type


class HttpConnectionError(HttpClientError):
    """Exception raised when an HTTP connection fails.

    This exception is raised for network-level errors like DNS resolution
    failures, connection refused, etc.
    """



class RetryExhaustedError(HttpClientError):
    """Exception raised when retry attempts are exhausted.

    Attributes:
        retry_history: List of dictionaries containing retry attempt details
    """

    def __init__(self, message: str, retry_history: list[dict]):
        super().__init__(message)
        self.retry_history = retry_history


class JSONPathError(HttpClientError):
    """Exception raised when JSONPath extraction fails.

    Attributes:
        path: The JSONPath expression that failed
    """

    def __init__(self, message: str, path: str | None = None):
        super().__init__(message)
        self.path = path


class VariableResolutionError(HttpClientError):
    """Exception raised when variable resolution fails.

    Attributes:
        missing_vars: List of variable names that could not be resolved
    """

    def __init__(self, message: str, missing_vars: list[str] | None = None):
        super().__init__(message)
        self.missing_vars = missing_vars or []
