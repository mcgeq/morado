# Design Document

## Overview

This document describes the design for two utility classes: `FileSystemUtil` and `TimeUtil`. These classes provide cross-platform abstractions for common file system and time operations, leveraging Python's standard library (`pathlib`, `shutil`, `datetime`, `zoneinfo`) to ensure consistent behavior across operating systems.

The utilities will be implemented as classes with static methods, making them easy to use without instantiation. They will include comprehensive error handling, type hints, and documentation.

## Architecture

### Module Structure

```
src/morado/common/utils/
├── __init__.py
├── filesystem.py    # FileSystemUtil class
├── time.py          # TimeUtil class (rename existing time module)
└── uuid.py          # Existing UUID utilities
```

### Design Principles

1. **Cross-platform compatibility**: Use `pathlib.Path` for all path operations to ensure OS-agnostic behavior
2. **Explicit error handling**: Raise descriptive exceptions rather than silently failing
3. **Type safety**: Full type hints for all methods
4. **Stateless design**: Static methods that don't require instantiation
5. **Standard library first**: Leverage Python's standard library to minimize dependencies

## Components and Interfaces

### FileSystemUtil Class

Located in `src/morado/common/utils/filesystem.py`

```python
from pathlib import Path
from typing import List, Optional, Callable
from datetime import datetime
import shutil

class FileSystemUtil:
    """Cross-platform file system utility class."""
    
    @staticmethod
    def exists(path: str | Path) -> bool:
        """Check if a path exists."""
        
    @staticmethod
    def create_directory(path: str | Path, parents: bool = True, exist_ok: bool = True) -> Path:
        """Create a directory, optionally creating parent directories."""
        
    @staticmethod
    def delete(path: str | Path, missing_ok: bool = True) -> None:
        """Delete a file or directory."""
        
    @staticmethod
    def copy_file(src: str | Path, dst: str | Path, overwrite: bool = False) -> Path:
        """Copy a file from source to destination."""
        
    @staticmethod
    def move(src: str | Path, dst: str | Path, overwrite: bool = False) -> Path:
        """Move a file or directory from source to destination."""
        
    @staticmethod
    def list_files(directory: str | Path, pattern: Optional[str] = None, 
                   recursive: bool = False) -> List[Path]:
        """List files in a directory with optional filtering."""
        
    @staticmethod
    def get_size(path: str | Path) -> int:
        """Get file size in bytes."""
        
    @staticmethod
    def get_modified_time(path: str | Path) -> datetime:
        """Get file modification time."""
        
    @staticmethod
    def join_path(*parts: str | Path) -> Path:
        """Join path components."""
        
    @staticmethod
    def get_absolute_path(path: str | Path) -> Path:
        """Get absolute path from relative path."""
        
    @staticmethod
    def get_extension(path: str | Path) -> str:
        """Get file extension."""
        
    @staticmethod
    def get_directory(path: str | Path) -> Path:
        """Get directory name from path."""
```

### TimeUtil Class

Located in `src/morado/common/utils/time.py`

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

class TimeUtil:
    """Time utility class for common time operations."""
    
    @staticmethod
    def now_utc() -> datetime:
        """Get current timestamp in UTC."""
        
    @staticmethod
    def now_local() -> datetime:
        """Get current timestamp in local timezone."""
        
    @staticmethod
    def to_iso8601(dt: datetime) -> str:
        """Format timestamp as ISO 8601 string."""
        
    @staticmethod
    def format_time(dt: datetime, format_string: str) -> str:
        """Format timestamp with custom format string."""
        
    @staticmethod
    def parse_iso8601(time_string: str) -> datetime:
        """Parse ISO 8601 string into datetime object."""
        
    @staticmethod
    def parse_time(time_string: str, format_string: str) -> datetime:
        """Parse custom formatted time string into datetime object."""
        
    @staticmethod
    def time_difference(dt1: datetime, dt2: datetime) -> timedelta:
        """Calculate time difference between two timestamps."""
        
    @staticmethod
    def add_duration(dt: datetime, **kwargs) -> datetime:
        """Add time duration to timestamp (days, hours, minutes, seconds, etc.)."""
        
    @staticmethod
    def subtract_duration(dt: datetime, **kwargs) -> datetime:
        """Subtract time duration from timestamp."""
        
    @staticmethod
    def convert_timezone(dt: datetime, target_tz: str | ZoneInfo) -> datetime:
        """Convert timestamp to target timezone."""
