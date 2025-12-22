# Implementation Plan

- [x] 1. Create custom exception classes





  - Create `FileSystemError`, `FileNotFoundError`, `FileExistsError`, and `TimeParseError` exception classes
  - Add docstrings and type hints
  - _Requirements: 2.1, 4.1_

- [x] 2. Implement FileSystemUtil class with path query methods





  - Create `src/morado/common/utils/filesystem.py` module
  - Implement `exists()`, `get_size()`, `get_modified_time()`, `get_extension()`, `get_directory()`, `get_absolute_path()`, and `join_path()` methods
  - Add comprehensive docstrings with examples
  - Add type hints for all parameters and return values
  - _Requirements: 1.1, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12_

- [ ]* 2.1 Write property test for path existence check
  - **Property 1: Path existence check accuracy**
  - **Validates: Requirements 1.1**

- [ ]* 2.2 Write property test for file size
  - **Property 7: File size is non-negative**
  - **Validates: Requirements 1.7**

- [ ]* 2.3 Write property test for modification time
  - **Property 8: Modification time is valid**
  - **Validates: Requirements 1.8**

- [ ]* 2.4 Write property test for path operations
  - **Property 9: Path joining produces valid paths**
  - **Property 10: Absolute path is absolute**
  - **Property 11: Extension extraction correctness**
  - **Property 12: Directory extraction correctness**
  - **Validates: Requirements 1.9, 1.10, 1.11, 1.12**

- [x] 3. Implement FileSystemUtil directory and file manipulation methods





  - Implement `create_directory()`, `delete()`, `copy_file()`, `move()`, and `list_files()` methods
  - Add input validation and error handling
  - Handle overwrite parameter logic
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.1 Write property test for directory creation
  - **Property 2: Directory creation idempotence**
  - **Validates: Requirements 1.2**

- [ ]* 3.2 Write property test for deletion
  - **Property 3: Deletion removes path**
  - **Validates: Requirements 1.3**

- [ ]* 3.3 Write property test for copy operation
  - **Property 4: Copy preserves content**
  - **Validates: Requirements 1.4**

- [ ]* 3.4 Write property test for move operation
  - **Property 5: Move transfers existence**
  - **Validates: Requirements 1.5**

- [ ]* 3.5 Write property test for list files
  - **Property 6: List files returns matching files**
  - **Validates: Requirements 1.6**

- [ ]* 3.6 Write property test for error handling
  - **Property 13: Failed operations raise exceptions**
  - **Property 14: Overwrite parameter controls behavior**
  - **Property 15: Invalid input raises exceptions**
  - **Validates: Requirements 2.1, 2.3, 2.4**

- [x] 4. Implement TimeUtil class with current time methods





  - Create `src/morado/common/utils/time.py` module
  - Implement `now_utc()` and `now_local()` methods
  - Ensure timezone-aware datetime objects are returned
  - Add comprehensive docstrings with examples
  - Add type hints for all parameters and return values
  - _Requirements: 3.1, 3.2_

- [ ]* 4.1 Write property test for UTC timestamp
  - **Property 16: UTC timestamp has UTC timezone**
  - **Validates: Requirements 3.1**

- [ ]* 4.2 Write property test for local timestamp
  - **Property 17: Local timestamp has local timezone**
  - **Validates: Requirements 3.2**

- [x] 5. Implement TimeUtil formatting and parsing methods





  - Implement `to_iso8601()`, `format_time()`, `parse_iso8601()`, and `parse_time()` methods
  - Add validation for timezone-aware datetimes
  - Add error handling for invalid time strings
  - _Requirements: 3.3, 3.4, 3.5, 3.6, 4.1, 4.4_

- [ ]* 5.1 Write property test for ISO 8601 round-trip
  - **Property 18: ISO 8601 round-trip preserves time**
  - **Validates: Requirements 3.3, 3.5**

- [ ]* 5.2 Write property test for custom format round-trip
  - **Property 19: Custom format round-trip preserves time**
  - **Validates: Requirements 3.4, 3.6**

- [ ]* 5.3 Write property test for timezone info preservation
  - **Property 26: Formatting preserves timezone info**
  - **Validates: Requirements 4.4**

- [ ]* 5.4 Write property test for parse error handling
  - **Property 24: Invalid time strings raise exceptions**
  - **Validates: Requirements 4.1**

- [x] 6. Implement TimeUtil calculation methods





  - Implement `time_difference()`, `add_duration()`, `subtract_duration()`, and `convert_timezone()` methods
  - Add validation for timezone-aware datetimes
  - Handle timezone conversions correctly
  - _Requirements: 3.7, 3.8, 3.9, 3.10, 4.2, 4.3_

- [ ]* 6.1 Write property test for time difference
  - **Property 20: Time difference is symmetric**
  - **Property 25: Time difference returns timedelta**
  - **Validates: Requirements 3.7, 4.3**

- [ ]* 6.2 Write property test for duration operations
  - **Property 21: Duration addition increases time**
  - **Property 22: Duration operations are inverses**
  - **Validates: Requirements 3.8, 3.9**

- [ ]* 6.3 Write property test for timezone conversion
  - **Property 23: Timezone conversion preserves absolute time**
  - **Validates: Requirements 3.10**

- [x] 7. Update utils package __init__.py




  - Export `FileSystemUtil` and `TimeUtil` classes
  - Add module-level docstring
  - Maintain backward compatibility with existing `uuid` module
  - _Requirements: 5.1, 5.2, 5.3_

- [ ]* 8. Write unit tests for FileSystemUtil edge cases
  - Test with empty directories, special characters in filenames
  - Test permission errors and IO errors
  - Test missing_ok parameter for delete operation
  - _Requirements: 1.1-1.12, 2.1-2.4_

- [ ]* 9. Write unit tests for TimeUtil edge cases
  - Test with epoch, Y2K, leap years
  - Test DST transitions
  - Test naive datetime rejection
  - _Requirements: 3.1-3.10, 4.1-4.4_

- [x] 10. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
