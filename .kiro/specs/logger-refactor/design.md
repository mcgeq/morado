# Logger and UUID Refactor Design Document

## Overview

This design refactors the Morado logging and UUID generation utilities into a clean, maintainable architecture with proper separation of concerns. The new design provides:

- **Configuration-driven architecture**: External YAML/TOML configuration with programmatic overrides
- **Modular components**: Independent UUID generator, configuration manager, and logger system
- **Extensible design**: Easy addition of custom processors, renderers, and UUID formats
- **Production-ready**: Comprehensive error handling, async support, and multiple output formats

The refactored system maintains backward compatibility where possible while providing a cleaner API for new code.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Code                         │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             │                                │
             v                                v
┌────────────────────────┐      ┌────────────────────────┐
│   Logger System        │      │   UUID Generator       │
│   - get_logger()       │      │   - generate()         │
│   - request_scope()    │◄─────│   - uuid4()            │
│   - configure()        │      │   - ulid()             │
└────────┬───────────────┘      └────────────────────────┘
         │                                   ▲
         │                                   │
         v                                   │
┌────────────────────────┐                  │
│ Configuration Manager  │──────────────────┘
│ - load_config()        │
│ - merge_configs()      │
└────────────────────────┘
         │
         v
┌────────────────────────┐
│  Config Files          │
│  - logging.toml        │
│  - .env                │
└────────────────────────┘
```

### Component Responsibilities

1. **UUID Generator** (`src/morado/common/utils/uuid.py`)
   - Generates various UUID formats independently
   - No dependencies on logger
   - Configurable through its own config object

2. **Configuration Manager** (`src/morado/common/logger/config.py`)
   - Loads configuration from files (TOML/YAML)
   - Merges configurations with precedence
   - Validates configuration schemas

3. **Logger System** (`src/morado/common/logger/logger.py`)
   - Initializes structlog with configuration
   - Manages context variables
   - Provides request scope and decorators

4. **Context Manager** (`src/morado/common/logger/context.py`)
   - Manages contextvars for request tracking
   - Provides context accessors and setters


## Components and Interfaces

### 1. UUID Generator Module

**File**: `src/morado/common/utils/uuid.py`

**Purpose**: Generate unique identifiers in various formats without external dependencies.

**Key Classes**:

```python
@dataclass
class UUIDConfig:
    """Configuration for UUID generation"""
    format: str = "alphanumeric"  # alphanumeric, numeric, uuid4, ulid, custom
    prefix: str = ""
    suffix: str = ""
    length: Optional[int] = 24
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    use_timestamp: bool = True
    secure: bool = True

class UUIDGenerator:
    """Stateless UUID generator with multiple format support"""
    
    @staticmethod
    def generate(config: Optional[UUIDConfig] = None) -> str:
        """Generate UUID based on configuration"""
    
    @staticmethod
    def uuid4() -> str:
        """Generate standard UUID4"""
    
    @staticmethod
    def ulid() -> str:
        """Generate ULID-like sortable ID"""
    
    @staticmethod
    def alphanumeric(length: int = 24, **kwargs) -> str:
        """Generate alphanumeric ID"""
    
    @staticmethod
    def numeric(length: int = 20, **kwargs) -> str:
        """Generate numeric ID"""
```

**Interface**:
- All methods are static - no state maintained
- Configuration passed as parameter or uses defaults
- No side effects or external dependencies

### 2. Configuration Manager

**File**: `src/morado/common/logger/config.py`

**Purpose**: Load, validate, and merge configuration from multiple sources.

**Key Classes**:

```python
@dataclass
class LoggerConfig:
    """Logger configuration schema"""
    level: str = "INFO"
    format: str = "console"  # console, json, structured
    output: str = "stdout"  # stdout, stderr, file path
    module_levels: Dict[str, str] = field(default_factory=dict)
    processors: List[str] = field(default_factory=list)
    context_vars: List[str] = field(default_factory=lambda: ["request_id", "user_id", "trace_id"])
    request_id_config: Optional[UUIDConfig] = None

class ConfigurationManager:
    """Manages configuration loading and merging"""
    
    @staticmethod
    def load_from_file(path: str) -> LoggerConfig:
        """Load configuration from TOML/YAML file"""
    
    @staticmethod
    def load_from_env() -> LoggerConfig:
        """Load configuration from environment variables"""
    
    @staticmethod
    def merge_configs(*configs: LoggerConfig) -> LoggerConfig:
        """Merge multiple configs with precedence"""
    
    @staticmethod
    def get_default_config() -> LoggerConfig:
        """Get default configuration"""
