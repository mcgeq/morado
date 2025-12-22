"""Custom exception classes for utility modules.

This module defines custom exceptions used by FileSystemUtil and TimeUtil
to provide clear, descriptive error messages for various failure scenarios.
"""


class FileSystemError(Exception):
    """Base exception for file system operations.

    This exception serves as the base class for all file system-related errors.
    It should be raised when a file system operation fails in a way that doesn't
    fit more specific exception types.

    Args:
        message: A descriptive error message explaining what went wrong.

    Example:
        >>> raise FileSystemError("Failed to access file system")
        Traceback (most recent call last):
        ...
        FileSystemError: Failed to access file system
    """

    def __init__(self, message: str) -> None:
        """Initialize the FileSystemError with a message.

        Args:
            message: A descriptive error message.
        """
        self.message = message
        super().__init__(self.message)


class FileNotFoundError(FileSystemError):
    """Raised when a file or directory is not found.

    This exception is raised when attempting to perform an operation on a file
    or directory that does not exist in the file system.

    Args:
        path: The path that was not found.
        message: Optional custom error message. If not provided, a default
                message will be generated using the path.

    Example:
        >>> raise FileNotFoundError("/path/to/missing/file.txt")
        Traceback (most recent call last):
        ...
        FileNotFoundError: File or directory not found: /path/to/missing/file.txt
    """

    def __init__(self, path: str, message: str | None = None) -> None:
        """Initialize the FileNotFoundError.

        Args:
            path: The path that was not found.
            message: Optional custom error message.
        """
        self.path = path
        if message is None:
            message = f"File or directory not found: {path}"
        super().__init__(message)


class FileExistsError(FileSystemError):
    """Raised when a file or directory already exists.

    This exception is raised when attempting to create or copy a file to a
    destination that already exists, and the overwrite flag is not set.

    Args:
        path: The path that already exists.
        message: Optional custom error message. If not provided, a default
                message will be generated using the path.

    Example:
        >>> raise FileExistsError("/path/to/existing/file.txt")
        Traceback (most recent call last):
        ...
        FileExistsError: File or directory already exists: /path/to/existing/file.txt
    """

    def __init__(self, path: str, message: str | None = None) -> None:
        """Initialize the FileExistsError.

        Args:
            path: The path that already exists.
            message: Optional custom error message.
        """
        self.path = path
        if message is None:
            message = f"File or directory already exists: {path}"
        super().__init__(message)


class TimeParseError(Exception):
    """Raised when time string parsing fails.

    This exception is raised when attempting to parse a time string that is
    invalid or doesn't match the expected format.

    Args:
        time_string: The time string that failed to parse.
        format_string: Optional format string that was expected.
        message: Optional custom error message. If not provided, a default
                message will be generated.

    Example:
        >>> raise TimeParseError("invalid-date", "%Y-%m-%d")
        Traceback (most recent call last):
        ...
        TimeParseError: Failed to parse time string 'invalid-date' with format '%Y-%m-%d'
    """

    def __init__(
        self,
        time_string: str,
        format_string: str | None = None,
        message: str | None = None
    ) -> None:
        """Initialize the TimeParseError.

        Args:
            time_string: The time string that failed to parse.
            format_string: Optional format string that was expected.
            message: Optional custom error message.
        """
        self.time_string = time_string
        self.format_string = format_string

        if message is None:
            if format_string:
                message = (
                    f"Failed to parse time string '{time_string}' "
                    f"with format '{format_string}'"
                )
            else:
                message = f"Failed to parse time string '{time_string}'"

        self.message = message
        super().__init__(self.message)
