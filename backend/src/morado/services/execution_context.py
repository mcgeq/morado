"""Execution Context Management for Four-Layer Architecture

This module provides execution context management for the test platform's
four-layer architecture, handling parameter resolution, variable substitution,
and data flow between layers.

The execution context implements the parameter priority system:
    Runtime Parameters (highest)
    ↓
    Test Case Data
    ↓
    Component Shared Variables
    ↓
    Script Variables
    ↓
    Script Parameter Defaults
    ↓
    Environment Configuration (lowest)

Variable substitution syntax:
    ${variable}              - Simple variable reference
    ${variable:default}      - Variable with default value
    ${env.path.to.value}     - Environment configuration reference

Built-in system variables:
    ${timestamp}    - Current timestamp
    ${date}         - Current date (YYYY-MM-DD)
    ${datetime}     - Current datetime (YYYY-MM-DD HH:MM:SS)
    ${uuid}         - Random UUID
    ${random_int}   - Random integer
    ${random_string}- Random string
"""

import random
import re
import string
from typing import Any

from morado.common.utils.time import TimeUtil
from morado.common.utils.uuid import generate_uuid4


class VariableResolver:
    """Variable resolver for parameter substitution.

    Handles variable substitution with support for:
    - Simple variables: ${variable}
    - Variables with defaults: ${variable:default}
    - Environment config references: ${env.path.to.value}
    - Built-in system variables: ${timestamp}, ${uuid}, etc.

    Example:
        >>> resolver = VariableResolver({"user": "test", "timeout": 30})
        >>> resolver.resolve("User: ${user}, Timeout: ${timeout:60}")
        'User: test, Timeout: 30'
        >>> resolver.resolve("ID: ${uuid}")
        'ID: 550e8400-e29b-41d4-a716-446655440000'
    """

    # Pattern to match ${variable}, ${variable:default}, ${env.path}
    VARIABLE_PATTERN = re.compile(r'\$\{([^}:]+)(?::([^}]*))?\}')

    def __init__(self, context: dict[str, Any] | None = None):
        """Initialize variable resolver.

        Args:
            context: Variable context dictionary
        """
        self.context = context or {}

    def resolve(self, value: Any) -> Any:
        """Resolve variables in a value.

        Args:
            value: Value to resolve (can be string, dict, list, or primitive)

        Returns:
            Resolved value with variables substituted

        Example:
            >>> resolver = VariableResolver({"name": "test"})
            >>> resolver.resolve("Hello ${name}")
            'Hello test'
            >>> resolver.resolve({"user": "${name}", "count": 5})
            {'user': 'test', 'count': 5}
        """
        if isinstance(value, str):
            return self._resolve_string(value)
        elif isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.resolve(item) for item in value]
        else:
            return value

    def _resolve_string(self, text: str) -> str:
        """Resolve variables in a string.

        Args:
            text: String containing variable references

        Returns:
            String with variables substituted
        """
        def replace_variable(match: re.Match) -> str:
            var_name = match.group(1)
            default_value = match.group(2)

            # Handle built-in system variables
            builtin_value = self._get_builtin_variable(var_name)
            if builtin_value is not None:
                return builtin_value

            # Handle environment config references (env.path.to.value)
            if var_name.startswith("env."):
                return self._resolve_env_variable(var_name, default_value, match.group(0))

            # Handle regular variables
            return self._resolve_regular_variable(var_name, default_value, match.group(0))

        return self.VARIABLE_PATTERN.sub(replace_variable, text)

    def _get_builtin_variable(self, var_name: str) -> str | None:
        """Get built-in system variable value.

        Args:
            var_name: Variable name

        Returns:
            Variable value or None if not a built-in variable
        """
        if var_name == "timestamp":
            return str(int(TimeUtil.now_utc().timestamp()))
        elif var_name == "date":
            return TimeUtil.format_time(TimeUtil.now_utc(), "%Y-%m-%d")
        elif var_name == "datetime":
            return TimeUtil.format_time(TimeUtil.now_utc(), "%Y-%m-%d %H:%M:%S")
        elif var_name == "uuid":
            return generate_uuid4()
        elif var_name == "random_int":
            return str(random.randint(1000, 9999))
        elif var_name == "random_string":
            return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return None

    def _resolve_env_variable(self, var_name: str, default_value: str | None, original: str) -> str:
        """Resolve environment config variable.

        Args:
            var_name: Variable name (starts with "env.")
            default_value: Default value if not found
            original: Original match string

        Returns:
            Resolved value
        """
        path = var_name[4:]  # Remove "env." prefix
        value = self._get_nested_value(self.context, path)
        if value is not None:
            return str(value)
        elif default_value is not None:
            return default_value
        else:
            return original

    def _resolve_regular_variable(self, var_name: str, default_value: str | None, original: str) -> str:
        """Resolve regular variable.

        Args:
            var_name: Variable name
            default_value: Default value if not found
            original: Original match string

        Returns:
            Resolved value
        """
        if var_name in self.context:
            return str(self.context[var_name])
        elif default_value is not None:
            return default_value
        else:
            return original

    def _get_nested_value(self, data: dict, path: str) -> Any:
        """Get nested value from dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., "api.base_url")

        Returns:
            Value at path or None if not found

        Example:
            >>> data = {"api": {"base_url": "https://example.com"}}
            >>> resolver = VariableResolver()
            >>> resolver._get_nested_value(data, "api.base_url")
            'https://example.com'
        """
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value


