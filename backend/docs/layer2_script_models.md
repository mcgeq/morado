# Layer 2: Script Models Documentation

## Overview

Layer 2 of the four-layer architecture implements the **Script Models**, which build upon Layer 1 (API Components) by creating executable test scripts that can be debugged independently and used in components and test cases.

## Models

### TestScript

The `TestScript` model represents an executable test script that references an API definition from Layer 1.

#### Key Features

1. **Script Types**
   - `SETUP`: Pre-execution scripts for environment preparation
   - `MAIN`: Core test logic scripts
   - `TEARDOWN`: Post-execution scripts for cleanup
   - `UTILITY`: Reusable utility scripts

2. **Execution Control**
   - Pre-script and post-script hooks
   - Execution order configuration
   - Retry mechanism with configurable count and interval
   - Timeout override capability

3. **Data Management**
   - Script-level variables
   - Variable extraction from API responses
   - Output variables for passing data to subsequent scripts
   - Support for variable substitution (e.g., `${variable}`)

4. **Validation**
   - Multiple assertion types:
     - Status code assertions
     - JSON path assertions
     - Regex matching
     - Response time validation
     - Custom assertions with Python/JavaScript code
   - JSON Schema validators for response validation

5. **Debugging Support**
   - Debug mode flag
   - Configurable breakpoints with conditions
   - Independent script execution for testing

6. **Configuration**
   - Version control
   - Tags for categorization
   - Active/inactive status
   - Creator tracking

#### Example Usage

```python
from morado.models.script import TestScript, ScriptType, AssertionType

# Create a main test script
login_script = TestScript(
    name="用户登录测试",
    description="测试用户登录功能",
    api_definition_id=1,
    script_type=ScriptType.MAIN,
    
    variables={
        "username": "testuser",
        "password": "Test@123"
    },
    
    assertions=[
        {
            "type": AssertionType.STATUS_CODE.value,
            "expected": 200,
            "message": "登录应该返回200状态码"
        },
        {
            "type": AssertionType.JSON_PATH.value,
            "path": "$.data.token",
            "assertion": "exists",
            "message": "响应应该包含token"
        }
    ],
    
    extract_variables={
        "auth_token": "$.data.token",
        "user_id": "$.data.user.id"
    },
    
    output_variables=["auth_token", "user_id"],
    retry_count=3,
    retry_interval=1.0
)
```

### ScriptParameter

The `ScriptParameter` model defines input parameters for scripts with type validation and default values.

#### Key Features

1. **Parameter Types**
   - `STRING`: Text values
   - `INTEGER`: Whole numbers
   - `FLOAT`: Decimal numbers
   - `BOOLEAN`: True/false values
   - `JSON`: JSON objects
   - `ARRAY`: Lists of values
   - `FILE`: File uploads

2. **Validation**
   - Required/optional flags
   - Default values
   - Custom validation rules (min/max, patterns, etc.)
   - Type checking

3. **Organization**
   - Display order
   - Parameter grouping
   - Descriptions

4. **Security**
   - Sensitive parameter flag for passwords/tokens
   - Masked display in UI

#### Example Usage

```python
from morado.models.script import ScriptParameter, ParameterType

# String parameter with validation
username_param = ScriptParameter(
    script_id=1,
    name="username",
    description="用户名",
    parameter_type=ParameterType.STRING,
    default_value="testuser",
    is_required=True,
    validation_rules={
        "min_length": 3,
        "max_length": 50,
        "pattern": "^[a-zA-Z0-9_]+$"
    },
    order=1
)

# Sensitive parameter
password_param = ScriptParameter(
    script_id=1,
    name="password",
    description="密码",
    parameter_type=ParameterType.STRING,
    is_required=True,
    is_sensitive=True,
    order=2
)

# Integer parameter with range validation
timeout_param = ScriptParameter(
    script_id=1,
    name="timeout",
    description="超时时间（秒）",
    parameter_type=ParameterType.INTEGER,
    default_value="30",
    validation_rules={
        "min": 1,
        "max": 300
    },
    order=3,
    group="Configuration"
)
```

## Database Schema

### test_scripts Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| uuid | VARCHAR(50) | Unique identifier |
| name | VARCHAR(200) | Script name |
| description | TEXT | Script description |
| api_definition_id | INTEGER | FK to api_definitions |
| script_type | ENUM | Script type (setup/main/teardown/utility) |
| execution_order | INTEGER | Execution order |
| variables | JSON | Script variables |
| assertions | JSON | Assertion list |
| validators | JSON | Validator configuration |
| pre_script | TEXT | Pre-execution script code |
| post_script | TEXT | Post-execution script code |
| extract_variables | JSON | Variable extraction config |
| output_variables | JSON | Output variable list |
| debug_mode | BOOLEAN | Debug mode flag |
| debug_breakpoints | JSON | Breakpoint configuration |
| retry_count | INTEGER | Retry count |
| retry_interval | FLOAT | Retry interval (seconds) |
| timeout_override | INTEGER | Timeout override (seconds) |
| is_active | BOOLEAN | Active status |
| version | VARCHAR(20) | Version number |
| tags | JSON | Tags |
| created_by | INTEGER | FK to users |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Update timestamp |

