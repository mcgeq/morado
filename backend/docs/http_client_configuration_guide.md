# HTTP Client Configuration Guide

Complete guide to configuring the Morado HTTP Client Wrapper.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Configuration Methods](#configuration-methods)
- [Configuration Options](#configuration-options)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Advanced Configuration](#advanced-configuration)

## Configuration Overview

The HTTP client can be configured in multiple ways:

1. **Default Configuration** - Use sensible defaults
2. **Programmatic Configuration** - Create configuration objects in code
3. **Dictionary Configuration** - Load from dictionaries (JSON, YAML, etc.)
4. **File Configuration** - Load from TOML files

## Configuration Methods

### 1. Default Configuration

The simplest approach - use defaults:

```python
from morado.common.http import create_default_client

# All defaults
client = create_default_client()

# With base URL
client = create_default_client(base_url="https://api.example.com")

# Disable specific features
client = create_default_client(
    enable_retry=False,
    enable_logging=False
)
```

**Default Values:**
- Connect timeout: 10 seconds
- Read timeout: 30 seconds
- Max retries: 3
- Retry strategy: Exponential backoff
- Logging: Enabled
- Tracing: Enabled

### 2. Programmatic Configuration

Create configuration objects for full control:

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

### 3. Dictionary Configuration

Load from dictionaries (useful for JSON/YAML):

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

### 4. TOML File Configuration

Load from TOML configuration files:

```python
from morado.common.http import load_config_from_toml, create_http_client

config = load_config_from_toml("config/http_client.toml")
client = create_http_client(config)
```

**Example TOML file:**

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

## Configuration Options

### Base Configuration

#### base_url

Base URL for all requests. All request URLs will be relative to this base.

- **Type:** `str` (optional)
- **Default:** `None`
- **Validation:** Must start with `http://` or `https://`

```python
config = HttpClientConfig(base_url="https://api.example.com")
```

#### connect_timeout

Connection timeout in seconds.

- **Type:** `int`
- **Default:** `10`
- **Range:** 1-300 seconds
- **Description:** Maximum time to wait for connection establishment

```python
config = HttpClientConfig(connect_timeout=15)
```

#### read_timeout

Read timeout in seconds.

- **Type:** `int`
- **Default:** `30`
- **Range:** 1-600 seconds
- **Description:** Maximum time to wait for response data

```python
config = HttpClientConfig(read_timeout=60)
```

#### pool_connections

Number of connection pools to cache.

- **Type:** `int`
- **Default:** `10`
- **Range:** 1-100
- **Description:** Number of different hosts to cache connections for

```python
config = HttpClientConfig(pool_connections=20)
```

#### pool_maxsize

Maximum number of connections per pool.

- **Type:** `int`
- **Default:** `10`
- **Range:** 1-100
- **Description:** Maximum connections to keep alive per host

```python
config = HttpClientConfig(pool_maxsize=20)
```

### Retry Configuration

#### enable_retry

Enable automatic retry on failures.

- **Type:** `bool`
- **Default:** `True`
- **Description:** Whether to automatically retry failed requests

```python
config = HttpClientConfig(enable_retry=True)
```

#### max_retries

Maximum number of retry attempts.

- **Type:** `int`
- **Default:** `3`
- **Range:** 0-10
- **Description:** How many times to retry before giving up

```python
config = HttpClientConfig(max_retries=5)
```

#### retry_strategy

Retry delay strategy.

- **Type:** `str`
- **Default:** `"exponential"`
- **Options:** `"fixed"`, `"exponential"`, `"linear"`
- **Description:** How to calculate delay between retries

**Strategies:**

- **fixed**: Same delay for each retry (initial_delay)
- **exponential**: Delay doubles each retry (1s, 2s, 4s, 8s, ...)
- **linear**: Delay increases linearly (1s, 2s, 3s, 4s, ...)

```python
config = HttpClientConfig(retry_strategy="exponential")
```

#### initial_delay

Initial delay between retries in seconds.

- **Type:** `float`
- **Default:** `1.0`
- **Range:** 0-60 seconds
- **Description:** Starting delay for retry strategies

```python
config = HttpClientConfig(initial_delay=2.0)
```

#### max_delay

Maximum delay between retries in seconds.

- **Type:** `float`
- **Default:** `60.0`
- **Range:** 0-300 seconds
- **Description:** Cap on retry delay (for exponential/linear strategies)

```python
config = HttpClientConfig(max_delay=120.0)
```

### Logging Configuration

#### enable_logging

Enable request/response logging.

- **Type:** `bool`
- **Default:** `True`
- **Description:** Whether to log HTTP requests and responses

```python
config = HttpClientConfig(enable_logging=True)
```

#### log_request_body

Log request body content.

- **Type:** `bool`
- **Default:** `True`
- **Description:** Whether to include request body in logs

```python
config = HttpClientConfig(log_request_body=True)
```

#### log_response_body

Log response body content.

- **Type:** `bool`
- **Default:** `True`
- **Description:** Whether to include response body in logs

```python
config = HttpClientConfig(log_response_body=True)
```

#### max_log_body_size

Maximum body size to log in bytes.

- **Type:** `int`
- **Default:** `1024`
- **Range:** 1-10240 bytes
- **Description:** Truncate bodies larger than this in logs

```python
config = HttpClientConfig(max_log_body_size=2048)
```

### Tracing Configuration

#### enable_tracing

Enable request tracing with execution context.

- **Type:** `bool`
- **Default:** `True`
- **Description:** Whether to add tracing headers from execution context

```python
config = HttpClientConfig(enable_tracing=True)
```

#### trace_header_name

HTTP header name for request ID.

- **Type:** `str`
- **Default:** `"X-Request-ID"`
- **Description:** Header name for propagating request ID

```python
config = HttpClientConfig(trace_header_name="X-Trace-ID")
```

## Environment-Specific Configuration

### Development Environment

```toml
[http_client]
base_url = "http://localhost:8000"
connect_timeout = 5
read_timeout = 30
enable_retry = false  # Fail fast in development
enable_logging = true
log_request_body = true
log_response_body = true
max_log_body_size = 4096  # More verbose logging
```

### Testing Environment

```toml
[http_client]
base_url = "https://test-api.example.com"
connect_timeout = 10
read_timeout = 30
enable_retry = true
max_retries = 2  # Fewer retries for faster tests
retry_strategy = "fixed"
initial_delay = 0.5
enable_logging = true
enable_tracing = true
```

### Staging Environment

```toml
[http_client]
base_url = "https://staging-api.example.com"
connect_timeout = 10
read_timeout = 60
enable_retry = true
max_retries = 3
retry_strategy = "exponential"
enable_logging = true
log_request_body = true
log_response_body = true
max_log_body_size = 2048
enable_tracing = true
```

### Production Environment

```toml
[http_client]
base_url = "https://api.example.com"
connect_timeout = 15
read_timeout = 120
pool_connections = 50  # Higher for production load
pool_maxsize = 50
enable_retry = true
max_retries = 5
retry_strategy = "exponential"
initial_delay = 1.0
max_delay = 60.0
enable_logging = true
log_request_body = false  # Don't log bodies in production
log_response_body = false
max_log_body_size = 512
enable_tracing = true
```

## Advanced Configuration

### Per-Request Configuration Override

Override configuration for specific requests:

```python
client = create_default_client(base_url="https://api.example.com")

# Override timeout for slow endpoint
response = client.get("/slow-endpoint", timeout=(30, 120))

# Override headers for specific request
response = client.post(
    "/users",
    json={"name": "John"},
    headers={"Authorization": "Bearer special-token"}
)
```

### Multiple Clients with Different Configurations

```python
# Fast API client
fast_config = HttpClientConfig(
    base_url="https://fast-api.example.com",
    connect_timeout=5,
    read_timeout=15,
    enable_retry=False
)
fast_client = create_http_client(fast_config)

# Slow API client
slow_config = HttpClientConfig(
    base_url="https://slow-api.example.com",
    connect_timeout=30,
    read_timeout=300,
    enable_retry=True,
    max_retries=5
)
slow_client = create_http_client(slow_config)
```

### Dynamic Configuration

```python
import os
from morado.common.http import HttpClientConfig, create_http_client

def create_client_for_environment():
    """Create client based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        config = HttpClientConfig(
            base_url=os.getenv("API_BASE_URL"),
            connect_timeout=15,
            read_timeout=120,
            max_retries=5,
            log_request_body=False,
            log_response_body=False
        )
    else:
        config = HttpClientConfig(
            base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
            connect_timeout=5,
            read_timeout=30,
            max_retries=2,
            log_request_body=True,
            log_response_body=True
        )
    
    return create_http_client(config)

client = create_client_for_environment()
```

### Configuration Validation

```python
from pydantic import ValidationError
from morado.common.http import HttpClientConfig

try:
    config = HttpClientConfig(
        base_url="invalid-url",  # Missing http:// or https://
        connect_timeout=500,  # Exceeds maximum
        retry_strategy="invalid"  # Invalid strategy
    )
except ValidationError as e:
    print("Configuration errors:")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg']}")
```

### Configuration Best Practices

1. **Use Environment Variables**
   ```python
   import os
   
   config = HttpClientConfig(
       base_url=os.getenv("API_BASE_URL", "https://api.example.com"),
       connect_timeout=int(os.getenv("API_CONNECT_TIMEOUT", "10")),
       max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
   )
   ```

2. **Separate Configuration Files**
   - `config/http_client_dev.toml`
   - `config/http_client_test.toml`
   - `config/http_client_prod.toml`

3. **Configuration Hierarchy**
   ```python
   # Load base configuration
   base_config = load_config_from_toml("config/http_client_base.toml")
   
   # Override with environment-specific settings
   env_overrides = {
       "base_url": os.getenv("API_BASE_URL"),
       "max_retries": int(os.getenv("API_MAX_RETRIES", "3"))
   }
   
   # Merge configurations
   final_config = HttpClientConfig(
       **{**base_config.model_dump(), **env_overrides}
   )
   ```

4. **Validate Configuration Early**
   ```python
   def validate_config(config: HttpClientConfig) -> None:
       """Validate configuration before use."""
       if config.base_url and not config.base_url.startswith("https://"):
           if os.getenv("ENVIRONMENT") == "production":
               raise ValueError("Production must use HTTPS")
       
       if config.max_retries > 5:
           print("Warning: High retry count may cause delays")
   
   config = HttpClientConfig(...)
   validate_config(config)
   client = create_http_client(config)
   ```

## Configuration Examples

### Minimal Configuration

```python
# Just the essentials
config = HttpClientConfig(
    base_url="https://api.example.com"
)
```

### High-Performance Configuration

```python
# Optimized for high throughput
config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=5,
    read_timeout=15,
    pool_connections=100,
    pool_maxsize=100,
    enable_retry=False,  # Fail fast
    enable_logging=False  # Reduce overhead
)
```

### Reliable Configuration

```python
# Optimized for reliability
config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=30,
    read_timeout=120,
    enable_retry=True,
    max_retries=10,
    retry_strategy="exponential",
    initial_delay=2.0,
    max_delay=120.0
)
```

### Debug Configuration

```python
# Optimized for debugging
config = HttpClientConfig(
    base_url="https://api.example.com",
    enable_logging=True,
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=10240,  # Log more data
    enable_tracing=True
)
```

## Troubleshooting Configuration

### Common Issues

1. **Invalid base_url**
   ```
   Error: base_url must start with http:// or https://
   Solution: Add protocol to URL
   ```

2. **Timeout too high**
   ```
   Error: connect_timeout must be <= 300
   Solution: Reduce timeout value
   ```

3. **Invalid retry_strategy**
   ```
   Error: retry_strategy must be one of {'fixed', 'exponential', 'linear'}
   Solution: Use valid strategy name
   ```

4. **TOML file not found**
   ```
   Error: Configuration file not found: config/http_client.toml
   Solution: Check file path and ensure file exists
   ```

### Configuration Debugging

```python
from morado.common.http import HttpClientConfig

# Print configuration
config = HttpClientConfig(base_url="https://api.example.com")
print(config.model_dump_json(indent=2))

# Validate configuration
try:
    config = HttpClientConfig(**config_dict)
    print("Configuration is valid")
except Exception as e:
    print(f"Configuration error: {e}")
```
