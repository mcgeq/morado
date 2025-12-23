"""Retry strategy implementation for HTTP client wrapper.


This module provides configurable retry logic for HTTP requests, supporting
different retry strategies (fixed, exponential backoff, linear) and retry
conditions based on error types and status codes.
"""

import time
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from morado.common.http.exceptions import (
    HttpConnectionError,
    HttpRequestError,
    HttpTimeoutError,
    RetryExhaustedError,
)


class RetryStrategy(str, Enum):
    """Retry strategy types.

    Defines the different strategies for calculating delay between retry attempts.
    """

    FIXED = "fixed"  # Fixed interval between retries
    EXPONENTIAL = "exponential"  # Exponential backoff (delay doubles each time)
    LINEAR = "linear"  # Linear increase (delay increases by fixed amount)


class RetryConfig:
    """Configuration for retry behavior.

    Defines how the retry handler should behave when requests fail.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        strategy: Retry strategy to use (default: exponential)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        multiplier: Multiplier for exponential backoff (default: 2.0)
        retry_on_status: List of HTTP status codes to retry on (default: 5xx)
        retry_on_exceptions: List of exception types to retry on
    """

    def __init__(
        self,
        max_retries: int = 3,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        retry_on_status: list[int] | None = None,
        retry_on_exceptions: list[type] | None = None,
    ):
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            strategy: Retry strategy (fixed, exponential, or linear)
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            multiplier: Multiplier for exponential backoff strategy
            retry_on_status: HTTP status codes that should trigger retry
            retry_on_exceptions: Exception types that should trigger retry

        Raises:
            ValueError: If configuration values are invalid
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if initial_delay <= 0:
            raise ValueError("initial_delay must be positive")
        if max_delay <= 0:
            raise ValueError("max_delay must be positive")
        if max_delay < initial_delay:
            raise ValueError("max_delay must be greater than or equal to initial_delay")
        if multiplier <= 1.0 and strategy == RetryStrategy.EXPONENTIAL:
            raise ValueError(
                "multiplier must be greater than 1.0 for exponential strategy"
            )

        self.max_retries = max_retries
        self.strategy = (
            strategy if isinstance(strategy, RetryStrategy) else RetryStrategy(strategy)
        )
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.multiplier = multiplier

        # Default to retrying on 5xx status codes
        self.retry_on_status = (
            retry_on_status if retry_on_status is not None else list(range(500, 600))
        )

        # Default to retrying on network and timeout errors
        self.retry_on_exceptions = (
            retry_on_exceptions
            if retry_on_exceptions is not None
            else [
                HttpConnectionError,
                HttpTimeoutError,
            ]
        )


class RetryHandler:
    """Handler for executing functions with retry logic.

    Implements configurable retry behavior with different strategies and
    maintains a history of retry attempts.
    """

    def __init__(self, config: RetryConfig):
        """Initialize retry handler.

        Args:
            config: Retry configuration
        """
        self.config = config
        self._retry_history: list[dict[str, Any]] = []

    @property
    def retry_history(self) -> list[dict[str, Any]]:
        """Get the history of retry attempts.

        Returns:
            List of dictionaries containing retry attempt details
        """
        return self._retry_history.copy()

    def should_retry(
        self,
        exception: Exception | None = None,
        status_code: int | None = None,
    ) -> bool:
        """Determine if a request should be retried.

        A request should be retried if:
        - An exception occurred and it's in the retry_on_exceptions list
        - A status code was returned and it's in the retry_on_status list

        Args:
            exception: Exception that was raised (if any)
            status_code: HTTP status code (if any)

        Returns:
            True if the request should be retried, False otherwise
        """
        # Check if we should retry based on exception type
        if exception is not None:
            for exc_type in self.config.retry_on_exceptions:
                if isinstance(exception, exc_type):
                    return True

        # Check if we should retry based on status code
        return bool(
            status_code is not None and status_code in self.config.retry_on_status
        )

    def calculate_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt.

        The delay is calculated based on the configured retry strategy:
        - FIXED: Always use initial_delay
        - EXPONENTIAL: delay = initial_delay * (multiplier ^ attempt)
        - LINEAR: delay = initial_delay * (attempt + 1)

        The calculated delay is capped at max_delay.

        Args:
            attempt: Current retry attempt number (0-indexed)

        Returns:
            Delay in seconds before the next retry
        """
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.initial_delay
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (self.config.multiplier**attempt)
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.initial_delay * (attempt + 1)
        else:
            # Fallback to fixed strategy
            delay = self.config.initial_delay

        # Cap the delay at max_delay
        return min(delay, self.config.max_delay)

    def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute a function with retry logic.

        Attempts to execute the function, retrying on failures according to
        the configured retry strategy. Maintains a history of all retry attempts.

        Args:
            func: Function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The return value of the function

        Raises:
            RetryExhaustedError: If all retry attempts are exhausted
            Exception: If an exception occurs that should not be retried
        """
        # Reset retry history for this execution
        self._retry_history = []

        last_exception: Exception | None = None
        last_status_code: int | None = None

        # Initial attempt + retries
        for attempt in range(self.config.max_retries + 1):
            try:
                # Record attempt start time
                start_time = datetime.now(UTC)

                # Execute the function
                result = func(*args, **kwargs)

                # If we get here, the function succeeded
                if attempt > 0:
                    # Record successful retry
                    self._retry_history.append(
                        {
                            "attempt": attempt,
                            "success": True,
                            "timestamp": start_time.isoformat(),
                            "delay": self.calculate_delay(attempt - 1)
                            if attempt > 0
                            else 0,
                        }
                    )

                return result

            except Exception as e:
                last_exception = e

                # Extract status code if it's an HttpRequestError
                if isinstance(e, HttpRequestError) and e.status_code is not None:
                    last_status_code = e.status_code
                else:
                    last_status_code = None

                # Check if we should retry
                should_retry = self.should_retry(
                    exception=e, status_code=last_status_code
                )

                # Record the failed attempt
                self._retry_history.append(
                    {
                        "attempt": attempt,
                        "success": False,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                        "status_code": last_status_code,
                        "should_retry": should_retry,
                    }
                )

                # If this is the last attempt or we shouldn't retry, raise the exception
                if attempt >= self.config.max_retries or not should_retry:
                    if should_retry and attempt >= self.config.max_retries:
                        # Retry exhausted
                        msg = (
                            f"Retry attempts exhausted after {attempt + 1} attempts. "
                            f"Last error: {type(e).__name__}: {e!s}"
                        )
                        raise RetryExhaustedError(
                            msg,
                            retry_history=self._retry_history,
                        ) from e
                    else:
                        # Exception should not be retried
                        raise

                # Calculate delay before next retry
                delay = self.calculate_delay(attempt)

                # Update the last history entry with the delay
                self._retry_history[-1]["delay_before_next"] = delay

                # Wait before retrying
                time.sleep(delay)

        # This should never be reached, but just in case
        if last_exception:
            msg = f"Retry attempts exhausted. Last error: {type(last_exception).__name__}: {last_exception!s}"
            raise RetryExhaustedError(
                msg,
                retry_history=self._retry_history,
            ) from last_exception
        else:
            raise RetryExhaustedError(
                "Retry attempts exhausted with no exception recorded",
                retry_history=self._retry_history,
            )