```

## Data Models

### Path Representation

All path operations use `pathlib.Path` objects internally, but accept both `str` and `Path` as input for convenience. Methods return `Path` objects for consistency.

### Time Representation

All time operations use `datetime` objects from Python's standard library. Timezone-aware datetimes are preferred and enforced where appropriate.

### Error Types

Custom exceptions for better error handling:

```python
class FileSystemError(Exception):
    """Base exception for file system operations."""
    pass

class FileNotFoundError(FileSystemError):
    """Raised when a file is not found."""
    pass

class FileExistsError(FileSystemError):
    """Raised when a file already exists."""
    pass

class TimeParseError(Exception):
    """Raised when time string parsing fails."""
    pass
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### FileSystem Properties

Property 1: Path existence check accuracy
*For any* path in the file system, calling `exists()` should return True if and only if the path actually exists on the file system
**Validates: Requirements 1.1**

Property 2: Directory creation idempotence
*For any* valid directory path, creating it with `create_directory()` should result in that path existing, regardless of whether it existed before
**Validates: Requirements 1.2**

Property 3: Deletion removes path
*For any* existing file or directory path, calling `delete()` should result in that path no longer existing
**Validates: Requirements 1.3**

Property 4: Copy preserves content
*For any* file, copying it from source to destination should result in both paths existing with identical file sizes and content
**Validates: Requirements 1.4**

Property 5: Move transfers existence
*For any* file, moving it from source to destination should result in the destination existing and the source not existing
**Validates: Requirements 1.5**

Property 6: List files returns matching files
*For any* directory and filter pattern, `list_files()` should return only files that match the pattern and exist in the directory
**Validates: Requirements 1.6**

Property 7: File size is non-negative
*For any* existing file, `get_size()` should return a non-negative integer representing the file size in bytes
**Validates: Requirements 1.7**

Property 8: Modification time is valid
*For any* existing file, `get_modified_time()` should return a valid datetime object
**Validates: Requirements 1.8**

Property 9: Path joining produces valid paths
*For any* set of path components, `join_path()` should produce a valid path that can be used in file operations
**Validates: Requirements 1.9**

Property 10: Absolute path is absolute
*For any* relative path, `get_absolute_path()` should return a path that is absolute (starts from root)
**Validates: Requirements 1.10**

Property 11: Extension extraction correctness
*For any* path with an extension, `get_extension()` should return the correct file extension including the dot
**Validates: Requirements 1.11**

Property 12: Directory extraction correctness
*For any* file path, `get_directory()` should return the parent directory path
**Validates: Requirements 1.12**

Property 13: Failed operations raise exceptions
*For any* invalid file operation (e.g., copying non-existent file), the method should raise an appropriate exception with a descriptive message
**Validates: Requirements 2.1**

Property 14: Overwrite parameter controls behavior
*For any* copy operation where destination exists, when overwrite=False an exception should be raised, and when overwrite=True the operation should succeed
**Validates: Requirements 2.3**

Property 15: Invalid input raises exceptions
*For any* path operation receiving invalid input (e.g., None, empty string), the method should raise an appropriate exception
**Validates: Requirements 2.4**

### Time Properties

Property 16: UTC timestamp has UTC timezone
*For any* call to `now_utc()`, the returned datetime should have timezone set to UTC
**Validates: Requirements 3.1**

Property 17: Local timestamp has local timezone
*For any* call to `now_local()`, the returned datetime should have timezone set to the system's local timezone
**Validates: Requirements 3.2**

Property 18: ISO 8601 round-trip preserves time
*For any* timezone-aware datetime, formatting to ISO 8601 and parsing back should produce an equivalent datetime
**Validates: Requirements 3.3, 3.5**

Property 19: Custom format round-trip preserves time
*For any* datetime and format string, formatting and parsing back with the same format should preserve the datetime components specified in the format
**Validates: Requirements 3.4, 3.6**

Property 20: Time difference is symmetric
*For any* two datetimes dt1 and dt2, the relationship `dt1 + (dt2 - dt1) == dt2` should hold
**Validates: Requirements 3.7**

Property 21: Duration addition increases time
*For any* datetime and positive duration, adding the duration should produce a datetime that is later than the original
**Validates: Requirements 3.8**

