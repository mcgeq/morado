# HTTP Client Usage Guide

## Overview

The Morado HTTP Client Wrapper provides a unified, reliable, and observable HTTP client for the test platform. It wraps the Python `requests` library and adds enterprise features like automatic retry, timeout control, logging, and request tracing.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Quick Start

### Installation

The HTTP client is part of the Morado platform and requires no additional installation beyond the platform dependencies.

### Simple Example

```python
from morado.common.http import create_default_client

# Create a client with default settings
client = create_default_client()

# Make a GET request
response = client.get("https://api.example.com/users")

# Access response data
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")
```

### With Context Manager

```python
from morado.common.http import create_default_client

# Automatically clean up resources
with create_default_client() as client:
    response = client.get("https://api.example.com/users")
    users = response.json()
    print(f"Found {len(users)} users")
```

## Basic Usage

### Making Requests

The HTTP client supports all standard HTTP methods:

```python
from morado.common.http import create_default_client

client = create_default_client(base_url="https://api.example.com")

# GET request
response = client.get("/users")

# POST request with JSON body
response = client.post("/users", json={"name": "John", "email": "john@example.com"})

# PUT request
response = client.put("/users/123", json={"name": "John Updated"})

# PATCH request
response = client.patch("/users/123", json={"email": "newemail@example.com"})

# DELETE request
response = client.delete("/users/123")

# HEAD request
response = client.head("/users")

# OPTIONS request
response = client.options("/users")
```

### Working with Responses

The `HttpResponse` object provides convenient methods for accessing response data:

```python
# Get status code
status = response.status_code

# Check if successful (2xx)
if response.is_success():
    print("Request succeeded!")

# Get response text
text = response.text

# Parse JSON response
data = response.json()

# Get response headers
content_type = response.get_header("Content-Type")
all_headers = response.headers

# Get request duration
duration = response.request_time
print(f"Request took {duration:.2f} seconds")

# Raise exception if not successful
response.raise_for_status()
```

### Query Parameters

```python
# Pass query parameters
response = client.get("/users", params={
    "page": 1,
    "limit": 10,
    "sort": "name"
})
# Requests: GET /users?page=1&limit=10&sort=name
```

### Request Headers

```python
# Add custom headers
response = client.get("/users", headers={
    "Authorization": "Bearer token123",
    "Accept": "application/json"
})

# Headers are automatically merged with default headers
```

### Request Body

```python
# JSON body
response = client.post("/users", json={
    "name": "John",
    "email": "john@example.com"
})

# Form data
response = client.post("/login", data={
    "username": "john",
    "password": "secret"
})

# Raw body
response = client.post("/data", data=b"raw binary data", headers={
    "Content-Type": "application/octet-stream"
})
```

### Timeout Control

```python
# Set timeout for a specific request (connect_timeout, read_timeout)
response = client.get("/users", timeout=(5, 15))

# Use default timeout from configuration
response = client.get("/users")
```

## Configuration

### Using Default Client

The simplest way to create a client:

```python
from morado.common.http import create_default_client

# With all defaults
client = create_default_client()

# With base URL
client = create_default_client(base_url="https://api.example.com")

# Disable retry
client = create_default_client(enable_retry=False)

# Disable logging
client = create_default_client(enable_logging=False)
```

### Using Configuration Object

For more control, use `HttpClientConfig`:

```python
from morado.common.http import create_http_client, HttpClientConfig

config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=15,
    read_timeout=60,
    max_retries=5,
    retry_strategy="exponential",
    enable_logging=True,
    enable_tracing=True,
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=2048
)

client = create_http_client(config)
```

### Loading Configuration from File

#### From Dictionary

```python
from morado.common.http import load_config_from_dict, create_http_client

config_dict = {
    "base_url": "https://api.example.com",
    "connect_timeout": 15,
    "read_timeout": 60,
    "max_retries": 5,
    "retry_strategy": "exponential"
}

config = load_config_from_dict(config_dict)
client = create_http_client(config)
```

#### From TOML File

```python
from morado.common.http import load_config_from_toml, create_http_client

# Load from TOML file
config = load_config_from_toml("config/http_client.toml")
client = create_http_client(config)
```

Example TOML file (`config/http_client.toml`):

