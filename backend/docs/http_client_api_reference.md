# HTTP Client API Reference

Complete API reference for the Morado HTTP Client Wrapper.

## Table of Contents

- [Factory Functions](#factory-functions)
- [HttpClient](#httpclient)
- [HttpResponse](#httpresponse)
- [HttpClientConfig](#httpclientconfig)
- [Interceptors](#interceptors)
- [Retry](#retry)
- [Session Management](#session-management)
- [Exceptions](#exceptions)
- [Utility Functions](#utility-functions)

## Factory Functions

### create_http_client

```python
def create_http_client(
    config: Optional[HttpClientConfig] = None,
    enable_logging: bool = True,
    enable_tracing: bool = True,
    enable_error_logging: bool = True,
) -> HttpClient
```

Create an HTTP client with the specified configuration.

**Parameters:**
- `config` (HttpClientConfig, optional): HTTP client configuration. If None, uses default configuration.
- `enable_logging` (bool): Whether to enable request/response logging. Default: True.
- `enable_tracing` (bool): Whether to enable request tracing. Default: True.
- `enable_error_logging` (bool): Whether to enable error logging. Default: True.

**Returns:**
- `HttpClient`: Configured HttpClient instance

**Example:**
```python
from morado.common.http import create_http_client, HttpClientConfig

config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=15,
    max_retries=5
)
client = create_http_client(config)
```

### create_default_client

```python
def create_default_client(
    base_url: Optional[str] = None,
    enable_logging: bool = True,
    enable_tracing: bool = True,
    enable_retry: bool = True,
) -> HttpClient
```

Create an HTTP client with sensible defaults.

**Parameters:**
- `base_url` (str, optional): Base URL for all requests
- `enable_logging` (bool): Whether to enable request/response logging. Default: True.
- `enable_tracing` (bool): Whether to enable request tracing. Default: True.
- `enable_retry` (bool): Whether to enable automatic retry. Default: True.

**Returns:**
- `HttpClient`: Configured HttpClient instance with default settings

**Example:**
```python
from morado.common.http import create_default_client

client = create_default_client(base_url="https://api.example.com")
```

### load_config_from_dict

```python
def load_config_from_dict(config_dict: dict) -> HttpClientConfig
```

Load HTTP client configuration from a dictionary.

**Parameters:**
- `config_dict` (dict): Dictionary containing configuration values

**Returns:**
- `HttpClientConfig`: Configuration instance

**Raises:**
- `ValidationError`: If the configuration values are invalid

**Example:**
```python
from morado.common.http import load_config_from_dict

config_dict = {
    "base_url": "https://api.example.com",
    "connect_timeout": 15,
    "max_retries": 5
}
config = load_config_from_dict(config_dict)
```

### load_config_from_toml

```python
def load_config_from_toml(filepath: str) -> HttpClientConfig
```

Load HTTP client configuration from a TOML file.

**Parameters:**
- `filepath` (str): Path to the TOML configuration file

**Returns:**
- `HttpClientConfig`: Configuration instance

**Raises:**
- `FileNotFoundError`: If the file does not exist
- `ValidationError`: If the configuration values are invalid
- `ImportError`: If tomllib/tomli is not available

**Example:**
```python
from morado.common.http import load_config_from_toml

config = load_config_from_toml("config/http_client.toml")
```

## HttpClient

Main HTTP client class for making requests.

### Constructor

```python
def __init__(
    self,
    session: Optional[Session] = None,
    base_url: Optional[str] = None,
    default_timeout: tuple[int, int] = (10, 30),
    default_headers: Optional[dict[str, str]] = None,
    session_manager: Optional[SessionManager] = None,
    retry_handler: Optional[RetryHandler] = None,
    interceptor_manager: Optional[InterceptorManager] = None,
)
```

**Parameters:**
- `session` (Session, optional): Existing requests.Session to use
- `base_url` (str, optional): Base URL for all requests
- `default_timeout` (tuple): Default timeout as (connect_timeout, read_timeout) in seconds
- `default_headers` (dict, optional): Default headers for all requests
- `session_manager` (SessionManager, optional): SessionManager instance
- `retry_handler` (RetryHandler, optional): RetryHandler instance for retry logic
- `interceptor_manager` (InterceptorManager, optional): InterceptorManager instance

### Methods

#### request

```python
def request(
    self,
    method: str,
    url: str,
    params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    data: Optional[Any] = None,
    json: Optional[Any] = None,
    files: Optional[dict[str, Any]] = None,
    timeout: Optional[tuple[int, int]] = None,
    **kwargs: Any,
) -> HttpResponse
```

Send an HTTP request.

**Parameters:**
- `method` (str): HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- `url` (str): Request URL (relative to base_url if set)
- `params` (dict, optional): Query parameters
- `headers` (dict, optional): Request headers
- `data` (Any, optional): Request body (form data)
- `json` (Any, optional): Request body (JSON data)
- `files` (dict, optional): Files to upload
- `timeout` (tuple, optional): Timeout as (connect_timeout, read_timeout)
- `**kwargs`: Additional parameters passed to requests

**Returns:**
- `HttpResponse`: Response object

**Raises:**
- `HttpConnectionError`: On connection failures
- `HttpTimeoutError`: On timeout
- `HttpRequestError`: On HTTP errors
- `RetryExhaustedError`: If retry attempts are exhausted

#### get

```python
def get(self, url: str, **kwargs: Any) -> HttpResponse
```

Send a GET request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (params, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### post

```python
def post(self, url: str, **kwargs: Any) -> HttpResponse
```

Send a POST request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (data, json, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### put

```python
def put(self, url: str, **kwargs: Any) -> HttpResponse
```

Send a PUT request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (data, json, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### patch

```python
def patch(self, url: str, **kwargs: Any) -> HttpResponse
```

Send a PATCH request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (data, json, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### delete

```python
def delete(self, url: str, **kwargs: Any) -> HttpResponse
```

Send a DELETE request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (params, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### head

```python
def head(self, url: str, **kwargs: Any) -> HttpResponse
```

Send a HEAD request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (params, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### options

```python
def options(self, url: str, **kwargs: Any) -> HttpResponse
```

Send an OPTIONS request.

**Parameters:**
- `url` (str): Request URL
- `**kwargs`: Additional parameters (params, headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### upload_file

```python
def upload_file(
    self,
    url: str,
    file_path: str,
    file_field_name: str = "file",
    additional_fields: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> HttpResponse
```

Upload a single file using multipart/form-data.

**Parameters:**
- `url` (str): Request URL
- `file_path` (str): Path to the file to upload
- `file_field_name` (str): Name of the form field for the file. Default: "file"
- `additional_fields` (dict, optional): Additional form fields to include
- `**kwargs`: Additional parameters (headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

**Raises:**
- `FileNotFoundError`: If the file does not exist
- `IOError`: If the file cannot be read

#### upload_files

```python
def upload_files(
    self,
    url: str,
    files: dict[str, str],
    additional_fields: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> HttpResponse
```

Upload multiple files using multipart/form-data.

**Parameters:**
- `url` (str): Request URL
- `files` (dict): Dictionary mapping form field names to file paths
- `additional_fields` (dict, optional): Additional form fields to include
- `**kwargs`: Additional parameters (headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

**Raises:**
- `FileNotFoundError`: If any file does not exist
- `IOError`: If any file cannot be read

#### upload_multipart

```python
def upload_multipart(
    self,
    url: str,
    files: Optional[dict[str, tuple[str, Any, Optional[str]]]] = None,
    data: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> HttpResponse
```

Upload files and form data using multipart/form-data with full control.

**Parameters:**
- `url` (str): Request URL
- `files` (dict, optional): Dictionary mapping field names to tuples of (filename, file_object, content_type)
- `data` (dict, optional): Dictionary of additional form fields
- `**kwargs`: Additional parameters (headers, timeout, etc.)

**Returns:**
- `HttpResponse`: Response object

#### close

```python
def close(self) -> None
```

Close the HTTP client and release resources.

### Properties

#### interceptor_manager

```python
@property
def interceptor_manager(self) -> InterceptorManager
```

Get the interceptor manager for adding custom interceptors.

**Returns:**
- `InterceptorManager`: The InterceptorManager instance

### Class Methods

#### from_config

```python
@classmethod
def from_config(cls, config: HttpClientConfig) -> "HttpClient"
```

Create an HTTP client from a configuration object.

**Parameters:**
- `config` (HttpClientConfig): Configuration instance

**Returns:**
- `HttpClient`: Configured HttpClient instance

### Context Manager

The HttpClient supports context manager protocol:

```python
with HttpClient() as client:
    response = client.get("https://api.example.com/users")
```

## HttpResponse

Response wrapper providing convenient access to response data.

### Properties

#### status_code

```python
@property
def status_code(self) -> int
```

HTTP status code.

#### headers

```python
@property
def headers(self) -> dict[str, str]
```

Response headers dictionary.

#### text

```python
@property
def text(self) -> str
```

Response text content.

#### content

```python
@property
def content(self) -> bytes
```

Response binary content.

#### request_time

```python
@property
def request_time(self) -> float
```

Request duration in seconds.

### Methods

#### json

```python
def json(self) -> Any
```

Parse JSON response.

**Returns:**
- `Any`: Parsed JSON object

**Raises:**
- `JSONDecodeError`: If JSON parsing fails

#### is_success

```python
def is_success(self) -> bool
```

Check if response is successful (2xx status code).

**Returns:**
- `bool`: True if successful, False otherwise

#### raise_for_status

```python
def raise_for_status(self) -> None
```

Raise exception if response is not successful.

**Raises:**
- `HttpRequestError`: If status code indicates an error

#### jsonpath

```python
def jsonpath(self, path: str) -> Any
```

Extract data from JSON response using JSONPath.

**Parameters:**
- `path` (str): JSONPath expression

**Returns:**
- `Any`: Extracted data

**Raises:**
- `JSONPathError`: If JSONPath parsing fails

#### get_header

```python
def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]
```

Get response header value (case-insensitive).

**Parameters:**
- `name` (str): Header name
- `default` (str, optional): Default value if header not found

**Returns:**
- `str | None`: Header value or default

#### save_to_file

```python
def save_to_file(self, filepath: str) -> None
```

Save response content to a file.

**Parameters:**
- `filepath` (str): Path where to save the file

**Raises:**
- `IOError`: If file cannot be written

## HttpClientConfig

Configuration model for HTTP client.

### Fields

- `base_url` (str, optional): Base URL for all requests
- `connect_timeout` (int): Connection timeout in seconds (1-300). Default: 10
- `read_timeout` (int): Read timeout in seconds (1-600). Default: 30
- `pool_connections` (int): Number of connection pools (1-100). Default: 10
- `pool_maxsize` (int): Maximum connections per pool (1-100). Default: 10
- `enable_retry` (bool): Enable automatic retry. Default: True
- `max_retries` (int): Maximum retry attempts (0-10). Default: 3
- `retry_strategy` (str): Retry strategy ("fixed", "exponential", "linear"). Default: "exponential"
- `initial_delay` (float): Initial retry delay in seconds (0-60). Default: 1.0
- `max_delay` (float): Maximum retry delay in seconds (0-300). Default: 60.0
- `enable_logging` (bool): Enable request/response logging. Default: True
- `log_request_body` (bool): Log request body content. Default: True
- `log_response_body` (bool): Log response body content. Default: True
- `max_log_body_size` (int): Maximum body size to log in bytes (1-10240). Default: 1024
- `enable_tracing` (bool): Enable request tracing. Default: True
- `trace_header_name` (str): HTTP header name for request ID. Default: "X-Request-ID"

### Example

```python
from morado.common.http import HttpClientConfig

config = HttpClientConfig(
    base_url="https://api.example.com",
    connect_timeout=15,
    read_timeout=60,
    max_retries=5,
    retry_strategy="exponential",
    enable_logging=True,
    enable_tracing=True
)
```

## Interceptors

### RequestInterceptor

Abstract base class for request interceptors.

```python
class RequestInterceptor(ABC):
    @abstractmethod
    def before_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        **kwargs: Any,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        pass
```

### ResponseInterceptor

Abstract base class for response interceptors.

```python
class ResponseInterceptor(ABC):
    @abstractmethod
    def after_response(self, response: HttpResponse) -> HttpResponse:
        pass
```

### InterceptorManager

Manager for request and response interceptors.

#### Methods

##### add_request_interceptor

```python
def add_request_interceptor(self, interceptor: RequestInterceptor) -> None
```

Register a request interceptor.

##### add_response_interceptor

```python
def add_response_interceptor(self, interceptor: ResponseInterceptor) -> None
```

Register a response interceptor.

##### clear_request_interceptors

```python
def clear_request_interceptors(self) -> None
```

Remove all request interceptors.

##### clear_response_interceptors

```python
def clear_response_interceptors(self) -> None
```

Remove all response interceptors.

##### clear_all_interceptors

```python
def clear_all_interceptors(self) -> None
```

Remove all interceptors.

### Built-in Interceptors

#### LoggingInterceptor

Logs request details before sending.

```python
from morado.common.http.logging_interceptor import LoggingInterceptor

interceptor = LoggingInterceptor(config=config)
client.interceptor_manager.add_request_interceptor(interceptor)
```

#### ErrorLoggingInterceptor

Logs error details after receiving response.

```python
from morado.common.http.logging_interceptor import ErrorLoggingInterceptor

interceptor = ErrorLoggingInterceptor()
client.interceptor_manager.add_response_interceptor(interceptor)
```

#### TracingInterceptor

Adds tracing headers from execution context.

```python
from morado.common.http.tracing_interceptor import TracingInterceptor

interceptor = TracingInterceptor()
client.interceptor_manager.add_request_interceptor(interceptor)
```

## Retry

### RetryStrategy

Enum defining retry strategies.

```python
class RetryStrategy(str, Enum):
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
```

### RetryConfig

Configuration for retry behavior.

```python
class RetryConfig:
    def __init__(
        self,
        max_retries: int = 3,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        retry_on_status: Optional[list[int]] = None,
        retry_on_exceptions: Optional[list[type]] = None
    )
```

### RetryHandler

Handles retry logic for failed requests.

#### Methods

##### execute_with_retry

```python
def execute_with_retry(
    self,
    func: Callable,
    *args,
    **kwargs
) -> Any
```

Execute function with retry on failure.

##### should_retry

```python
def should_retry(
    self,
    exception: Optional[Exception] = None,
    status_code: Optional[int] = None
) -> bool
```

Determine if request should be retried.

##### calculate_delay

```python
def calculate_delay(self, attempt: int) -> float
```

Calculate delay before next retry attempt.

## Session Management

### SessionManager

Manages HTTP session lifecycle.

```python
class SessionManager:
    def __init__(
        self,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: int = 0
    )
```

#### Methods

##### create_session

```python
def create_session(self) -> Session
```

Create a new HTTP session.

##### close_session

```python
def close_session(self, session: Session) -> None
```

Close session and release resources.

##### session_scope

```python
@contextmanager
def session_scope(self) -> Generator[Session, None, None]
```

Context manager for automatic session lifecycle management.

## Exceptions

### HttpClientError

Base exception for all HTTP client errors.

### HttpRequestError

Raised for HTTP request errors.

### HttpTimeoutError

Raised when request times out.

**Attributes:**
- `timeout_type` (str): Type of timeout ("connect", "read", or "unknown")

### HttpConnectionError

Raised for connection failures.

### RetryExhaustedError

Raised when retry attempts are exhausted.

**Attributes:**
- `retry_history` (list): List of retry attempt details

### JSONPathError

Raised for JSONPath parsing errors.

### VariableResolutionError

Raised for variable resolution errors.

## Utility Functions

### resolve_variables

```python
def resolve_variables(template: str, context: dict[str, Any]) -> str
```

Resolve variables in template string.

### build_url

```python
def build_url(base_url: str, path: str, path_params: Optional[dict[str, Any]] = None) -> str
```

Build URL with path parameters.

### encode_query_params

```python
def encode_query_params(params: dict[str, Any]) -> str
```

Encode query parameters for URL.

### serialize_body

```python
def serialize_body(body: Any, content_type: Optional[str] = None) -> Any
```

Serialize request body based on content type.

### mask_sensitive_data

```python
def mask_sensitive_data(data: Any, sensitive_keys: list[str]) -> Any
```

Mask sensitive data in dictionary or string.

### mask_sensitive_headers

```python
def mask_sensitive_headers(headers: dict[str, str]) -> dict[str, str]
```

Mask sensitive headers (Authorization, Cookie, etc.).

### truncate_for_logging

```python
def truncate_for_logging(text: str, max_length: int = 1024) -> str
```

Truncate text for logging with indicator.
