# Morado Logger & UUID System - Quick Overview

## System Architecture (High-Level)

```mermaid
graph LR
    subgraph "User Code"
        A[Application]
    end
    
    subgraph "Public API"
        B[get_logger]
        C[request_scope]
        D[configure_logger]
    end
    
    subgraph "Core Components"
        E[Configuration<br/>Manager]
        F[Context<br/>Manager]
        G[UUID<br/>Generator]
    end
    
    subgraph "External"
        H[structlog]
        I[Config Files<br/>TOML/YAML]
        J[Environment<br/>Variables]
    end
    
    A --> B
    A --> C
    A --> D
    
    B --> H
    C --> F
    D --> E
    
    F --> G
    E --> I
    E --> J
    
    style A fill:#e8f5e9
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#f3e5f5
    style F fill:#e1f5ff
    style G fill:#e1f5ff
```

## Request Processing Flow (Simplified)

```mermaid
sequenceDiagram
    autonumber
    
    participant App
    participant request_scope
    participant UUIDGenerator
    participant ContextVars
    participant Logger
    
    App->>request_scope: Enter scope (user_id=42)
    request_scope->>UUIDGenerator: Generate request_id
    UUIDGenerator-->>request_scope: "REQ20231222143055123ABC..."
    request_scope->>ContextVars: Set context (request_id, user_id)
    request_scope-->>App: Context ready
    
    App->>Logger: logger.info("Processing")
    Logger->>ContextVars: Get context
    ContextVars-->>Logger: {request_id, user_id}
    Logger->>Logger: Format & output log
    
    App->>request_scope: Exit scope
    request_scope->>ContextVars: Restore previous context
```

## UUID Generation Formats

```mermaid
graph TD
    START[UUIDGenerator.generate] --> FORMAT{Format?}
    
    FORMAT -->|uuid4| A["RFC 4122 UUID4<br/>550e8400-e29b-41d4-a716-446655440000"]
    FORMAT -->|ulid| B["ULID (sortable)<br/>01ARZ3NDEKTSV4RRFFQ69G5FAV"]
    FORMAT -->|alphanumeric| C["Alphanumeric<br/>REQ20231222143055123ABCDEFGH..."]
    FORMAT -->|numeric| D["Numeric<br/>20231222143055123456789"]
    FORMAT -->|custom| E["Custom<br/>PREFIX + timestamp + random + SUFFIX"]
    
    style A fill:#c8e6c9
    style B fill:#c8e6c9
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#c8e6c9
```

## Configuration Precedence

```mermaid
graph LR
    A[Defaults] -->|Overridden by| B[Config File]
    B -->|Overridden by| C[Environment]
    C -->|Overridden by| D[Code]
    
    style A fill:#ffebee
    style B fill:#fff3e0
    style C fill:#e1f5ff
    style D fill:#c8e6c9
```

## Context Variable Lifecycle

```mermaid
stateDiagram-v2
    [*] --> NoContext
    NoContext --> Entering: request_scope() called
    Entering --> SavePrevious: Save old values
    SavePrevious --> Generate: Generate request_id
    Generate --> SetNew: Set new context
    SetNew --> Active: Context active
    Active --> Active: Application code runs
    Active --> Exiting: Exit scope
    Exiting --> Restore: Restore old values
    Restore --> NoContext
    NoContext --> [*]
```

## Key Components Summary

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **UUIDGenerator** | Generate unique IDs | Multiple formats, configurable, stateless |
| **ConfigurationManager** | Load & merge configs | TOML/YAML/env support, validation |
| **ContextManager** | Manage request context | Thread-safe, async-safe, auto-cleanup |
| **request_scope** | Context lifecycle | Auto-generate IDs, context isolation |
| **Decorators** | Convenience wrappers | Auto-context, execution logging |

## Data Flow Summary

### 1. Startup Configuration
```
Load defaults → Load file → Load env → Merge → Validate → Configure logger
```

### 2. Request Processing
```
Enter scope → Generate ID → Set context → Execute code → Log with context → Exit scope → Restore context
```

### 3. UUID Generation
```
Config → Select format → Generate components → Assemble → Return
```

### 4. Context Management
```
Save previous → Set new → Yield to app → Restore previous
```

## Integration Points

```mermaid
graph TB
    subgraph "Configuration Layer"
        LC[LoggerConfig]
        UC[UUIDConfig]
        LC --> UC
    end
    
    subgraph "Runtime Layer"
        RS[request_scope]
        UG[UUIDGenerator]
        CM[ContextManager]
        
        RS --> UG
        RS --> CM
        UG --> UC
    end
    
    subgraph "Logging Layer"
        GL[get_logger]
        SL[structlog]
        
        GL --> CM
        GL --> SL
    end
    
    LC --> RS
    LC --> GL
```

## Thread & Async Safety

| Component | Thread-Safe | Async-Safe | Mechanism |
|-----------|-------------|------------|-----------|
| UUIDGenerator | ✅ | ✅ | Stateless static methods |
| ContextManager | ✅ | ✅ | Python contextvars |
| Configuration | ✅ | ✅ | Immutable Pydantic models |
| request_scope | ✅ | ✅ | contextvars + proper cleanup |

## Common Usage Patterns

### Pattern 1: Basic Request Logging
```python
with request_scope(user_id=42):
    logger.info("Processing request")
```

### Pattern 2: Custom UUID Format
```python
config = UUIDConfig(format="alphanumeric", prefix="REQ", length=38)
with request_scope(user_id=42, request_id_config=config):
    logger.info("Processing")
```

### Pattern 3: Decorator-Based Context
```python
@with_request_context()
def process_request(request_id: str, user_id: int):
    logger.info("Processing")
```

### Pattern 4: Configuration from File
```python
config = ConfigurationManager.load_config("logging.toml")
configure_logger(config)
```

## Error Handling Strategy

| Error Type | Handling | Result |
|------------|----------|--------|
| Missing config file | Warning + defaults | Continue with defaults |
| Invalid config value | Warning + default | Use default value |
| UUID generation error | ValueError | Propagate to caller |
| Context cleanup error | Guaranteed cleanup | Always restores context |

## Performance Characteristics

| Operation | Performance | Notes |
|-----------|-------------|-------|
| UUID generation | ~1-10 μs | Depends on format |
| Context creation | ~1-2 μs | Very fast (contextvars) |
| Context retrieval | ~0.1 μs | O(1) lookup |
| Config loading | One-time | At startup only |
| Log output | Depends on structlog | Not measured here |

## Design Principles

1. **Separation of Concerns**: UUID, Config, Context, Logging are independent
2. **Stateless Design**: No shared mutable state
3. **Thread Safety**: Built-in via contextvars and immutability
4. **Configuration Flexibility**: Multiple sources with clear precedence
5. **Graceful Degradation**: Sensible defaults for all errors
6. **Clean API**: Simple, intuitive public interface
7. **Extensibility**: Easy to add new UUID formats, processors, etc.
