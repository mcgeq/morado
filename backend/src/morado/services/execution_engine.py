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
        output_variables: dict[str, Any] | None = None
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
            'status': self.status.value,
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'duration': self.duration,
            'output_variables': self.output_variables
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
        debug_mode: bool = False  # noqa: ARG002
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

            # NOTE: Actual script execution logic to be implemented
            # This is a placeholder for the actual HTTP request execution
            # In real implementation, this would:
            # 1. Get API definition from script
            # 2. Build HTTP request with resolved parameters
            # 3. Execute HTTP request
            # 4. Validate response against assertions
            # 5. Extract output variables

            # Simulate script execution
            output = {
                'script_name': script.name,
                'parameters': resolved_params,
                'response': {
                    'status_code': 200,
                    'body': {'message': 'Success'}
                }
            }

            # Extract output variables
            output_variables = context.get_script_output()

            duration = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                success=True,
                output=output,
                duration=duration,
                output_variables=output_variables
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                success=False,
                error=str(e),
                duration=duration
            )

    async def execute_component(
        self,
        component: Any,  # TestComponent model
        context: ComponentExecutionContext,
        debug_mode: bool = False
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
                component.component_scripts,
                key=lambda cs: cs.execution_order
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
                            comp_script.execution_condition,
                            context
                        )
                        if not condition_met and comp_script.skip_on_condition:
                            continue

                    # Create script context
                    script_context = context.create_script_context(
                        comp_script.script,
                        comp_script.script_parameters
                    )

                    # Execute script
                    result = await self.execute_script(
                        comp_script.script,
                        script_context,
                        debug_mode
                    )

                    # Save result
                    context.save_script_result(
                        comp_script.script.name,
                        result.to_dict()
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
                        comp_script.script,
                        comp_script.script_parameters
                    )

                    task = self.execute_script(
                        comp_script.script,
                        script_context,
                        debug_mode
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
                status=ExecutionStatus.SUCCESS if all_success else ExecutionStatus.FAILED,
                success=all_success,
                output={
                    'component_name': component.name,
                    'script_results': [r.to_dict() for r in script_results],
                    'shared_variables': context.params
                },
                duration=duration,
                output_variables=context.params
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                success=False,
                error=str(e),
                duration=duration
            )

    async def execute_nested_component(
        self,
        component: Any,  # TestComponent model
        context: ComponentExecutionContext,
        debug_mode: bool = False
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
        if hasattr(component, 'child_components') and component.child_components:
            # Execute child components first
            for child_component in component.child_components:
                child_context = ComponentExecutionContext(
                    child_component,
                    override_params=context.params.copy()
                )

                # Recursive execution
                child_result = await self.execute_nested_component(
                    child_component,
                    child_context,
                    debug_mode
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
        debug_mode: bool = False
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
                test_case,
                runtime_params=runtime_params,
                env_config=env_config
            )

            # Collect all execution items (scripts and components)
            items = []

            # Add scripts
            if hasattr(test_case, 'test_case_scripts'):
                for case_script in test_case.test_case_scripts:
                    items.append((
                        case_script.execution_order,
                        'script',
                        case_script
                    ))

            # Add components
            if hasattr(test_case, 'test_case_components'):
                for case_component in test_case.test_case_components:
                    items.append((
                        case_component.execution_order,
                        'component',
                        case_component
                    ))

            # Sort by execution order
            items.sort(key=lambda x: x[0])

            # Execute items in order
            for _order, item_type, item in items:
                if item_type == 'script':
                    # Execute script
                    if not item.is_enabled:
                        continue

                    script_context = context.create_script_context(
                        item.script,
                        item.script_parameters
                    )

                    result = await self.execute_script(
                        item.script,
                        script_context,
                        debug_mode
                    )

                    # Add to execution history
                    context.add_execution_record(
                        'script',
                        item.script.name,
                        result.to_dict()
                    )

                    # Check if should continue on failure
                    if not result.success and not test_case.continue_on_failure:
                        break

                elif item_type == 'component':
                    # Execute component
                    if not item.is_enabled:
                        continue

                    component_context = context.create_component_context(
                        item.component,
                        item.component_parameters
                    )

                    result = await self.execute_nested_component(
                        item.component,
                        component_context,
                        debug_mode
                    )

                    # Add to execution history
                    context.add_execution_record(
                        'component',
                        item.component.name,
                        result.to_dict()
                    )

                    # Check if should continue on failure
                    if not result.success and not test_case.continue_on_failure:
                        break

            # Get execution summary
            summary = context.get_execution_summary()
            duration = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS if summary['failed'] == 0 else ExecutionStatus.FAILED,
                success=summary['failed'] == 0,
                output={
                    'test_case_name': test_case.name,
                    'execution_history': context.get_execution_history(),
                    'summary': summary,
                    'final_params': context.params
                },
                duration=duration,
                output_variables=context.params
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                success=False,
                error=str(e),
                duration=duration
            )

    def _evaluate_condition(
        self,
        condition: str,
        context: ComponentExecutionContext
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


# Convenience functions for direct execution
async def execute_script(
    script: Any,
    params: dict[str, Any] | None = None,
    debug_mode: bool = False
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
    component: Any,
    params: dict[str, Any] | None = None,
    debug_mode: bool = False
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
    debug_mode: bool = False
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
        debug_mode=debug_mode
    )
