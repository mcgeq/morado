"""HTTP Client Wrapper Module

This module provides a unified, reliable, and observable HTTP client for the Morado test platform.
It wraps the requests library and provides enterprise features like retry, timeout control,
logging, and request tracing.

Quick Start
-----------

Basic usage with default configuration:

    >>> from morado.common.http import create_default_client
    >>>
    >>> client = create_default_client()
    >>> response = client.get("https://api.example.com/users")
    >>> print(response.json())

Custom configuration:

    >>> from morado.common.http import create_http_client, HttpClientConfig
    >>>
    >>> config = HttpClientConfig(
    ...     base_url="https://api.example.com",
    ...     connect_timeout=15,
    ...     max_retries=5
    ... )
    >>> client = create_http_client(config)
    >>> response = client.get("/users")

With logging and tracing:

    >>> from morado.common.http import create_default_client
    >>>
    >>> client = create_default_client(
    ...     enable_logging=True,
    ...     enable_tracing=True
    ... )
    >>> response = client.post("/users", json={"name": "John"})

File upload:

    >>> client = create_default_client()
    >>> response = client.upload_file(
    ...     "https://api.example.com/upload",
    ...     "/path/to/file.pdf"
    ... )

Context manager for automatic cleanup:

    >>> from morado.common.http import create_default_client
    >>>
    >>> with create_default_client() as client:
    ...     response = client.get("https://api.example.com/users")
    ...     print(response.json())
"""

# Core client
from morado.common.http.client import HttpClient

# Import currently implemented modules
from morado.common.http.config import HttpClientConfig
from morado.common.http.exceptions import (
    HttpClientError,
    HttpConnectionError,
    HttpRequestError,
    HttpTimeoutError,
    JSONPathError,
    RetryExhaustedError,
    VariableResolutionError,
)

# Interceptors
from morado.common.http.interceptor import (
    InterceptorManager,
    RequestInterceptor,
    ResponseInterceptor,
)
from morado.common.http.logging_interceptor import (
    ErrorLoggingInterceptor,
    LoggingInterceptor,
)
from morado.common.http.response import HttpResponse
from morado.common.http.retry import RetryConfig, RetryHandler, RetryStrategy
from morado.common.http.session import SessionManager
from morado.common.http.tracing_interceptor import TracingInterceptor
from morado.common.http.utils import (
    build_url,
    encode_query_params,
    mask_sensitive_data,
    mask_sensitive_headers,
    resolve_variables,
    serialize_body,
    truncate_for_logging,
)

# Factory Functions
# -----------------


def create_http_client(
    config: HttpClientConfig | None = None,
    enable_logging: bool = True,
    enable_tracing: bool = True,
    enable_error_logging: bool = True,
) -> HttpClient:
    """Create an HTTP client with the specified configuration.

    This is the main factory function for creating HTTP clients. It handles
    the creation and configuration of all components (session manager, retry
    handler, interceptors) based on the provided configuration.

    Args:
        config: HTTP client configuration. If None, uses default configuration.
        enable_logging: Whether to enable request/response logging (default: True)
        enable_tracing: Whether to enable request tracing (default: True)
        enable_error_logging: Whether to enable error logging (default: True)

    Returns:
        Configured HttpClient instance

    Example:
        >>> from morado.common.http import create_http_client, HttpClientConfig
        >>>
        >>> # Create with custom configuration
        >>> config = HttpClientConfig(
        ...     base_url="https://api.example.com",
        ...     connect_timeout=15,
        ...     read_timeout=60,
        ...     max_retries=5,
        ...     retry_strategy="exponential"
        ... )
        >>> client = create_http_client(config)
        >>>
        >>> # Create with default configuration
        >>> client = create_http_client()
        >>>
        >>> # Create without logging
        >>> client = create_http_client(enable_logging=False)
    """
    # Use default config if none provided
    if config is None:
        config = HttpClientConfig()

    # Create the client from config
    client = HttpClient.from_config(config)

    # Add interceptors based on configuration
    if enable_tracing and config.enable_tracing:
        client.interceptor_manager.add_request_interceptor(TracingInterceptor())

    if enable_logging and config.enable_logging:
        client.interceptor_manager.add_request_interceptor(
            LoggingInterceptor(config=config)
        )

        if enable_error_logging:
            client.interceptor_manager.add_response_interceptor(
                ErrorLoggingInterceptor()
            )

    return client


