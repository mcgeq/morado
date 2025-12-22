# Morado Logger Usage Examples

This document provides practical examples for using the Morado logger system in various scenarios.

## Table of Contents

- [Basic Logging](#basic-logging)
- [Request Scope](#request-scope)
- [Async Logging](#async-logging)
- [Custom Processors](#custom-processors)
- [Custom Renderers](#custom-renderers)
- [UUID Generation](#uuid-generation)
- [Configuration](#configuration)
- [Real-World Scenarios](#real-world-scenarios)

## Basic Logging

### Simple Logging

```python
from morado.common.logger import get_logger

logger = get_logger(__name__)

# Basic log messages
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Logging with Context

```python
from morado.common.logger import get_logger

logger = get_logger(__name__)

# Add context to log messages
logger.info("User logged in", user_id=42, username="alice")
logger.error("Database connection failed", host="db.example.com", port=5432)
```

### Structured Logging

```python
from morado.common.logger import get_logger

logger = get_logger(__name__)

# Log structured data
user_data = {
    "id": 42,
    "username": "alice",
    "email": "alice@example.com"
}

logger.info("User created", user=user_data)
```

### Module-Specific Loggers

```python
# In api.py
from morado.common.logger import get_logger

logger = get_logger(__name__)  # Logger for 'myapp.api'
logger.info("API request received")

# In database.py
from morado.common.logger import get_logger

logger = get_logger(__name__)  # Logger for 'myapp.database'
logger.debug("Executing query")
```

## Request Scope

### Basic Request Scope

```python
from morado.common.logger import get_logger, request_scope

logger = get_logger(__name__)

def handle_request(request_id: str, user_id: int):
    with request_scope(request_id=request_id, user_id=user_id):
        logger.info("Processing request")
        # All logs within this scope will include request_id and user_id
        process_data()
        logger.info("Request completed")

def process_data():
    logger = get_logger(__name__)
    logger.debug("Processing data")
    # This log also includes request_id and user_id from parent scope
```

### Auto-Generated Request ID

```python
from morado.common.logger import get_logger, request_scope

logger = get_logger(__name__)

def handle_request(user_id: int):
    # Request ID is auto-generated if not provided
    with request_scope(user_id=user_id) as ctx:
        logger.info("Processing request", **ctx)
        # ctx contains the auto-generated request_id
        print(f"Request ID: {ctx['request_id']}")
```

### Nested Request Scopes

```python
from morado.common.logger import get_logger, request_scope

logger = get_logger(__name__)

def outer_operation():
    with request_scope(request_id="REQ123", user_id=42):
        logger.info("Outer operation started")
        
        # Inner scope with additional context
        with request_scope(trace_id="TRACE456"):
            logger.info("Inner operation")
            # Logs include: request_id=REQ123, user_id=42, trace_id=TRACE456
        
        logger.info("Outer operation completed")
        # Logs include: request_id=REQ123, user_id=42 (trace_id restored)
```

### Request Scope with Additional Context

```python
from morado.common.logger import get_logger, request_scope

logger = get_logger(__name__)

def handle_request(request_id: str, user_id: int, session_id: str):
    with request_scope(
        request_id=request_id,
        user_id=user_id,
        session_id=session_id  # Additional context
    ) as ctx:
        logger.info("Request received", **ctx)
        # All context variables are included in logs
```

### Using Decorators

```python
from morado.common.logger import get_logger, with_request_context

logger = get_logger(__name__)

@with_request_context(request_id_arg='req_id', user_id_arg='user')
def handle_request(req_id: str, user: int, data: dict):
    # Context is automatically set from function arguments
    logger.info("Processing request")
    return process_data(data)

# Call the function
handle_request(req_id="REQ123", user=42, data={"key": "value"})
```

## Async Logging

### Basic Async Logging

```python
import asyncio
from morado.common.logger import get_logger, async_request_scope

logger = get_logger(__name__)

async def handle_async_request(request_id: str, user_id: int):
    async with async_request_scope(request_id=request_id, user_id=user_id):
        logger.info("Async request started")
        await process_async_data()
        logger.info("Async request completed")

async def process_async_data():
    logger = get_logger(__name__)
    logger.debug("Processing async data")
    await asyncio.sleep(0.1)
    logger.debug("Async data processed")

# Run the async function
asyncio.run(handle_async_request("REQ123", 42))
```

### Concurrent Async Tasks

```python
import asyncio
from morado.common.logger import get_logger, async_request_scope

logger = get_logger(__name__)

async def process_task(task_id: int, user_id: int):
    # Each task has its own isolated context
    async with async_request_scope(user_id=user_id) as ctx:
        logger.info(f"Task {task_id} started", task_id=task_id, **ctx)
        await asyncio.sleep(0.1)
        logger.info(f"Task {task_id} completed", task_id=task_id)

async def main():
    # Run multiple tasks concurrently
    tasks = [
        process_task(1, user_id=42),
        process_task(2, user_id=43),
        process_task(3, user_id=44),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

### Async Decorator

```python
import asyncio
from morado.common.logger import get_logger, async_with_request_context

logger = get_logger(__name__)

@async_with_request_context(request_id_arg='req_id', user_id_arg='user')
async def handle_async_request(req_id: str, user: int, data: dict):
    # Context is automatically set from function arguments
    logger.info("Processing async request")
    await asyncio.sleep(0.1)
    return {"status": "success"}

# Call the async function
asyncio.run(handle_async_request(req_id="REQ123", user=42, data={}))
```

### Async with FastAPI

```python
from fastapi import FastAPI, Request
from morado.common.logger import get_logger, async_request_scope

app = FastAPI()
logger = get_logger(__name__)

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, request: Request):
    # Extract request ID from headers or generate one
    request_id = request.headers.get("X-Request-ID")
    
    async with async_request_scope(request_id=request_id, user_id=user_id):
        logger.info("Fetching user data")
        user_data = await fetch_user_from_db(user_id)
        logger.info("User data fetched successfully")
        return user_data

async def fetch_user_from_db(user_id: int):
    logger = get_logger(__name__)
    logger.debug("Querying database", user_id=user_id)
    # Database query here
    return {"id": user_id, "name": "Alice"}
```

## Custom Processors

### Creating a Custom Processor

```python
# myapp/logging/processors.py

def add_hostname_processor(logger, method_name, event_dict):
    """Add hostname to all log events"""
    import socket
    event_dict['hostname'] = socket.gethostname()
    return event_dict

def add_environment_processor(logger, method_name, event_dict):
    """Add environment information to log events"""
    import os
    event_dict['environment'] = os.getenv('APP_ENV', 'development')
    return event_dict

def redact_sensitive_data_processor(logger, method_name, event_dict):
    """Redact sensitive fields from log events"""
    sensitive_fields = ['password', 'token', 'api_key', 'secret']
    
    for field in sensitive_fields:
        if field in event_dict:
            event_dict[field] = '***REDACTED***'
    
    return event_dict
```

### Using Custom Processors (Configuration File)

```toml
# logging.toml
[logging]
level = "INFO"
format = "json"

[logging.processors.add_hostname]
module = "myapp.logging.processors"
enabled = true

[logging.processors.add_environment]
module = "myapp.logging.processors"
enabled = true

[logging.processors.redact_sensitive]
module = "myapp.logging.processors"
enabled = true
```

### Using Custom Processors (Programmatic)

```python
from morado.common.logger import configure_logger, LoggerConfig, ProcessorConfig

# Define processor
def add_version_processor(logger, method_name, event_dict):
    event_dict['app_version'] = '1.0.0'
    return event_dict

# Configure with custom processor
config = LoggerConfig(
    level="INFO",
    format="json",
    processors=[
        ProcessorConfig(
            name="add_version",
            module="__main__",  # Current module
            enabled=True
        )
    ]
)

configure_logger(config)

# Or add processor at runtime
from morado.common.logger import LoggerSystem

logger_system = LoggerSystem()
logger_system.add_processor(add_version_processor)
```

### Processor with Parameters

```python
# myapp/logging/processors.py

def add_custom_field_processor(logger, method_name, event_dict, field_name='custom', field_value='default'):
    """Add a custom field with configurable name and value"""
    event_dict[field_name] = field_value
    return event_dict
```

```toml
# logging.toml
[logging.processors.add_custom_field]
module = "myapp.logging.processors"
enabled = true

[logging.processors.add_custom_field.params]
field_name = "service_name"
field_value = "my-api-service"
```

## Custom Renderers

### Creating a Custom Renderer

```python
# myapp/logging/renderers.py

def custom_renderer(logger, method_name, event_dict):
    """Custom log format: [LEVEL] timestamp - message (key=value, ...)"""
    import datetime
    
    level = event_dict.get('level', 'INFO').upper()
    timestamp = event_dict.get('timestamp', datetime.datetime.now().isoformat())
    message = event_dict.get('event', '')
    
    # Build key-value pairs
    kvs = []
    for key, value in event_dict.items():
        if key not in ['level', 'timestamp', 'event']:
            kvs.append(f"{key}={value}")
    
    kv_str = ', '.join(kvs) if kvs else ''
    
    if kv_str:
        return f"[{level}] {timestamp} - {message} ({kv_str})\n"
    else:
        return f"[{level}] {timestamp} - {message}\n"
```

### Using Custom Renderer

```python
from morado.common.logger import configure_logger, LoggerConfig
from myapp.logging.renderers import custom_renderer

# Note: Custom renderer support requires LoggerSystem implementation (task 4)
# This is a placeholder example for when that's available

config = LoggerConfig(
    level="INFO",
    format="custom"  # Specify custom format
)

# Configure with custom renderer
# configure_logger(config, custom_renderer=custom_renderer)
```

### Colored Console Renderer

```python
# myapp/logging/renderers.py

def colored_console_renderer(logger, method_name, event_dict):
    """Console renderer with colors based on log level"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    level = event_dict.get('level', 'INFO').upper()
    message = event_dict.get('event', '')
    
    color = COLORS.get(level, COLORS['RESET'])
    reset = COLORS['RESET']
    
    # Format: [LEVEL] message
    output = f"{color}[{level}]{reset} {message}"
    
    # Add context if present
    context_keys = ['request_id', 'user_id', 'trace_id']
    context_parts = []
    for key in context_keys:
        if key in event_dict:
            context_parts.append(f"{key}={event_dict[key]}")
    
    if context_parts:
        output += f" ({', '.join(context_parts)})"
    
    return output + "\n"
```

## UUID Generation

### Basic UUID Generation

```python
from morado.common.utils import uuid4, ulid, alphanumeric, numeric

# Standard UUID4
id1 = uuid4()
print(id1)  # e.g., "550e8400-e29b-41d4-a716-446655440000"

# ULID (sortable)
id2 = ulid()
print(id2)  # e.g., "01ARZ3NDEKTSV4RRFFQ69G5FAV"

# Alphanumeric
id3 = alphanumeric(length=24)
print(id3)  # e.g., "ABC123XYZ789DEF456GHI012"

# Numeric
id4 = numeric(length=20)
print(id4)  # e.g., "12345678901234567890"
```

### UUID with Prefix/Suffix

```python
from morado.common.utils import alphanumeric, numeric

# Request ID with prefix
request_id = alphanumeric(length=24, prefix="REQ")
print(request_id)  # e.g., "REQABC123XYZ789DEF456GH"

# User ID with prefix and suffix
user_id = numeric(length=20, prefix="USER", suffix="END")
print(user_id)  # e.g., "USER12345678901234END"
```

### Custom Charset

```python
from morado.common.utils import alphanumeric

# Hexadecimal ID
hex_id = alphanumeric(
    length=32,
    charset="0123456789ABCDEF"
)
print(hex_id)  # e.g., "A1B2C3D4E5F67890A1B2C3D4E5F67890"

# Lowercase alphanumeric
lower_id = alphanumeric(
    length=24,
    charset="abcdefghijklmnopqrstuvwxyz0123456789"
)
print(lower_id)  # e.g., "abc123xyz789def456ghi012"
```

### UUID with Configuration

```python
from morado.common.utils import UUIDGenerator, UUIDConfig

# Create configuration
config = UUIDConfig(
    format="alphanumeric",
    length=32,
    prefix="REQ",
    suffix="",
    charset="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    use_timestamp=True,
    secure=True
)

# Generate UUID with configuration
request_id = UUIDGenerator.generate(config)
print(request_id)
```

### Sortable IDs with Timestamp

```python
from morado.common.utils import alphanumeric
import time

# Generate sortable IDs
id1 = alphanumeric(length=24, use_timestamp=True)
time.sleep(0.001)
id2 = alphanumeric(length=24, use_timestamp=True)

# IDs are sortable by time
print(id1 < id2)  # True
```

## Configuration

### Loading Configuration from File

```python
from morado.common.logger import configure_logger

# Auto-discover configuration file
configure_logger()

# Load from specific file
configure_logger(config_file="logging.toml")

# Load from custom location
configure_logger(config_file="/etc/myapp/logging.toml")
```

### Programmatic Configuration

```python
from morado.common.logger import configure_logger, LoggerConfig
from morado.common.utils import UUIDConfig

config = LoggerConfig(
    level="DEBUG",
    format="json",
    output="stdout",
    module_levels={
        "myapp.api": "DEBUG",
        "myapp.db": "WARNING"
    },
    request_id_config=UUIDConfig(
        format="ulid",
        prefix="REQ"
    )
)

configure_logger(config)
```

### Environment-Based Configuration

```python
import os
from morado.common.logger import configure_logger, LoggerConfig

# Determine environment
env = os.getenv("APP_ENV", "development")

if env == "production":
    config = LoggerConfig(level="INFO", format="json")
elif env == "staging":
    config = LoggerConfig(level="DEBUG", format="json")
else:
    config = LoggerConfig(level="DEBUG", format="console")

configure_logger(config)
```

### Dynamic Log Level Changes

```python
from morado.common.logger import LoggerSystem

logger_system = LoggerSystem()

# Change global log level
logger_system.set_level("DEBUG")

# Change log level for specific module
logger_system.set_level("WARNING", module="myapp.db")

# Change log level for module pattern
logger_system.set_level("ERROR", module="external.*")
```

## Real-World Scenarios

### Web API with Request Tracking

```python
from fastapi import FastAPI, Request
from morado.common.logger import get_logger, configure_logger, LoggerConfig, async_request_scope
from morado.common.utils import UUIDConfig
import time

# Configure logger
configure_logger(LoggerConfig(
    level="INFO",
    format="json",
    request_id_config=UUIDConfig(format="ulid", prefix="REQ")
))

app = FastAPI()
logger = get_logger(__name__)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Extract or generate request ID
    request_id = request.headers.get("X-Request-ID")
    
    async with async_request_scope(request_id=request_id) as ctx:
        start_time = time.time()
        
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            **ctx
        )
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            **ctx
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = ctx['request_id']
        return response

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    logger.info("Fetching user", user_id=user_id)
    # Business logic here
    return {"id": user_id, "name": "Alice"}
```

### Background Task Processing

```python
import asyncio
from morado.common.logger import get_logger, async_request_scope, configure_logger, LoggerConfig
from morado.common.utils import UUIDConfig

# Configure logger
configure_logger(LoggerConfig(
    level="INFO",
    format="json",
    request_id_config=UUIDConfig(format="alphanumeric", prefix="TASK")
))

logger = get_logger(__name__)

async def process_task(task_id: int, data: dict):
    """Process a background task with logging"""
    async with async_request_scope() as ctx:
        logger.info("Task started", task_id=task_id, **ctx)
        
        try:
            # Simulate task processing
            await asyncio.sleep(1)
            result = {"status": "success", "data": data}
            
            logger.info("Task completed", task_id=task_id, result=result)
            return result
            
        except Exception as e:
            logger.error("Task failed", task_id=task_id, error=str(e), exc_info=True)
            raise

async def main():
    tasks = [
        process_task(1, {"key": "value1"}),
        process_task(2, {"key": "value2"}),
        process_task(3, {"key": "value3"}),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("All tasks completed", total=len(tasks))

if __name__ == "__main__":
    asyncio.run(main())
```

### Database Operations with Context

```python
from morado.common.logger import get_logger, request_scope
import sqlite3

logger = get_logger(__name__)

class UserRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger(__name__)
    
    def create_user(self, user_id: int, username: str, email: str):
        """Create a user with request context"""
        with request_scope(user_id=user_id) as ctx:
            self.logger.info("Creating user", username=username, **ctx)
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO users (id, username, email) VALUES (?, ?, ?)",
                    (user_id, username, email)
                )
                
                conn.commit()
                self.logger.info("User created successfully", username=username)
                
            except sqlite3.IntegrityError as e:
                self.logger.error("User creation failed", username=username, error=str(e))
                raise
            
            finally:
                conn.close()
    
    def get_user(self, user_id: int):
        """Get user with logging"""
        with request_scope(user_id=user_id) as ctx:
            self.logger.debug("Fetching user", **ctx)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user:
                self.logger.debug("User found", **ctx)
            else:
                self.logger.warning("User not found", **ctx)
            
            return user

# Usage
repo = UserRepository("users.db")
repo.create_user(42, "alice", "alice@example.com")
user = repo.get_user(42)
```

### Microservice with Distributed Tracing

```python
from fastapi import FastAPI, Request, Header
from morado.common.logger import get_logger, configure_logger, LoggerConfig, async_request_scope
from morado.common.utils import UUIDConfig
import httpx

# Configure logger
configure_logger(LoggerConfig(
    level="INFO",
    format="json",
    context_vars=["request_id", "user_id", "trace_id", "service_name"],
    request_id_config=UUIDConfig(format="ulid", prefix="REQ")
))

app = FastAPI()
logger = get_logger(__name__)

SERVICE_NAME = "user-service"

@app.get("/api/users/{user_id}")
async def get_user(
    user_id: int,
    x_request_id: str = Header(None),
    x_trace_id: str = Header(None)
):
    """Get user with distributed tracing"""
    async with async_request_scope(
        request_id=x_request_id,
        user_id=user_id,
        trace_id=x_trace_id,
        service_name=SERVICE_NAME
    ) as ctx:
        logger.info("Fetching user data", **ctx)
        
        # Fetch user from database
        user_data = await fetch_user_from_db(user_id)
        
        # Call another microservice
        async with httpx.AsyncClient() as client:
            logger.info("Calling orders service", **ctx)
            
            response = await client.get(
                f"http://orders-service/api/orders/user/{user_id}",
                headers={
                    "X-Request-ID": ctx['request_id'],
                    "X-Trace-ID": ctx['trace_id']
                }
            )
            
            orders = response.json()
        
        logger.info("User data fetched successfully", order_count=len(orders), **ctx)
        
        return {
            "user": user_data,
            "orders": orders
        }

async def fetch_user_from_db(user_id: int):
    logger.info("Querying database", user_id=user_id)
    # Database query here
    return {"id": user_id, "name": "Alice", "email": "alice@example.com"}
```

### CLI Application with Logging

```python
import click
from morado.common.logger import get_logger, configure_logger, LoggerConfig, request_scope
from morado.common.utils import UUIDConfig

@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--json', 'use_json', is_flag=True, help='Output logs as JSON')
def cli(verbose, use_json):
    """CLI application with logging"""
    level = "DEBUG" if verbose else "INFO"
    format_type = "json" if use_json else "console"
    
    configure_logger(LoggerConfig(
        level=level,
        format=format_type,
        request_id_config=UUIDConfig(format="alphanumeric", prefix="CLI")
    ))

@cli.command()
@click.argument('user_id', type=int)
@click.argument('username')
def create_user(user_id, username):
    """Create a new user"""
    logger = get_logger(__name__)
    
    with request_scope(user_id=user_id) as ctx:
        logger.info("Creating user", username=username, **ctx)
        
        try:
            # User creation logic
            logger.debug("Validating user data", username=username)
            # ... validation ...
            
            logger.debug("Saving user to database", username=username)
            # ... database save ...
            
            logger.info("User created successfully", username=username)
            click.echo(f"User {username} created with ID {user_id}")
            
        except Exception as e:
            logger.error("User creation failed", username=username, error=str(e))
            click.echo(f"Error: {e}", err=True)
            raise

if __name__ == "__main__":
    cli()
```

## Summary

These examples demonstrate:

- Basic logging with structured data
- Request scope for context tracking
- Async logging with proper isolation
- Custom processors for extending functionality
- Custom renderers for output formatting
- UUID generation in various formats
- Configuration management
- Real-world scenarios (APIs, background tasks, microservices, CLI)

For more information:
- [Configuration Reference](CONFIGURATION_REFERENCE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- Design document at `.kiro/specs/logger-refactor/design.md`