```

**Configuration File Format** (`logging.toml`):

```toml
[logging]
level = "INFO"
format = "console"  # console, json, structured
output = "stdout"

[logging.module_levels]
"morado.api" = "DEBUG"
"morado.db" = "WARNING"

[logging.processors]
# Built-in processors are added automatically
# Add custom processors here
custom = ["myapp.logging.custom_processor"]

[logging.request_id]
format = "alphanumeric"
length = 24
prefix = "REQ"
use_timestamp = true
secure = true
```


### 3. Context Manager

**File**: `src/morado/common/logger/context.py`

**Purpose**: Manage request-scoped context variables using contextvars.

**Key Components**:

```python
# Context variables
_request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
_user_id_var: ContextVar[Optional[int]] = ContextVar('user_id', default=None)
_trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)

class ContextManager:
    """Manages logging context variables"""
    
    @staticmethod
    def get_request_id() -> Optional[str]:
        """Get current request ID"""
    
    @staticmethod
    def set_request_id(request_id: str) -> Token:
        """Set current request ID"""
    
    @staticmethod
    def get_user_id() -> Optional[int]:
        """Get current user ID"""
    
    @staticmethod
    def set_user_id(user_id: int) -> Token:
        """Set current user ID"""
    
    @staticmethod
    def get_trace_id() -> Optional[str]:
        """Get current trace ID"""
    
    @staticmethod
    def set_trace_id(trace_id: str) -> Token:
        """Set current trace ID"""
    
    @staticmethod
    def get_all_context() -> Dict[str, Any]:
        """Get all context variables as dict"""
    
    @staticmethod
    def clear_context() -> None:
        """Clear all context variables"""

@contextmanager
def request_scope(
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    trace_id: Optional[str] = None,
    **additional_context: Any
) -> Generator[Dict[str, Any], None, None]:
    """Context manager for request-scoped logging"""

@contextmanager
async def async_request_scope(
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
    trace_id: Optional[str] = None,
    **additional_context: Any
) -> AsyncGenerator[Dict[str, Any], None]:
    """Async context manager for request-scoped logging"""
```

### 4. Logger System

**File**: `src/morado/common/logger/logger.py`

**Purpose**: Initialize and configure structlog, provide logger instances.

**Key Classes**:

```python
class LoggerSystem:
    """Main logger system (singleton)"""
    
    _instance: Optional['LoggerSystem'] = None
    _configured: bool = False
    _config: LoggerConfig
    
    def __new__(cls) -> 'LoggerSystem':
        """Ensure singleton instance"""
    
    def configure(
        self,
        config: Optional[LoggerConfig] = None,
        config_file: Optional[str] = None,
        **overrides
    ) -> None:
        """Configure the logger system"""
    
    def get_logger(self, name: Optional[str] = None) -> BoundLogger:
        """Get a logger instance"""
    
    def add_processor(self, processor: Callable) -> None:
        """Add a custom processor"""
    
    def set_level(self, level: str, module: Optional[str] = None) -> None:
        """Set log level globally or for specific module"""
    
    def _build_processor_chain(self) -> List[Callable]:
        """Build the processor chain from configuration"""
    
    def _get_renderer(self) -> Callable:
        """Get the appropriate renderer based on configuration"""
    
    def _inject_context_vars(self, logger, method_name, event_dict):
        """Processor to inject context variables"""

# Global functions
def get_logger(name: Optional[str] = None) -> BoundLogger:
    """Get a logger instance (convenience function)"""

def configure_logger(
    config: Optional[LoggerConfig] = None,
    config_file: Optional[str] = None,
    **overrides
) -> None:
    """Configure the logger system (convenience function)"""
```


### 5. Decorators Module

**File**: `src/morado/common/logger/decorators.py`

**Purpose**: Provide decorators for automatic context management.

**Key Components**:

```python
def with_request_context(
    request_id_arg: str = 'request_id',
    user_id_arg: str = 'user_id',
    trace_id_arg: str = 'trace_id',
    auto_generate: bool = True
):
    """Decorator to automatically apply request context from function arguments"""

def log_execution(
    level: str = "INFO",
    include_args: bool = False,
    include_result: bool = False
):
    """Decorator to log function execution"""

def async_with_request_context(
    request_id_arg: str = 'request_id',
    user_id_arg: str = 'user_id',
    trace_id_arg: str = 'trace_id',
    auto_generate: bool = True
):
    """Async version of with_request_context"""
```

## Data Models

### Configuration Data Models

```python
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

@dataclass
class UUIDConfig:
    """UUID generation configuration"""
    format: str = "alphanumeric"
    prefix: str = ""
    suffix: str = ""
    length: Optional[int] = 24
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    use_timestamp: bool = True
    secure: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UUIDConfig':
        """Create from dictionary"""

