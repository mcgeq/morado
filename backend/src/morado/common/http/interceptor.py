"""Interceptor mechanism for HTTP client.

This module provides request and response interceptors that allow custom logic
to be executed before requests are sent and after responses are received.
Interceptors can modify requests, responses, or perform side effects like logging.
"""

from abc import ABC, abstractmethod
from typing import Any

from morado.common.http.response import HttpResponse


class RequestInterceptor(ABC):
    """Abstract base class for request interceptors.

    Request interceptors are called before an HTTP request is sent.
    They can modify the request parameters (method, URL, headers, etc.)
    or perform side effects like logging or adding authentication.

    Subclasses must implement the before_request method.
    """

    @abstractmethod
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Hook called before sending an HTTP request.

        This method is called before the request is sent, allowing the interceptor
        to modify the request parameters or perform side effects.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers dictionary
            **kwargs: Additional request parameters (params, data, json, files, timeout, etc.)

        Returns:
            A tuple of (method, url, headers, kwargs) with potentially modified values.
            The returned values will be used for the actual HTTP request.

        Example:
            def before_request(self, method, url, headers, **kwargs):
                # Add authentication header
                headers['Authorization'] = 'Bearer token123'
                return method, url, headers, kwargs
        """


class ResponseInterceptor(ABC):
    """Abstract base class for response interceptors.

    Response interceptors are called after an HTTP response is received.
    They can modify the response object or perform side effects like logging
    or validation.

    Subclasses must implement the after_response method.
    """

    @abstractmethod
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Hook called after receiving an HTTP response.

        This method is called after the response is received, allowing the interceptor
        to modify the response object or perform side effects.

        Args:
            response: The HTTP response object

        Returns:
            The response object (potentially modified). The returned response
            will be passed to the next interceptor or returned to the caller.

        Raises:
            Any exception raised by this method will be propagated to the caller.

        Example:
            def after_response(self, response):
                # Log response status
                logger.info(f"Response status: {response.status_code}")
                return response
        """


class InterceptorManager:
    """Manager for request and response interceptors.

    The InterceptorManager maintains lists of request and response interceptors
    and provides methods to register interceptors and process them in order.

    Interceptors are executed in the order they are registered:
    - Request interceptors: first registered -> last registered
    - Response interceptors: first registered -> last registered

    Attributes:
        _request_interceptors: List of registered request interceptors
        _response_interceptors: List of registered response interceptors
    """

    def __init__(self):
        """Initialize the interceptor manager with empty interceptor lists."""
        self._request_interceptors: list[RequestInterceptor] = []
        self._response_interceptors: list[ResponseInterceptor] = []

    def add_request_interceptor(self, interceptor: RequestInterceptor) -> None:
        """Register a request interceptor.

        The interceptor will be added to the end of the request interceptor list
        and will be executed in registration order.

        Args:
            interceptor: The request interceptor to register

        Example:
            manager = InterceptorManager()
            manager.add_request_interceptor(AuthInterceptor())
            manager.add_request_interceptor(LoggingInterceptor())
        """
        self._request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: ResponseInterceptor) -> None:
        """Register a response interceptor.

        The interceptor will be added to the end of the response interceptor list
        and will be executed in registration order.

        Args:
            interceptor: The response interceptor to register

        Example:
            manager = InterceptorManager()
            manager.add_response_interceptor(LoggingInterceptor())
            manager.add_response_interceptor(ValidationInterceptor())
        """
        self._response_interceptors.append(interceptor)

    def process_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Process the request through all registered request interceptors.

        Executes all registered request interceptors in order, passing the output
        of each interceptor as input to the next one. This creates a chain where
        each interceptor can modify the request parameters.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers dictionary
            **kwargs: Additional request parameters

        Returns:
            A tuple of (method, url, headers, kwargs) after processing through
            all interceptors.

        Example:
            method, url, headers, kwargs = manager.process_request(
                'GET', 'https://api.example.com', {}, params={'key': 'value'}
            )
        """
        # Start with the original request parameters
        current_method = method
        current_url = url
        current_headers = headers.copy()  # Copy to avoid modifying original
        current_kwargs = kwargs.copy()  # Copy to avoid modifying original

        # Process through each request interceptor in order
        for interceptor in self._request_interceptors:
            current_method, current_url, current_headers, current_kwargs = (
                interceptor.before_request(
                    current_method,
                    current_url,
                    current_headers,
                    **current_kwargs,
                )
            )

        return current_method, current_url, current_headers, current_kwargs

    def process_response(self, response: HttpResponse) -> HttpResponse:
        """Process the response through all registered response interceptors.

        Executes all registered response interceptors in order, passing the output
        of each interceptor as input to the next one. This creates a chain where
        each interceptor can modify the response or perform side effects.

        Args:
            response: The HTTP response object

        Returns:
            The response object after processing through all interceptors.

        Raises:
            Any exception raised by an interceptor will be propagated to the caller.

        Example:
            response = manager.process_response(response)
        """
        # Start with the original response
        current_response = response

        # Process through each response interceptor in order
        for interceptor in self._response_interceptors:
            current_response = interceptor.after_response(current_response)

        return current_response

    def clear_request_interceptors(self) -> None:
        """Remove all registered request interceptors.

        This method is useful for testing or when you need to reset
        the interceptor configuration.
        """
        self._request_interceptors.clear()

    def clear_response_interceptors(self) -> None:
        """Remove all registered response interceptors.

        This method is useful for testing or when you need to reset
        the interceptor configuration.
        """
        self._response_interceptors.clear()

    def clear_all_interceptors(self) -> None:
        """Remove all registered interceptors (both request and response).

        This method is useful for testing or when you need to reset
        the entire interceptor configuration.
        """
        self.clear_request_interceptors()
        self.clear_response_interceptors()

    @property
    def request_interceptor_count(self) -> int:
        """Get the number of registered request interceptors.

        Returns:
            The count of registered request interceptors
        """
        return len(self._request_interceptors)

    @property
    def response_interceptor_count(self) -> int:
        """Get the number of registered response interceptors.

        Returns:
            The count of registered response interceptors
        """
        return len(self._response_interceptors)
