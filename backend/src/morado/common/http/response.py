"""HTTP response wrapper for the HTTP client.

This module provides a wrapper around requests.Response that adds convenience
methods for response handling, validation, and data extraction.
"""

import json
from pathlib import Path
from typing import Any

from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError
from requests import Response

from morado.common.http.exceptions import HttpRequestError, JSONPathError


class HttpResponse:
    """HTTP response wrapper.

    Provides a standardized interface for accessing HTTP response data with
    convenience methods for JSON parsing, JSONPath extraction, header access,
    and file saving.

    Attributes:
        _response: The underlying requests.Response object
        _request_time: Time taken for the request in seconds
    """

    def __init__(self, response: Response, request_time: float):
        """Initialize the HTTP response wrapper.

        Args:
            response: The requests.Response object to wrap
            request_time: Time taken for the request in seconds
        """
        self._response = response
        self._request_time = request_time

    @property
    def status_code(self) -> int:
        """Get the HTTP status code.

        Returns:
            The HTTP status code (e.g., 200, 404, 500)
        """
        return self._response.status_code

    @property
    def headers(self) -> dict[str, str]:
        """Get the response headers.

        Returns:
            Dictionary of response headers (case-insensitive)
        """
        return dict(self._response.headers)

    @property
    def text(self) -> str:
        """Get the response body as text.

        Returns:
            The response body decoded as a string
        """
        return self._response.text

    @property
    def content(self) -> bytes:
        """Get the response body as bytes.

        Returns:
            The raw response body as bytes
        """
        return self._response.content

    @property
    def request_time(self) -> float:
        """Get the request duration.

        Returns:
            Time taken for the request in seconds
        """
        return self._request_time

    def json(self) -> Any:
        """Parse the response body as JSON.

        Returns:
            The parsed JSON object (dict, list, or primitive)

        Raises:
            json.JSONDecodeError: If the response body is not valid JSON
        """
        try:
            return self._response.json()
        except json.JSONDecodeError as e:
            msg = f"Failed to parse response as JSON: {e.msg}"
            raise json.JSONDecodeError(
                msg,
                e.doc,
                e.pos,
            ) from e

    def is_success(self) -> bool:
        """Check if the response status code indicates success (2xx).

        Returns:
            True if status code is in the 2xx range, False otherwise
        """
        return 200 <= self.status_code < 300

    def raise_for_status(self) -> None:
        """Raise an exception if the response status indicates an error.

        Raises:
            HttpRequestError: If the status code indicates an error (4xx or 5xx)
        """
        if not self.is_success():
            msg = f"HTTP {self.status_code} error for URL {self._response.url}"
            raise HttpRequestError(
                msg,
                status_code=self.status_code,
                response=self,
            )

    def jsonpath(self, path: str) -> Any:
        """Extract data from JSON response using JSONPath.

        Args:
            path: JSONPath expression (e.g., "$.data.items[*].name")

        Returns:
            The extracted data. Returns a list of matches if multiple values match,
            a single value if only one match, or None if no matches.

        Raises:
            JSONPathError: If the JSONPath expression is invalid or extraction fails
            json.JSONDecodeError: If the response body is not valid JSON
        """
        try:
            # Parse the response as JSON first
            data = self.json()
        except json.JSONDecodeError as e:
            msg = f"Cannot extract JSONPath from non-JSON response: {e.msg}"
            raise JSONPathError(
                msg,
                path=path,
            ) from e

        try:
            # Parse and apply the JSONPath expression
            jsonpath_expr = parse(path)
            matches = jsonpath_expr.find(data)

            # Return None if no matches
            if not matches:
                return None

            # Return single value if only one match
            if len(matches) == 1:
                return matches[0].value

            # Return list of values if multiple matches
            return [match.value for match in matches]

        except JsonPathParserError as e:
            msg = f"Invalid JSONPath expression: {e!s}"
            raise JSONPathError(
                msg,
                path=path,
            ) from e
        except Exception as e:
            msg = f"Failed to extract JSONPath: {e!s}"
            raise JSONPathError(
                msg,
                path=path,
            ) from e

    def get_header(self, name: str, default: str | None = None) -> str | None:
        """Get a response header value (case-insensitive).

        Args:
            name: Header name (case-insensitive)
            default: Default value if header is not found

        Returns:
            The header value, or default if not found
        """
        return self._response.headers.get(name, default)

    def save_to_file(self, filepath: str, chunk_size: int = 8192) -> None:
        """Save the response content to a file.

        For large files, this method uses streaming to avoid loading the entire
        content into memory at once.

        Args:
            filepath: Path where the file should be saved
            chunk_size: Size of chunks to read when streaming (default: 8192 bytes)

        Raises:
            IOError: If the file cannot be written
        """
        try:
            path = Path(filepath)
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            # Use streaming for potentially large files
            with open(path, 'wb') as f:
                for chunk in self.iter_content(chunk_size=chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
        except Exception as e:
            msg = f"Failed to save response to file '{filepath}': {e!s}"
            raise OSError(msg) from e

    def iter_content(self, chunk_size: int = 8192) -> Any:
        """Iterate over the response content in chunks.

        This method allows streaming large responses without loading the entire
        content into memory. Useful for downloading large files.

        Args:
            chunk_size: Size of chunks to yield (default: 8192 bytes)

        Yields:
            Chunks of response content as bytes

        Example:
            >>> response = client.get("https://example.com/large-file.zip")
            >>> with open("large-file.zip", "wb") as f:
            ...     for chunk in response.iter_content(chunk_size=8192):
            ...         if chunk:
            ...             f.write(chunk)
        """
        return self._response.iter_content(chunk_size=chunk_size)

    def stream_to_file(self, filepath: str, chunk_size: int = 8192) -> int:
        """Stream the response content directly to a file.

        This is an alias for save_to_file() that emphasizes the streaming nature
        and returns the total bytes written.

        Args:
            filepath: Path where the file should be saved
            chunk_size: Size of chunks to read when streaming (default: 8192 bytes)

        Returns:
            Total number of bytes written

        Raises:
            IOError: If the file cannot be written

        Example:
            >>> response = client.get("https://example.com/large-file.zip")
            >>> bytes_written = response.stream_to_file("large-file.zip")
            >>> print(f"Downloaded {bytes_written} bytes")
        """
        try:
            path = Path(filepath)
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            total_bytes = 0
            with open(path, 'wb') as f:
                for chunk in self.iter_content(chunk_size=chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        total_bytes += len(chunk)

            return total_bytes
        except Exception as e:
            msg = f"Failed to stream response to file '{filepath}': {e!s}"
            raise OSError(msg) from e
