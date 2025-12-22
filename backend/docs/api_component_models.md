# API Component Models (Layer 1)

## Overview

The API Component models form the first layer of the Morado test platform's four-layer architecture. This layer provides reusable components for defining API interfaces:

- **Header**: Reusable HTTP header components
- **Body**: Reusable request/response body templates
- **ApiDefinition**: Complete API interface definitions

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 第一层：接口定义层 (API Definition)                │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────┐        │
│  │  Header  │───▶│   Body   │───▶│  API Definition    │        │
│  │  组件    │    │   组件   │    │  (引用或内联)       │        │
│  └──────────┘    └──────────┘    └────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Models

### Header

Reusable HTTP header components that can be shared across multiple API definitions.

**Attributes:**
- `name`: Header name
- `headers`: Dictionary of header key-value pairs (supports variable substitution with `${variable}`)
- `scope`: Scope (global/project/private)
- `is_active`: Whether the header is active
- `version`: Version number

**Example:**
```python
from morado.models import Header, HeaderScope

# Create an authentication header
auth_header = Header(
    name="认证Header",
    description="包含Bearer Token的认证Header",
    headers={
        "Authorization": "Bearer ${token}",
        "X-API-Key": "${api_key}"
    },
    scope=HeaderScope.GLOBAL
)

# Create a JSON content-type header
json_header = Header(
    name="JSON Content-Type",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    scope=HeaderScope.GLOBAL
)
```

### Body

Reusable request/response body templates with JSON Schema validation.

**Attributes:**
- `name`: Body name
- `body_type`: Type (request/response/both)
- `content_type`: Content type (e.g., "application/json")
- `body_schema`: JSON Schema definition
- `example_data`: Example data
- `scope`: Scope (global/project/private)

**Example:**
```python
from morado.models import Body, BodyType

# Create a user information body
user_body = Body(
    name="用户信息Body",
    description="用户基本信息的请求/响应体",
    body_type=BodyType.BOTH,
    content_type="application/json",
    body_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "email"]
    },
    example_data={
        "name": "张三",
        "age": 25,
        "email": "zhangsan@example.com"
    },
    scope=HeaderScope.GLOBAL
)
```

### ApiDefinition

Complete API interface definitions that can reference Header and Body components or use inline definitions.

**Two Composition Methods:**

#### Method 1: Reference Header and Body Components
```python
from morado.models import ApiDefinition, HttpMethod

# Reference existing Header and Body components
api_def = ApiDefinition(
    name="获取用户信息",
    method=HttpMethod.GET,
    path="/api/users/{id}",
    header_id=1,  # Reference authentication header
    response_body_id=2,  # Reference user info body
    path_parameters={"id": {"type": "integer", "description": "用户ID"}}
)
```

#### Method 2: Reference Header + Inline Body
```python
# Reference Header but use inline body
api_def = ApiDefinition(
    name="创建用户",
    method=HttpMethod.POST,
    path="/api/users",
    header_id=1,  # Reference authentication header
    inline_request_body={  # Inline request body
        "name": "李四",
        "age": 30,
        "email": "lisi@example.com"
    }
)
```

**Attributes:**
- `name`: API name
- `method`: HTTP method (GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS)
- `path`: API path (supports path parameters with `{param}`)
- `base_url`: Base URL (optional)
- `header_id`: Reference to Header component (optional)
- `request_body_id`: Reference to request Body component (optional)
- `response_body_id`: Reference to response Body component (optional)
- `inline_request_body`: Inline request body (optional)
- `inline_response_body`: Inline response body (optional)
- `query_parameters`: Query parameter definitions
- `path_parameters`: Path parameter definitions
- `timeout`: Timeout in seconds

## Relationships

### Header Relationships
- `creator`: Many-to-One with User
- `api_definitions`: One-to-Many with ApiDefinition

### Body Relationships
- `creator`: Many-to-One with User
- `api_definitions_request`: One-to-Many with ApiDefinition (as request body)
- `api_definitions_response`: One-to-Many with ApiDefinition (as response body)

