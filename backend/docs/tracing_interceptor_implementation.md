# Tracing Interceptor Implementation

## Overview

The tracing interceptor has been successfully implemented for the HTTP client wrapper. This interceptor integrates with the execution context to automatically propagate tracing information (request_id and user_id) across HTTP requests.

## Implementation Details

### Files Created

1. **`backend/src/morado/common/http/tracing_interceptor.py`**
   - Main implementation of the `TracingInterceptor` class
   - Inherits from `RequestInterceptor` base class
   - Integrates with the existing context variable system

2. **`backend/scripts/verify_tracing_interceptor.py`**
   - Comprehensive verification script with 7 test cases
   - Tests all aspects of the tracing interceptor functionality

3. **`backend/scripts/demo_tracing_integration.py`**
   - Demonstration script showing real-world usage
   - Includes 4 different scenarios

### Files Modified

1. **`backend/src/morado/common/http/__init__.py`**
   - Added `TracingInterceptor` to exports

2. **`backend/src/morado/common/http/client.py`**
   - Added `interceptor_manager` property to expose the interceptor manager
   - Allows users to easily add custom interceptors

## Features

### Core Functionality

The `TracingInterceptor` class provides:

1. **Automatic Request ID Propagation**
   - Retrieves `request_id` from the context variable system
   - Adds it as `X-Request-ID` header to outgoing requests
   - Supports custom header names

2. **User ID Propagation**
   - Retrieves `user_id` from context data
   - Adds it as `X-User-ID` header to outgoing requests
   - Can be disabled via configuration
   - Automatically converts user_id to string

3. **Configurable Behavior**
   - Custom header names for both request_id and user_id
   - Option to disable user_id propagation
   - Respects existing headers (doesn't overwrite)

### Integration with Execution Context

The interceptor integrates with the existing context variable system:

- Uses `get_request_id()` from `morado.common.logger.context`
- Uses `get_context_data("user_id")` for user information
- No changes required to the execution context module
- Works seamlessly with the existing middleware and logging system

## Usage Examples

### Basic Usage

```python
from morado.common.http.client import HttpClient
from morado.common.http.tracing_interceptor import TracingInterceptor
from morado.common.logger.context import set_request_id, set_context_data

# Set up context
set_request_id("REQ-12345")
set_context_data("user_id", 42)

# Create client with tracing
client = HttpClient()
client.interceptor_manager.add_request_interceptor(TracingInterceptor())

# Make request - headers will be added automatically
response = client.get("https://api.example.com/users")
# Request will include:
# X-Request-ID: REQ-12345
# X-User-ID: 42
```

### Custom Configuration

```python
# Use custom header names
interceptor = TracingInterceptor(
    trace_header_name="X-Trace-ID",
    user_header_name="X-User"
)
client.interceptor_manager.add_request_interceptor(interceptor)
```

### Disable User ID

```python
# Only propagate request_id, not user_id
interceptor = TracingInterceptor(include_user_id=False)
client.interceptor_manager.add_request_interceptor(interceptor)
```

## Verification Results

All verification tests passed successfully:

1. ✓ Basic tracing with request_id
2. ✓ Tracing with request_id and user_id
3. ✓ No headers added when context is empty
4. ✓ Existing headers not overwritten
5. ✓ Custom header names work correctly
6. ✓ User ID not included when disabled
7. ✓ User ID converted to string

## Requirements Validation

This implementation satisfies the following requirements:

### Requirement 4.1
**WHEN 发送 HTTP 请求 THEN 系统 SHALL 自动从执行上下文获取 request_id 和 user_id**

✓ The interceptor automatically retrieves request_id using `get_request_id()` and user_id using `get_context_data("user_id")` from the execution context.

### Requirement 4.2
**WHEN 发送 HTTP 请求 THEN 系统 SHALL 将 request_id 添加到请求头（X-Request-ID）**

✓ The interceptor adds the request_id as the `X-Request-ID` header to all outgoing HTTP requests. The header name is configurable.

## Design Decisions

### 1. Integration with Existing Context System

Rather than creating a new context management system, the tracing interceptor integrates with the existing `morado.common.logger.context` module. This provides:

- Consistency with the existing logging and middleware systems
- No duplication of context management code
- Seamless integration with the execution engine

### 2. Optional User ID Propagation

User ID propagation is optional and can be disabled. This allows:

- Public API calls without user context
- Flexibility in different execution scenarios
- Privacy-conscious implementations

### 3. Non-Overwriting Behavior

The interceptor respects existing headers and doesn't overwrite them. This allows:

- Manual override of tracing headers when needed
- Compatibility with other interceptors
- Flexibility in testing scenarios

### 4. Type Conversion

User IDs are automatically converted to strings for header values. This handles:

- Integer user IDs from databases
- String user IDs from authentication systems
- Any other type that can be converted to string

## Testing Strategy

### Unit Testing (Verification Script)

The verification script tests:
- Basic functionality with request_id
- Combined request_id and user_id
- Behavior with no context
- Preservation of existing headers
- Custom header names
- Disabled user_id propagation
- Type conversion

### Integration Testing (Demo Script)

The demo script demonstrates:
- Real HTTP requests with tracing
- Multiple requests with same context
- Custom configuration
- Different scenarios

## Future Enhancements

Potential improvements for future iterations:

1. **Additional Context Data**
   - Support for more context fields (session_id, tenant_id, etc.)
   - Configurable context field mapping

2. **Trace ID Generation**
   - Automatic generation of request_id if not present
   - Support for distributed tracing standards (W3C Trace Context)

3. **Correlation ID Support**
   - Support for correlation IDs across service boundaries
   - Parent-child request relationships

4. **Metrics Integration**
   - Track request counts by user_id
   - Monitor tracing header propagation

## Conclusion

The tracing interceptor implementation is complete and fully functional. It successfully integrates with the execution context to provide automatic request tracing across HTTP requests, satisfying all specified requirements (4.1 and 4.2).

The implementation is:
- ✓ Well-tested with comprehensive verification
- ✓ Documented with clear examples
- ✓ Integrated with existing systems
- ✓ Flexible and configurable
- ✓ Ready for production use
