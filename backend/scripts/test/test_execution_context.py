"""Test script for execution context and engine.

This script demonstrates the execution context and engine functionality
for the four-layer architecture.
"""

import asyncio
from datetime import datetime

from morado.services.execution_context import (
    ComponentExecutionContext,
    ExecutionContext,
    ScriptExecutionContext,
    TestCaseExecutionContext,
    VariableResolver,
)
from morado.services.execution_engine import ExecutionEngine, ExecutionStatus


# Mock models for testing
class MockScript:
    """Mock TestScript model."""
    def __init__(self, name: str, variables: dict | None = None):
        self.name = name
        self.variables = variables or {}
        self.parameters = []
        self.output_variables = []


class MockComponent:
    """Mock TestComponent model."""
    def __init__(self, name: str, shared_variables: dict | None = None):
        self.name = name
        self.shared_variables = shared_variables or {}
        self.component_scripts = []
        self.execution_mode = type('ExecutionMode', (), {'value': 'sequential'})()
        self.continue_on_failure = False


class MockTestCase:
    """Mock TestCase model."""
    def __init__(self, name: str, test_data: dict | None = None, environment: str = "test"):
        self.name = name
        self.test_data = test_data or {}
        self.environment = environment
        self.test_case_scripts = []
        self.test_case_components = []
        self.continue_on_failure = False


def test_variable_resolver():
    """Test variable resolver functionality."""
    print("\n=== Testing Variable Resolver ===")

    # Test simple variable resolution
    resolver = VariableResolver({"user": "test_user", "timeout": 30})

    result = resolver.resolve("User: ${user}, Timeout: ${timeout}")
    print(f"Simple resolution: {result}")
    assert result == "User: test_user, Timeout: 30"

    # Test default values
    result = resolver.resolve("Role: ${role:admin}")
    print(f"Default value: {result}")
    assert result == "Role: admin"

    # Test built-in variables
    result = resolver.resolve("UUID: ${uuid}")
    print(f"Built-in UUID: {result}")
    assert "UUID:" in result

    result = resolver.resolve("Date: ${date}")
    print(f"Built-in date: {result}")
    assert "Date:" in result

    # Test nested dict resolution
    nested = {"api": {"base_url": "https://example.com", "timeout": 60}}
    context = ExecutionContext()
    flat_dict = context._flatten_dict(nested)
    resolver = VariableResolver(flat_dict)
    result = resolver.resolve("URL: ${api.base_url}")
    print(f"Nested resolution: {result}")
    assert result == "URL: https://example.com"

    print("✓ Variable resolver tests passed")


def test_execution_context():
    """Test execution context functionality."""
    print("\n=== Testing Execution Context ===")

    # Test base execution context
    context = ExecutionContext(environment="test")
    context.set_param("user", "test_user")
    context.set_param("timeout", 30)

    assert context.get_param("user") == "test_user"
    assert context.get_param("timeout") == 30
    print(f"✓ Base context params: {context.params}")

    # Test parameter resolution
    context.set_param("base_url", "https://api.example.com")
    result = context.resolve_value("URL: ${base_url}/users/${user}")
    print(f"✓ Resolved value: {result}")
    assert "https://api.example.com/users/test_user" in result

    print("✓ Execution context tests passed")


def test_script_execution_context():
    """Test script execution context."""
    print("\n=== Testing Script Execution Context ===")

    # Create mock script
    script = MockScript(
        name="Test Script",
        variables={"timeout": 30, "retry": 3}
    )

    # Test without override
    context = ScriptExecutionContext(script)
    assert context.get_param("timeout") == 30
    assert context.get_param("retry") == 3
    print(f"✓ Script context without override: {context.params}")

    # Test with override
    context = ScriptExecutionContext(script, override_params={"timeout": 60})
    assert context.get_param("timeout") == 60  # Override wins
    assert context.get_param("retry") == 3  # From script
    print(f"✓ Script context with override: {context.params}")

    print("✓ Script execution context tests passed")


