# Layer 3: Component Models Documentation

## Overview

The Component Models represent the third layer in the Morado test platform's four-layer architecture. Components are composite units that combine multiple test scripts into reusable, executable groups. They support nesting, parameter overrides, and flexible execution modes.

## Architecture Position

```
Layer 1: API Definition (Header, Body, ApiDefinition)
    ↓
Layer 2: Test Scripts (TestScript, ScriptParameter)
    ↓
Layer 3: Test Components (TestComponent, ComponentScript) ← YOU ARE HERE
    ↓
Layer 4: Test Cases (TestCase, TestCaseScript, TestCaseComponent)
```

## Models

### TestComponent

The `TestComponent` model represents a composite unit that combines multiple scripts.

#### Key Features

1. **Script Composition**: Combine multiple scripts into a single executable unit
2. **Component Nesting**: Support parent-child relationships for hierarchical organization
3. **Shared Variables**: Define variables that are shared across all scripts in the component
4. **Execution Modes**: Sequential, parallel, or conditional execution
5. **Parameter Override**: Component-level parameters override script defaults

#### Component Types

- **SIMPLE**: Contains only scripts, no nested components
- **COMPOSITE**: Can contain both scripts and nested child components
- **TEMPLATE**: Reusable template that can be copied and customized

#### Execution Modes

- **SEQUENTIAL**: Execute scripts one after another in order
- **PARALLEL**: Execute scripts concurrently (where possible)
- **CONDITIONAL**: Execute scripts based on conditions

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | int | Primary key |
| `uuid` | str | Unique identifier |
| `name` | str | Component name |
| `description` | str | Component description |
| `component_type` | ComponentType | Type of component (simple/composite/template) |
| `execution_mode` | ExecutionMode | How scripts are executed (sequential/parallel/conditional) |
| `parent_component_id` | int | Parent component ID for nesting |
| `shared_variables` | dict | Variables shared across all scripts |
| `timeout` | int | Timeout in seconds (default: 300) |
| `retry_count` | int | Number of retries on failure (default: 0) |
| `continue_on_failure` | bool | Continue execution if a script fails |
| `execution_condition` | str | Condition for conditional execution mode |
| `is_active` | bool | Whether the component is active |
| `version` | str | Version number |
| `tags` | list | Tags for categorization |
| `created_by` | int | Creator user ID |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

#### Relationships

- **creator**: User who created the component
- **parent_component**: Parent component (for nested components)
- **child_components**: List of child components
- **component_scripts**: List of ComponentScript associations
- **test_case_components**: List of TestCaseComponent associations

#### Example Usage

```python
from morado.models.component import TestComponent, ComponentType, ExecutionMode

# Create a simple component
component = TestComponent(
    name="User Login Flow",
    description="Complete user login process with validation",
    component_type=ComponentType.SIMPLE,
    execution_mode=ExecutionMode.SEQUENTIAL,
    shared_variables={
        "base_url": "https://api.example.com",
        "timeout": 30,
        "retry_enabled": True
    },
    timeout=300,
    retry_count=2,
    tags=["authentication", "user-management"]
)

# Create a composite component with nesting
parent = TestComponent(
    name="Complete Test Suite",
    description="Full test suite with multiple sub-components",
    component_type=ComponentType.COMPOSITE,
    execution_mode=ExecutionMode.SEQUENTIAL
)

child = TestComponent(
    name="Login Sub-Component",
    description="Login-specific tests",
    component_type=ComponentType.SIMPLE,
    parent_component_id=parent.id
)
```

### ComponentScript

The `ComponentScript` model represents the association between a component and a script, defining execution order and parameter overrides.

#### Key Features

1. **Execution Order**: Define the sequence in which scripts execute
2. **Parameter Override**: Override script parameters at the component level
3. **Conditional Execution**: Execute scripts based on conditions
4. **Enable/Disable**: Temporarily disable scripts without removing them

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | int | Primary key |
| `component_id` | int | Component ID (foreign key) |
| `script_id` | int | Script ID (foreign key) |
| `execution_order` | int | Execution order (lower numbers execute first) |
| `is_enabled` | bool | Whether this script is enabled |
| `script_parameters` | dict | Parameter overrides for the script |
| `execution_condition` | str | Condition expression for execution |
| `skip_on_condition` | bool | Skip if condition is not met |
| `description` | str | Description of this association |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last update timestamp |

#### Relationships

