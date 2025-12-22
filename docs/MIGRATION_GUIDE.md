# Morado Logger Migration Guide

This guide helps you migrate from the old logger implementation to the new refactored logger system.

## Overview of Changes

The refactored logger system provides:

- **Configuration-driven architecture**: External TOML/YAML configuration files
- **Modular design**: Separated UUID generation from logging
- **Improved API**: Cleaner imports and simpler usage
- **Better extensibility**: Easy to add custom processors and renderers
- **Enhanced async support**: Proper async context management

## Import Changes

### Logger Imports

**Before:**
```python
from morado.common.logger.log import get_logger, request_scope
from morado.common.logger.log import LoggerUtil
```

**After:**
```python
from morado.common.logger import get_logger, request_scope
from morado.common.logger import configure_logger, LoggerConfig
```

### UUID Generator Imports

**Before:**
```python
from morado.common.utils.uuid_generator import UUIDGenerator
```

**After:**
```python
from morado.common.utils import UUIDGenerator, uuid4, ulid
from morado.common.utils import alphanumeric, numeric
```

### Context Management Imports

**Before:**
```python
from morado.common.logger.log import request_scope
```

**After:**
```python
from morado.common.logger import request_scope, async_request_scope
from morado.common.logger import ContextManager
```

## API Changes

### 1. Logger Initialization

**Before:**
```python
from morado.common.logger.log import LoggerUtil

logger_util = LoggerUtil()
logger = logger_util.get_logger(__name__)
```

**After:**
```python
from morado.common.logger import get_logger

# Simple usage - no initialization needed
logger = get_logger(__name__)

# Or with configuration
from morado.common.logger import configure_logger, LoggerConfig

config = LoggerConfig(level="DEBUG", format="json")
configure_logger(config)
logger = get_logger(__name__)
```

**Key Changes:**
- No need to instantiate `LoggerUtil` class
- Direct function calls for cleaner API
- Configuration is now explicit and optional

### 2. Request Scope Usage

**Before:**
```python
from morado.common.logger.log import request_scope

with request_scope(request_id="REQ123", user_id=42):
    logger.info("Processing request")
```

**After:**
```python
from morado.common.logger import request_scope

# Same API - fully backward compatible
with request_scope(request_id="REQ123", user_id=42):
    logger.info("Processing request")

# Auto-generates request_id if not provided
with request_scope(user_id=42) as ctx:
    logger.info("Processing request", **ctx)
```

**Key Changes:**
- API remains the same for basic usage
- Now auto-generates `request_id` if not provided
- Context dict is yielded for convenience

### 3. Async Request Scope

**Before:**
```python
# Not available in old implementation
```

**After:**
```python
from morado.common.logger import async_request_scope

async def handle_request(user_id: int):
    async with async_request_scope(user_id=user_id) as ctx:
        logger.info("Processing async request", **ctx)
```

**Key Changes:**
- New async-specific context manager
- Proper async context isolation
- Same API as sync version

### 4. UUID Generation

**Before:**
```python
from morado.common.utils.uuid_generator import UUIDGenerator

generator = UUIDGenerator()
request_id = generator.generate_alphanumeric(length=24, prefix="REQ")
```

**After:**
```python
from morado.common.utils import UUIDGenerator, alphanumeric, uuid4, ulid

# Using convenience functions (recommended)
request_id = alphanumeric(length=24, prefix="REQ")
standard_uuid = uuid4()
sortable_id = ulid()

# Using generator class (for advanced usage)
from morado.common.utils import UUIDConfig

config = UUIDConfig(format="alphanumeric", length=24, prefix="REQ")
request_id = UUIDGenerator.generate(config)
```

**Key Changes:**
- Stateless generator (all methods are static)
- Convenience functions for common formats
- Configuration-based generation
- New formats: UUID4, ULID

### 5. Configuration

**Before:**
```python
# Configuration was hard-coded in the implementation
# No external configuration support
```

