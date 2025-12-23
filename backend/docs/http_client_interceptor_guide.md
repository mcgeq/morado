# HTTP Client Interceptor Development Guide

Guide to creating custom interceptors for the Morado HTTP Client Wrapper.

## Table of Contents

- [Interceptor Overview](#interceptor-overview)
- [Request Interceptors](#request-interceptors)
- [Response Interceptors](#response-interceptors)
- [Built-in Interceptors](#built-in-interceptors)
- [Custom Interceptor Examples](#custom-interceptor-examples)
- [Best Practices](#best-practices)

## Interceptor Overview

Interceptors allow you to execute custom logic before requests are sent and after responses are received. They can:

- Modify request parameters (URL, headers, body, etc.)
- Add authentication headers
- Log requests and responses
- Transform response data
- Implement custom error handling
- Add metrics collection
- Implement caching logic

### Interceptor Types

1. **Request Interceptors** - Execute before sending requests
2. **Response Interceptors** - Execute after receiving responses

### Execution Order

Interceptors execute in registration order:

```python
client.interceptor_manager.add_request_interceptor(AuthInterceptor())      # 1st
client.interceptor_manager.add_request_interceptor(LoggingInterceptor())   # 2nd
client.interceptor_manager.add_request_interceptor(MetricsInterceptor())   # 3rd

# Request flow: AuthInterceptor -> LoggingInterceptor -> MetricsInterceptor -> HTTP Request
```

## Request Interceptors

Request interceptors modify requests before they are sent.

### Creating a Request Interceptor

```python
from morado.common.http.interceptor import RequestInterceptor
from typing import Any

class MyRequestInterceptor(RequestInterceptor):
    """Custom request interceptor."""
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Modify request before sending.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            **kwargs: Additional request parameters
            
        Returns:
            Tuple of (method, url, headers, kwargs)
        """
        # Modify request here
        headers["X-Custom-Header"] = "value"
        
        # Return modified parameters
        return method, url, headers, kwargs
```

### Registering a Request Interceptor

```python
from morado.common.http import create_default_client

client = create_default_client()
client.interceptor_manager.add_request_interceptor(MyRequestInterceptor())
```

## Response Interceptors

Response interceptors process responses after they are received.

### Creating a Response Interceptor

```python
from morado.common.http.interceptor import ResponseInterceptor
from morado.common.http.response import HttpResponse

class MyResponseInterceptor(ResponseInterceptor):
    """Custom response interceptor."""
    
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Process response after receiving.
        
        Args:
            response: HTTP response object
            
        Returns:
            Modified response object
        """
        # Process response here
        if not response.is_success():
            # Log error or raise custom exception
            print(f"Request failed: {response.status_code}")
        
        # Return response (modified or original)
        return response
```

### Registering a Response Interceptor

```python
from morado.common.http import create_default_client

client = create_default_client()
client.interceptor_manager.add_response_interceptor(MyResponseInterceptor())
```

## Built-in Interceptors

### LoggingInterceptor

Logs request details before sending.

```python
from morado.common.http.logging_interceptor import LoggingInterceptor
from morado.common.http import HttpClientConfig

config = HttpClientConfig(
    log_request_body=True,
    log_response_body=True,
    max_log_body_size=2048
)

interceptor = LoggingInterceptor(config=config)
client.interceptor_manager.add_request_interceptor(interceptor)
```

### ErrorLoggingInterceptor

Logs error details after receiving response.

```python
from morado.common.http.logging_interceptor import ErrorLoggingInterceptor

interceptor = ErrorLoggingInterceptor()
client.interceptor_manager.add_response_interceptor(interceptor)
```

### TracingInterceptor

Adds tracing headers from execution context.

```python
from morado.common.http.tracing_interceptor import TracingInterceptor

interceptor = TracingInterceptor()
client.interceptor_manager.add_request_interceptor(interceptor)
```

## Custom Interceptor Examples

### Authentication Interceptor

Add authentication headers to all requests:

```python
from morado.common.http.interceptor import RequestInterceptor
from typing import Any

class AuthInterceptor(RequestInterceptor):
    """Add authentication to requests."""
    
    def __init__(self, token: str):
        self.token = token
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Add Authorization header."""
        headers["Authorization"] = f"Bearer {self.token}"
        return method, url, headers, kwargs

# Usage
client = create_default_client()
client.interceptor_manager.add_request_interceptor(
    AuthInterceptor(token="your-api-token")
)
```

### API Key Interceptor

Add API key to query parameters:

```python
from morado.common.http.interceptor import RequestInterceptor
from typing import Any

class APIKeyInterceptor(RequestInterceptor):
    """Add API key to query parameters."""
    
    def __init__(self, api_key: str, param_name: str = "api_key"):
        self.api_key = api_key
        self.param_name = param_name
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Add API key to params."""
        params = kwargs.get("params", {})
        params[self.param_name] = self.api_key
        kwargs["params"] = params
        return method, url, headers, kwargs

# Usage
client = create_default_client()
client.interceptor_manager.add_request_interceptor(
    APIKeyInterceptor(api_key="your-api-key")
)
```

### User Agent Interceptor

Add custom User-Agent header:

```python
from morado.common.http.interceptor import RequestInterceptor
from typing import Any

class UserAgentInterceptor(RequestInterceptor):
    """Add custom User-Agent header."""
    
    def __init__(self, user_agent: str):
        self.user_agent = user_agent
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Add User-Agent header."""
        headers["User-Agent"] = self.user_agent
        return method, url, headers, kwargs

# Usage
client = create_default_client()
client.interceptor_manager.add_request_interceptor(
    UserAgentInterceptor(user_agent="MyApp/1.0")
)
```

### Rate Limiting Interceptor

Implement client-side rate limiting:

```python
import time
from morado.common.http.interceptor import RequestInterceptor
from typing import Any

class RateLimitInterceptor(RequestInterceptor):
    """Rate limit requests."""
    
    def __init__(self, requests_per_second: float):
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Enforce rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        return method, url, headers, kwargs

# Usage - limit to 10 requests per second
client = create_default_client()
client.interceptor_manager.add_request_interceptor(
    RateLimitInterceptor(requests_per_second=10)
)
```

### Metrics Interceptor

Collect request metrics:

```python
from morado.common.http.interceptor import RequestInterceptor, ResponseInterceptor
from morado.common.http.response import HttpResponse
from typing import Any
import time

class MetricsInterceptor(RequestInterceptor, ResponseInterceptor):
    """Collect request metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_duration = 0.0
        self.request_start_times = {}
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Record request start time."""
        request_id = id((method, url))
        self.request_start_times[request_id] = time.time()
        self.request_count += 1
        return method, url, headers, kwargs
    
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Record response metrics."""
        if not response.is_success():
            self.error_count += 1
        
        self.total_duration += response.request_time
        return response
    
    def get_metrics(self) -> dict:
        """Get collected metrics."""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "success_rate": (self.request_count - self.error_count) / self.request_count if self.request_count > 0 else 0,
            "average_duration": self.total_duration / self.request_count if self.request_count > 0 else 0
        }

# Usage
metrics = MetricsInterceptor()
client = create_default_client()
client.interceptor_manager.add_request_interceptor(metrics)
client.interceptor_manager.add_response_interceptor(metrics)

# Make requests...
response = client.get("https://api.example.com/users")

# Get metrics
print(metrics.get_metrics())
```

### Response Validation Interceptor

Validate response structure:

```python
from morado.common.http.interceptor import ResponseInterceptor
from morado.common.http.response import HttpResponse

class ResponseValidationInterceptor(ResponseInterceptor):
    """Validate response structure."""
    
    def __init__(self, required_fields: list[str]):
        self.required_fields = required_fields
    
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Validate response has required fields."""
        if response.is_success():
            try:
                data = response.json()
                missing_fields = [
                    field for field in self.required_fields
                    if field not in data
                ]
                
                if missing_fields:
                    raise ValueError(
                        f"Response missing required fields: {missing_fields}"
                    )
            except Exception as e:
                # Log validation error
                print(f"Response validation failed: {e}")
        
        return response

# Usage
client = create_default_client()
client.interceptor_manager.add_response_interceptor(
    ResponseValidationInterceptor(required_fields=["id", "name", "email"])
)
```

### Caching Interceptor

Implement simple response caching:

```python
from morado.common.http.interceptor import RequestInterceptor, ResponseInterceptor
from morado.common.http.response import HttpResponse
from typing import Any, Optional
import hashlib
import json

class CachingInterceptor(RequestInterceptor, ResponseInterceptor):
    """Cache GET request responses."""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def _get_cache_key(self, method: str, url: str, params: Any) -> str:
        """Generate cache key."""
        key_data = f"{method}:{url}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """Check cache for GET requests."""
        if method == "GET":
            cache_key = self._get_cache_key(method, url, kwargs.get("params"))
            cached = self.cache.get(cache_key)
            
            if cached:
                import time
                if time.time() - cached["timestamp"] < self.ttl:
                    # Return cached response
                    # Note: This is simplified - actual implementation would need
                    # to short-circuit the request
                    print(f"Cache hit for {url}")
        
        return method, url, headers, kwargs
    
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Cache successful GET responses."""
        # Note: This is simplified - would need request context
        # to properly cache responses
        return response

# Usage
client = create_default_client()
caching = CachingInterceptor(ttl=300)  # 5 minute TTL
client.interceptor_manager.add_request_interceptor(caching)
client.interceptor_manager.add_response_interceptor(caching)
```

### Error Handling Interceptor

Custom error handling and transformation:

```python
from morado.common.http.interceptor import ResponseInterceptor
from morado.common.http.response import HttpResponse

class ErrorHandlingInterceptor(ResponseInterceptor):
    """Handle specific error responses."""
    
    def after_response(self, response: HttpResponse) -> HttpResponse:
        """Handle error responses."""
        if response.status_code == 401:
            raise Exception("Authentication failed - please check credentials")
        elif response.status_code == 403:
            raise Exception("Access forbidden - insufficient permissions")
        elif response.status_code == 429:
            retry_after = response.get_header("Retry-After", "60")
            raise Exception(f"Rate limit exceeded - retry after {retry_after} seconds")
        elif response.status_code >= 500:
            raise Exception(f"Server error: {response.status_code}")
        
        return response

# Usage
client = create_default_client()
client.interceptor_manager.add_response_interceptor(
    ErrorHandlingInterceptor()
)
```

## Best Practices

### 1. Keep Interceptors Focused

Each interceptor should have a single responsibility:

```python
# Good - focused interceptor
class AuthInterceptor(RequestInterceptor):
    """Only handles authentication."""
    pass

# Bad - does too much
class MegaInterceptor(RequestInterceptor):
    """Handles auth, logging, metrics, caching..."""
    pass
```

### 2. Handle Errors Gracefully

```python
class SafeInterceptor(RequestInterceptor):
    def before_request(self, method, url, headers, **kwargs):
        try:
            # Interceptor logic
            headers["X-Custom"] = self.get_custom_value()
        except Exception as e:
            # Log error but don't break the request
            print(f"Interceptor error: {e}")
        
        return method, url, headers, kwargs
```

### 3. Avoid Modifying Original Objects

```python
class GoodInterceptor(RequestInterceptor):
    def before_request(self, method, url, headers, **kwargs):
        # Create copies to avoid side effects
        new_headers = headers.copy()
        new_headers["X-Custom"] = "value"
        return method, url, new_headers, kwargs
```

### 4. Document Interceptor Behavior

```python
class WellDocumentedInterceptor(RequestInterceptor):
    """Add custom authentication header.
    
    This interceptor adds an X-API-Key header to all requests
    using the API key provided during initialization.
    
    Args:
        api_key: The API key to use for authentication
        
    Example:
        >>> interceptor = WellDocumentedInterceptor(api_key="key123")
        >>> client.interceptor_manager.add_request_interceptor(interceptor)
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def before_request(self, method, url, headers, **kwargs):
        """Add X-API-Key header to request."""
        headers["X-API-Key"] = self.api_key
        return method, url, headers, kwargs
```

### 5. Consider Interceptor Order

```python
# Order matters!
client = create_default_client()

# 1. Add auth first (other interceptors may need it)
client.interceptor_manager.add_request_interceptor(AuthInterceptor())

# 2. Add logging (logs authenticated requests)
client.interceptor_manager.add_request_interceptor(LoggingInterceptor())

# 3. Add metrics last (measures everything)
client.interceptor_manager.add_request_interceptor(MetricsInterceptor())
```

### 6. Test Interceptors Independently

```python
def test_auth_interceptor():
    """Test authentication interceptor."""
    interceptor = AuthInterceptor(token="test-token")
    
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/users",
        {},
        params={}
    )
    
    assert headers["Authorization"] == "Bearer test-token"
```

### 7. Use Type Hints

```python
from typing import Any
from morado.common.http.interceptor import RequestInterceptor

class TypedInterceptor(RequestInterceptor):
    def __init__(self, value: str) -> None:
        self.value = value
    
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        headers["X-Value"] = self.value
        return method, url, headers, kwargs
```

### 8. Clean Up Resources

```python
class ResourceInterceptor(RequestInterceptor):
    def __init__(self):
        self.resource = self.acquire_resource()
    
    def before_request(self, method, url, headers, **kwargs):
        # Use resource
        return method, url, headers, kwargs
    
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'resource'):
            self.release_resource()
```

## Advanced Patterns

### Conditional Interceptor

Only apply interceptor to certain requests:

```python
class ConditionalInterceptor(RequestInterceptor):
    def __init__(self, condition_func):
        self.condition_func = condition_func
    
    def before_request(self, method, url, headers, **kwargs):
        if self.condition_func(method, url):
            # Apply interceptor logic
            headers["X-Conditional"] = "applied"
        
        return method, url, headers, kwargs

# Usage - only apply to POST requests
client.interceptor_manager.add_request_interceptor(
    ConditionalInterceptor(lambda method, url: method == "POST")
)
```

### Stateful Interceptor

Maintain state across requests:

```python
class StatefulInterceptor(RequestInterceptor):
    def __init__(self):
        self.request_count = 0
    
    def before_request(self, method, url, headers, **kwargs):
        self.request_count += 1
        headers["X-Request-Number"] = str(self.request_count)
        return method, url, headers, kwargs
```

### Composite Interceptor

Combine multiple interceptors:

```python
class CompositeInterceptor(RequestInterceptor):
    def __init__(self, *interceptors):
        self.interceptors = interceptors
    
    def before_request(self, method, url, headers, **kwargs):
        for interceptor in self.interceptors:
            method, url, headers, kwargs = interceptor.before_request(
                method, url, headers, **kwargs
            )
        return method, url, headers, kwargs
```

## Troubleshooting

### Common Issues

1. **Interceptor not executing**
   - Check if interceptor is registered
   - Verify interceptor type (request vs response)
   - Check for exceptions in interceptor code

2. **Headers not being added**
   - Ensure you're modifying the headers dict
   - Return the modified headers in the tuple
   - Check interceptor execution order

3. **Performance issues**
   - Profile interceptor code
   - Avoid expensive operations
   - Consider caching in interceptors

4. **State management issues**
   - Be careful with shared state
   - Consider thread safety
   - Clean up resources properly