### ApiDefinition Relationships
- `creator`: Many-to-One with User
- `header`: Many-to-One with Header
- `request_body`: Many-to-One with Body
- `response_body`: Many-to-One with Body
- `scripts`: One-to-Many with TestScript (Layer 2)

## Usage Patterns

### Pattern 1: Global Reusable Components

Create global headers and bodies that can be reused across the entire platform:

```python
# Create global authentication header
auth_header = Header(
    name="Global Auth Header",
    headers={"Authorization": "Bearer ${token}"},
    scope=HeaderScope.GLOBAL
)

# Create global user body
user_body = Body(
    name="Global User Body",
    body_type=BodyType.BOTH,
    body_schema={...},
    scope=HeaderScope.GLOBAL
)

# Reference them in multiple API definitions
api1 = ApiDefinition(name="Get User", method=HttpMethod.GET, path="/users/{id}", header_id=auth_header.id)
api2 = ApiDefinition(name="Update User", method=HttpMethod.PUT, path="/users/{id}", header_id=auth_header.id)
```

### Pattern 2: Project-Specific Components

Create project-specific components for better organization:

```python
# Create project-specific header
project_header = Header(
    name="Project X Auth",
    headers={"X-Project-Key": "${project_key}"},
    scope=HeaderScope.PROJECT,
    project_id=123
)
```

### Pattern 3: Quick API Definition with Inline Body

For one-off APIs, use inline bodies:

```python
api = ApiDefinition(
    name="Quick Test API",
    method=HttpMethod.POST,
    path="/test",
    inline_request_body={"test": "data"}
)
```

## Best Practices

1. **Use Global Headers for Common Authentication**: Create global headers for authentication that can be reused across all APIs.

2. **Create Reusable Bodies for Common Data Structures**: Define bodies for common data structures (users, orders, etc.) to ensure consistency.

3. **Use Inline Bodies for One-Off Cases**: For unique API definitions that won't be reused, inline bodies are more convenient.

4. **Version Your Components**: Use the `version` field to track changes to headers and bodies.

5. **Use Descriptive Names**: Give clear, descriptive names to headers and bodies to make them easy to find and reuse.

6. **Leverage Variable Substitution**: Use `${variable}` syntax in headers and bodies to support parameterization.

7. **Define JSON Schemas**: Always define JSON schemas for bodies to enable validation.

## Database Schema

```sql
-- Headers table
CREATE TABLE headers (
    id INTEGER PRIMARY KEY,
    uuid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    headers JSON NOT NULL,
    scope VARCHAR(20) DEFAULT 'private',
    project_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0.0',
    tags JSON,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bodies table
CREATE TABLE bodies (
    id INTEGER PRIMARY KEY,
    uuid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    body_type VARCHAR(20) DEFAULT 'request',
    content_type VARCHAR(100) DEFAULT 'application/json',
    body_schema JSON,
    example_data JSON,
    scope VARCHAR(20) DEFAULT 'private',
    project_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0.0',
    tags JSON,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API Definitions table
CREATE TABLE api_definitions (
    id INTEGER PRIMARY KEY,
    uuid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(500) NOT NULL,
    base_url VARCHAR(500),
    header_id INTEGER REFERENCES headers(id),
    request_body_id INTEGER REFERENCES bodies(id),
    response_body_id INTEGER REFERENCES bodies(id),
    inline_request_body JSON,
    inline_response_body JSON,
    query_parameters JSON,
    path_parameters JSON,
    timeout INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0.0',
    tags JSON,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Next Steps

After creating API definitions, you can:

1. **Create Test Scripts (Layer 2)**: Reference API definitions in test scripts to add testing logic
2. **Create Test Components (Layer 3)**: Combine multiple scripts into reusable components
3. **Create Test Cases (Layer 4)**: Build complete test cases using scripts and components

See the [Four-Layer Architecture Guide](../../docs/four-layer-architecture.md) for more information.
