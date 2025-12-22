# Morado Logger Configuration Reference

This document provides a complete reference for all configuration options in the Morado logger system.

## Table of Contents

- [Configuration Sources](#configuration-sources)
- [Configuration Precedence](#configuration-precedence)
- [Configuration File Format](#configuration-file-format)
- [Configuration Options](#configuration-options)
- [Environment Variables](#environment-variables)
- [Programmatic Configuration](#programmatic-configuration)
- [Examples](#examples)

## Configuration Sources

The logger system can be configured from multiple sources:

1. **Configuration Files**: TOML or YAML files
2. **Environment Variables**: Override specific settings
3. **Programmatic Configuration**: Python code
4. **Defaults**: Built-in sensible defaults

## Configuration Precedence

When multiple configuration sources are present, they are merged with the following precedence (highest to lowest):

1. **Programmatic configuration** (code)
2. **Environment variables**
3. **Configuration file**
4. **Default values**

This means programmatic configuration always wins, followed by environment variables, then file configuration, and finally defaults.

### Example of Precedence

```toml
# logging.toml
[logging]
level = "INFO"
format = "console"
```

```bash
# Environment variable
export MORADO_LOG_LEVEL=DEBUG
```

```python
# Python code
from morado.common.logger import configure_logger, LoggerConfig

config = LoggerConfig(format="json")
configure_logger(config)
```

**Result:**
- `level = "DEBUG"` (from environment variable)
- `format = "json"` (from programmatic config)

## Configuration File Format

### File Locations

The system searches for configuration files in the following order:

1. Path specified in `MORADO_LOG_CONFIG` environment variable
2. `./logging.toml` (current directory)
3. `./config/logging.toml`
4. `~/.morado/logging.toml` (user home directory)

The first file found is used. If no file is found, defaults are used.

### TOML Format

```toml
[logging]
level = "INFO"
format = "console"
output = "stdout"

[logging.module_levels]
"module.name" = "LEVEL"

[logging.request_id]
format = "alphanumeric"
length = 24

[logging.processors.processor_name]
module = "path.to.module"
enabled = true
```

### YAML Format

```yaml
logging:
  level: INFO
  format: console
  output: stdout
  
  module_levels:
    module.name: LEVEL
  
  request_id:
    format: alphanumeric
    length: 24
  
  processors:
    processor_name:
      module: path.to.module
      enabled: true
```

## Configuration Options

### Core Logging Options

#### `level`

**Type:** String  
**Default:** `"INFO"`  
**Valid Values:** `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`

Global log level for all loggers.

```toml
[logging]
level = "DEBUG"
```

```python
config = LoggerConfig(level="DEBUG")
```

#### `format`

**Type:** String  
**Default:** `"console"`  
**Valid Values:** `"console"`, `"json"`, `"structured"`

Output format for log messages.

- `console`: Human-readable colored output for development
- `json`: Machine-readable JSON format for production
- `structured`: Structured format with key-value pairs

```toml
[logging]
format = "json"
```

```python
config = LoggerConfig(format="json")
```

#### `output`

**Type:** String  
**Default:** `"stdout"`  
**Valid Values:** `"stdout"`, `"stderr"`, or any file path

Destination for log output.

```toml
[logging]
output = "stdout"
# or
output = "/var/log/myapp.log"
```

```python
config = LoggerConfig(output="stdout")
# or
config = LoggerConfig(output="/var/log/myapp.log")
```

### Module-Specific Log Levels

#### `module_levels`

**Type:** Dictionary  
**Default:** `{}`

Set different log levels for specific modules or module patterns.

```toml
[logging.module_levels]
"morado.api" = "DEBUG"
"morado.db" = "WARNING"
"morado.utils" = "INFO"
"external.library" = "ERROR"
```

```python
config = LoggerConfig(
    module_levels={
        "morado.api": "DEBUG",
        "morado.db": "WARNING",
        "morado.utils": "INFO",
        "external.library": "ERROR"
    }
)
```

**Pattern Matching:**

Module patterns support wildcard matching:

```toml
[logging.module_levels]
"morado.*" = "DEBUG"        # All morado modules
"morado.api.*" = "INFO"     # All API modules (more specific, takes precedence)
```

### Context Variables

#### `context_vars`

**Type:** List of Strings  
**Default:** `["request_id", "user_id", "trace_id"]`

List of context variables to include in log output.

```toml
[logging]
context_vars = ["request_id", "user_id", "trace_id", "session_id"]
```

```python
config = LoggerConfig(
    context_vars=["request_id", "user_id", "trace_id", "session_id"]
)
```

### Request ID Configuration

#### `request_id` Section

Configuration for automatic request ID generation.

##### `format`

**Type:** String  
**Default:** `"alphanumeric"`  
**Valid Values:** `"alphanumeric"`, `"numeric"`, `"uuid4"`, `"ulid"`

Format for auto-generated request IDs.

- `alphanumeric`: Uppercase letters and numbers (e.g., `ABC123XYZ789`)
- `numeric`: Numbers only (e.g., `1234567890`)
- `uuid4`: Standard RFC 4122 UUID4 (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- `ulid`: ULID-like sortable IDs (e.g., `01ARZ3NDEKTSV4RRFFQ69G5FAV`)

```toml
[logging.request_id]
format = "ulid"
```

```python
from morado.common.utils import UUIDConfig

config = LoggerConfig(
    request_id_config=UUIDConfig(format="ulid")
)
```

##### `length`

**Type:** Integer  
**Default:** `24`  
**Valid Range:** 1-256

Length of generated request IDs (for alphanumeric and numeric formats).

```toml
[logging.request_id]
format = "alphanumeric"
length = 32
```

```python
config = LoggerConfig(
    request_id_config=UUIDConfig(format="alphanumeric", length=32)
)
```

##### `prefix`

**Type:** String  
**Default:** `""`

Prefix to prepend to generated request IDs.

```toml
[logging.request_id]
format = "alphanumeric"
length = 24
prefix = "REQ"
```

```python
config = LoggerConfig(
    request_id_config=UUIDConfig(format="alphanumeric", length=24, prefix="REQ")
)
```

##### `suffix`

**Type:** String  
**Default:** `""`

Suffix to append to generated request IDs.

```toml
[logging.request_id]
format = "alphanumeric"
length = 24
suffix = "END"
```

```python
config = LoggerConfig(
    request_id_config=UUIDConfig(format="alphanumeric", length=24, suffix="END")
)
```

##### `charset`

**Type:** String  
**Default:** `"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"`

Character set for alphanumeric IDs.

```toml
[logging.request_id]
format = "alphanumeric"
charset = "0123456789ABCDEF"  # Hexadecimal
```

```python
config = LoggerConfig(
    request_id_config=UUIDConfig(
        format="alphanumeric",
        charset="0123456789ABCDEF"
    )
)
```

##### `use_timestamp`

**Type:** Boolean  
**Default:** `true`

Include timestamp component in generated IDs for sortability.

```toml
[logging.request_id]
format = "alphanumeric"
use_timestamp = true
```

```python
config = LoggerConfig(
    request_id_config=UUIDConfig(format="alphanumeric", use_timestamp=True)
)
```

##### `secure`

**Type:** Boolean  
**Default:** `true`

Use cryptographically secure random source.

```toml
[logging.request_id]
format = "alphanumeric"
secure = true
```

```python
config = LoggerConfig(
    request_id_config=UUIDConfig(format="alphanumeric", secure=True)
)
```

### Custom Processors

#### `processors` Section

Configure custom log processors.

```toml
[logging.processors.add_hostname]
module = "myapp.logging.processors"
enabled = true

[logging.processors.add_hostname.params]
include_ip = true
```

```python
from morado.common.logger import ProcessorConfig

config = LoggerConfig(
    processors=[
        ProcessorConfig(
            name="add_hostname",
            module="myapp.logging.processors",
            enabled=True,
            params={"include_ip": True}
        )
    ]
)
```

**Processor Fields:**

- `name`: Processor identifier
- `module`: Python module path containing the processor function
- `enabled`: Whether the processor is active
- `params`: Dictionary of parameters passed to the processor

## Environment Variables

Override configuration options using environment variables:

### Core Options

| Environment Variable | Configuration Option | Example |
|---------------------|---------------------|---------|
| `MORADO_LOG_CONFIG` | Config file path | `/etc/myapp/logging.toml` |
| `MORADO_LOG_LEVEL` | `level` | `DEBUG` |
| `MORADO_LOG_FORMAT` | `format` | `json` |
| `MORADO_LOG_OUTPUT` | `output` | `stderr` |

### Request ID Options

| Environment Variable | Configuration Option | Example |
|---------------------|---------------------|---------|
| `MORADO_REQUEST_ID_FORMAT` | `request_id.format` | `ulid` |
| `MORADO_REQUEST_ID_LENGTH` | `request_id.length` | `32` |
| `MORADO_REQUEST_ID_PREFIX` | `request_id.prefix` | `REQ` |
| `MORADO_REQUEST_ID_SUFFIX` | `request_id.suffix` | `END` |

### Example Usage

```bash
# Set log level to DEBUG
export MORADO_LOG_LEVEL=DEBUG

# Use JSON format
export MORADO_LOG_FORMAT=json

# Use ULID format for request IDs
export MORADO_REQUEST_ID_FORMAT=ulid

# Specify custom config file
export MORADO_LOG_CONFIG=/etc/myapp/logging.toml
```

## Programmatic Configuration

### Basic Configuration

```python
from morado.common.logger import configure_logger, LoggerConfig

# Simple configuration
config = LoggerConfig(level="DEBUG", format="json")
configure_logger(config)
```

### Full Configuration

```python
from morado.common.logger import configure_logger, LoggerConfig, ProcessorConfig
from morado.common.utils import UUIDConfig

config = LoggerConfig(
    level="DEBUG",
    format="json",
    output="stdout",
    module_levels={
        "morado.api": "DEBUG",
        "morado.db": "WARNING"
    },
    context_vars=["request_id", "user_id", "trace_id", "session_id"],
    request_id_config=UUIDConfig(
        format="ulid",
        length=26,
        prefix="REQ",
        secure=True
    ),
    processors=[
        ProcessorConfig(
            name="add_hostname",
            module="myapp.logging.processors",
            enabled=True,
            params={"include_ip": True}
        )
    ]
)

configure_logger(config)
```

### Loading from File

```python
from morado.common.logger import configure_logger

# Load from specific file
configure_logger(config_file="logging.toml")

# Auto-discover config file
configure_logger()

# Load and override
from morado.common.logger import LoggerConfig

configure_logger(
    config_file="logging.toml",
    level="DEBUG"  # Override file setting
)
```

### Merging Configurations

```python
from morado.common.logger import LoggerConfig

# Base configuration
base_config = LoggerConfig(level="INFO", format="console")

# Override configuration
override_config = LoggerConfig(level="DEBUG")

# Merge (override takes precedence)
merged_config = base_config.merge(override_config)

# Result: level="DEBUG", format="console"
```

## Examples

### Development Configuration

```toml
# logging.toml
[logging]
level = "DEBUG"
format = "console"
output = "stdout"

[logging.module_levels]
"morado.api" = "DEBUG"
"morado.db" = "INFO"
"external.library" = "WARNING"

[logging.request_id]
format = "alphanumeric"
length = 16
prefix = "DEV"
```

### Production Configuration

```toml
# logging.toml
[logging]
level = "INFO"
format = "json"
output = "/var/log/myapp/app.log"

[logging.module_levels]
"morado.api" = "INFO"
"morado.db" = "WARNING"
"external.library" = "ERROR"

[logging.request_id]
format = "ulid"
secure = true
```

### Testing Configuration

```toml
# logging.toml
[logging]
level = "WARNING"
format = "console"
output = "stderr"

[logging.request_id]
format = "numeric"
length = 10
secure = false
```

### Microservices Configuration

```toml
# logging.toml
[logging]
level = "INFO"
format = "json"
output = "stdout"

[logging]
context_vars = ["request_id", "user_id", "trace_id", "service_name", "pod_id"]

[logging.module_levels]
"myservice.api" = "DEBUG"
"myservice.business" = "INFO"
"myservice.data" = "WARNING"

[logging.request_id]
format = "ulid"
prefix = "SVC"
```

### Multi-Environment Configuration

```python
import os
from morado.common.logger import configure_logger, LoggerConfig

# Determine environment
env = os.getenv("APP_ENV", "development")

if env == "production":
    config = LoggerConfig(
        level="INFO",
        format="json",
        output="/var/log/myapp/app.log"
    )
elif env == "staging":
    config = LoggerConfig(
        level="DEBUG",
        format="json",
        output="stdout"
    )
else:  # development
    config = LoggerConfig(
        level="DEBUG",
        format="console",
        output="stdout"
    )

configure_logger(config)
```

## Validation

The configuration system automatically validates all settings:

### Invalid Values

When invalid values are provided, the system:

1. Logs a warning message
2. Uses the default value for that setting
3. Continues operation without crashing

**Example:**

```toml
[logging]
level = "INVALID"  # Warning logged, defaults to "INFO"
format = "unknown"  # Warning logged, defaults to "console"
```

### Valid Values Reference

| Option | Valid Values |
|--------|-------------|
| `level` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `format` | `console`, `json`, `structured` |
| `output` | `stdout`, `stderr`, or any file path |
| `request_id.format` | `alphanumeric`, `numeric`, `uuid4`, `ulid` |
| `request_id.length` | 1-256 (integer) |
| `request_id.secure` | `true`, `false` (boolean) |
| `request_id.use_timestamp` | `true`, `false` (boolean) |

## Best Practices

### 1. Use Configuration Files for Environments

Create separate configuration files for each environment:

```
config/
  ├── logging.dev.toml
  ├── logging.staging.toml
  └── logging.prod.toml
```

Load the appropriate file based on environment:

```python
import os
from morado.common.logger import configure_logger

env = os.getenv("APP_ENV", "dev")
config_file = f"config/logging.{env}.toml"
configure_logger(config_file=config_file)
```

### 2. Use Environment Variables for Secrets

Don't put sensitive information in config files. Use environment variables:

```bash
export MORADO_LOG_OUTPUT=/secure/path/app.log
```

### 3. Set Module-Specific Levels

Reduce noise by setting appropriate levels for different modules:

```toml
[logging.module_levels]
"myapp.api" = "DEBUG"      # Detailed API logs
"myapp.business" = "INFO"  # Business logic
"myapp.data" = "WARNING"   # Only warnings from data layer
"sqlalchemy" = "ERROR"     # Only errors from SQLAlchemy
```

### 4. Use ULID for Distributed Systems

For microservices and distributed systems, use ULID format for sortable, time-based IDs:

```toml
[logging.request_id]
format = "ulid"
```

### 5. Use JSON Format in Production

For production environments, use JSON format for easy parsing and analysis:

```toml
[logging]
format = "json"
output = "stdout"  # Let container orchestration handle log collection
```

## Troubleshooting

### Configuration Not Loading

**Problem:** Configuration file is not being loaded.

**Solution:**
1. Check file location (see [File Locations](#file-locations))
2. Verify file format (TOML or YAML)
3. Check for syntax errors
4. Set `MORADO_LOG_CONFIG` environment variable to explicit path

### Invalid Configuration Values

**Problem:** Configuration values are being ignored.

**Solution:**
1. Check console for warning messages
2. Verify values against [Valid Values Reference](#valid-values-reference)
3. Check spelling and case sensitivity

### Environment Variables Not Working

**Problem:** Environment variables are not overriding configuration.

**Solution:**
1. Verify environment variable names (see [Environment Variables](#environment-variables))
2. Ensure variables are exported: `export MORADO_LOG_LEVEL=DEBUG`
3. Check precedence order (env vars override file config)

## Summary

The Morado logger configuration system provides:

- Multiple configuration sources (files, env vars, code)
- Clear precedence rules
- Automatic validation with sensible defaults
- Flexible module-specific settings
- Comprehensive request ID configuration
- Easy extensibility with custom processors

For usage examples, see [Usage Examples](USAGE_EXAMPLES.md).  
For migration from the old system, see [Migration Guide](MIGRATION_GUIDE.md).