```toml
[http_client]
base_url = "https://api.example.com"
connect_timeout = 15
read_timeout = 60
pool_connections = 20
pool_maxsize = 20

# Retry configuration
enable_retry = true
max_retries = 5
retry_strategy = "exponential"
initial_delay = 1.0
max_delay = 60.0

# Logging configuration
enable_logging = true
log_request_body = true
log_response_body = true
max_log_body_size = 2048

# Tracing configuration
enable_tracing = true
trace_header_name = "X-Request-ID"
```

## Advanced Features

### Automatic Retry

The client automatically retries failed requests based on configuration:

```python
from morado.common.http import create_http_client, HttpClientConfig

config = HttpClientConfig(
    enable_retry=True,
    max_retries=3,
    retry_strategy="exponential",  # or "fixed" or "linear"
    initial_delay=1.0,
    max_delay=60.0
)

client = create_http_client(config)

# This request will be retried up to 3 times on failure
response = client.get("https://api.example.com/users")
```

**Retry Strategies:**

- **Fixed**: Same delay between each retry
- **Exponential**: Delay doubles with each retry (1s, 2s, 4s, 8s, ...)
- **Linear**: Delay increases linearly (1s, 2s, 3s, 4s, ...)

**Retryable Errors:**

- Network connection errors
- Timeout errors (both connect and read)
- HTTP 5xx server errors

**Non-Retryable Errors:**

- HTTP 4xx client errors
- JSON parsing errors
- Variable resolution errors

### File Upload

#### Single File Upload

```python
# Simple file upload
response = client.upload_file(
    "https://api.example.com/upload",
    "/path/to/document.pdf"
)

# With custom field name and additional fields
response = client.upload_file(
    "https://api.example.com/upload",
    "/path/to/document.pdf",
    file_field_name="document",
    additional_fields={
        "title": "My Document",
        "category": "reports"
    }
)
```

#### Multiple File Upload

```python
response = client.upload_files(
    "https://api.example.com/upload",
    files={
        "document": "/path/to/document.pdf",
        "image": "/path/to/image.png",
        "data": "/path/to/data.csv"
    },
    additional_fields={
        "description": "Multiple files upload"
    }
)
```

#### Advanced Multipart Upload

```python
# Full control over multipart upload
with open("/path/to/file.pdf", "rb") as f:
    response = client.upload_multipart(
        "https://api.example.com/upload",
        files={
            "document": ("report.pdf", f, "application/pdf"),
            "thumbnail": ("thumb.png", image_bytes, "image/png")
        },
        data={
            "title": "My Report",
            "category": "finance"
        }
    )
```

### File Download

```python
# Download and save to file
response = client.get("https://api.example.com/files/report.pdf")
response.save_to_file("/path/to/save/report.pdf")

# Stream large files
response = client.get("https://api.example.com/files/large.zip", stream=True)
with open("/path/to/save/large.zip", "wb") as f:
    for chunk in response._response.iter_content(chunk_size=8192):
        f.write(chunk)
```

### JSONPath Extraction

Extract data from JSON responses using JSONPath:

```python
response = client.get("https://api.example.com/users")

# Extract specific fields
user_names = response.jsonpath("$.users[*].name")
first_user_email = response.jsonpath("$.users[0].email")

# Complex queries
active_users = response.jsonpath("$.users[?(@.active == true)]")
```

### Session Management

Sessions maintain state across multiple requests:

```python
from morado.common.http import HttpClient, SessionManager

# Create a session manager
session_manager = SessionManager(
    pool_connections=20,
    pool_maxsize=20
)

# Create client with session
client = HttpClient(session_manager=session_manager)

# Make multiple requests - cookies and connections are reused
response1 = client.post("/login", json={"username": "john", "password": "secret"})
response2 = client.get("/profile")  # Uses cookies from login
response3 = client.get("/settings")  # Reuses connection

# Clean up
client.close()
```

### Request Tracing

Automatic request tracing with execution context:

```python
from morado.common.http import create_default_client
from morado.services.execution_context import ExecutionContext

# Create execution context
context = ExecutionContext(
    request_id="req-123",
    user_id=456,
    script_id=789
)

# Client automatically adds X-Request-ID header
with context:
    client = create_default_client(enable_tracing=True)
    response = client.get("https://api.example.com/users")
    # Request includes header: X-Request-ID: req-123
```

