"""Execution Context Management

This module provides context management for test execution across all four layers.
It handles parameter resolution, variable substitution, and data flow between layers.
"""

import re
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from morado.common.utils.uuid import generate_uuid
from morado.core.config import get_settings


class VariableResolver:
    """Resolves variable references in strings and dictionaries.

    Supports the following syntax:
    - ${variable_name}: Simple variable reference
    - ${variable_name:default}: Variable with default value
    - ${env.path.to.config}: Environment configuration reference
    """

    # Pattern to match ${variable_name} or ${variable_name:default}
    VARIABLE_PATTERN = re.compile(r'\$\{([^}:]+)(?::([^}]*))?\}')

    def __init__(self, context: dict[str, Any]):
        """Initialize resolver with a context dictionary.

        Args:
            context: Dictionary containing all available variables
        """
        self.context = context
        self._add_builtin_variables()

    def _add_builtin_variables(self):
        """Add built-in system variables."""
        self.context.update({
            'timestamp': int(time.time()),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'uuid': str(uuid4()),
            'random_int': str(int(time.time() * 1000) % 1000000),
            'random_string': generate_uuid()[:8]
        })

    def resolve(self, value: Any) -> Any:
        """Resolve variables in a value.

        Args:
            value: Value to resolve (can be string, dict, list, or primitive)

        Returns:
            Resolved value with all variables substituted
        """
        if isinstance(value, str):
            return self._resolve_string(value)
        elif isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.resolve(item) for item in value]
        else:
            return value

    def _resolve_string(self, text: str) -> Any:
        """Resolve variables in a string.

        Args:
            text: String containing variable references

        Returns:
            Resolved string or original type if entire string is a variable
        """
        # Check if the entire string is a single variable reference
        match = self.VARIABLE_PATTERN.fullmatch(text)
        if match:
            var_name, default = match.groups()
            value = self._get_variable(var_name, default)
            return value  # Return original type (not converted to string)

        # Replace all variable references in the string
        def replace_var(match):
            var_name, default = match.groups()
            value = self._get_variable(var_name, default)
            return str(value) if value is not None else ''

        return self.VARIABLE_PATTERN.sub(replace_var, text)

    def _get_variable(self, var_name: str, default: str | None = None) -> Any:
        """Get variable value from context.

        Args:
            var_name: Variable name (supports dot notation for nested access)
            default: Default value if variable not found

        Returns:
            Variable value or default
        """
        # Handle dot notation (e.g., env.api.base_url)
        keys = var_name.split('.')
        value = self.context

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    break
            else:
                value = None
                break

        # Return value or default
        if value is not None:
            return value
        elif default is not None:
            return default
        else:
            return f"${{{var_name}}}"  # Return original if not found