- **component**: The TestComponent this association belongs to
- **script**: The TestScript being associated

#### Parameter Priority

Parameters follow this priority order (highest to lowest):

1. Runtime parameters (provided at execution time)
2. Test case parameters
3. **Component parameters** ← ComponentScript.script_parameters
4. Script parameters
5. Environment configuration

#### Example Usage

```python
from morado.models.component import ComponentScript

# Add a script to a component with parameter override
component_script = ComponentScript(
    component_id=1,
    script_id=1,
    execution_order=1,
    is_enabled=True,
    script_parameters={
        "username": "test_user",
        "timeout": 60,  # Override script's default timeout
        "retry_count": 3
    },
    description="Login script with extended timeout"
)

# Add a conditional script
conditional_script = ComponentScript(
    component_id=1,
    script_id=2,
    execution_order=2,
    execution_condition="${prev_status} == 'success'",
    skip_on_condition=True,
    description="Only execute if previous script succeeded"
)

# Add a disabled script (for temporary exclusion)
disabled_script = ComponentScript(
    component_id=1,
    script_id=3,
    execution_order=3,
    is_enabled=False,
    description="Temporarily disabled for debugging"
)
```

## Component Nesting

Components support hierarchical nesting through the `parent_component_id` field.

### Benefits of Nesting

1. **Organization**: Group related components logically
2. **Reusability**: Create modular components that can be combined
3. **Maintainability**: Update child components independently
4. **Scalability**: Build complex test scenarios from simple building blocks

### Example Nesting Structure

```
Complete E2E Test Suite (Composite)
├── User Management Component (Composite)
│   ├── User Registration Component (Simple)
│   ├── User Login Component (Simple)
│   └── User Profile Component (Simple)
├── Product Management Component (Composite)
│   ├── Product Creation Component (Simple)
│   └── Product Search Component (Simple)
└── Order Processing Component (Simple)
```

### Implementation

```python
# Create parent component
e2e_suite = TestComponent(
    name="Complete E2E Test Suite",
    component_type=ComponentType.COMPOSITE,
    execution_mode=ExecutionMode.SEQUENTIAL
)

# Create child component
user_mgmt = TestComponent(
    name="User Management Component",
    component_type=ComponentType.COMPOSITE,
    parent_component_id=e2e_suite.id
)

# Create grandchild component
user_login = TestComponent(
    name="User Login Component",
    component_type=ComponentType.SIMPLE,
    parent_component_id=user_mgmt.id
)
```

## Execution Flow

### Sequential Execution

Scripts execute one after another in order:

```
Script 1 (order: 1) → Script 2 (order: 2) → Script 3 (order: 3)
```

### Parallel Execution

Scripts execute concurrently (where dependencies allow):

```
Script 1 (order: 1) ┐
Script 2 (order: 1) ├→ All execute simultaneously
Script 3 (order: 1) ┘
```

### Conditional Execution

Scripts execute based on conditions:

```
Script 1 → Check Condition → Script 2 (if condition met)
                          → Skip Script 2 (if condition not met)
```

## Data Flow and Variable Sharing

### Shared Variables

Components can define shared variables that are accessible to all scripts:

```python
component = TestComponent(
    name="API Test Component",
    shared_variables={
        "base_url": "https://api.example.com",
        "api_version": "v1",
        "timeout": 30
    }
)
```

Scripts can access these variables using the `${variable}` syntax:

```json
{
  "url": "${base_url}/${api_version}/users",
  "timeout": "${timeout}"
}
```

### Parameter Override Chain

```
Runtime Parameters
    ↓ (overrides)
Test Case Parameters
    ↓ (overrides)
Component Parameters ← ComponentScript.script_parameters
    ↓ (overrides)
Script Parameters
    ↓ (overrides)
Environment Configuration
```

## Best Practices

### 1. Component Organization

- Use **SIMPLE** components for single-purpose test flows
- Use **COMPOSITE** components for complex scenarios with multiple sub-flows
- Use **TEMPLATE** components for reusable patterns

### 2. Naming Conventions

- Use descriptive names that indicate the component's purpose
- Include the scope in the name (e.g., "User Login Flow", "API Integration Suite")
- Use consistent naming patterns across related components

### 3. Execution Order

- Use increments of 10 for execution order (10, 20, 30) to allow easy insertion
- Group related scripts with similar order numbers
- Document the execution flow in the component description

### 4. Parameter Management