Property 22: Duration operations are inverses
*For any* datetime and duration, adding then subtracting the same duration should return the original datetime
**Validates: Requirements 3.9**

Property 23: Timezone conversion preserves absolute time
*For any* timezone-aware datetime and target timezone, converting to the target timezone should preserve the absolute point in time (UTC equivalent)
**Validates: Requirements 3.10**

Property 24: Invalid time strings raise exceptions
*For any* invalid time string, parsing should raise a TimeParseError with a descriptive message
**Validates: Requirements 4.1**

Property 25: Time difference returns timedelta
*For any* two datetimes, `time_difference()` should always return a timedelta object
**Validates: Requirements 4.3**

Property 26: Formatting preserves timezone info
*For any* timezone-aware datetime, formatting and parsing back should preserve the timezone information
**Validates: Requirements 4.4**

## Error Handling

### FileSystem Error Handling

1. **Path validation**: All methods validate input paths and raise `ValueError` for invalid inputs (None, empty strings)
2. **File not found**: Operations on non-existent paths raise `FileNotFoundError` unless explicitly allowed (e.g., `delete()` with `missing_ok=True`)
3. **File exists**: Copy/move operations raise `FileExistsError` when destination exists and `overwrite=False`
4. **Permission errors**: Wrap OS permission errors in `FileSystemError` with descriptive messages
5. **IO errors**: Wrap OS IO errors in `FileSystemError` with context about the operation

### Time Error Handling

1. **Parse errors**: Invalid time strings raise `TimeParseError` with details about what failed
2. **Timezone errors**: Invalid timezone names raise `ValueError` with available timezone suggestions
3. **Type errors**: Non-datetime inputs raise `TypeError` with expected type information
4. **Naive datetime warnings**: Operations requiring timezone-aware datetimes raise `ValueError` when given naive datetimes

## Testing Strategy

### Unit Testing Approach

Unit tests will verify specific examples and edge cases:

- **FileSystem**: Test with known file paths, empty directories, special characters in filenames
- **Time**: Test with specific dates (epoch, Y2K, leap years), known timezones, DST transitions
- **Error cases**: Test invalid inputs, permission errors, non-existent paths

### Property-Based Testing Approach

Property-based tests will use the `hypothesis` library (already in the project) to verify universal properties:

- **FileSystem**: Generate random paths, file contents, directory structures
- **Time**: Generate random datetimes, timezones, durations, format strings
- **Round-trip properties**: Test serialization/deserialization cycles
- **Invariants**: Test properties that should hold regardless of input

Each property-based test will:
- Run a minimum of 100 iterations
- Use smart generators that constrain to valid input spaces
- Include explicit comments linking to design document properties
- Use format: `# Feature: utility-classes, Property {number}: {property_text}`

### Test Organization

```
tests/
├── test_filesystem_basic.py      # Unit tests for FileSystemUtil
├── test_filesystem_properties.py # Property-based tests for FileSystemUtil
├── test_time_basic.py            # Unit tests for TimeUtil
└── test_time_properties.py       # Property-based tests for TimeUtil
```

### Testing Tools

- **pytest**: Test framework
- **hypothesis**: Property-based testing library
- **pytest-cov**: Coverage reporting
- **freezegun**: Time mocking for deterministic tests (unit tests only)

## Implementation Notes

### FileSystem Implementation Details

1. Use `pathlib.Path` for all path operations to ensure cross-platform compatibility
2. Use `shutil` for high-level file operations (copy, move)
3. Convert string inputs to `Path` objects at method entry
4. Use `Path.glob()` for pattern matching in `list_files()`
5. Handle both files and directories in `delete()` using `Path.unlink()` and `shutil.rmtree()`

### Time Implementation Details

1. Always use timezone-aware datetimes; reject naive datetimes in public APIs
2. Use `datetime.now(timezone.utc)` for UTC times
3. Use `datetime.now(ZoneInfo("localtime"))` for local times (Python 3.9+)
4. Use `datetime.fromisoformat()` for ISO 8601 parsing
5. Use `datetime.strftime()` and `datetime.strptime()` for custom formats
6. Store durations as `timedelta` objects
7. Use `zoneinfo.ZoneInfo` for timezone handling (Python 3.9+)

### Backward Compatibility

The existing `uuid.py` module will remain unchanged. The new utilities will be added alongside it in the `utils` package.