@dataclass
class ProcessorConfig:
    """Processor configuration"""
    name: str
    module: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class LoggerConfig:
    """Complete logger configuration"""
    level: str = "INFO"
    format: str = "console"
    output: str = "stdout"
    module_levels: Dict[str, str] = field(default_factory=dict)
    processors: List[ProcessorConfig] = field(default_factory=list)
    context_vars: List[str] = field(default_factory=lambda: ["request_id", "user_id", "trace_id"])
    request_id_config: Optional[UUIDConfig] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoggerConfig':
        """Create from dictionary"""
    
    def merge(self, other: 'LoggerConfig') -> 'LoggerConfig':
        """Merge with another config (other takes precedence)"""
```

### Context Data Models

```python
@dataclass
class RequestContext:
    """Request context data"""
    request_id: Optional[str] = None
    user_id: Optional[int] = None
    trace_id: Optional[str] = None
    additional: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration application consistency

*For any* valid log level value, when the Logger System is configured with that level, all subsequently created loggers should use that level.

**Validates: Requirements 1.3**

### Property 2: Renderer selection correctness

*For any* valid output format (console, JSON, structured), when the Logger System is configured with that format, the system should use the corresponding renderer for all log output.

**Validates: Requirements 1.4**

### Property 3: Processor execution order

*For any* ordered list of processors, when the Logger System is configured with those processors, they should execute in exactly that order for every log event.

**Validates: Requirements 1.5, 4.4**

### Property 4: Programmatic configuration precedence

*For any* configuration parameter, when set both in a file and programmatically, the programmatic value should take precedence.

**Validates: Requirements 2.2, 2.5**

### Property 5: UUID generator independence

*For any* UUID generation operation, the UUID Generator should produce valid UUIDs without requiring the Logger System to be initialized.

**Validates: Requirements 3.2**

### Property 6: Custom processor execution

*For any* custom processor registered with the Logger System, that processor should be invoked for every log event that passes through the system.

**Validates: Requirements 4.2**

### Property 7: JSON output validity

*For any* log entry when JSON format is configured, the output should be valid, parseable JSON that can be deserialized without errors.

**Validates: Requirements 5.4**

### Property 8: Context propagation

*For any* request scope with a request_id, all log entries created within that scope should include that request_id in their output.

**Validates: Requirements 6.1**

### Property 9: Context restoration round-trip

*For any* initial context state, entering and then exiting a request scope should restore the context to its original state.

**Validates: Requirements 6.4**

### Property 10: Request ID auto-generation uniqueness

*For any* sequence of request scopes without explicit request_ids, the Logger System should generate unique request_ids for each scope.

**Validates: Requirements 7.1**

### Property 11: Request ID format compliance

*For any* UUID format configuration, when the Logger System auto-generates request_ids, they should conform to the specified format.

**Validates: Requirements 7.2**

### Property 12: Explicit request ID preservation

*For any* explicitly provided request_id, when entering a request scope with that ID, the Logger System should use it exactly as provided without modification.

**Validates: Requirements 7.3**

### Property 13: Async context isolation

*For any* set of concurrent async tasks with different request contexts, each task should maintain its own context without interference from other tasks.

**Validates: Requirements 10.2**

### Property 14: Module-level log configuration

*For any* module with a configured log level, loggers created for that module should use the module-specific level rather than the global default.

**Validates: Requirements 11.1**

### Property 15: UUID4 RFC compliance

*For any* UUID generated with UUID4 format, it should conform to RFC 4122 UUID4 specification (version 4, variant 1).

**Validates: Requirements 12.1**

### Property 16: ULID temporal ordering

*For any* sequence of ULIDs generated in chronological order, they should be lexicographically sortable such that sorting them produces the same order as their generation time.

**Validates: Requirements 12.2**

### Property 17: Timestamp-based ID monotonicity

*For any* sequence of timestamp-based IDs generated within the same millisecond, they should maintain monotonic ordering through the random component.

**Validates: Requirements 12.5**


## Error Handling

### Configuration Errors

1. **Missing Configuration File**
   - Behavior: Log info message, use default configuration
   - No exception raised
   - System continues with defaults

2. **Malformed Configuration File**
   - Behavior: Log warning with parse error details
   - Fall back to default configuration
   - System continues with defaults

3. **Invalid Configuration Values**
   - Behavior: Log warning for each invalid value
   - Use default value for that specific setting
   - Continue with partial configuration

### Runtime Errors

1. **Processor Exceptions**
   - Behavior: Catch exception, log error with processor name
   - Continue with remaining processors
   - Original log event still processed