**After:**
```python
from morado.common.logger import configure_logger, LoggerConfig
from morado.common.utils import UUIDConfig

# Programmatic configuration
config = LoggerConfig(
    level="DEBUG",
    format="json",
    output="stdout",
    module_levels={
        "morado.api": "DEBUG",
        "morado.db": "WARNING"
    },
    request_id_config=UUIDConfig(
        format="alphanumeric",
        length=24,
        prefix="REQ"
    )
)
configure_logger(config)

# Or load from file
configure_logger(config_file="logging.toml")

# Or use auto-discovery
configure_logger()  # Searches for logging.toml in standard locations
```

**Key Changes:**
- External configuration files (TOML/YAML)
- Programmatic configuration with dataclasses
- Configuration precedence: code > env vars > file > defaults
- Module-specific log levels

### 6. Decorators

**Before:**
```python
# Not available in old implementation
```

**After:**
```python
from morado.common.logger import with_request_context, log_execution

@with_request_context(request_id_arg='req_id', user_id_arg='user')
def handle_request(req_id: str, user: int):
    logger.info("Handling request")

@log_execution(level="DEBUG", include_args=True)
def process_data(data: dict):
    return {"result": "success"}

# Async version
from morado.common.logger import async_with_request_context

@async_with_request_context()
async def handle_async_request(request_id: str, user_id: int):
    logger.info("Handling async request")
```

**Key Changes:**
- New decorator-based context management
- Automatic context extraction from function arguments
- Execution logging decorator
- Async decorator support

## Configuration File Format

Create a `logging.toml` file in your project root:

```toml
[logging]
level = "INFO"
format = "console"  # console, json, structured
output = "stdout"   # stdout, stderr, or file path

# Module-specific log levels
[logging.module_levels]
"morado.api" = "DEBUG"
"morado.db" = "WARNING"
"morado.utils" = "INFO"

# Request ID configuration
[logging.request_id]
format = "alphanumeric"  # alphanumeric, numeric, uuid4, ulid
length = 24
prefix = "REQ"
suffix = ""
use_timestamp = false
secure = true

# Custom processors (optional)
[logging.processors.custom_processor]
module = "myapp.logging.processors"
enabled = true

[logging.processors.custom_processor.params]
param1 = "value1"
```

## Environment Variables

Override configuration with environment variables:

```bash
# Log level
export MORADO_LOG_LEVEL=DEBUG

# Output format
export MORADO_LOG_FORMAT=json

# Output destination
export MORADO_LOG_OUTPUT=stdout

# Request ID configuration
export MORADO_REQUEST_ID_FORMAT=ulid
export MORADO_REQUEST_ID_LENGTH=26
export MORADO_REQUEST_ID_PREFIX=REQ
```

## Migration Steps

### Step 1: Update Imports

Replace all old imports with new ones:

```bash
# Find and replace in your codebase
# Old: from morado.common.logger.log import
# New: from morado.common.logger import
```

### Step 2: Remove LoggerUtil Instantiation

**Before:**
```python
from morado.common.logger.log import LoggerUtil

class MyService:
    def __init__(self):
        self.logger_util = LoggerUtil()
        self.logger = self.logger_util.get_logger(__name__)
```

**After:**
```python
from morado.common.logger import get_logger

class MyService:
    def __init__(self):
        self.logger = get_logger(__name__)
```

### Step 3: Update UUID Generation

**Before:**
```python
from morado.common.utils.uuid_generator import UUIDGenerator

generator = UUIDGenerator()
id1 = generator.generate_alphanumeric(length=24)
id2 = generator.generate_numeric(length=20)
```

**After:**
```python
from morado.common.utils import alphanumeric, numeric

id1 = alphanumeric(length=24)
id2 = numeric(length=20)
```

### Step 4: Add Configuration (Optional)

Create a `logging.toml` file in your project root with your desired configuration. If you don't create one, the system will use sensible defaults.

### Step 5: Initialize Logger (Optional)