- Define shared variables at the component level for common values
- Use parameter overrides sparingly and document why they're needed
- Prefer environment configuration for environment-specific values

### 5. Component Nesting

- Keep nesting depth reasonable (2-3 levels maximum)
- Ensure child components are cohesive and focused
- Document the nesting structure in parent component descriptions

### 6. Error Handling

- Set appropriate timeout values based on expected execution time
- Use `retry_count` for flaky operations
- Set `continue_on_failure` carefully based on test dependencies

## Database Schema

### test_components Table

```sql
CREATE TABLE test_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    component_type VARCHAR(20) NOT NULL DEFAULT 'simple',
    execution_mode VARCHAR(20) NOT NULL DEFAULT 'sequential',
    parent_component_id INTEGER REFERENCES test_components(id) ON DELETE CASCADE,
    shared_variables JSON,
    timeout INTEGER NOT NULL DEFAULT 300,
    retry_count INTEGER NOT NULL DEFAULT 0,
    continue_on_failure BOOLEAN NOT NULL DEFAULT FALSE,
    execution_condition TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    tags JSON,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### component_scripts Table

```sql
CREATE TABLE component_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL REFERENCES test_components(id) ON DELETE CASCADE,
    script_id INTEGER NOT NULL REFERENCES test_scripts(id) ON DELETE CASCADE,
    execution_order INTEGER NOT NULL DEFAULT 0,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    script_parameters JSON,
    execution_condition TEXT,
    skip_on_condition BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Integration with Other Layers

### Layer 2 (Scripts)

Components reference scripts through the `ComponentScript` association:

```python
# Add scripts to component
ComponentScript(component_id=1, script_id=1, execution_order=1)
ComponentScript(component_id=1, script_id=2, execution_order=2)
```

### Layer 4 (Test Cases)

Test cases reference components through the `TestCaseComponent` association:

```python
# Add component to test case
TestCaseComponent(test_case_id=1, component_id=1, execution_order=1)
```

## Common Use Cases

### 1. Login Flow Component

```python
login_component = TestComponent(
    name="User Login Flow",
    component_type=ComponentType.SIMPLE,
    execution_mode=ExecutionMode.SEQUENTIAL,
    shared_variables={"base_url": "https://api.example.com"}
)

# Add scripts
ComponentScript(component_id=login_component.id, script_id=1, execution_order=1)  # Setup
ComponentScript(component_id=login_component.id, script_id=2, execution_order=2)  # Login
ComponentScript(component_id=login_component.id, script_id=3, execution_order=3)  # Verify
```

### 2. Parallel API Tests

```python
api_tests = TestComponent(
    name="Parallel API Tests",
    component_type=ComponentType.SIMPLE,
    execution_mode=ExecutionMode.PARALLEL
)

# All scripts execute simultaneously
ComponentScript(component_id=api_tests.id, script_id=1, execution_order=1)
ComponentScript(component_id=api_tests.id, script_id=2, execution_order=1)
ComponentScript(component_id=api_tests.id, script_id=3, execution_order=1)
```

### 3. Conditional Cleanup

```python
test_with_cleanup = TestComponent(
    name="Test with Conditional Cleanup",
    component_type=ComponentType.SIMPLE,
    execution_mode=ExecutionMode.CONDITIONAL
)

# Main test
ComponentScript(component_id=test_with_cleanup.id, script_id=1, execution_order=1)

# Cleanup only if test succeeded
ComponentScript(
    component_id=test_with_cleanup.id,
    script_id=2,
    execution_order=2,
    execution_condition="${prev_status} == 'success'",
    skip_on_condition=True
)
```

## Troubleshooting

### Issue: Scripts not executing in expected order

**Solution**: Check the `execution_order` values in `ComponentScript`. Lower numbers execute first.

### Issue: Parameter overrides not working

**Solution**: Verify the parameter priority chain. Component parameters should override script parameters but are overridden by test case and runtime parameters.

### Issue: Nested components not executing

**Solution**: Ensure the `parent_component_id` is correctly set and the parent component's `component_type` is `COMPOSITE`.

### Issue: Conditional execution not working

**Solution**: Check the `execution_condition` syntax and ensure the referenced variables are available in the execution context.

## See Also

- [Layer 2: Script Models](layer2_script_models.md)
- [Layer 4: Test Case Models](layer4_test_case_models.md)
- [Data Management and Execution](../../docs/data-management-and-execution.md)
- [Parameter Override Logic](../../docs/parameter-override-logic.md)