2. **Renderer Exceptions**
   - Behavior: Catch exception, log error
   - Fall back to console renderer
   - Log event is not lost

3. **Context Variable Errors**
   - Behavior: Catch exception, log warning
   - Continue logging without context
   - No crash or data loss

4. **UUID Generation Errors**
   - Behavior: Catch exception, log error
   - Fall back to simple UUID4
   - Request scope continues

### Error Recovery Strategy

```python
def safe_processor_chain(processors: List[Callable]) -> Callable:
    """Wrap processor chain with error handling"""
    def wrapped(logger, method_name, event_dict):
        for processor in processors:
            try:
                event_dict = processor(logger, method_name, event_dict)
            except Exception as e:
                # Log error but continue
                fallback_log(f"Processor {processor.__name__} failed: {e}")
        return event_dict
    return wrapped

def safe_renderer(renderer: Callable) -> Callable:
    """Wrap renderer with fallback"""
    def wrapped(logger, method_name, event_dict):
        try:
            return renderer(logger, method_name, event_dict)
        except Exception as e:
            # Fall back to console renderer
            fallback_log(f"Renderer failed: {e}")
            return ConsoleRenderer()(logger, method_name, event_dict)
    return wrapped
```

## Testing Strategy

### Unit Testing

The refactored logger and UUID system will use pytest for unit testing. Unit tests will cover:

1. **Configuration Loading**
   - Test loading from TOML files
   - Test loading from environment variables
   - Test configuration merging with correct precedence
   - Test default configuration fallback

2. **UUID Generation**
   - Test each UUID format (alphanumeric, numeric, UUID4, ULID)
   - Test prefix/suffix application
   - Test length constraints
   - Test charset validation

3. **Context Management**
   - Test context variable get/set operations
   - Test context scope entry/exit
   - Test context restoration after scope exit
   - Test async context isolation

4. **Logger Configuration**
   - Test logger initialization with various configs
   - Test processor registration
   - Test renderer selection
   - Test module-level log levels

5. **Error Handling**
   - Test behavior with missing config files
   - Test behavior with malformed config files
   - Test processor exception handling
   - Test renderer fallback

### Property-Based Testing

Property-based testing will be implemented using the **Hypothesis** library for Python. Each correctness property will be implemented as a property-based test.

**Configuration**:
- Minimum 100 iterations per property test
- Use Hypothesis strategies for generating test data
- Each test tagged with property number and requirement reference

**Property Test Implementation**:

```python
from hypothesis import given, strategies as st
import pytest

# Property 1: Configuration application consistency
@given(log_level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
def test_property_1_config_application(log_level):
    """
    Feature: logger-refactor, Property 1: Configuration application consistency
    Validates: Requirements 1.3
    """
    config = LoggerConfig(level=log_level)
    logger_system = LoggerSystem()
    logger_system.configure(config)
    
    logger = logger_system.get_logger("test")
    assert logger.level == log_level

# Property 10: Request ID auto-generation uniqueness
@given(num_scopes=st.integers(min_value=2, max_value=100))
def test_property_10_request_id_uniqueness(num_scopes):
    """
    Feature: logger-refactor, Property 10: Request ID auto-generation uniqueness
    Validates: Requirements 7.1
    """
    generated_ids = set()
    
    for _ in range(num_scopes):
        with request_scope() as ctx:
            request_id = ctx['request_id']
            assert request_id is not None
            assert request_id not in generated_ids
            generated_ids.add(request_id)
    
    assert len(generated_ids) == num_scopes
```

**Test Organization**:
- Property tests in `tests/properties/test_logger_properties.py`
- Property tests in `tests/properties/test_uuid_properties.py`
- Unit tests in `tests/unit/test_logger.py`, `tests/unit/test_uuid.py`, etc.


## Implementation Details

### Module Structure

```
src/morado/common/
├── logger/
│   ├── __init__.py          # Public API exports
│   ├── logger.py            # LoggerSystem class
│   ├── config.py            # Configuration management
│   ├── context.py           # Context variable management
│   ├── decorators.py        # Logging decorators
│   ├── processors.py        # Custom processors
│   └── renderers.py         # Custom renderers
└── utils/
    ├── __init__.py          # Public API exports
    └── uuid.py              # UUID generator (refactored)
```

### Configuration File Locations

The system will search for configuration files in the following order:

1. Path specified in `MORADO_LOG_CONFIG` environment variable
2. `./logging.toml` (current directory)
3. `./config/logging.toml`
4. `~/.morado/logging.toml` (user home)
5. Default configuration (no file)

### Environment Variable Support

Configuration can be overridden via environment variables:

