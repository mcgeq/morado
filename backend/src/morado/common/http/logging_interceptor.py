"""Logging interceptor for HTTP client.

This module provides logging interceptors that integrate with the structlog
logging system to record HTTP requests, responses, and errors.
"""

import traceback
from typing import Any

from morado.common.http.config import HttpClientConfig
from morado.common.http.interceptor import RequestInterceptor, ResponseInterceptor
from morado.common.http.response import HttpResponse
from morado.common.http.utils import (
    mask_sensitive_data,
    mask_sensitive_headers,
    truncate_for_logging,
)
from morado.common.logger.logger import get_logger


class LoggingInterceptor(RequestInterceptor, ResponseInterceptor):
    """Logging interceptor for HTTP requests and responses.

    This interceptor logs HTTP requests before they are sent and responses
    after they are received. It integrates with the structlog logging system
    and supports:
    - Request logging (method, URL, headers, body, parameters)
    - Response logging (status code, headers, body, duration)
    - Error logging (exception type, message, stack trace)
    - Sensitive information masking
    - Log size limiting

    Attributes:
        _logger: Structlog logger instance
        _config: HTTP client configuration
        _log_request_body: Whether to log request body
        _log_response_body: Whether to log response body
        _max_log_body_size: Maximum size of body to log
    """

    def __init__(
        self,
        config: HttpClientConfig | None = None,
        logger_name: str | None = None,
    ):
        """Initialize the logging interceptor.

        Args:
            config: HTTP client configuration (uses defaults if None)
            logger_name: Logger name (defaults to module name)
        """
        self._logger = get_logger(logger_name or __name__)

        # Use config or defaults
        if config is None:
            config = HttpClientConfig()

        self._config = config
        self._log_request_body = config.log_request_body
        self._log_response_body = config.log_response_body
        self._max_log_body_size = config.max_log_body_size

    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Log HTTP request before it is sent.

        Logs the request method, URL, headers, query parameters, and body.
        Sensitive information is masked and large bodies are truncated.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            **kwargs: Additional request parameters (params, data, json, files, etc.)

        Returns:
            Unmodified request parameters (method, url, headers, kwargs)
        """
        # Build log context
        log_context = {
            "http_method": method,
            "http_url": url,
        }

        # Add masked headers
        if headers:
            masked_headers = mask_sensitive_headers(headers)
            log_context["http_headers"] = masked_headers

        # Add query parameters
        if kwargs.get("params"):
            log_context["http_params"] = kwargs["params"]

        # Add request body if enabled
        if self._log_request_body:
            body = self._extract_request_body(kwargs)
            if body is not None:
                # Mask sensitive data
                masked_body = mask_sensitive_data(body)
                # Truncate for logging
                truncated_body = truncate_for_logging(
                    masked_body,
                    max_size=self._max_log_body_size
                )
                log_context["http_request_body"] = truncated_body

        # Add timeout if specified
        if kwargs.get("timeout"):
            log_context["http_timeout"] = kwargs["timeout"]

        # Log the request
        self._logger.info(
            "HTTP request",
            **log_context
        )

        # Return unmodified parameters
        return method, url, headers, kwargs

    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Log HTTP response after it is received.

        Logs the response status code, headers, body, and duration.
        Sensitive information is masked and large bodies are truncated.

        Args:
            response: The HTTP response object

        Returns:
            Unmodified response object
        """
        # Build log context
        log_context = {
            "http_status_code": response.status_code,
            "http_duration": response.request_time,
        }

        # Add masked headers
        if response.headers:
            masked_headers = mask_sensitive_headers(response.headers)
            log_context["http_response_headers"] = masked_headers

        # Add response body if enabled
        if self._log_response_body:
            body = self._extract_response_body(response)
            if body is not None:
                # Mask sensitive data
                masked_body = mask_sensitive_data(body)
                # Truncate for logging
                truncated_body = truncate_for_logging(
                    masked_body,
                    max_size=self._max_log_body_size
                )
                log_context["http_response_body"] = truncated_body

        # Determine log level based on status code
        if response.is_success():
            self._logger.info(
                "HTTP response",
                **log_context
            )
        else:
            self._logger.warning(
                "HTTP response with error status",
                **log_context
            )

        # Return unmodified response
        return response

    def log_error(
        self,
        exception: Exception,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> None:
        """Log HTTP request error.

        This method should be called when an HTTP request fails with an exception.
        It logs the exception type, message, and stack trace.

        Args:
            exception: The exception that occurred
            method: HTTP method that was attempted
            url: URL that was requested
            **kwargs: Additional context (headers, params, etc.)
        """
        # Build log context
        log_context = {
            "http_method": method,
            "http_url": url,
            "error_type": type(exception).__name__,
            "error_message": str(exception),
        }

        # Add stack trace
        stack_trace = "".join(traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__
        ))
        log_context["error_stack_trace"] = stack_trace

        # Add request context if available
        if kwargs.get("headers"):
            masked_headers = mask_sensitive_headers(kwargs["headers"])
            log_context["http_headers"] = masked_headers

        if kwargs.get("params"):
            log_context["http_params"] = kwargs["params"]

        # Log the error
        self._logger.error(
            "HTTP request failed",
            **log_context
        )

    def _extract_request_body(self, kwargs: dict[str, Any]) -> Any:
        """Extract request body from kwargs.

        Args:
            kwargs: Request parameters

        Returns:
            Request body (data, json, or files) or None
        """
        # Check for JSON body
        if "json" in kwargs and kwargs["json"] is not None:
            return kwargs["json"]

        # Check for form data
        if "data" in kwargs and kwargs["data"] is not None:
            return kwargs["data"]

        # Check for files (don't log file content, just metadata)
        if "files" in kwargs and kwargs["files"] is not None:
            files = kwargs["files"]
            if isinstance(files, dict):
                return {
                    "files": list(files.keys()),
                    "file_count": len(files)
                }
            return {"files": "present"}

        return None

    def _extract_response_body(self, response: HttpResponse) -> Any:
        """Extract response body for logging.

        Args:
            response: HTTP response object

        Returns:
            Response body (parsed JSON if possible, otherwise text)
        """
        # Try to parse as JSON first
        try:
            return response.json()
        except Exception:
            # If not JSON, return text (but limit size)
            return response.text