### script_parameters Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| uuid | VARCHAR(50) | Unique identifier |
| script_id | INTEGER | FK to test_scripts |
| name | VARCHAR(100) | Parameter name |
| description | TEXT | Parameter description |
| parameter_type | ENUM | Parameter type |
| default_value | TEXT | Default value (JSON string) |
| is_required | BOOLEAN | Required flag |
| validation_rules | JSON | Validation rules |
| order | INTEGER | Display order |
| group | VARCHAR(100) | Parameter group |
| is_sensitive | BOOLEAN | Sensitive flag |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Update timestamp |

## Relationships

### TestScript Relationships

- **creator** (Many-to-One): Links to User model
- **api_definition** (Many-to-One): Links to ApiDefinition (Layer 1)
- **parameters** (One-to-Many): Links to ScriptParameter
- **component_scripts** (One-to-Many): Links to ComponentScript (Layer 3)
- **test_case_scripts** (One-to-Many): Links to TestCaseScript (Layer 4)

### ScriptParameter Relationships

- **script** (Many-to-One): Links to TestScript

## Integration with Four-Layer Architecture

```
Layer 1: API Components (Header, Body, ApiDefinition)
    ↓ (referenced by)
Layer 2: Scripts (TestScript, ScriptParameter) ← YOU ARE HERE
    ↓ (used by)
Layer 3: Components (TestComponent, ComponentScript)
    ↓ (used by)
Layer 4: Test Cases (TestCase, TestCaseScript, TestCaseComponent)
```

### Data Flow

1. **Layer 1 → Layer 2**: Scripts reference API definitions
2. **Layer 2 → Layer 3**: Components contain multiple scripts
3. **Layer 2 → Layer 4**: Test cases can directly reference scripts
4. **Parameter Override**: Parameters flow from Layer 4 → Layer 3 → Layer 2

### Parameter Priority

```
Runtime Parameters (highest priority)
    ↓
Test Case Data
    ↓
Component Shared Variables
    ↓
Script Variables
    ↓
Script Parameter Defaults
    ↓
Environment Config (lowest priority)
```

## Assertion Types

### Built-in Assertions

1. **EQUALS**: Value equality check
2. **NOT_EQUALS**: Value inequality check
3. **CONTAINS**: Substring/element containment
4. **NOT_CONTAINS**: Absence check
5. **GREATER_THAN**: Numeric comparison
6. **LESS_THAN**: Numeric comparison
7. **REGEX_MATCH**: Regular expression matching
8. **JSON_PATH**: JSON path-based validation
9. **STATUS_CODE**: HTTP status code check
10. **RESPONSE_TIME**: Response time validation
11. **CUSTOM**: Custom Python/JavaScript code

### Assertion Examples

```python
# Status code assertion
{
    "type": "status_code",
    "expected": 200,
    "message": "Should return 200 OK"
}

# JSON path assertion
{
    "type": "json_path",
    "path": "$.data.users[*].email",
    "assertion": "all_match",
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
    "message": "All emails should be valid"
}

# Response time assertion
{
    "type": "response_time",
    "max_time": 2000,
    "message": "Response should be under 2 seconds"
}

# Custom assertion
{
    "type": "custom",
    "script": """
def validate_response(response):
    data = response.json()
    assert len(data['users']) > 0, "Should have users"
    return True
    """,
    "message": "Custom validation failed"
}
```

## Best Practices

### 1. Script Organization

- Use **SETUP** scripts for data preparation
- Use **MAIN** scripts for core test logic
- Use **TEARDOWN** scripts for cleanup
- Use **UTILITY** scripts for reusable functions

### 2. Variable Management

- Extract important values for reuse
- Use descriptive variable names
- Document variable purposes in descriptions
- Use output_variables to pass data between scripts

### 3. Assertions

- Add meaningful assertion messages
- Use appropriate assertion types
- Validate both success and error cases
- Consider response time assertions for performance

### 4. Parameters

- Provide sensible default values
- Add validation rules for data integrity
- Group related parameters
- Mark sensitive data appropriately

### 5. Debugging

- Enable debug mode during development
- Set breakpoints at critical points
- Use pre/post scripts for logging
- Test scripts independently before integration

## Verification

Run the verification script to ensure models are correctly implemented:

```bash
cd backend
uv run python scripts/verify_script_models.py
```

Run the demonstration script to see usage examples:

```bash
cd backend
uv run python scripts/demo_script_models.py
```

## Next Steps

After implementing Layer 2 (Scripts), proceed to:

1. **Layer 3**: Implement Component models (TestComponent, ComponentScript)
2. **Layer 4**: Update TestCase models to reference scripts
3. **Schemas**: Create Pydantic schemas for API validation
4. **Repositories**: Implement data access layer
5. **Services**: Implement business logic layer
6. **Execution Engine**: Implement script execution with parameter resolution

## References

- Design Document: `.kiro/specs/project-restructure/design.md`
- Requirements: `.kiro/specs/project-restructure/requirements.md`
- Data Management: `docs/data-management-and-execution.md`
- Layer 1 Models: `backend/src/morado/models/api_component.py`
- Layer 2 Models: `backend/src/morado/models/script.py`
