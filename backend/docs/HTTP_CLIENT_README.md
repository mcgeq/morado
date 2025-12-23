# HTTP Client Wrapper Documentation

Complete documentation for the Morado HTTP Client Wrapper.

## Overview

The Morado HTTP Client Wrapper provides a unified, reliable, and observable HTTP client for the test platform. It wraps the Python `requests` library and adds enterprise features like:

- ✅ Automatic retry with configurable strategies
- ✅ Timeout control at multiple levels
- ✅ Request/response logging with structlog integration
- ✅ Request tracing with execution context
- ✅ Session management with connection pooling
- ✅ Interceptor mechanism for custom logic
- ✅ File upload and download support
- ✅ JSONPath extraction from responses
- ✅ Comprehensive error handling

## Quick Start

```python
from morado.common.http import create_default_client

# Create a client with default settings
client = create_default_client()

# Make a GET request
response = client.get("https://api.example.com/users")

# Access response data
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")

# Clean up
client.close()
```

Or use a context manager for automatic cleanup:

```python
from morado.common.http import create_default_client

with create_default_client() as client:
    response = client.get("https://api.example.com/users")
    users = response.json()
    print(f"Found {len(users)} users")
```

## Documentation

### Core Documentation

1. **[Usage Guide](http_client_usage_guide.md)** - Complete guide to using the HTTP client
   - Basic usage and common patterns
   - Configuration options
   - Advanced features (retry, file operations, etc.)
   - Best practices

2. **[API Reference](http_client_api_reference.md)** - Detailed API documentation
   - All classes and methods
   - Parameters and return types
   - Examples for each API

3. **[Configuration Guide](http_client_configuration_guide.md)** - Configuration reference
   - All configuration options
   - Environment-specific configurations
   - Loading from files (TOML, JSON, etc.)
   - Configuration best practices

4. **[Interceptor Development Guide](http_client_interceptor_guide.md)** - Creating custom interceptors
   - Request and response interceptors
   - Built-in interceptors
   - Custom interceptor examples
   - Best practices

5. **[Troubleshooting Guide](http_client_troubleshooting.md)** - Common issues and solutions
   - Connection issues
   - Timeout issues
   - Authentication issues
   - Performance issues
   - Debugging tips

6. **[Examples](http_client_examples.py)** - Practical code examples
   - Basic usage examples
   - Configuration examples
   - Advanced patterns
   - API client class example

## Features

### Automatic Retry

Automatically retry failed requests with configurable strategies:

```python
from morado.common.http import create_http_client, HttpClientConfig

config = HttpClientConfig(
    enable_retry=True,
    max_retries=5,
    retry_strategy="exponential",  # or "fixed" or "linear"
    initial_delay=1.0,
    max_delay=60.0
)

client = create_http_client(config)
```

**Retry Strategies:**
- **Fixed**: Same delay between each retry
- **Exponential**: Delay doubles with each retry (1s, 2s, 4s, 8s, ...)
- **Linear**: Delay increases linearly (1s, 2s, 3s, 4s, ...)

**Retryable Errors:**
- Network connection errors
- Timeout errors (both connect and read)
- HTTP 5xx server errors

### Timeout Control

Configure timeouts at multiple levels:

```python
# Global configuration
config = HttpClientConfig(
    connect_timeout=15,  # Connection timeout
    read_timeout=60      # Read timeout
)
client = create_http_client(config)

# Per-request override
response = client.get("/users", timeout=(30, 120))
```

### Request/Response Logging

Automatic logging with structlog integration:

```python
config = HttpClientConfig(
    enable_logging=True,
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=2048
)

client = create_http_client(config)
```

Logs include:
- Request: method, URL, headers, body, params
- Response: status code, headers, body, duration
- Errors: exception type, message, stack trace

### Request Tracing

Automatic request tracing with execution context:

