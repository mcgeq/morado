# Execution Engine HTTP Client Integration

## Overview

This document describes the integration of the HTTP client wrapper into the execution engine. The integration enables the execution engine to:

1. Build HTTP requests from API definitions
2. Apply parameter overrides from multiple layers
3. Execute HTTP requests with retry and logging
4. Validate responses against assertions
5. Extract variables from responses

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Execution Engine                          │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  execute_script()                                       │ │
│  │                                                          │ │
│  │  1. Build Request from API Definition                   │ │
│  │     ↓                                                    │ │
│  │  2. Create HTTP Client                                  │ │
│  │     ↓                                                    │ │
│  │  3. Execute HTTP Request                                │ │
│  │     ↓                                                    │ │
│  │  4. Validate Response (Assertions)                      │ │
│  │     ↓                                                    │ │
│  │  5. Extract Variables                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Client Wrapper                       │
│                                                               │
│  • Session Management                                        │
│  • Retry Logic                                               │
│  • Request/Response Interceptors                             │
│  • Logging & Tracing                                         │
└─────────────────────────────────────────────────────────────┘
```

## Request Building

The `_build_request_from_api_definition()` method constructs HTTP requests by merging data from multiple sources with the following priority:

### Priority Order (Highest to Lowest)

1. **Script Parameters** (from execution context)
2. **API Definition** (from database)
3. **Header/Body Components** (referenced by API definition)

### Merging Logic

#### Headers
```python
# 1. Start with Header component
headers = api_definition.header.headers

# 2. Override with script parameters
if 'headers' in resolved_params:
    headers.update(resolved_params['headers'])

# 3. Resolve variables
headers = context.resolve_value(headers)
```

#### Query Parameters
```python
# 1. Start with API definition
query_params = api_definition.query_parameters

# 2. Override with script parameters
if 'params' in resolved_params:
    query_params.update(resolved_params['params'])

# 3. Resolve variables
query_params = context.resolve_value(query_params)
```

#### Path Parameters
```python
# 1. Start with API definition
path_params = api_definition.path_parameters

# 2. Override with script parameters
if 'path_params' in resolved_params:
    path_params.update(resolved_params['path_params'])

# 3. Resolve variables and replace in URL
path_params = context.resolve_value(path_params)
for key, value in path_params.items():
    url = url.replace(f'{{{key}}}', str(value))
```

#### Request Body
```python
# 1. Start with Body component or inline body
body = api_definition.request_body.example_data or api_definition.inline_request_body

# 2. Merge with script parameters
if 'body' in resolved_params:
    if isinstance(body, dict) and isinstance(resolved_params['body'], dict):
        body.update(resolved_params['body'])
    else:
        body = resolved_params['body']

# 3. Resolve variables
body = context.resolve_value(body)
```

## Response Validation

The `_validate_response()` method validates HTTP responses against assertion rules defined in the script.

### Supported Assertion Types

#### 1. Status Code
```python
{
    "type": "status_code",
    "expected": 200,
    "message": "Status should be 200"
}
```

#### 2. Equals
```python
{
    "type": "equals",
    "path": "$.data.name",
    "expected": "John Doe",
    "message": "Name should be John Doe"
}
```

#### 3. Not Equals
```python
{
    "type": "not_equals",
    "path": "$.data.status",
    "expected": "deleted",
    "message": "Status should not be deleted"
}
```

#### 4. Contains
```python
{
    "type": "contains",
    "path": "$.data.tags",
    "expected": "important",
    "message": "Tags should contain 'important'"
}
```

#### 5. Not Contains
```python
{
    "type": "not_contains",
    "path": "$.data.tags",
    "expected": "spam",
    "message": "Tags should not contain 'spam'"
}
```

#### 6. Greater Than
```python
{
    "type": "greater_than",
    "path": "$.data.count",
    "expected": 10,
    "message": "Count should be greater than 10"
}
```

#### 7. Less Than
```python
{
    "type": "less_than",
    "path": "$.data.count",
    "expected": 100,
    "message": "Count should be less than 100"
}
```

#### 8. Regex Match
```python
{
    "type": "regex_match",
    "path": "$.data.email",
    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "message": "Email should be valid"
}
```

#### 9. JSONPath
```python
{
    "type": "json_path",
    "path": "$.data.id",
    "assertion": "exists",  # or "not_exists", "equals"
    "expected": 123,  # only for "equals"
    "message": "ID should exist"
}
```

#### 10. Response Time
```python
{
    "type": "response_time",
    "expected": 2.0,  # seconds
    "message": "Response time should be under 2 seconds"
}
```

### Assertion Result Format

```python
{
    "type": "status_code",
    "expected": 200,
    "actual": 200,
    "passed": True,
    "message": "Status should be 200",
    "error": None  # or error message if failed
}
```

## Variable Extraction

The `_extract_variables()` method extracts values from HTTP responses using JSONPath expressions.

### Configuration Format

```python
extract_variables = {
    "user_id": "$.data.id",
    "user_name": "$.data.name",
    "auth_token": "$.data.token"
}
```

### Extraction Process

1. For each variable in `extract_variables`:
   - Extract value using JSONPath expression
   - Store in execution context
   - Add to output variables

2. Extracted variables are available to:
   - Subsequent scripts in the same component
   - Subsequent components in the same test case
   - Variable resolution in later requests

### Example

```python
# Response:
{
    "data": {
        "id": 456,
        "name": "John Doe",
        "token": "abc123xyz"
    }
}