If you need custom configuration, add initialization code at your application entry point:

```python
from morado.common.logger import configure_logger, LoggerConfig

def main():
    # Configure logger at startup
    configure_logger(config_file="logging.toml")
    
    # Or use programmatic configuration
    config = LoggerConfig(level="DEBUG", format="json")
    configure_logger(config)
    
    # Rest of your application
    ...
```

### Step 6: Test Your Application

Run your tests to ensure everything works:

```bash
pytest tests/
```

## Common Migration Issues

### Issue 1: Import Errors

**Problem:**
```python
ImportError: cannot import name 'LoggerUtil' from 'morado.common.logger'
```

**Solution:**
`LoggerUtil` class no longer exists. Use `get_logger()` function instead:

```python
# Old
from morado.common.logger.log import LoggerUtil
logger_util = LoggerUtil()
logger = logger_util.get_logger()

# New
from morado.common.logger import get_logger
logger = get_logger()
```

### Issue 2: UUID Generator Methods

**Problem:**
```python
AttributeError: 'UUIDGenerator' object has no attribute 'generate_alphanumeric'
```

**Solution:**
Method names have changed. Use convenience functions or the `generate()` method:

```python
# Old
generator = UUIDGenerator()
id = generator.generate_alphanumeric(length=24)

# New - Option 1: Convenience function
from morado.common.utils import alphanumeric
id = alphanumeric(length=24)

# New - Option 2: Generator with config
from morado.common.utils import UUIDGenerator, UUIDConfig
config = UUIDConfig(format="alphanumeric", length=24)
id = UUIDGenerator.generate(config)
```

### Issue 3: Request Scope Context

**Problem:**
Context variables not appearing in logs.

**Solution:**
Ensure you're using the logger system correctly and that context injection is enabled:

```python
from morado.common.logger import get_logger, request_scope

logger = get_logger(__name__)

with request_scope(request_id="REQ123", user_id=42):
    # Context will be automatically included in logs
    logger.info("Processing request")
```

### Issue 4: Configuration Not Loading

**Problem:**
Configuration file is not being loaded.

**Solution:**
Ensure the file is in one of the search locations:

1. Path in `MORADO_LOG_CONFIG` environment variable
2. `./logging.toml` (current directory)
3. `./config/logging.toml`
4. `~/.morado/logging.toml`

Or explicitly specify the path:

```python
from morado.common.logger import configure_logger
configure_logger(config_file="/path/to/logging.toml")
```

## Backward Compatibility

The new system maintains backward compatibility for most common use cases:

- ✅ `get_logger()` function works the same
- ✅ `request_scope()` context manager works the same
- ✅ Basic logging calls are unchanged
- ❌ `LoggerUtil` class is removed (use functions instead)
- ❌ UUID generator method names changed (use convenience functions)

## Benefits of Migration

After migration, you'll benefit from:

1. **Cleaner Code**: Simpler imports and no class instantiation
2. **Better Configuration**: External config files and environment variables
3. **More Flexibility**: Easy to add custom processors and renderers
4. **Improved Performance**: Stateless design and optimized context management
5. **Better Testing**: Easier to mock and test with the new architecture
6. **Async Support**: Proper async context isolation
7. **More UUID Formats**: UUID4, ULID, and custom formats

## Getting Help

If you encounter issues during migration:

1. Check this migration guide
2. Review the [Configuration Reference](CONFIGURATION_REFERENCE.md)
3. See [Usage Examples](USAGE_EXAMPLES.md)
4. Check the design document at `.kiro/specs/logger-refactor/design.md`

## Summary

The migration process is straightforward:

1. Update imports from `morado.common.logger.log` to `morado.common.logger`
2. Replace `LoggerUtil()` instantiation with direct `get_logger()` calls
3. Update UUID generator method calls to use convenience functions
4. Optionally add configuration file for customization
5. Test your application

Most code will work with minimal changes, and you'll gain access to powerful new features!
