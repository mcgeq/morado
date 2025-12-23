"""Execution Engine for Four-Layer Architecture

This module provides the execution engine for running scripts, components,
and test cases in the four-layer architecture. It handles:
- Script independent execution and debugging
- Component execution (multiple scripts)
- Component nesting execution
- Test case execution (scripts and components)
- Sequential and parallel execution modes
- Error handling and result aggregation

The execution engine coordinates with execution contexts to manage
parameter flow and variable propagation across layers.
"""

import asyncio
from enum import Enum
from typing import Any

from morado.services.execution_context import (
    ComponentExecutionContext,
    ScriptExecutionContext,
    TestCaseExecutionContext,
)


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


class ExecutionResult:
    """Execution result container.

    Attributes:
        status: Execution status
        success: Whether execution was successful
        output: Execution output data
        error: Error message if failed
        duration: Execution duration in seconds
        output_variables: Variables to propagate to next execution
    """

    def __init__(
        self,
        status: ExecutionStatus,
        success: bool,
        output: Any = None,
        error: str | None = None,
        duration: float = 0.0,
        output_variables: dict[str, Any] | None = None,
    ):
        """Initialize execution result.

        Args:
            status: Execution status
            success: Whether execution was successful
            output: Execution output data
            error: Error message if failed
            duration: Execution duration in seconds
            output_variables: Variables to propagate
        """
        self.status = status
        self.success = success
        self.output = output
        self.error = error
        self.duration = duration
        self.output_variables = output_variables or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of result
        """
        return {
            "status": self.status.value,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "duration": self.duration,
            "output_variables": self.output_variables,
        }


class ExecutionEngine:
    """Execution engine for four-layer architecture.

    Provides methods to execute:
    - Individual scripts (with debugging support)
    - Components (multiple scripts, sequential or parallel)
    - Nested components (recursive execution)
    - Test cases (scripts and components)

    Example:
        >>> engine = ExecutionEngine()
        >>> # Execute a script
        >>> result = await engine.execute_script(script, context)
        >>> # Execute a component
        >>> result = await engine.execute_component(component, context)
        >>> # Execute a test case
        >>> result = await engine.execute_test_case(test_case, runtime_params)
    """

    async def execute_script(
        self,
        script: Any,  # TestScript model
        context: ScriptExecutionContext,
        debug_mode: bool = False,  # noqa: ARG002
    ) -> ExecutionResult:
        """Execute a single script.

        Args:
            script: TestScript model instance
            context: Script execution context
            debug_mode: Whether to enable debug mode

        Returns:
            ExecutionResult with script execution outcome

        Example:
            >>> from morado.models.script import TestScript
            >>> from morado.services.execution_context import ScriptExecutionContext
            >>> script = TestScript(name="Test Script")
            >>> context = ScriptExecutionContext(script)
            >>> engine = ExecutionEngine()
            >>> result = await engine.execute_script(script, context)
            >>> print(result.success)
            True
        """
        import time

        start_time = time.time()

        try:
            # Resolve all parameters
            resolved_params = context.resolve_params(context.params)

            # Get API definition from script
            api_definition = script.api_definition
            if not api_definition:
                error_msg = f"Script '{script.name}' has no API definition"
                raise ValueError(error_msg)

            # Build HTTP request from API definition
            request_data = self._build_request_from_api_definition(
                api_definition, resolved_params, context
            )

            # Create HTTP client
            from morado.common.http import create_default_client

            # Configure timeout from script or API definition
            timeout = None
            if script.timeout_override:
                timeout = (10, script.timeout_override)
            elif api_definition.timeout:
                timeout = (10, api_definition.timeout)

            # Execute HTTP request
            with create_default_client(base_url=api_definition.base_url) as client:
                response = client.request(
                    method=request_data["method"],
                    url=request_data["url"],
                    headers=request_data.get("headers"),
                    params=request_data.get("params"),
                    json=request_data.get("json"),
                    data=request_data.get("data"),
                    files=request_data.get("files"),
                    timeout=timeout,
                )

            # Validate response against assertions
            assertion_results = self._validate_response(
                response, script.assertions or [], context
            )

            # Extract output variables from response
            extracted_vars = self._extract_variables(
                response, script.extract_variables or {}, context
            )

            # Update context with extracted variables
            context.update_params(extracted_vars)

            # Prepare output
            output = {
                "script_name": script.name,
                "api_definition": api_definition.name,
                "request": {
                    "method": request_data["method"],
                    "url": request_data["url"],
                    "headers": request_data.get("headers"),
                    "params": request_data.get("params"),
                },
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else response.text,
                    "request_time": response.request_time,
                },
                "assertions": assertion_results,
                "extracted_variables": extracted_vars,
            }

            # Check if all assertions passed
            all_assertions_passed = all(
                result["passed"] for result in assertion_results
            )

            # Get output variables
            output_variables = context.get_script_output()

            duration = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS
                if all_assertions_passed
                else ExecutionStatus.FAILED,
                success=all_assertions_passed,
                output=output,
                duration=duration,
                output_variables=output_variables,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                success=False,
                error=str(e),
                duration=duration,
            )

    async def execute_component(
        self,
        component: Any,  # TestComponent model
        context: ComponentExecutionContext,
        debug_mode: bool = False,
    ) -> ExecutionResult:
        """Execute a component (multiple scripts).

        Executes all scripts in the component according to execution mode:
        - Sequential: Execute scripts one by one in order
        - Parallel: Execute all scripts concurrently
        - Conditional: Execute scripts based on conditions

        Args:
            component: TestComponent model instance
            context: Component execution context
            debug_mode: Whether to enable debug mode

        Returns:
            ExecutionResult with component execution outcome

        Example:
            >>> from morado.models.component import TestComponent
            >>> from morado.services.execution_context import ComponentExecutionContext
            >>> component = TestComponent(name="Test Component")
            >>> context = ComponentExecutionContext(component)
            >>> engine = ExecutionEngine()
            >>> result = await engine.execute_component(component, context)
            >>> print(result.success)
            True
        """
        import time

        start_time = time.time()

        try:
            # Get component scripts sorted by execution order
            component_scripts = sorted(
                component.component_scripts, key=lambda cs: cs.execution_order
            )

            script_results = []

            # Execute based on execution mode
            if component.execution_mode.value == "sequential":
                # Sequential execution
                for comp_script in component_scripts:
                    if not comp_script.is_enabled:
                        continue

                    # Check execution condition if specified
                    if comp_script.execution_condition:
                        condition_met = self._evaluate_condition(
                            comp_script.execution_condition, context
                        )
                        if not condition_met and comp_script.skip_on_condition:
                            continue

                    # Create script context
                    script_context = context.create_script_context(
                        comp_script.script, comp_script.script_parameters
                    )

                    # Execute script
                    result = await self.execute_script(
                        comp_script.script, script_context, debug_mode
                    )

                    # Save result
                    context.save_script_result(
                        comp_script.script.name, result.to_dict()
                    )
                    script_results.append(result)

                    # Check if should continue on failure
                    if not result.success and not component.continue_on_failure:
                        break

            elif component.execution_mode.value == "parallel":
                # Parallel execution
                tasks = []
                for comp_script in component_scripts:
                    if not comp_script.is_enabled:
                        continue

                    script_context = context.create_script_context(
                        comp_script.script, comp_script.script_parameters
                    )

                    task = self.execute_script(
                        comp_script.script, script_context, debug_mode
                    )
                    tasks.append((comp_script.script.name, task))

                # Wait for all tasks
                results = await asyncio.gather(*[task for _, task in tasks])

                # Save results
                for (script_name, _), result in zip(tasks, results):
                    context.save_script_result(script_name, result.to_dict())
                    script_results.append(result)

            # Determine overall success
            all_success = all(r.success for r in script_results)
            duration = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS
                if all_success
                else ExecutionStatus.FAILED,
                success=all_success,
                output={
                    "component_name": component.name,
                    "script_results": [r.to_dict() for r in script_results],
                    "shared_variables": context.params,
                },
                duration=duration,
                output_variables=context.params,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                success=False,
                error=str(e),
                duration=duration,
            )

    async def execute_nested_component(
        self,
        component: Any,  # TestComponent model
        context: ComponentExecutionContext,
        debug_mode: bool = False,
    ) -> ExecutionResult:
        """Execute a component with nested components.

        Handles recursive execution of nested components.

        Args:
            component: TestComponent model instance
            context: Component execution context
            debug_mode: Whether to enable debug mode

        Returns:
            ExecutionResult with nested component execution outcome
        """
        # Check if component has child components
        if hasattr(component, "child_components") and component.child_components:
            # Execute child components first
            for child_component in component.child_components:
                child_context = ComponentExecutionContext(
                    child_component, override_params=context.params.copy()
                )

                # Recursive execution
                child_result = await self.execute_nested_component(
                    child_component, child_context, debug_mode
                )

                # Update parent context with child output
                if child_result.output_variables:
                    context.update_params(child_result.output_variables)

        # Execute this component's scripts
        return await self.execute_component(component, context, debug_mode)

    async def execute_test_case(
        self,
        test_case: Any,  # TestCase model
        runtime_params: dict[str, Any] | None = None,
        env_config: dict[str, Any] | None = None,
        debug_mode: bool = False,
    ) -> ExecutionResult:
        """Execute a test case (scripts and components).

        Executes all scripts and components in the test case according to
        execution order. Manages parameter flow and variable propagation.

        Args:
            test_case: TestCase model instance
            runtime_params: Runtime parameters (highest priority)
            env_config: Environment configuration
            debug_mode: Whether to enable debug mode

        Returns:
            ExecutionResult with test case execution outcome

        Example:
            >>> from morado.models.test_case import TestCase
            >>> test_case = TestCase(
            ...     name="User Login Test",
            ...     test_data={"username": "test"}
            ... )
            >>> engine = ExecutionEngine()
            >>> result = await engine.execute_test_case(
            ...     test_case,
            ...     runtime_params={"password": "pass123"}
            ... )
            >>> print(result.success)
            True
        """
        import time

        start_time = time.time()

        try:
            # Create test case execution context
            context = TestCaseExecutionContext(
                test_case, runtime_params=runtime_params, env_config=env_config
            )

            # Collect all execution items (scripts and components)
            items = []

            # Add scripts
            if hasattr(test_case, "test_case_scripts"):
                for case_script in test_case.test_case_scripts:
                    items.append((case_script.execution_order, "script", case_script))

            # Add components
            if hasattr(test_case, "test_case_components"):
                for case_component in test_case.test_case_components:
                    items.append(
                        (case_component.execution_order, "component", case_component)
                    )

            # Sort by execution order
            items.sort(key=lambda x: x[0])

            # Execute items in order
            for _order, item_type, item in items:
                if item_type == "script":
                    # Execute script
                    if not item.is_enabled:
                        continue

                    script_context = context.create_script_context(
                        item.script, item.script_parameters
                    )

                    result = await self.execute_script(
                        item.script, script_context, debug_mode
                    )

                    # Add to execution history
                    context.add_execution_record(
                        "script", item.script.name, result.to_dict()
                    )

                    # Check if should continue on failure
                    if not result.success and not test_case.continue_on_failure:
                        break

                elif item_type == "component":
                    # Execute component
                    if not item.is_enabled:
                        continue

                    component_context = context.create_component_context(
                        item.component, item.component_parameters
                    )

                    result = await self.execute_nested_component(
                        item.component, component_context, debug_mode
                    )

                    # Add to execution history
                    context.add_execution_record(
                        "component", item.component.name, result.to_dict()
                    )

                    # Check if should continue on failure
                    if not result.success and not test_case.continue_on_failure:
                        break

            # Get execution summary
            summary = context.get_execution_summary()
            duration = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS
                if summary["failed"] == 0
                else ExecutionStatus.FAILED,
                success=summary["failed"] == 0,
                output={
                    "test_case_name": test_case.name,
                    "execution_history": context.get_execution_history(),
                    "summary": summary,
                    "final_params": context.params,
                },
                duration=duration,
                output_variables=context.params,
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                success=False,
                error=str(e),
                duration=duration,
            )

    def _evaluate_condition(
        self, condition: str, context: ComponentExecutionContext
    ) -> bool:
        """Evaluate execution condition.

        Args:
            condition: Condition expression (e.g., "${prev_status} == 'success'")
            context: Execution context

        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Resolve variables in condition
            resolved_condition = context.resolve_value(condition)

            # Simple evaluation (can be enhanced with safe eval)
            # For now, just check if it's a truthy value
            return bool(resolved_condition)

        except Exception:
            # If evaluation fails, return False
            return False

    def _build_request_from_api_definition(
        self,
        api_definition: Any,
        resolved_params: dict[str, Any],
        context: ScriptExecutionContext,
    ) -> dict[str, Any]:
        """Build HTTP request from API definition and parameters.

        This method implements the request building logic according to Requirements 1.1 and 1.3:
        - Constructs complete HTTP request from API Definition
        - Merges headers from Header component and script parameters
        - Merges body from Body component and script parameters
        - Applies parameter overrides (script params > API definition)

        Args:
            api_definition: ApiDefinition model instance
            resolved_params: Resolved parameters from execution context
            context: Script execution context

        Returns:
            Dictionary containing request data (method, url, headers, params, json, data, files)
        """
        request_data = {
            "method": api_definition.method.value,
            "url": api_definition.path,
        }

        # Build headers (merge Header component + script parameters)
        headers = {}

        # Add headers from Header component
        if api_definition.header and api_definition.header.headers:
            headers.update(api_definition.header.headers)

        # Override with headers from script parameters
        if "headers" in resolved_params:
            headers.update(resolved_params["headers"])

        # Resolve variables in headers
        headers = context.resolve_value(headers)
        request_data["headers"] = headers

        # Build query parameters
        query_params = {}

        # Add query parameters from API definition
        if api_definition.query_parameters:
            query_params.update(api_definition.query_parameters)

        # Override with query parameters from script parameters
        if "params" in resolved_params:
            query_params.update(resolved_params["params"])
        elif "query_params" in resolved_params:
            query_params.update(resolved_params["query_params"])

        # Resolve variables in query parameters
        if query_params:
            query_params = context.resolve_value(query_params)
            request_data["params"] = query_params

        # Build path parameters and update URL
        path_params = {}

        # Add path parameters from API definition
        if api_definition.path_parameters:
            path_params.update(api_definition.path_parameters)

        # Override with path parameters from script parameters
        if "path_params" in resolved_params:
            path_params.update(resolved_params["path_params"])

        # Resolve variables in path parameters
        if path_params:
            path_params = context.resolve_value(path_params)
            # Replace path parameters in URL
            for key, value in path_params.items():
                request_data["url"] = request_data["url"].replace(
                    f"{{{key}}}", str(value)
                )
                request_data["url"] = request_data["url"].replace(f":{key}", str(value))

        # Build request body (merge Body component + script parameters)
        body = None

        # Get body from Body component (referenced)
        if api_definition.request_body and api_definition.request_body.example_data:
            body = api_definition.request_body.example_data.copy()

        # Get body from inline definition
        elif api_definition.inline_request_body:
            body = api_definition.inline_request_body.copy()

        # Override with body from script parameters
        if "body" in resolved_params:
            if body:
                # Merge with existing body
                if isinstance(body, dict) and isinstance(resolved_params["body"], dict):
                    body.update(resolved_params["body"])
                else:
                    body = resolved_params["body"]
            else:
                body = resolved_params["body"]
        elif "json" in resolved_params:
            if body:
                # Merge with existing body
                if isinstance(body, dict) and isinstance(resolved_params["json"], dict):
                    body.update(resolved_params["json"])
                else:
                    body = resolved_params["json"]
            else:
                body = resolved_params["json"]

        # Resolve variables in body
        if body:
            body = context.resolve_value(body)

            # Determine content type and set appropriate field
            # Get content type, handling case where headers might be resolved to dict
            content_type = "application/json"  # default
            if isinstance(headers, dict):
                content_type = (
                    headers.get("Content-Type")
                    or headers.get("content-type")
                    or "application/json"
                )

            if isinstance(content_type, str) and "application/json" in content_type:
                request_data["json"] = body
            elif isinstance(content_type, str) and (
                "application/x-www-form-urlencoded" in content_type
                or "multipart/form-data" in content_type
            ):
                request_data["data"] = body
            else:
                # Default to JSON
                request_data["json"] = body

        # Handle file uploads
        if "files" in resolved_params:
            request_data["files"] = resolved_params["files"]

        return request_data

    def _validate_response(
        self,
        response: Any,  # HttpResponse
        assertions: list[dict[str, Any]],
        context: ScriptExecutionContext,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """Validate response against assertions.

        This method implements response validation according to Requirement 7.5:
        - Validates response against assertion rules
        - Returns detailed error information on validation failure

        Args:
            response: HttpResponse object
            assertions: List of assertion definitions
            context: Script execution context (reserved for future use)

        Returns:
            List of assertion results with pass/fail status and details
        """
        results = []

        for assertion in assertions:
            assertion_type = assertion.get("type")
            expected = assertion.get("expected")
            message = assertion.get("message", f"Assertion {assertion_type} failed")

            result = {
                "type": assertion_type,
                "expected": expected,
                "message": message,
                "passed": False,
                "actual": None,
                "error": None,
            }

            try:
                if assertion_type == "status_code":
                    # Validate status code
                    actual = response.status_code
                    result["actual"] = actual
                    result["passed"] = actual == expected

                elif assertion_type == "equals":
                    # Extract value using path and compare
                    path = assertion.get("path", "$")
                    actual = response.jsonpath(path) if path != "$" else response.json()
                    result["actual"] = actual
                    result["passed"] = actual == expected

                elif assertion_type == "not_equals":
                    # Extract value and ensure it's not equal
                    path = assertion.get("path", "$")
                    actual = response.jsonpath(path) if path != "$" else response.json()
                    result["actual"] = actual
                    result["passed"] = actual != expected

                elif assertion_type == "contains":
                    # Check if value contains expected
                    path = assertion.get("path", "$")
                    actual = response.jsonpath(path) if path != "$" else response.json()
                    result["actual"] = actual

                    if isinstance(actual, (list, dict, str)):
                        result["passed"] = expected in actual
                    else:
                        result["passed"] = False

                elif assertion_type == "not_contains":
                    # Check if value does not contain expected
                    path = assertion.get("path", "$")
                    actual = response.jsonpath(path) if path != "$" else response.json()
                    result["actual"] = actual

                    if isinstance(actual, (list, dict, str)):
                        result["passed"] = expected not in actual
                    else:
                        result["passed"] = True

                elif assertion_type == "greater_than":
                    # Compare numeric values
                    path = assertion.get("path", "$")
                    actual = response.jsonpath(path) if path != "$" else response.json()
                    result["actual"] = actual
                    # Ensure values are not None before conversion
                    try:
                        if actual is not None and expected is not None:
                            result["passed"] = float(str(actual)) > float(str(expected))
                        else:
                            result["passed"] = False
                            result["error"] = "Cannot compare None values"
                    except (ValueError, TypeError) as e:
                        result["passed"] = False
                        result["error"] = f"Type conversion error: {e}"

                elif assertion_type == "less_than":
                    # Compare numeric values
                    path = assertion.get("path", "$")
                    actual = response.jsonpath(path) if path != "$" else response.json()
                    result["actual"] = actual
                    # Ensure values are not None before conversion
                    try:
                        if actual is not None and expected is not None:
                            result["passed"] = float(str(actual)) < float(str(expected))
                        else:
                            result["passed"] = False
                            result["error"] = "Cannot compare None values"
                    except (ValueError, TypeError) as e:
                        result["passed"] = False
                        result["error"] = f"Type conversion error: {e}"

                elif assertion_type == "regex_match":
                    # Match against regex pattern
                    import re

                    path = assertion.get("path", "$")
                    actual = str(
                        response.jsonpath(path) if path != "$" else response.text
                    )
                    result["actual"] = actual
                    pattern = assertion.get("pattern", expected)
                    result["passed"] = bool(re.search(pattern, actual))

                elif assertion_type == "json_path":
                    # Check if JSONPath exists or matches value
                    path = assertion.get("path")
                    assertion_check = assertion.get("assertion", "exists")

                    try:
                        actual = response.jsonpath(path)
                        result["actual"] = actual

                        if assertion_check == "exists":
                            result["passed"] = actual is not None
                        elif assertion_check == "not_exists":
                            result["passed"] = actual is None
                        elif assertion_check == "equals":
                            result["passed"] = actual == expected
                        else:
                            result["passed"] = False
                    except Exception:
                        result["actual"] = None
                        result["passed"] = assertion_check == "not_exists"

                elif assertion_type == "response_time":
                    # Validate response time
                    actual = response.request_time
                    result["actual"] = actual
                    # Ensure expected is not None before conversion
                    try:
                        if expected is not None:
                            result["passed"] = actual <= float(str(expected))
                        else:
                            result["passed"] = False
                            result["error"] = "Expected response time is None"
                    except (ValueError, TypeError) as e:
                        result["passed"] = False
                        result["error"] = f"Type conversion error: {e}"

                else:
                    # Unknown assertion type
                    result["error"] = f"Unknown assertion type: {assertion_type}"
                    result["passed"] = False

            except Exception as e:
                result["error"] = str(e)
                result["passed"] = False

            results.append(result)

        return results

    def _extract_variables(
        self,
        response: Any,  # HttpResponse
        extract_config: dict[str, str],
        context: ScriptExecutionContext,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Extract variables from response.

        This method implements variable extraction according to Requirement 6.2:
        - Extracts values from response using JSONPath
        - Stores extracted values in execution context

        Args:
            response: HttpResponse object
            extract_config: Dictionary mapping variable names to JSONPath expressions
            context: Script execution context (reserved for future use)

        Returns:
            Dictionary of extracted variables
        """
        extracted = {}

        for var_name, jsonpath_expr in extract_config.items():
            try:
                # Extract value using JSONPath
                value = response.jsonpath(jsonpath_expr)
                extracted[var_name] = value
            except Exception as e:
                # Log extraction failure but continue
                # In production, this should use proper logging
                print(
                    f"Failed to extract variable '{var_name}' using path '{jsonpath_expr}': {e}"
                )
                extracted[var_name] = None

        return extracted


# Convenience functions for direct execution
async def execute_script(
    script: Any, params: dict[str, Any] | None = None, debug_mode: bool = False
) -> ExecutionResult:
    """Execute a script with given parameters.

    Args:
        script: TestScript model instance
        params: Script parameters
        debug_mode: Whether to enable debug mode

    Returns:
        ExecutionResult

    Example:
        >>> from morado.models.script import TestScript
        >>> script = TestScript(name="Test Script")
        >>> result = await execute_script(script, {"user": "test"})
        >>> print(result.success)
        True
    """
    context = ScriptExecutionContext(script, override_params=params)
    engine = ExecutionEngine()
    return await engine.execute_script(script, context, debug_mode)


async def execute_component(
    component: Any, params: dict[str, Any] | None = None, debug_mode: bool = False
) -> ExecutionResult:
    """Execute a component with given parameters.

    Args:
        component: TestComponent model instance
        params: Component parameters
        debug_mode: Whether to enable debug mode

    Returns:
        ExecutionResult

    Example:
        >>> from morado.models.component import TestComponent
        >>> component = TestComponent(name="Test Component")
        >>> result = await execute_component(component, {"timeout": 30})
        >>> print(result.success)
        True
    """
    context = ComponentExecutionContext(component, override_params=params)
    engine = ExecutionEngine()
    return await engine.execute_nested_component(component, context, debug_mode)


async def execute_test_case(
    test_case: Any,
    runtime_params: dict[str, Any] | None = None,
    env_config: dict[str, Any] | None = None,
    debug_mode: bool = False,
) -> ExecutionResult:
    """Execute a test case with given parameters.

    Args:
        test_case: TestCase model instance
        runtime_params: Runtime parameters
        env_config: Environment configuration
        debug_mode: Whether to enable debug mode

    Returns:
        ExecutionResult

    Example:
        >>> from morado.models.test_case import TestCase
        >>> test_case = TestCase(name="User Login Test")
        >>> result = await execute_test_case(test_case, {"password": "test123"})
        >>> print(result.success)
        True
    """
    engine = ExecutionEngine()
    return await engine.execute_test_case(
        test_case,
        runtime_params=runtime_params,
        env_config=env_config,
        debug_mode=debug_mode,
    )