### Logging Integration

Automatic logging of requests and responses:

```python
from morado.common.http import create_default_client

# Enable logging (enabled by default)
client = create_default_client(enable_logging=True)

# Logs include:
# - Request: method, URL, headers, body, params
# - Response: status code, headers, body, duration
# - Errors: exception type, message, stack trace

response = client.get("https://api.example.com/users")
# Logs: "HTTP request" with method=GET, url=https://api.example.com/users
# Logs: "HTTP response" with status_code=200, duration=0.234
```

## Best Practices

### 1. Use Context Managers

Always use context managers to ensure proper resource cleanup:

```python
# Good
with create_default_client() as client:
    response = client.get("https://api.example.com/users")
    process_users(response.json())

# Also good - explicit cleanup
client = create_default_client()
try:
    response = client.get("https://api.example.com/users")
    process_users(response.json())
finally:
    client.close()
```

### 2. Use Base URL

Set a base URL to avoid repeating it in every request:

```python
# Good
client = create_default_client(base_url="https://api.example.com")
response1 = client.get("/users")
response2 = client.get("/posts")

# Less ideal
client = create_default_client()
response1 = client.get("https://api.example.com/users")
response2 = client.get("https://api.example.com/posts")
```

### 3. Handle Errors Gracefully

```python
from morado.common.http import (
    create_default_client,
    HttpTimeoutError,
    HttpConnectionError,
    HttpRequestError
)

client = create_default_client()

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

### 4. Configure Timeouts Appropriately

```python
# For fast APIs
client = create_http_client(HttpClientConfig(
    connect_timeout=5,
    read_timeout=10
))

# For slow APIs or large responses
client = create_http_client(HttpClientConfig(
    connect_timeout=15,
    read_timeout=120
))
```

### 5. Use Retry for Unreliable Services

```python
# Enable retry for external APIs
client = create_http_client(HttpClientConfig(
    enable_retry=True,
    max_retries=5,
    retry_strategy="exponential"
))

# Disable retry for internal services
client = create_http_client(HttpClientConfig(
    enable_retry=False
))
```

## Common Patterns

### API Client Class

```python
from morado.common.http import create_default_client, HttpClient

class UserAPIClient:
    """Client for User API."""
    
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
    
    def create_user(self, name: str, email: str) -> dict:
        response = self.client.post(
            "/users",
            json={"name": name, "email": email},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def close(self):
        self.client.close()

# Usage
api = UserAPIClient("https://api.example.com", "api-key-123")
try:
    user = api.get_user(123)
    print(f"User: {user['name']}")
finally:
    api.close()
```

### Pagination

```python
def fetch_all_users(client: HttpClient) -> list[dict]:
    """Fetch all users with pagination."""
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

### Batch Requests

```python
def batch_create_users(client: HttpClient, users: list[dict]) -> list[dict]:
    """Create multiple users in batch."""
    results = []
    
    for user in users:
        try:
            response = client.post("/users", json=user)
            response.raise_for_status()
            results.append({"success": True, "data": response.json()})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    
    return results
```

### Conditional Requests

```python
def get_if_modified(client: HttpClient, url: str, etag: str) -> Optional[dict]:
    """Get resource only if modified."""
    response = client.get(url, headers={"If-None-Match": etag})
    
    if response.status_code == 304:
        # Not modified
        return None
    
    response.raise_for_status()
    return response.json()
```

### Polling

```python
import time

def poll_until_complete(client: HttpClient, job_id: str, timeout: int = 300) -> dict:
    """Poll job status until complete."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = client.get(f"/jobs/{job_id}")
        response.raise_for_status()
        
        job = response.json()
        status = job.get("status")
        
        if status == "completed":
            return job
        elif status == "failed":
            raise Exception(f"Job failed: {job.get('error')}")
        
        time.sleep(5)  # Wait 5 seconds before next poll
    
    raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
```

## Next Steps

- [API Reference](http_client_api_reference.md) - Detailed API documentation
- [Configuration Guide](http_client_configuration_guide.md) - Complete configuration options
- [Interceptor Development Guide](http_client_interceptor_guide.md) - Creating custom interceptors
- [Troubleshooting Guide](http_client_troubleshooting.md) - Common issues and solutions