```python
from morado.common.http import create_default_client
from morado.services.execution_context import ExecutionContext

context = ExecutionContext(
    request_id="req-123",
    user_id=456
)

with context:
    client = create_default_client(enable_tracing=True)
    response = client.get("https://api.example.com/users")
    # Request includes header: X-Request-ID: req-123
```

### Session Management

Maintain state across multiple requests:

```python
from morado.common.http import HttpClient, SessionManager

session_manager = SessionManager(
    pool_connections=20,
    pool_maxsize=20
)

client = HttpClient(session_manager=session_manager)

# Make multiple requests - cookies and connections are reused
response1 = client.post("/login", json={"username": "john", "password": "secret"})
response2 = client.get("/profile")  # Uses cookies from login
response3 = client.get("/settings")  # Reuses connection

client.close()
```

### Interceptors

Add custom logic before/after requests:

```python
from morado.common.http.interceptor import RequestInterceptor

class AuthInterceptor(RequestInterceptor):
    def __init__(self, token):
        self.token = token
    
    def before_request(self, method, url, headers, **kwargs):
        headers["Authorization"] = f"Bearer {self.token}"
        return method, url, headers, kwargs

client = create_default_client()
client.interceptor_manager.add_request_interceptor(
    AuthInterceptor(token="your-token")
)
```

### File Operations

Upload and download files easily:

```python
# Single file upload
response = client.upload_file(
    "https://api.example.com/upload",
    "/path/to/document.pdf",
    file_field_name="document",
    additional_fields={"description": "My document"}
)

# Multiple file upload
response = client.upload_files(
    "https://api.example.com/upload",
    files={
        "document": "/path/to/document.pdf",
        "image": "/path/to/image.png"
    }
)

# File download
response = client.get("https://api.example.com/files/report.pdf")
response.save_to_file("/path/to/save/report.pdf")
```

### JSONPath Extraction

Extract data from JSON responses:

```python
response = client.get("https://api.example.com/users")

# Extract specific fields
user_names = response.jsonpath("$.users[*].name")
first_user_email = response.jsonpath("$.users[0].email")

# Complex queries
active_users = response.jsonpath("$.users[?(@.active == true)]")
```

## Architecture

The HTTP client is organized into modular components:

```
┌─────────────────────────────────────────────────────────────┐
│                  HTTP Client Facade                          │
│              (Unified Interface)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Interceptor │  │   Retry     │  │  Response   │
│   Manager   │  │  Strategy   │  │   Handler   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌─────────────────┐
              │ Session Manager │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  Core HTTP      │
              │  Client         │
              │  (requests)     │
              └─────────────────┘
```

## Module Structure

```
backend/src/morado/common/http/
├── __init__.py                 # Public API exports
├── client.py                   # Core HTTP client
├── session.py                  # Session manager
├── retry.py                    # Retry strategies
├── interceptor.py              # Request/response interceptors
├── logging_interceptor.py      # Logging interceptors
├── tracing_interceptor.py      # Tracing interceptor
├── response.py                 # Response wrapper
├── exceptions.py               # Custom exceptions
├── config.py                   # Configuration models
└── utils.py                    # Utility functions
```

## Configuration

### Default Configuration

```python
from morado.common.http import create_default_client

client = create_default_client(
    base_url="https://api.example.com",
    enable_retry=True,
    enable_logging=True,
    enable_tracing=True
)
```

### Custom Configuration

```python
from morado.common.http import create_http_client, HttpClientConfig

config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=15,
    read_timeout=60,
    pool_connections=20,
    pool_maxsize=20,
    enable_retry=True,
    max_retries=5,
    retry_strategy="exponential",
    initial_delay=1.0,
    max_delay=60.0,
    enable_logging=True,
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=2048,
    enable_tracing=True,
    trace_header_name="X-Request-ID"
)

client = create_http_client(config)
```

### From TOML File

