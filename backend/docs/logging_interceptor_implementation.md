# Logging Interceptor Implementation

## Overview

This document describes the implementation of the logging interceptor for the HTTP client wrapper, completed as part of Task 8.

## Implementation Details

### Files Created

1. **`backend/src/morado/common/http/logging_interceptor.py`**
   - Main logging interceptor implementation
   - Contains `LoggingInterceptor` and `ErrorLoggingInterceptor` classes

2. **`backend/scripts/verify_logging_interceptor.py`**
   - Verification script to test the logging interceptor functionality
   - Tests initialization, request logging, response logging, error logging, and data masking

3. **`backend/scripts/demo_logging_integration.py`**
   - Demo script showing integration with HTTP client
   - Demonstrates basic logging, error logging, and sensitive data masking

### Files Modified

1. **`backend/src/morado/common/http/__init__.py`**
   - Added exports for `LoggingInterceptor` and `ErrorLoggingInterceptor`

2. **`backend/src/morado/common/logger/logger.py`**
   - Fixed import to use function-based context API instead of `ContextManager` class
   - Updated to use `get_request_id()` and `get_context_data()` functions

## Features Implemented

### LoggingInterceptor

The `LoggingInterceptor` class implements both `RequestInterceptor` and `ResponseInterceptor` interfaces to provide comprehensive logging:

#### Request Logging
- Logs HTTP method, URL, headers, query parameters, and request body
- Supports configurable body logging (can be disabled)
- Implements body size limiting (configurable max size)
- Masks sensitive information in headers and body
- Integrates with structlog for structured logging

#### Response Logging
- Logs HTTP status code, headers, response body, and duration
- Supports configurable body logging
- Implements body size limiting
- Masks sensitive information
- Uses different log levels based on status code (info for success, warning for errors)

#### Error Logging
- Provides `log_error()` method for logging exceptions
- Logs exception type, message, and full stack trace
- Includes request context (method, URL, headers, params)
- Masks sensitive information in error logs

#### Sensitive Data Masking
- Automatically masks sensitive headers (Authorization, Cookie, API keys, etc.)
- Masks sensitive fields in request/response bodies (password, token, secret, etc.)
- Uses `mask_sensitive_headers()` and `mask_sensitive_data()` utility functions
- Configurable mask value (default: "***")

#### Body Truncation
- Limits log body size to prevent log bloat
- Configurable max size (default: 1024 bytes)
- Adds truncation marker with original size
- Uses `truncate_for_logging()` utility function

### ErrorLoggingInterceptor

Specialized interceptor for detailed error logging:

- Focuses on error responses (4xx and 5xx status codes)
- Extracts error details from response body (error, message, code fields)
- Uses warning level for 4xx errors (client errors)
- Uses error level for 5xx errors (server errors)
- Provides additional context for debugging

## Configuration

The logging interceptor respects the following configuration options from `HttpClientConfig`:

```python
class HttpClientConfig(BaseModel):
    enable_logging: bool = True          # Enable/disable logging
    log_request_body: bool = True        # Log request body
    log_response_body: bool = True       # Log response body
    max_log_body_size: int = 1024       # Max body size in logs (bytes)
```

## Usage Example

```python
from morado.common.http import (
    HttpClient,
    HttpClientConfig,
    InterceptorManager,
    SessionManager,
)
from morado.common.http.logging_interceptor import LoggingInterceptor

# Create configuration
config = HttpClientConfig(
    enable_logging=True,
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=1024
)

# Create interceptor manager and add logging interceptor
interceptor_manager = InterceptorManager()
logging_interceptor = LoggingInterceptor(config=config)
interceptor_manager.add_request_interceptor(logging_interceptor)
interceptor_manager.add_response_interceptor(logging_interceptor)

# Create HTTP client
session_manager = SessionManager()
client = HttpClient(
    session_manager=session_manager,
    interceptor_manager=interceptor_manager,
    config=config
)

# Make requests - they will be automatically logged
response = client.get("https://api.example.com/users")
```

## Integration with Structlog

The logging interceptor integrates seamlessly with the existing structlog logging system:

- Uses `get_logger()` to obtain logger instances
- Logs are structured with consistent field names
- Automatically includes context variables (request_id, user_id, trace_id)
- Supports multiple output formats (console, JSON, structured)

## Log Fields

### Request Logs
- `http_method`: HTTP method (GET, POST, etc.)
- `http_url`: Request URL
- `http_headers`: Request headers (sensitive values masked)
- `http_params`: Query parameters
- `http_request_body`: Request body (masked and truncated)
- `http_timeout`: Timeout configuration (if specified)

### Response Logs
- `http_status_code`: HTTP status code
- `http_duration`: Request duration in seconds
- `http_response_headers`: Response headers (sensitive values masked)
- `http_response_body`: Response body (masked and truncated)

### Error Logs
- `error_type`: Exception class name
- `error_message`: Exception message
- `error_stack_trace`: Full stack trace
- `http_method`: HTTP method that failed
- `http_url`: URL that was requested
- `http_headers`: Request headers (masked)
- `http_params`: Query parameters

## Testing

The implementation has been verified with comprehensive tests:

1. **Initialization Tests**
   - Default configuration
   - Custom configuration

2. **Request Logging Tests**
   - Basic request logging
   - Sensitive data masking
   - Parameter preservation

3. **Response Logging Tests**
   - Success response logging
   - Error response logging
   - Response preservation

4. **Error Logging Tests**
   - Exception logging
   - Stack trace inclusion
   - Context preservation

5. **Data Masking Tests**
   - Sensitive header masking
   - Sensitive body field masking
   - Original data preservation

6. **Body Truncation Tests**
   - Large body truncation
   - Truncation marker
   - Original data preservation

All tests pass successfully as verified by `verify_logging_interceptor.py`.

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 1.5**: HTTP request completion logging with detailed information
- **Requirement 4.3**: Request logging (method, URL, headers, body, parameters)
- **Requirement 4.4**: Response logging (status code, headers, body, time)
- **Requirement 4.5**: Error logging (exception type, message, stack trace)
- **Requirement 4.6**: Integration with structlog logging system

## Next Steps

The logging interceptor is now ready for integration with:

1. **Tracing Interceptor** (Task 9): Add request ID propagation
2. **HTTP Client** (Task 7): Already integrated via InterceptorManager
3. **Execution Engine** (Task 12): Will use logging for script execution tracking

## Notes

- The implementation uses the function-based context API (`get_request_id()`, `get_context_data()`) instead of the `ContextManager` class
- Sensitive data masking is automatic and comprehensive
- Log size limiting prevents log bloat while preserving important information
- The interceptor is non-invasive - it doesn't modify request/response data