- `MORADO_LOG_LEVEL`: Global log level
- `MORADO_LOG_FORMAT`: Output format (console, json, structured)
- `MORADO_LOG_OUTPUT`: Output destination (stdout, stderr, file path)
- `MORADO_REQUEST_ID_FORMAT`: Request ID format
- `MORADO_REQUEST_ID_LENGTH`: Request ID length

### Backward Compatibility

To maintain backward compatibility with existing code:

1. **Import Compatibility**
   ```python
   # Old import (still works)
   from morado.common.logger.log import get_logger, request_scope
   
   # New import (preferred)
   from morado.common.logger import get_logger, request_scope
   ```

2. **API Compatibility**
   - All existing functions remain available
   - Old function signatures still work
   - Deprecation warnings for old patterns

3. **Migration Path**
   ```python
   # Old code
   from morado.common.logger.log import LoggerUtil
   logger_util = LoggerUtil()
   logger = logger_util.get_logger()
   
   # New code (simpler)
   from morado.common.logger import get_logger
   logger = get_logger()
   ```

### Performance Considerations

1. **Lazy Initialization**
   - Logger system initializes on first use
   - Configuration loaded once and cached
   - Processors compiled into efficient chain

2. **Context Variable Performance**
   - contextvars are highly optimized in Python 3.7+
   - Minimal overhead for context access
   - No global state or locks needed

3. **UUID Generation Performance**
   - Stateless generation (no locks)
   - Secure random uses OS entropy efficiently
   - Timestamp generation cached per millisecond

4. **Processor Chain Optimization**
   - Processors compiled into single callable
   - No dynamic lookup per log event
   - Exception handling isolated to failing processor

### Security Considerations

1. **Secure Random Generation**
   - Use `secrets` module for cryptographic randomness
   - Configurable fallback to `random` for non-security contexts

2. **Log Injection Prevention**
   - Structured logging prevents injection attacks
   - All user data properly escaped in renderers
   - JSON renderer uses safe serialization

3. **Sensitive Data Handling**
   - Processors can redact sensitive fields
   - Configuration for sensitive field names
   - No passwords or tokens in default logging

### Extensibility Points

1. **Custom Processors**
   ```python
   def custom_processor(logger, method_name, event_dict):
       """Add custom field to all logs"""
       event_dict['custom_field'] = 'value'
       return event_dict
   
   configure_logger(processors=[custom_processor])
   ```

2. **Custom Renderers**
   ```python
   def custom_renderer(logger, method_name, event_dict):
       """Custom log format"""
       return f"[{event_dict['level']}] {event_dict['event']}"
   
   config = LoggerConfig(format='custom')
   configure_logger(config, custom_renderer=custom_renderer)
   ```

3. **Custom UUID Formats**
   ```python
   class CustomUUIDGenerator:
       @staticmethod
       def generate(config: UUIDConfig) -> str:
           """Custom UUID generation logic"""
           return "CUSTOM-" + str(uuid.uuid4())
   
   UUIDGenerator.register_format('custom', CustomUUIDGenerator.generate)
   ```

## Migration Guide

### Step 1: Update Imports

```python
# Before
from morado.common.logger.log import get_logger, request_scope

# After
from morado.common.logger import get_logger, request_scope
```

### Step 2: Create Configuration File (Optional)

Create `logging.toml`:

```toml
[logging]
level = "INFO"
format = "console"

[logging.request_id]
format = "alphanumeric"
length = 24
prefix = "REQ"
```

### Step 3: Update Initialization Code

```python
# Before
from morado.common.logger.log import LoggerUtil
logger_util = LoggerUtil()
logger_util.configure_request_id(...)

# After
from morado.common.logger import configure_logger
from morado.common.logger.config import LoggerConfig, UUIDConfig

config = LoggerConfig(
    request_id_config=UUIDConfig(format="alphanumeric", length=24, prefix="REQ")
)
configure_logger(config)
```

### Step 4: Test and Validate

1. Run existing tests to ensure compatibility
2. Verify log output format matches expectations
3. Check request ID generation works as before
4. Validate context propagation in request scopes

## Dependencies

### Required Dependencies

- `structlog >= 25.5.0`: Structured logging framework
- `python >= 3.13`: For contextvars and type hints

### Optional Dependencies

- `pyyaml`: For YAML configuration file support
- `tomli`: For TOML configuration file support (Python < 3.11)
- `hypothesis >= 6.0`: For property-based testing

### Development Dependencies

- `pytest >= 9.0`: Testing framework
- `pytest-asyncio >= 1.3`: Async test support
- `pytest-cov >= 7.0`: Coverage reporting