```python
from morado.common.http import load_config_from_toml, create_http_client

config = load_config_from_toml("config/http_client.toml")
client = create_http_client(config)
```

Example TOML file:

```toml
[http_client]
base_url = "https://api.example.com"
connect_timeout = 15
read_timeout = 60
enable_retry = true
max_retries = 5
retry_strategy = "exponential"
enable_logging = true
enable_tracing = true
```

## Best Practices

1. **Use Context Managers** - Always use context managers for automatic cleanup
2. **Set Base URL** - Use base_url to avoid repeating it in every request
3. **Handle Errors** - Always handle exceptions gracefully
4. **Configure Timeouts** - Set appropriate timeouts for your use case
5. **Use Retry for Unreliable Services** - Enable retry for external APIs
6. **Reuse Client Instances** - Don't create new clients for each request
7. **Close Clients** - Always close clients when done

## Common Patterns

### API Client Class

```python
from morado.common.http import create_default_client

class UserAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = create_default_client(base_url=base_url)
        self.api_key = api_key
    
    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    def get_user(self, user_id: int) -> dict:
        response = self.client.get(
            f"/users/{user_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def close(self):
        self.client.close()
```

### Pagination

```python
def fetch_all_users(client) -> list[dict]:
    all_users = []
    page = 1
    
    while True:
        response = client.get("/users", params={"page": page, "limit": 100})
        response.raise_for_status()
        
        data = response.json()
        users = data.get("users", [])
        
        if not users:
            break
        
        all_users.extend(users)
        page += 1
    
    return all_users
```

## Error Handling

```python
from morado.common.http import (
    create_default_client,
    HttpTimeoutError,
    HttpConnectionError,
    HttpRequestError
)

with create_default_client() as client:
    try:
        response = client.get("https://api.example.com/users")
        response.raise_for_status()
        users = response.json()
        
    except HttpTimeoutError as e:
        print(f"Request timed out: {e}")
    except HttpConnectionError as e:
        print(f"Connection failed: {e}")
    except HttpRequestError as e:
        print(f"Request failed: {e}")
```

## Testing

The HTTP client includes comprehensive test coverage:

- **Unit Tests** - Test individual components
- **Property-Based Tests** - Test universal properties with Hypothesis
- **Integration Tests** - Test with real HTTP servers

Run tests:

```bash
# All tests
pytest tests/backend/unit/test_http/

# Specific test file
pytest tests/backend/unit/test_http/test_client.py

# With coverage
pytest --cov=morado.common.http tests/backend/unit/test_http/
```

## Performance

### Connection Pooling

The client uses connection pooling for better performance:

```python
config = HttpClientConfig(
    pool_connections=50,  # Number of different hosts
    pool_maxsize=50       # Max connections per host
)
```

### Reuse Clients

Reuse client instances instead of creating new ones:

```python
# Good - reuse client
client = create_default_client()
for i in range(100):
    response = client.get(f"/users/{i}")
client.close()

# Bad - creates new client each time
for i in range(100):
    client = create_default_client()
    response = client.get(f"/users/{i}")
    client.close()
```

### Streaming Large Files

Use streaming for large files to avoid memory issues:

```python
response = client.get("/large-file", stream=True)
with open("output.bin", "wb") as f:
    for chunk in response._response.iter_content(chunk_size=8192):
        f.write(chunk)
```

## Security

- **SSL/TLS Verification** - Enabled by default
- **Sensitive Data Masking** - Automatic masking in logs
- **Timeout Protection** - Prevents resource exhaustion
- **URL Validation** - Validates URL format

## Contributing

When contributing to the HTTP client:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Add examples for new features

## Support

For issues or questions:

1. Check the [Troubleshooting Guide](http_client_troubleshooting.md)
2. Review the [API Reference](http_client_api_reference.md)
3. Look at [Examples](http_client_examples.py)
4. Check existing tests for usage patterns

## License

Part of the Morado Test Platform.