class ExecutionContext:
    """Base execution context for parameter management.

    Provides the foundation for all execution contexts with:
    - Parameter storage and retrieval
    - Variable resolution
    - Environment configuration loading

    This is the base class for script, component, and test case contexts.

    Example:
        >>> context = ExecutionContext(environment="test")
        >>> context.set_param("user", "test_user")
        >>> context.get_param("user")
        'test_user'
        >>> context.resolve_value("User: ${user}")
        'User: test_user'
    """

    def __init__(
        self,
        environment: str = "development",
        env_config: dict[str, Any] | None = None
    ):
        """Initialize execution context.

        Args:
            environment: Environment name (development, testing, production)
            env_config: Environment configuration dictionary
        """
        self.environment = environment
        self.params: dict[str, Any] = {}

        # Load environment configuration
        if env_config:
            self.params.update(self._flatten_dict(env_config))

        # Create variable resolver
        self.resolver = VariableResolver(self.params)

    def set_param(self, key: str, value: Any) -> None:
        """Set a parameter value.

        Args:
            key: Parameter key
            value: Parameter value
        """
        self.params[key] = value
        self.resolver.context = self.params

    def get_param(self, key: str, default: Any = None) -> Any:
        """Get a parameter value.

        Args:
            key: Parameter key
            default: Default value if key not found

        Returns:
            Parameter value or default
        """
        return self.params.get(key, default)

    def update_params(self, params: dict[str, Any]) -> None:
        """Update multiple parameters at once.

        Args:
            params: Dictionary of parameters to update
        """
        self.params.update(params)
        self.resolver.context = self.params

    def resolve_value(self, value: Any) -> Any:
        """Resolve variables in a value.

        Args:
            value: Value to resolve

        Returns:
            Resolved value with variables substituted
        """
        return self.resolver.resolve(value)

    def resolve_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Resolve variables in all parameters.

        Args:
            params: Parameters to resolve

        Returns:
            Dictionary with resolved parameters
        """
        return self.resolver.resolve(params)

    def _flatten_dict(self, data: dict, prefix: str = "") -> dict[str, Any]:
        """Flatten nested dictionary with dot notation keys.

        Args:
            data: Dictionary to flatten
            prefix: Key prefix for nested keys

        Returns:
            Flattened dictionary

        Example:
            >>> context = ExecutionContext()
            >>> nested = {"api": {"base_url": "https://example.com", "timeout": 30}}
            >>> context._flatten_dict(nested)
            {'api.base_url': 'https://example.com', 'api.timeout': 30}
        """
        flat_dict = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat_dict.update(self._flatten_dict(value, full_key))
            else:
                flat_dict[full_key] = value
        return flat_dict


class ScriptExecutionContext(ExecutionContext):
    """Execution context for script layer (Layer 2).

    Manages script-level parameters with priority:
        Runtime/Override Parameters (highest)
        ↓
        Script Variables
        ↓
        Script Parameter Defaults
        ↓
        Environment Configuration (lowest)

    Example:
        >>> from morado.models.script import TestScript
        >>> script = TestScript(
        ...     name="Test Script",
        ...     variables={"timeout": 30, "retry": 3}
        ... )
        >>> context = ScriptExecutionContext(script, override_params={"timeout": 60})
        >>> context.get_param("timeout")  # Override wins
        60
        >>> context.get_param("retry")  # From script variables
        3
    """

    def __init__(
        self,
        script: Any,  # TestScript model
        override_params: dict[str, Any] | None = None,
        env_config: dict[str, Any] | None = None
    ):
        """Initialize script execution context.

        Args:
            script: TestScript model instance
            override_params: Parameters to override script defaults
            env_config: Environment configuration
        """
        super().__init__(environment="development", env_config=env_config)

        # Store script reference
        self.script = script

        # Load script parameter defaults
        if hasattr(script, 'parameters'):
            for param in script.parameters:
                if param.default_value:
                    self.set_param(param.name, param.default_value)

        # Load script variables
        if script.variables:
            self.update_params(script.variables)

        # Apply override parameters (highest priority)
        if override_params:
            self.update_params(override_params)

    def get_script_output(self) -> dict[str, Any]:
        """Get script output variables.

        Returns:
            Dictionary of output variables defined in script
        """
        if hasattr(self.script, 'output_variables') and self.script.output_variables:
            return {var: self.get_param(var) for var in self.script.output_variables}
        return {}


class ComponentExecutionContext(ExecutionContext):
    """Execution context for component layer (Layer 3).

    Manages component-level parameters and script execution with priority:
        Runtime/Override Parameters (highest)
        ↓
        Component Shared Variables
        ↓
        Script Variables (per script)
        ↓
        Environment Configuration (lowest)

    Supports:
    - Shared variables across scripts in the component
    - Script output variable propagation
    - Script-specific parameter overrides

    Example:
        >>> from morado.models.component import TestComponent
        >>> component = TestComponent(
        ...     name="Test Component",
        ...     shared_variables={"base_url": "https://api.example.com"}
        ... )
        >>> context = ComponentExecutionContext(component)
        >>> context.get_param("base_url")
        'https://api.example.com'
    """

    def __init__(
        self,
        component: Any,  # TestComponent model
        override_params: dict[str, Any] | None = None,
        env_config: dict[str, Any] | None = None
    ):
        """Initialize component execution context.

        Args:
            component: TestComponent model instance
            override_params: Parameters to override component defaults
            env_config: Environment configuration
        """
        super().__init__(environment="development", env_config=env_config)

        # Store component reference
        self.component = component

        # Load component shared variables
        if component.shared_variables:
            self.update_params(component.shared_variables)

        # Apply override parameters (highest priority)
        if override_params:
            self.update_params(override_params)

        # Storage for script execution results
        self.script_results: dict[str, Any] = {}

    def create_script_context(
        self,
        script: Any,
        script_params: dict[str, Any] | None = None
    ) -> ScriptExecutionContext:
        """Create execution context for a script within this component.

        Args:
            script: TestScript model instance
            script_params: Script-specific parameter overrides

        Returns:
            ScriptExecutionContext with component parameters as base
        """
        # Merge component params with script-specific params
        merged_params = self.params.copy()
        if script_params:
            # Resolve variables in script params
            resolved_script_params = self.resolve_params(script_params)
            merged_params.update(resolved_script_params)

        return ScriptExecutionContext(
            script=script,
            override_params=merged_params,
            env_config=None  # Already loaded in component context
        )

    def save_script_result(self, script_name: str, result: dict[str, Any]) -> None:
        """Save script execution result.

        Args:
            script_name: Name of the executed script
            result: Execution result dictionary
        """
        self.script_results[script_name] = result

        # Update shared variables with script output
        if 'output_variables' in result:
            self.update_params(result['output_variables'])

    def get_script_result(self, script_name: str) -> dict[str, Any] | None:
        """Get script execution result.

        Args:
            script_name: Name of the script

        Returns:
            Script result dictionary or None if not found
        """
        return self.script_results.get(script_name)


class TestCaseExecutionContext(ExecutionContext):
    """Execution context for test case layer (Layer 4).

    Manages test case-level parameters with full priority chain:
        Runtime Parameters (highest)
        ↓
        Test Case Data
        ↓
        Component Shared Variables (per component)
        ↓
        Script Variables (per script)
        ↓
        Environment Configuration (lowest)

    Supports:
    - Test case data management
    - Component and script execution
    - Execution history tracking
    - Variable propagation across all layers

    Example:
        >>> from morado.models.test_case import TestCase
        >>> test_case = TestCase(
        ...     name="User Login Test",
        ...     test_data={"username": "test", "password": "pass123"},
        ...     environment="test"
        ... )
        >>> context = TestCaseExecutionContext(
        ...     test_case,
        ...     runtime_params={"password": "override123"}
        ... )
        >>> context.get_param("password")  # Runtime wins
        'override123'
        >>> context.get_param("username")  # From test case
        'test'
    """

    def __init__(
        self,
        test_case: Any,  # TestCase model
        runtime_params: dict[str, Any] | None = None,
        env_config: dict[str, Any] | None = None
    ):
        """Initialize test case execution context.

        Args:
            test_case: TestCase model instance
            runtime_params: Runtime parameters (highest priority)
            env_config: Environment configuration
        """
        super().__init__(
            environment=test_case.environment if hasattr(test_case, 'environment') else "development",
            env_config=env_config
        )

        # Store test case reference
        self.test_case = test_case

        # Load test case data
        if hasattr(test_case, 'test_data') and test_case.test_data:
            self.update_params(test_case.test_data)

        # Apply runtime parameters (highest priority)
        if runtime_params:
            self.update_params(runtime_params)

        # Execution history
        self.execution_history: list[dict[str, Any]] = []

    def create_script_context(
        self,
        script: Any,
        script_params: dict[str, Any] | None = None
    ) -> ScriptExecutionContext:
        """Create execution context for a script within this test case.

        Args:
            script: TestScript model instance
            script_params: Script-specific parameter overrides

        Returns:
            ScriptExecutionContext with test case parameters as base
        """
        # Merge test case params with script-specific params
        merged_params = self.params.copy()
        if script_params:
            # Resolve variables in script params
            resolved_script_params = self.resolve_params(script_params)
            merged_params.update(resolved_script_params)

        return ScriptExecutionContext(
            script=script,
            override_params=merged_params,
            env_config=None  # Already loaded in test case context
        )

    def create_component_context(
        self,
        component: Any,
        component_params: dict[str, Any] | None = None
    ) -> ComponentExecutionContext:
        """Create execution context for a component within this test case.

        Args:
            component: TestComponent model instance
            component_params: Component-specific parameter overrides

        Returns:
            ComponentExecutionContext with test case parameters as base
        """
        # Merge test case params with component-specific params
        merged_params = self.params.copy()
        if component_params:
            # Resolve variables in component params
            resolved_component_params = self.resolve_params(component_params)
            merged_params.update(resolved_component_params)

        return ComponentExecutionContext(
            component=component,
            override_params=merged_params,
            env_config=None  # Already loaded in test case context
        )

    def add_execution_record(
        self,
        item_type: str,
        item_name: str,
        result: dict[str, Any]
    ) -> None:
        """Add execution record to history.

        Args:
            item_type: Type of item executed ('script' or 'component')
            item_name: Name of the executed item
            result: Execution result dictionary
        """
        record = {
            'type': item_type,
            'name': item_name,
            'result': result,
            'timestamp': TimeUtil.now_utc().isoformat()
        }
        self.execution_history.append(record)

        # Update context with output variables
        if 'output_variables' in result:
            self.update_params(result['output_variables'])

    def get_execution_history(self) -> list[dict[str, Any]]:
        """Get execution history.

        Returns:
            List of execution records
        """
        return self.execution_history

    def get_execution_summary(self) -> dict[str, Any]:
        """Get execution summary.

        Returns:
            Dictionary with execution statistics
        """
        total = len(self.execution_history)
        successful = sum(1 for record in self.execution_history
                        if record['result'].get('success', False))
        failed = total - successful

        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