def create_default_client(
    base_url: str | None = None,
    enable_logging: bool = True,
    enable_tracing: bool = True,
    enable_retry: bool = True,
) -> HttpClient:
    """Create an HTTP client with sensible defaults.

    This is a convenience function for quickly creating an HTTP client with
    default settings. It's ideal for simple use cases where you don't need
    fine-grained control over the configuration.

    Args:
        base_url: Base URL for all requests (optional)
        enable_logging: Whether to enable request/response logging (default: True)
        enable_tracing: Whether to enable request tracing (default: True)
        enable_retry: Whether to enable automatic retry (default: True)

    Returns:
        Configured HttpClient instance with default settings

    Example:
        >>> from morado.common.http import create_default_client
        >>>
        >>> # Simple client with defaults
        >>> client = create_default_client()
        >>> response = client.get("https://api.example.com/users")
        >>>
        >>> # Client with base URL
        >>> client = create_default_client(base_url="https://api.example.com")
        >>> response = client.get("/users")  # Relative URL
        >>>
        >>> # Client without retry
        >>> client = create_default_client(enable_retry=False)
    """
    config = HttpClientConfig(
        base_url=base_url,
        enable_retry=enable_retry,
        enable_logging=enable_logging,
        enable_tracing=enable_tracing,
    )

    return create_http_client(
        config=config,
        enable_logging=enable_logging,
        enable_tracing=enable_tracing,
    )


def load_config_from_dict(config_dict: dict) -> HttpClientConfig:
    """Load HTTP client configuration from a dictionary.

    This function creates an HttpClientConfig instance from a dictionary,
    which is useful when loading configuration from JSON, YAML, or other
    sources.

    Args:
        config_dict: Dictionary containing configuration values

    Returns:
        HttpClientConfig instance

    Raises:
        ValidationError: If the configuration values are invalid

    Example:
        >>> from morado.common.http import load_config_from_dict, create_http_client
        >>>
        >>> config_dict = {
        ...     "base_url": "https://api.example.com",
        ...     "connect_timeout": 15,
        ...     "read_timeout": 60,
        ...     "max_retries": 5,
        ...     "retry_strategy": "exponential"
        ... }
        >>> config = load_config_from_dict(config_dict)
        >>> client = create_http_client(config)
    """
    return HttpClientConfig(**config_dict)


def load_config_from_toml(filepath: str) -> HttpClientConfig:
    """Load HTTP client configuration from a TOML file.

    This function reads a TOML configuration file and creates an
    HttpClientConfig instance from it.

    Args:
        filepath: Path to the TOML configuration file

    Returns:
        HttpClientConfig instance

    Raises:
        FileNotFoundError: If the file does not exist
        ValidationError: If the configuration values are invalid
        ImportError: If tomllib/tomli is not available

    Example:
        >>> from morado.common.http import load_config_from_toml, create_http_client
        >>>
        >>> # Load from TOML file
        >>> config = load_config_from_toml("config/http_client.toml")
        >>> client = create_http_client(config)

    Example TOML file:

        [http_client]
        base_url = "https://api.example.com"
        connect_timeout = 15
        read_timeout = 60
        max_retries = 5
        retry_strategy = "exponential"
        enable_logging = true
        enable_tracing = true
    """
    from pathlib import Path

    # Try to import tomllib (Python 3.11+) or tomli (fallback)
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[import-not-found]
        except ImportError:
            raise ImportError(
                "TOML support requires Python 3.11+ or the 'tomli' package. "
                "Install with: pip install tomli"
            ) from None

    config_path = Path(filepath)
    if not config_path.exists():
        msg = f"Configuration file not found: {filepath}"
        raise FileNotFoundError(msg)

    with open(config_path, "rb") as f:
        config_data = tomllib.load(f)

    # Support both flat structure and nested under "http_client" key
    if "http_client" in config_data:
        config_data = config_data["http_client"]

    return HttpClientConfig(**config_data)


__all__ = [
    "ErrorLoggingInterceptor",
    # Core Client
    "HttpClient",
    # Configuration
    "HttpClientConfig",
    # Exceptions
    "HttpClientError",
    "HttpConnectionError",
    "HttpRequestError",
    # Response
    "HttpResponse",
    "HttpTimeoutError",
    "InterceptorManager",
    "JSONPathError",
    "LoggingInterceptor",
    # Interceptor
    "RequestInterceptor",
    "ResponseInterceptor",
    # Retry
    "RetryConfig",
    "RetryExhaustedError",
    "RetryHandler",
    "RetryStrategy",
    # Session
    "SessionManager",
    "TracingInterceptor",
    "VariableResolutionError",
    "build_url",
    "create_default_client",
    # Factory Functions
    "create_http_client",
    "encode_query_params",
    "load_config_from_dict",
    "load_config_from_toml",
    "mask_sensitive_data",
    "mask_sensitive_headers",
    # Utils
    "resolve_variables",
    "serialize_body",
    "truncate_for_logging",
]
