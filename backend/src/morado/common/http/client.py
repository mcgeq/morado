"""Core HTTP client implementation.

This module provides the main HttpClient class that integrates all components
of the HTTP client wrapper: session management, retry logic, interceptors,
and response handling.
"""

import time
from typing import Any
from urllib.parse import urljoin

import requests
from requests import Session

from morado.common.http.config import HttpClientConfig
from morado.common.http.exceptions import (
    HttpConnectionError,
    HttpRequestError,
    HttpTimeoutError,
)
from morado.common.http.interceptor import InterceptorManager
from morado.common.http.response import HttpResponse
from morado.common.http.retry import RetryConfig, RetryHandler, RetryStrategy
from morado.common.http.session import SessionManager


class HttpClient:
    """Core HTTP client with integrated session management, retry, and interceptors.

    This class provides a unified interface for making HTTP requests with support for:
    - All standard HTTP methods (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
    - Session management with connection pooling
    - Automatic retry with configurable strategies
    - Request/response interceptors for custom logic
    - Timeout control at multiple levels
    - Request parameter merging and building

    Attributes:
        _session_manager: Manages HTTP sessions and connection pooling
        _session: The active HTTP session
        _retry_handler: Handles retry logic (if enabled)
        _interceptor_manager: Manages request/response interceptors
        _base_url: Base URL for all requests
        _default_timeout: Default timeout tuple (connect, read)
        _default_headers: Default headers for all requests
    """

    def __init__(
        self,
        session: Session | None = None,
        base_url: str | None = None,
        default_timeout: tuple[int, int] = (10, 30),
        default_headers: dict[str, str] | None = None,
        session_manager: SessionManager | None = None,
        retry_handler: RetryHandler | None = None,
        interceptor_manager: InterceptorManager | None = None,
    ):
        """Initialize the HTTP client.

        Args:
            session: Existing requests.Session to use. If None, creates a new session.
            base_url: Base URL for all requests. Request URLs will be joined with this.
            default_timeout: Default timeout as (connect_timeout, read_timeout) in seconds.
            default_headers: Default headers to include in all requests.
            session_manager: SessionManager instance. If None, creates a new one.
            retry_handler: RetryHandler instance for retry logic. If None, no retry.
            interceptor_manager: InterceptorManager instance. If None, creates a new one.
        """
        # Initialize session management
        self._session_manager = session_manager or SessionManager()
        self._session = session or self._session_manager.create_session()

        # Initialize retry handling
        self._retry_handler = retry_handler

        # Initialize interceptor management
        self._interceptor_manager = interceptor_manager or InterceptorManager()

        # Store configuration
        self._base_url = base_url
        self._default_timeout = default_timeout
        self._default_headers = default_headers or {}

    @property
    def interceptor_manager(self) -> InterceptorManager:
        """Get the interceptor manager for adding custom interceptors.

        Returns:
            The InterceptorManager instance used by this client

        Example:
            >>> from morado.common.http.client import HttpClient
            >>> from morado.common.http.tracing_interceptor import TracingInterceptor
            >>>
            >>> client = HttpClient()
            >>> client.interceptor_manager.add_request_interceptor(TracingInterceptor())
        """
        return self._interceptor_manager

    @classmethod
    def from_config(cls, config: HttpClientConfig) -> "HttpClient":
        """Create an HTTP client from a configuration object.

        Args:
            config: HttpClientConfig instance with all settings

        Returns:
            Configured HttpClient instance
        """
        # Create session manager
        session_manager = SessionManager(
            pool_connections=config.pool_connections,
            pool_maxsize=config.pool_maxsize,
            max_retries=0,  # Retry handled by RetryHandler
        )

        # Create retry handler if enabled
        retry_handler = None
        if config.enable_retry:
            retry_config = RetryConfig(
                max_retries=config.max_retries,
                strategy=RetryStrategy(config.retry_strategy),
                initial_delay=config.initial_delay,
                max_delay=config.max_delay,
            )
            retry_handler = RetryHandler(retry_config)

        # Create client
        return cls(
            base_url=config.base_url,
            default_timeout=(config.connect_timeout, config.read_timeout),
            session_manager=session_manager,
            retry_handler=retry_handler,
        )

    def _build_url(self, url: str) -> str:
        """Build the complete URL by joining with base_url if present.

        Args:
            url: Request URL (can be relative or absolute)

        Returns:
            Complete URL
        """
        if self._base_url:
            return urljoin(self._base_url, url)
        return url

    def _merge_headers(
        self,
        request_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Merge default headers with request-specific headers.

        Request headers take precedence over default headers.

        Args:
            request_headers: Headers specific to this request

        Returns:
            Merged headers dictionary
        """
        merged = self._default_headers.copy()
        if request_headers:
            merged.update(request_headers)
        return merged

    def _get_timeout(
        self,
        timeout: tuple[int, int] | None = None,
    ) -> tuple[int, int]:
        """Get the timeout to use for a request.

        Request-specific timeout takes precedence over default timeout.

        Args:
            timeout: Request-specific timeout (connect, read)

        Returns:
            Timeout tuple to use
        """
        return timeout if timeout is not None else self._default_timeout

    def _execute_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> HttpResponse:
        """Execute a single HTTP request (without retry logic).

        This is the core request execution method that:
        1. Processes request through interceptors
        2. Executes the HTTP request
        3. Processes response through interceptors
        4. Wraps the response in HttpResponse

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Request parameters (headers, params, data, json, files, timeout, etc.)

        Returns:
            HttpResponse object

        Raises:
            HttpConnectionError: On connection failures
            HttpTimeoutError: On timeout
            HttpRequestError: On HTTP errors (if raise_for_status is called)
        """
        # Extract headers from kwargs for interceptor processing
        headers = kwargs.pop("headers", {})

        # Process request through interceptors
        method, url, headers, kwargs = self._interceptor_manager.process_request(
            method, url, headers, **kwargs
        )

        # Put headers back in kwargs
        kwargs["headers"] = headers

        # Record start time
        start_time = time.time()

        try:
            # Execute the request
            response = self._session.request(method, url, **kwargs)

            # Calculate request time
            request_time = time.time() - start_time

            # Wrap response
            http_response = HttpResponse(response, request_time)

            # Process response through interceptors
            http_response = self._interceptor_manager.process_response(http_response)

            return http_response

        except requests.exceptions.ConnectTimeout as e:
            msg = f"Connection timeout for URL {url}"
            raise HttpTimeoutError(
                msg,
                timeout_type="connect",
            ) from e
        except requests.exceptions.ReadTimeout as e:
            msg = f"Read timeout for URL {url}"
            raise HttpTimeoutError(
                msg,
                timeout_type="read",
            ) from e
        except requests.exceptions.Timeout as e:
            msg = f"Timeout for URL {url}"
            raise HttpTimeoutError(
                msg,
                timeout_type="unknown",
            ) from e
        except requests.exceptions.ConnectionError as e:
            msg = f"Connection error for URL {url}: {e!s}"
            raise HttpConnectionError(msg) from e
        except requests.exceptions.RequestException as e:
            # Generic request exception
            msg = f"Request failed for URL {url}: {e!s}"
            raise HttpRequestError(msg) from e

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        data: Any | None = None,
        json: Any | None = None,
        files: dict[str, Any] | None = None,
        timeout: tuple[int, int] | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """Send an HTTP request.

        This is the main request method that:
        1. Builds the complete URL
        2. Merges headers
        3. Sets timeout
        4. Executes request with retry (if configured)

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
            url: Request URL (relative to base_url if set)
            params: Query parameters
            headers: Request headers
            data: Request body (form data)
            json: Request body (JSON data)
            files: Files to upload
            timeout: Timeout as (connect_timeout, read_timeout)
            **kwargs: Additional parameters passed to requests

        Returns:
            HttpResponse object

        Raises:
            HttpConnectionError: On connection failures
            HttpTimeoutError: On timeout
            HttpRequestError: On HTTP errors
            RetryExhaustedError: If retry attempts are exhausted
        """
        # Build complete URL
        full_url = self._build_url(url)

        # Merge headers
        merged_headers = self._merge_headers(headers)

        # Get timeout
        request_timeout = self._get_timeout(timeout)

        # Build request kwargs
        request_kwargs = {
            "headers": merged_headers,
            "timeout": request_timeout,
        }

        # Add optional parameters
        if params is not None:
            request_kwargs["params"] = params
        if data is not None:
            request_kwargs["data"] = data
        if json is not None:
            request_kwargs["json"] = json
        if files is not None:
            request_kwargs["files"] = files

        # Add any additional kwargs
        request_kwargs.update(kwargs)

        # Execute request with retry if configured
        if self._retry_handler:
            return self._retry_handler.execute_with_retry(
                self._execute_request,
                method,
                full_url,
                **request_kwargs,
            )
        else:
            return self._execute_request(method, full_url, **request_kwargs)

    def get(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a GET request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (params, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a POST request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (data, json, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a PUT request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (data, json, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a PATCH request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (data, json, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a DELETE request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (params, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a HEAD request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (params, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send an OPTIONS request.

        Args:
            url: Request URL
            **kwargs: Additional parameters (params, headers, timeout, etc.)

        Returns:
            HttpResponse object
        """
        return self.request("OPTIONS", url, **kwargs)

    def upload_file(
        self,
        url: str,
        file_path: str,
        file_field_name: str = "file",
        additional_fields: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """Upload a single file using multipart/form-data.

        This is a convenience method for uploading a single file. The file is
        automatically opened and sent as multipart/form-data.

        Args:
            url: Request URL
            file_path: Path to the file to upload
            file_field_name: Name of the form field for the file (default: "file")
            additional_fields: Additional form fields to include with the file
            **kwargs: Additional parameters (headers, timeout, etc.)

        Returns:
            HttpResponse object

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If the file cannot be read

        Example:
            >>> client = HttpClient()
            >>> response = client.upload_file(
            ...     "https://api.example.com/upload",
            ...     "/path/to/document.pdf",
            ...     file_field_name="document",
            ...     additional_fields={"description": "My document"}
            ... )
        """
        from pathlib import Path

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        # Open the file and prepare for upload
        with open(file_path, "rb") as f:
            files = {file_field_name: (file_path_obj.name, f, None)}

            # Add additional form fields if provided
            data = additional_fields if additional_fields else None

            return self.post(url, files=files, data=data, **kwargs)

    def upload_files(
        self,
        url: str,
        files: dict[str, str],
        additional_fields: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """Upload multiple files using multipart/form-data.

        This is a convenience method for uploading multiple files. All files are
        automatically opened and sent as multipart/form-data.

        Args:
            url: Request URL
            files: Dictionary mapping form field names to file paths
            additional_fields: Additional form fields to include with the files
            **kwargs: Additional parameters (headers, timeout, etc.)

        Returns:
            HttpResponse object

        Raises:
            FileNotFoundError: If any file does not exist
            IOError: If any file cannot be read

        Example:
            >>> client = HttpClient()
            >>> response = client.upload_files(
            ...     "https://api.example.com/upload",
            ...     files={
            ...         "document": "/path/to/document.pdf",
            ...         "image": "/path/to/image.png"
            ...     },
            ...     additional_fields={"description": "Multiple files"}
            ... )
        """
        from pathlib import Path

        # Prepare files for upload
        files_to_upload = {}

        try:
            # Open all files using context managers
            file_handles = []
            for field_name, file_path in files.items():
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    msg = f"File not found: {file_path}"
                    raise FileNotFoundError(msg)

                # Open file and keep handle for cleanup
                file_handle = open(file_path, "rb")  # noqa: SIM115
                file_handles.append(file_handle)

                files_to_upload[field_name] = (file_path_obj.name, file_handle, None)

            # Add additional form fields if provided
            data = additional_fields if additional_fields else None

            # Send the request
            return self.post(url, files=files_to_upload, data=data, **kwargs)

        finally:
            # Always close file handles
            for handle in file_handles:
                try:
                    handle.close()
                except Exception as e:
                    # Log the error but don't fail the request
                    self.logger.warning(
                        f"Failed to close file handle: {e}",
                        extra={"error": str(e), "error_type": type(e).__name__},
                    )

    def upload_multipart(
        self,
        url: str,
        files: dict[str, tuple[str, Any, str | None]] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """Upload files and form data using multipart/form-data with full control.

        This method provides the most flexibility for multipart uploads, allowing
        you to specify file names, content types, and mix files with form fields.

        Args:
            url: Request URL
            files: Dictionary mapping field names to tuples of (filename, file_object, content_type).
                   The file_object can be a file handle, bytes, or string.
                   The content_type is optional and will be auto-detected if None.
            data: Dictionary of additional form fields
            **kwargs: Additional parameters (headers, timeout, etc.)

        Returns:
            HttpResponse object

        Example:
            >>> client = HttpClient()
            >>> with open("/path/to/file.pdf", "rb") as f:
            ...     response = client.upload_multipart(
            ...         "https://api.example.com/upload",
            ...         files={
            ...             "document": ("report.pdf", f, "application/pdf"),
            ...             "thumbnail": ("thumb.png", image_bytes, "image/png")
            ...         },
            ...         data={"title": "My Report", "category": "finance"}
            ...     )
        """
        return self.post(url, files=files, data=data, **kwargs)

    def close(self) -> None:
        """Close the HTTP client and release resources.

        This closes the underlying session and cleans up connection pools.
        After calling this method, the client should not be used anymore.
        """
        if self._session:
            self._session_manager.close_session(self._session)

    def __enter__(self) -> "HttpClient":
        """Context manager entry.

        Returns:
            Self for use in with statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit.

        Ensures the client is properly closed when exiting the context.
        """
        self.close()