# Extract configuration:
extract_variables = {
    "user_id": "$.data.id",
    "user_name": "$.data.name",
    "auth_token": "$.data.token"
}

# Result:
{
    "user_id": 456,
    "user_name": "John Doe",
    "auth_token": "abc123xyz"
}

# Usage in next request:
headers = {
    "Authorization": "Bearer ${auth_token}"
}
# Resolves to: "Bearer abc123xyz"
```

## Timeout Configuration

Timeout is configured with the following priority:

1. **Script Override** (`script.timeout_override`)
2. **API Definition** (`api_definition.timeout`)
3. **HTTP Client Default** (10s connect, 30s read)

```python
timeout = None
if script.timeout_override:
    timeout = (10, script.timeout_override)
elif api_definition.timeout:
    timeout = (10, api_definition.timeout)
# else: use HTTP client default
```

## Error Handling

### Request Building Errors

- Missing API definition
- Invalid parameter types
- Variable resolution failures

### HTTP Request Errors

- Connection errors (retried automatically)
- Timeout errors (retried automatically)
- HTTP errors (4xx, 5xx)

### Validation Errors

- Assertion failures
- JSONPath extraction failures
- Type conversion errors

### Error Result Format

```python
{
    "status": "failed",
    "success": False,
    "error": "Error message",
    "duration": 1.234
}
```

## Usage Examples

### Basic Script Execution

```python
from morado.models.script import TestScript
from morado.services.execution_context import ScriptExecutionContext
from morado.services.execution_engine import ExecutionEngine

# Create script with API definition
script = TestScript(
    name="Get User",
    api_definition=api_definition,
    assertions=[
        {
            "type": "status_code",
            "expected": 200
        }
    ],
    extract_variables={
        "user_id": "$.data.id"
    }
)

# Create execution context
context = ScriptExecutionContext(script)

# Execute script
engine = ExecutionEngine()
result = await engine.execute_script(script, context)

print(f"Success: {result.success}")
print(f"User ID: {result.output_variables['user_id']}")
```

### Script with Parameter Override

```python
# Create context with parameter overrides
context = ScriptExecutionContext(
    script,
    override_params={
        "headers": {
            "Authorization": "Bearer token123"
        },
        "path_params": {
            "id": 999
        },
        "body": {
            "age": 30
        }
    }
)

# Execute script
result = await engine.execute_script(script, context)
```

### Script with Variable Resolution

```python
# Set variables in context
context.set_param("user_id", 123)
context.set_param("auth_token", "abc123")

# API definition with variables
api_definition.path = "/api/users/${user_id}"
api_definition.header.headers = {
    "Authorization": "Bearer ${auth_token}"
}

# Execute script (variables will be resolved)
result = await engine.execute_script(script, context)
```

## Testing

The integration includes comprehensive tests in `backend/scripts/verify_execution_engine_integration.py`:

1. **Request Building Test**: Verifies correct merging of parameters
2. **Response Validation Test**: Verifies assertion execution
3. **Variable Extraction Test**: Verifies JSONPath extraction
4. **Full Execution Test**: Verifies end-to-end script execution

Run tests:
```bash
$env:PYTHONPATH="backend/src"
.venv\Scripts\python.exe backend/scripts/verify_execution_engine_integration.py
```

## Requirements Validation

This integration satisfies the following requirements:

- **Requirement 1.1**: Constructs complete HTTP requests from API definitions
- **Requirement 1.3**: Merges headers, body, and parameters from multiple sources
- **Requirement 6.1**: Replaces path parameter placeholders
- **Requirement 6.2**: Resolves variable placeholders from execution context
- **Requirement 7.5**: Provides detailed error information on validation failure

## Future Enhancements

1. **Pre/Post Scripts**: Execute Python/JavaScript code before/after requests
2. **Conditional Execution**: Skip requests based on conditions
3. **Response Caching**: Cache responses for repeated requests
4. **Mock Support**: Mock responses for testing
5. **Performance Metrics**: Collect detailed performance metrics