class ErrorLoggingInterceptor(ResponseInterceptor):
    """Specialized interceptor for logging HTTP errors.

    This interceptor focuses on logging error responses (4xx and 5xx status codes)
    with detailed information for debugging.

    Attributes:
        _logger: Structlog logger instance
    """

    def __init__(self, logger_name: str | None = None):
        """Initialize the error logging interceptor.

        Args:
            logger_name: Logger name (defaults to module name)
        """
        self._logger = get_logger(logger_name or __name__)

    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Log error responses with detailed information.

        Args:
            response: The HTTP response object

        Returns:
            Unmodified response object
        """
        # Only log if it's an error response
        if not response.is_success():
            log_context = {
                "http_status_code": response.status_code,
                "http_duration": response.request_time,
            }

            # Try to extract error details from response
            try:
                body = response.json()
                if isinstance(body, dict):
                    # Look for common error fields
                    if "error" in body:
                        log_context["error_details"] = body["error"]
                    if "message" in body:
                        log_context["error_message"] = body["message"]
                    if "code" in body:
                        log_context["error_code"] = body["code"]
            except Exception:
                # If not JSON, just log the text
                log_context["error_body"] = response.text[:500]  # Limit size

            # Log based on error type
            if 400 <= response.status_code < 500:
                self._logger.warning(
                    "HTTP client error (4xx)",
                    **log_context
                )
            else:  # 5xx
                self._logger.error(
                    "HTTP server error (5xx)",
                    **log_context
                )

        return response