def test_component_execution_context():
    """Test component execution context."""
    print("\n=== Testing Component Execution Context ===")

    # Create mock component
    component = MockComponent(
        name="Test Component",
        shared_variables={"base_url": "https://api.example.com", "timeout": 30}
    )

    # Test component context
    context = ComponentExecutionContext(component)
    assert context.get_param("base_url") == "https://api.example.com"
    assert context.get_param("timeout") == 30
    print(f"✓ Component context: {context.params}")

    # Test script context creation
    script = MockScript(name="Script 1", variables={"retry": 3})
    script_context = context.create_script_context(
        script,
        script_params={"timeout": 60}  # Override component timeout
    )
    assert script_context.get_param("timeout") == 60  # Override wins
    assert script_context.get_param("base_url") == "https://api.example.com"  # From component
    assert script_context.get_param("retry") == 3  # From script
    print(f"✓ Script context from component: {script_context.params}")

    # Test result saving
    context.save_script_result("Script 1", {
        "success": True,
        "output_variables": {"user_id": 123}
    })
    assert context.get_param("user_id") == 123  # Output variable propagated
    print(f"✓ Output variable propagated: user_id = {context.get_param('user_id')}")

    print("✓ Component execution context tests passed")


def test_test_case_execution_context():
    """Test test case execution context."""
    print("\n=== Testing Test Case Execution Context ===")

    # Create mock test case
    test_case = MockTestCase(
        name="User Login Test",
        test_data={"username": "test", "password": "pass123"},
        environment="test"
    )

    # Test without runtime params
    context = TestCaseExecutionContext(test_case)
    assert context.get_param("username") == "test"
    assert context.get_param("password") == "pass123"
    print(f"✓ Test case context without runtime: {context.params}")

    # Test with runtime params (highest priority)
    context = TestCaseExecutionContext(
        test_case,
        runtime_params={"password": "override123"}
    )
    assert context.get_param("password") == "override123"  # Runtime wins
    assert context.get_param("username") == "test"  # From test case
    print(f"✓ Test case context with runtime: {context.params}")

    # Test execution history
    context.add_execution_record("script", "Script 1", {
        "success": True,
        "output_variables": {"token": "abc123"}
    })
    assert context.get_param("token") == "abc123"  # Output variable propagated
    assert len(context.get_execution_history()) == 1
    print(f"✓ Execution history: {len(context.get_execution_history())} records")

    # Test execution summary
    context.add_execution_record("script", "Script 2", {"success": True})
    context.add_execution_record("script", "Script 3", {"success": False})
    summary = context.get_execution_summary()
    assert summary["total"] == 3
    assert summary["successful"] == 2
    assert summary["failed"] == 1
    print(f"✓ Execution summary: {summary}")

    print("✓ Test case execution context tests passed")


async def test_execution_engine():
    """Test execution engine."""
    print("\n=== Testing Execution Engine ===")

    engine = ExecutionEngine()

    # Test script execution
    script = MockScript(name="Test Script", variables={"timeout": 30})
    context = ScriptExecutionContext(script)

    result = await engine.execute_script(script, context)
    assert result.success
    assert result.status == ExecutionStatus.SUCCESS
    print(f"✓ Script execution: {result.status.value}, duration: {result.duration:.3f}s")

    # Test component execution
    component = MockComponent(
        name="Test Component",
        shared_variables={"base_url": "https://api.example.com"}
    )
    comp_context = ComponentExecutionContext(component)

    result = await engine.execute_component(component, comp_context)
    assert result.success
    assert result.status == ExecutionStatus.SUCCESS
    print(f"✓ Component execution: {result.status.value}, duration: {result.duration:.3f}s")

    # Test test case execution
    test_case = MockTestCase(
        name="User Login Test",
        test_data={"username": "test"}
    )

    result = await engine.execute_test_case(
        test_case,
        runtime_params={"password": "pass123"}
    )
    assert result.success
    assert result.status == ExecutionStatus.SUCCESS
    print(f"✓ Test case execution: {result.status.value}, duration: {result.duration:.3f}s")

    print("✓ Execution engine tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Execution Context and Engine")
    print("=" * 60)

    try:
        # Test variable resolver
        test_variable_resolver()

        # Test execution contexts
        test_execution_context()
        test_script_execution_context()
        test_component_execution_context()
        test_test_case_execution_context()

        # Test execution engine (async)
        asyncio.run(test_execution_engine())

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
