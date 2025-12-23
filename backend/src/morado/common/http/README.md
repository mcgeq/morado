# HTTP Client Wrapper

A unified, reliable, and observable HTTP client for the Morado test platform.

## Features

- ✅ **All HTTP Methods**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- ✅ **Automatic Retry**: Configurable retry strategies (fixed, exponential, linear)
- ✅ **Timeout Control**: Separate connection and read timeouts
- ✅ **Session Management**: Connection pooling and lifecycle management
- ✅ **Request/Response Interceptors**: Extensible hook system
- ✅ **Logging Integration**: Structured logging with structlog
- ✅ **Request Tracing**: Distributed tracing with execution context
- ✅ **File Operations**: Upload and download with streaming support
- ✅ **JSONPath Support**: Extract data from JSON responses
- ✅ **Variable Resolution**: Template variables in requests
- ✅ **Error Handling**: Specific exceptions for different error types

## Quick Start

```python
from morado.common.http import create_default_client

# Create a client with sensible defaults
client = create_default_client()

# Make a request
response = client.get("https://api.example.com/users")
print(response.json())
```

## Installation

The HTTP client wrapper is part of the Morado platform. No additional installation is required.

## Basic Usage

### Creating a Client

```python
from morado.common.http import create_default_client, create_http_client, HttpClientConfig

# Option 1: Default client (recommended for simple use cases)
client = create_default_client()

# Option 2: Default client with base URL
client = create_default_client(base_url="https://api.example.com")

# Option 3: Custom configuration
config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=15,
    max_retries=5
)
client = create_http_client(config)
```

### Making Requests

```python
# GET request
response = client.get("/users")

# POST request with JSON
response = client.post("/users", json={"name": "John"})

# PUT request
response = client.put("/users/123", json={"name": "John Updated"})

# DELETE request
response = client.delete("/users/123")
```

### Working with Responses

```python
response = client.get("/users/123")

# Status code
print(response.status_code)

# Check if successful
if response.is_success():
    print("Success!")

# Parse JSON
data = response.json()

# Get headers
content_type = response.get_header("Content-Type")

# Request timing
print(f"Request took {response.request_time:.2f}s")
```

### Context Manager

```python
from morado.common.http import create_default_client

with create_default_client() as client:
    response = client.get("https://api.example.com/users")
    print(response.json())
# Client is automatically closed
```

## Configuration

### Configuration Options

```python
from morado.common.http import HttpClientConfig

config = HttpClientConfig(
    # Base configuration
    base_url="https://api.example.com",
    connect_timeout=10,  # seconds
    read_timeout=30,     # seconds
    pool_connections=10,
    pool_maxsize=10,
    
    # Retry configuration
    enable_retry=True,
    max_retries=3,
    retry_strategy="exponential",  # "fixed", "exponential", or "linear"
    initial_delay=1.0,
    max_delay=60.0,
    
    # Logging configuration
    enable_logging=True,
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=1024,
    
    # Tracing configuration
    enable_tracing=True,
    trace_header_name="X-Request-ID"
)
```

### Loading from File

```python
from morado.common.http import load_config_from_toml, create_http_client

# Load from TOML file
config = load_config_from_toml("config/http_client.toml")
client = create_http_client(config)
```

Example TOML file:

```toml
[http_client]
base_url = "https://api.example.com"
connect_timeout = 15
read_timeout = 60
max_retries = 5
retry_strategy = "exponential"
enable_logging = true
enable_tracing = true
```

## Advanced Features

### File Upload

```python
# Upload single file
response = client.upload_file(
    "https://api.example.com/upload",
    "/path/to/file.pdf",
    file_field_name="document"
)

# Upload multiple files
response = client.upload_files(
    "https://api.example.com/upload",
    files={
        "document": "/path/to/doc.pdf",
        "image": "/path/to/img.png"
    }
)
```

### File Download

```python
# Download and save
response = client.get("https://api.example.com/files/report.pdf")
response.save_to_file("/path/to/save/report.pdf")

# Stream large files
bytes_written = response.stream_to_file("/path/to/save/large-file.zip")
```

### JSONPath Extraction

```python
response = client.get("/users")

# Extract all user names
names = response.jsonpath("$[*].name")

# Extract first user's email
email = response.jsonpath("$[0].email")
```

### Custom Interceptors

```python
from morado.common.http import RequestInterceptor

class AuthInterceptor(RequestInterceptor):
    def __init__(self, token):
        self.token = token
    
    def before_request(self, method, url, headers, **kwargs):
        headers["Authorization"] = f"Bearer {self.token}"
        return method, url, headers, kwargs

# Add to client
client = create_default_client()
client.interceptor_manager.add_request_interceptor(AuthInterceptor("token123"))
```

## Error Handling

```python
from morado.common.http import (
    HttpConnectionError,
    HttpTimeoutError,
    HttpRequestError,
    RetryExhaustedError
)

try:
    response = client.get("/users")
    response.raise_for_status()
except HttpConnectionError as e:
    print(f"Connection failed: {e}")
except HttpTimeoutError as e:
    print(f"Timeout ({e.timeout_type}): {e}")
except HttpRequestError as e:
    print(f"HTTP {e.status_code} error: {e}")
except RetryExhaustedError as e:
    print(f"All retries failed: {e}")
    print(f"Retry history: {e.retry_history}")
```

## Documentation

- [Usage Guide](../../../docs/http_client_usage_guide.md) - Comprehensive usage documentation
- [Examples](../../../docs/http_client_examples.py) - Code examples
- [Design Document](../../../../.kiro/specs/http-client-wrapper/design.md) - Architecture and design
- [Requirements](../../../../.kiro/specs/http-client-wrapper/requirements.md) - Feature requirements

## Architecture

The HTTP client wrapper is organized into the following modules:

- `client.py` - Core HTTP client with request methods
- `session.py` - Session management and connection pooling
- `retry.py` - Retry strategies and logic
- `interceptor.py` - Request/response interceptor framework
- `response.py` - Response wrapper with convenience methods
- `config.py` - Configuration models
- `exceptions.py` - Custom exception types
- `utils.py` - Utility functions
- `logging_interceptor.py` - Logging interceptors
- `tracing_interceptor.py` - Tracing interceptor

## Testing

The HTTP client wrapper includes comprehensive tests:

- Unit tests for all components
- Property-based tests for correctness properties
- Integration tests with real HTTP servers

Run tests:

```bash
# All tests
pytest tests/backend/unit/test_http/

# Specific test file
pytest tests/backend/unit/test_http/test_client.py

# With coverage
pytest --cov=morado.common.http tests/backend/unit/test_http/
```

## Contributing

When contributing to the HTTP client wrapper:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## License

Part of the Morado test platform.
