# HTTP Client Troubleshooting Guide

Common issues and solutions for the Morado HTTP Client Wrapper.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Timeout Issues](#timeout-issues)
- [Retry Issues](#retry-issues)
- [Authentication Issues](#authentication-issues)
- [Response Parsing Issues](#response-parsing-issues)
- [File Upload Issues](#file-upload-issues)
- [Configuration Issues](#configuration-issues)
- [Performance Issues](#performance-issues)
- [Logging and Debugging](#logging-and-debugging)

## Connection Issues

### Problem: Connection Refused

**Symptoms:**
```
HttpConnectionError: Connection error for URL https://api.example.com: Connection refused
```

**Possible Causes:**
1. Server is not running
2. Wrong URL or port
3. Firewall blocking connection
4. Network connectivity issues

**Solutions:**

```python
# 1. Verify the URL is correct
client = create_default_client(base_url="https://api.example.com")

# 2. Check if server is accessible
import socket
try:
    socket.create_connection(("api.example.com", 443), timeout=5)
    print("Server is reachable")
except Exception as e:
    print(f"Server not reachable: {e}")

# 3. Try with explicit timeout
response = client.get("/users", timeout=(10, 30))

# 4. Check network connectivity
import requests
try:
    requests.get("https://www.google.com", timeout=5)
    print("Internet connection OK")
except Exception as e:
    print(f"No internet connection: {e}")
```

### Problem: SSL Certificate Verification Failed

**Symptoms:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions:**

```python
# For development/testing only - disable SSL verification
import requests
from morado.common.http import HttpClient, SessionManager

session_manager = SessionManager()
session = session_manager.create_session()
session.verify = False  # Disable SSL verification

client = HttpClient(session=session)

# For production - use custom CA certificate
session.verify = "/path/to/ca-bundle.crt"
```

**Warning:** Never disable SSL verification in production!

### Problem: DNS Resolution Failed

**Symptoms:**
```
HttpConnectionError: Failed to resolve hostname
```

**Solutions:**

```python
# 1. Verify DNS resolution
import socket
try:
    ip = socket.gethostbyname("api.example.com")
    print(f"Resolved to: {ip}")
except socket.gaierror as e:
    print(f"DNS resolution failed: {e}")

# 2. Use IP address directly (temporary workaround)
client = create_default_client(base_url="https://192.168.1.100")

# 3. Check /etc/hosts or DNS settings
```

## Timeout Issues

### Problem: Connection Timeout

**Symptoms:**
```
HttpTimeoutError: Connection timeout for URL https://api.example.com
```

**Solutions:**

```python
# 1. Increase connection timeout
config = HttpClientConfig(
    connect_timeout=30,  # Increase from default 10
    read_timeout=60
)
client = create_http_client(config)

# 2. Per-request timeout override
response = client.get("/users", timeout=(30, 60))

# 3. Check network latency
import time
start = time.time()
response = client.get("/users")
print(f"Request took: {time.time() - start:.2f}s")
```

### Problem: Read Timeout

**Symptoms:**
```
HttpTimeoutError: Read timeout for URL https://api.example.com
```

**Solutions:**

```python
# 1. Increase read timeout for slow endpoints
config = HttpClientConfig(
    connect_timeout=10,
    read_timeout=120  # Increase from default 30
)
client = create_http_client(config)

# 2. Use streaming for large responses
response = client.get("/large-file", stream=True)
with open("output.bin", "wb") as f:
    for chunk in response._response.iter_content(chunk_size=8192):
        f.write(chunk)

# 3. Check server response time
# If server is consistently slow, consider:
# - Optimizing server-side code
# - Adding pagination
# - Using async requests
```

### Problem: Timeout During Retry

**Symptoms:**
```
RetryExhaustedError: All retry attempts failed
```

**Solutions:**

```python
# 1. Adjust retry configuration
config = HttpClientConfig(
    enable_retry=True,
    max_retries=5,  # More retries
    retry_strategy="exponential",
    initial_delay=2.0,  # Longer initial delay
    max_delay=120.0  # Higher max delay
)
client = create_http_client(config)

# 2. Disable retry for specific requests
client_no_retry = create_default_client(enable_retry=False)
response = client_no_retry.get("/users")

# 3. Check retry history
try:
    response = client.get("/users")
except RetryExhaustedError as e:
    print("Retry history:")
    for attempt in e.retry_history:
        print(f"  Attempt {attempt['attempt']}: {attempt['error']}")
```

## Retry Issues

### Problem: Too Many Retries

**Symptoms:**
- Requests taking too long
- Excessive API calls

**Solutions:**

```python
# 1. Reduce retry count
config = HttpClientConfig(
    max_retries=2,  # Reduce from default 3
    retry_strategy="fixed",
    initial_delay=1.0
)
client = create_http_client(config)

# 2. Disable retry for specific scenarios
if environment == "development":
    client = create_default_client(enable_retry=False)
else:
    client = create_default_client(enable_retry=True)

# 3. Use fixed delay instead of exponential
config = HttpClientConfig(
    retry_strategy="fixed",  # Same delay each time
    initial_delay=1.0
)
```

### Problem: Retrying Non-Retryable Errors

**Symptoms:**
- 4xx errors being retried
- Wasting time on permanent failures

**Solution:**

The client automatically handles this - only retries:
- Network errors
- Timeout errors
- 5xx server errors

4xx client errors are NOT retried by default.

## Authentication Issues

### Problem: 401 Unauthorized

**Symptoms:**
```
Response status: 401 Unauthorized
```

**Solutions:**

```python
# 1. Add authentication header
response = client.get("/users", headers={
    "Authorization": "Bearer your-token-here"
})

# 2. Use authentication interceptor
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

# 3. Check token expiration
import jwt
try:
    decoded = jwt.decode(token, options={"verify_signature": False})
    exp = decoded.get("exp")
    if exp and time.time() > exp:
        print("Token expired - refresh needed")
except Exception as e:
    print(f"Invalid token: {e}")
```

### Problem: 403 Forbidden

**Symptoms:**
```
Response status: 403 Forbidden
```

**Solutions:**

```python
# 1. Check permissions
# Ensure your API key/token has required permissions

# 2. Verify API key is correct
response = client.get("/users", headers={
    "X-API-Key": "your-api-key"
})

# 3. Check IP whitelist
# Some APIs restrict access by IP address
```

## Response Parsing Issues

### Problem: JSON Decode Error

**Symptoms:**
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solutions:**

```python
# 1. Check if response is actually JSON
response = client.get("/users")
content_type = response.get_header("Content-Type")
print(f"Content-Type: {content_type}")

if "application/json" in content_type:
    data = response.json()
else:
    print(f"Not JSON: {response.text}")

# 2. Handle empty responses
try:
    data = response.json()
except Exception as e:
    if not response.text:
        print("Empty response")
        data = {}
    else:
        raise

# 3. Check response status first
response = client.get("/users")
if response.is_success():
    data = response.json()
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Problem: JSONPath Extraction Failed

**Symptoms:**
```
JSONPathError: JSONPath extraction failed
```

**Solutions:**

```python
# 1. Verify JSON structure
response = client.get("/users")
data = response.json()
print(json.dumps(data, indent=2))

# 2. Test JSONPath expression
try:
    result = response.jsonpath("$.users[*].name")
    print(f"Found: {result}")
except JSONPathError as e:
    print(f"JSONPath error: {e}")
    # Try simpler path
    result = response.jsonpath("$.users")

# 3. Handle missing fields
try:
    email = response.jsonpath("$.user.email")
except JSONPathError:
    email = None  # Field doesn't exist
```

## File Upload Issues

### Problem: File Not Found

**Symptoms:**
```
FileNotFoundError: File not found: /path/to/file.pdf
```

**Solutions:**

```python
# 1. Verify file exists
from pathlib import Path

file_path = "/path/to/file.pdf"
if not Path(file_path).exists():
    print(f"File not found: {file_path}")
else:
    response = client.upload_file(url, file_path)

# 2. Use absolute path
file_path = Path("/path/to/file.pdf").resolve()
response = client.upload_file(url, str(file_path))

# 3. Check file permissions
if not Path(file_path).is_file():
    print("Not a file or no read permission")
```

### Problem: Upload Timeout

**Symptoms:**
```
HttpTimeoutError: Read timeout during file upload
```

**Solutions:**

```python
# 1. Increase timeout for large files
response = client.upload_file(
    url,
    "/path/to/large-file.zip",
    timeout=(30, 300)  # 5 minute read timeout
)

# 2. Check file size
file_size = Path(file_path).stat().st_size
print(f"File size: {file_size / 1024 / 1024:.2f} MB")

# 3. Use streaming for very large files
with open(file_path, "rb") as f:
    response = client.post(
        url,
        data=f,
        headers={"Content-Type": "application/octet-stream"},
        timeout=(30, 600)
    )
```

### Problem: Multipart Upload Failed

**Symptoms:**
```
Server returns 400 Bad Request for multipart upload
```

**Solutions:**

```python
# 1. Verify multipart format
response = client.upload_file(
    url,
    file_path,
    file_field_name="file",  # Match server expectation
    additional_fields={"description": "My file"}
)

# 2. Check server requirements
# Some servers expect specific field names or formats

# 3. Use manual multipart
with open(file_path, "rb") as f:
    files = {"file": (Path(file_path).name, f, "application/pdf")}
    response = client.post(url, files=files)
```

## Configuration Issues

### Problem: Invalid Configuration

**Symptoms:**
```
ValidationError: base_url must start with http:// or https://
```

**Solutions:**

```python
# 1. Fix base_url
config = HttpClientConfig(
    base_url="https://api.example.com"  # Add https://
)

# 2. Validate configuration
try:
    config = HttpClientConfig(**config_dict)
    print("Configuration valid")
except ValidationError as e:
    print("Configuration errors:")
    for error in e.errors():
        print(f"  {error['loc'][0]}: {error['msg']}")

# 3. Use default values
config = HttpClientConfig()  # All defaults
```

### Problem: Configuration Not Loading

**Symptoms:**
```
FileNotFoundError: Configuration file not found
```

**Solutions:**

```python
# 1. Check file path
from pathlib import Path

config_path = "config/http_client.toml"
if not Path(config_path).exists():
    print(f"Config file not found: {config_path}")
    # Use default configuration
    config = HttpClientConfig()
else:
    config = load_config_from_toml(config_path)

# 2. Use absolute path
config_path = Path(__file__).parent / "config" / "http_client.toml"
config = load_config_from_toml(str(config_path))

# 3. Handle missing TOML library
try:
    config = load_config_from_toml(config_path)
except ImportError:
    print("Install tomli: pip install tomli")
    # Use dict configuration instead
    config = load_config_from_dict(config_dict)
```

## Performance Issues

### Problem: Slow Requests

**Symptoms:**
- Requests taking longer than expected
- High latency

**Solutions:**

```python
# 1. Measure request time
import time

start = time.time()
response = client.get("/users")
duration = time.time() - start
print(f"Request took: {duration:.2f}s")

# 2. Increase connection pool
config = HttpClientConfig(
    pool_connections=50,  # More pools
    pool_maxsize=50  # More connections per pool
)
client = create_http_client(config)

# 3. Reuse client instance
# Bad - creates new client each time
for i in range(100):
    client = create_default_client()
    response = client.get("/users")
    client.close()

# Good - reuse client
client = create_default_client()
for i in range(100):
    response = client.get("/users")
client.close()

# 4. Use session for multiple requests
with create_default_client() as client:
    for i in range(100):
        response = client.get(f"/users/{i}")
```

### Problem: Memory Issues

**Symptoms:**
- High memory usage
- Out of memory errors

**Solutions:**

```python
# 1. Use streaming for large responses
response = client.get("/large-file", stream=True)
with open("output.bin", "wb") as f:
    for chunk in response._response.iter_content(chunk_size=8192):
        f.write(chunk)

# 2. Close clients properly
client = create_default_client()
try:
    response = client.get("/users")
finally:
    client.close()

# 3. Limit log body size
config = HttpClientConfig(
    max_log_body_size=512  # Smaller log size
)

# 4. Disable logging for high-volume requests
client = create_default_client(enable_logging=False)
```

## Logging and Debugging

### Enable Debug Logging

```python
import logging

# Enable debug logging for HTTP client
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("morado.common.http")
logger.setLevel(logging.DEBUG)

# Make request
client = create_default_client(enable_logging=True)
response = client.get("https://api.example.com/users")
```

### Inspect Request Details

```python
# Use logging interceptor
from morado.common.http.logging_interceptor import LoggingInterceptor

config = HttpClientConfig(
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=4096  # More verbose
)

client = create_default_client()
client.interceptor_manager.add_request_interceptor(
    LoggingInterceptor(config=config)
)

response = client.get("/users")
```

### Debug Interceptors

```python
class DebugInterceptor(RequestInterceptor):
    def before_request(self, method, url, headers, **kwargs):
        print(f"Request: {method} {url}")
        print(f"Headers: {headers}")
        print(f"Params: {kwargs.get('params')}")
        return method, url, headers, kwargs

client = create_default_client()
client.interceptor_manager.add_request_interceptor(DebugInterceptor())
```

### Capture Raw Response

```python
response = client.get("/users")

# Access raw response object
raw_response = response._response

# Get raw content
raw_content = raw_response.content
print(f"Raw content: {raw_content[:100]}")

# Get all headers
print(f"All headers: {raw_response.headers}")

# Get request details
print(f"Request URL: {raw_response.request.url}")
print(f"Request headers: {raw_response.request.headers}")
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** - Enable debug logging to see detailed information
2. **Test with curl** - Verify the API works outside the client
3. **Check API documentation** - Ensure you're using the API correctly
4. **Review configuration** - Verify all settings are correct
5. **Create minimal reproduction** - Isolate the issue with minimal code
6. **Check for updates** - Ensure you're using the latest version

### Minimal Reproduction Example

```python
from morado.common.http import create_default_client

# Minimal code to reproduce issue
client = create_default_client()
try:
    response = client.get("https://api.example.com/users")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
finally:
    client.close()
```