class ExecutionContext:
    """Base execution context for managing parameters and variables."""

    def __init__(self, environment: str = "test", initial_params: dict[str, Any] | None = None):
        """Initialize execution context.

        Args:
            environment: Environment name (test, production, etc.)
            initial_params: Initial parameters
        """
        self.environment = environment
        self.params: dict[str, Any] = {}
        self.execution_history: list = []

        # Load environment configuration
        self._load_environment_config()

        # Apply initial parameters
        if initial_params:
            self.params.update(initial_params)

    def _load_environment_config(self):
        """Load environment configuration."""
        try:
            settings = get_settings()
            # Create a simple config dict from settings
            config_dict = {
                'api': {
                    'base_url': f"http://{settings.host}:{settings.port}",
                    'timeout': 30
                },
                'database': {
                    'url': settings.database_url
                },
                'redis': {
                    'url': settings.redis_url
                }
            }
            # Flatten config to support dot notation
            self.params['env'] = self._flatten_dict(config_dict)
        except Exception as e:
            print(f"Warning: Could not load environment config: {e}")
            self.params['env'] = {}

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """Flatten nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key prefix
            sep: Separator for keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def update_params(self, params: dict[str, Any], resolve: bool = True):
        """Update context parameters.

        Args:
            params: Parameters to add/update
            resolve: Whether to resolve variables in parameters
        """
        if resolve:
            resolver = VariableResolver(self.params)
            resolved_params = resolver.resolve(params)
            self.params.update(resolved_params)
        else:
            self.params.update(params)

    def get_param(self, key: str, default: Any = None) -> Any:
        """Get parameter value.

        Args:
            key: Parameter key (supports dot notation)
            default: Default value if not found

        Returns:
            Parameter value or default
        """
        keys = key.split('.')
        value = self.params

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def resolve_variables(self, data: Any) -> Any:
        """Resolve all variables in data.

        Args:
            data: Data containing variable references

        Returns:
            Data with all variables resolved
        """
        resolver = VariableResolver(self.params)
        return resolver.resolve(data)

    def add_execution_record(self, record: dict[str, Any]):
        """Add execution record to history.

        Args:
            record: Execution record
        """
        self.execution_history.append(record)


class ScriptExecutionContext(ExecutionContext):
    """Execution context for script layer."""

    def __init__(self, script, override_params: dict[str, Any] | None = None,
                 environment: str = "test"):
        """Initialize script execution context.

        Args:
            script: TestScript instance
            override_params: Parameters to override script defaults
            environment: Environment name
        """
        super().__init__(environment)

        self.script = script

        # Load script variables
        if script.variables:
            self.params.update(script.variables)

        # Load script parameter defaults
        for param in script.parameters:
            if param.default_value:
                self.params[param.name] = param.default_value

        # Apply override parameters
        if override_params:
            self.update_params(override_params)


class ComponentExecutionContext(ExecutionContext):
    """Execution context for component layer."""

    def __init__(self, component, override_params: dict[str, Any] | None = None,
                 environment: str = "test"):
        """Initialize component execution context.

        Args:
            component: TestComponent instance
            override_params: Parameters to override component defaults
            environment: Environment name
        """
        super().__init__(environment)

        self.component = component
        self.script_results: dict[str, Any] = {}

        # Load component shared variables
        if component.shared_variables:
            self.params.update(component.shared_variables)

        # Apply override parameters
        if override_params:
            self.update_params(override_params)

    def execute_script(self, component_script) -> dict[str, Any]:
        """Execute a script within the component context.

        Args:
            component_script: ComponentScript instance

        Returns:
            Execution result
        """
        # Build script parameters
        script_params = self.params.copy()

        # Apply script-level parameter overrides
        if component_script.script_parameters:
            resolved_params = self.resolve_variables(component_script.script_parameters)
            script_params.update(resolved_params)

        # Create script execution context
        ScriptExecutionContext(
            component_script.script,
            script_params,
            self.environment
        )

        # Execute script (placeholder - actual execution would be implemented)
        result = {
            'success': True,
            'script_name': component_script.script.name,
            'output_variables': {}
        }

        # Store result
        self.script_results[component_script.script.name] = result

        # Update shared variables with script output
        if result.get('output_variables'):
            self.params.update(result['output_variables'])

        # Add to execution history
        self.add_execution_record({
            'type': 'script',
            'name': component_script.script.name,
            'order': component_script.execution_order,
            'result': result
        })

        return result


class TestCaseExecutionContext(ExecutionContext):
    """Execution context for test case layer."""

    def __init__(self, test_case, runtime_params: dict[str, Any] | None = None):
        """Initialize test case execution context.

        Args:
            test_case: TestCase instance
            runtime_params: Runtime parameters (highest priority)
        """
        super().__init__(test_case.environment)

        self.test_case = test_case

        # Load test case data
        if test_case.test_data:
            self.params.update(test_case.test_data)

        # Apply runtime parameters (highest priority)
        if runtime_params:
            self.update_params(runtime_params)

    def execute_script(self, case_script) -> dict[str, Any]:
        """Execute a script within the test case context.

        Args:
            case_script: TestCaseScript instance

        Returns:
            Execution result
        """
        # Build script parameters
        script_params = self.params.copy()

        # Apply script-level parameter overrides
        if case_script.script_parameters:
            resolved_params = self.resolve_variables(case_script.script_parameters)
            script_params.update(resolved_params)

        # Create script execution context
        ScriptExecutionContext(
            case_script.script,
            script_params,
            self.environment
        )

        # Execute script (placeholder)
        result = {
            'success': True,
            'script_name': case_script.script.name,
            'output_variables': {}
        }

        # Update context with script output
        if result.get('output_variables'):
            self.params.update(result['output_variables'])

        # Add to execution history
        self.add_execution_record({
            'type': 'script',
            'name': case_script.script.name,
            'order': case_script.execution_order,
            'result': result
        })

        return result

    def execute_component(self, case_component) -> dict[str, Any]:
        """Execute a component within the test case context.

        Args:
            case_component: TestCaseComponent instance

        Returns:
            Execution result
        """
        # Build component parameters
        component_params = self.params.copy()

        # Apply component-level parameter overrides
        if case_component.component_parameters:
            resolved_params = self.resolve_variables(case_component.component_parameters)
            component_params.update(resolved_params)

        # Create component execution context
        comp_context = ComponentExecutionContext(
            case_component.component,
            component_params,
            self.environment
        )

        # Execute all scripts in the component
        component_results = []
        for comp_script in case_component.component.component_scripts:
            if comp_script.is_enabled:
                script_result = comp_context.execute_script(comp_script)
                component_results.append(script_result)

                # Stop if script failed and continue_on_failure is False
                if not script_result['success'] and not case_component.component.continue_on_failure:
                    break

        result = {
            'success': all(r['success'] for r in component_results),
            'component_name': case_component.component.name,
            'script_results': component_results,
            'output_variables': comp_context.params
        }

        # Update context with component output
        if result.get('output_variables'):
            self.params.update(result['output_variables'])

        # Add to execution history
        self.add_execution_record({
            'type': 'component',
            'name': case_component.component.name,
            'order': case_component.execution_order,
            'result': result
        })

        return result
