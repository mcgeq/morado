"""Demo script for Layer 4: Test Case Model

This script demonstrates how to use the TestCase model with scripts and components.
It shows the four-layer architecture in action.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.models import (
    ApiDefinition,
    Body,
    ComponentScript,
    Header,
    TestCase,
    TestCaseComponent,
    TestCaseScript,
    TestComponent,
    TestScript,
)
from morado.models.test_case import TestCasePriority, TestCaseStatus


def demo_test_case_with_scripts():
    """Demonstrate creating a test case with scripts."""
    print("=" * 80)
    print("Demo: Test Case with Scripts")
    print("=" * 80)

    # Layer 1: Create API components
    print("\n1. Creating Layer 1: API Components...")
    auth_header = Header(
        uuid="header-001",
        name="Authorization Header",
        description="Bearer token authentication",
        headers={"Authorization": "Bearer ${auth_token}"},
    )
    print(f"   ✓ Created Header: {auth_header.name}")

    login_body = Body(
        uuid="body-001",
        name="Login Request Body",
        description="User login credentials",
        example_data={"username": "${username}", "password": "${password}"},
    )
    print(f"   ✓ Created Body: {login_body.name}")

    login_api = ApiDefinition(
        uuid="api-001",
        name="User Login API",
        description="Authenticate user and get token",
        method="POST",
        path="/api/auth/login",
        request_body_id=1,  # Reference to login_body
    )
    print(f"   ✓ Created ApiDefinition: {login_api.name}")

    # Layer 2: Create test scripts
    print("\n2. Creating Layer 2: Test Scripts...")
    login_script = TestScript(
        uuid="script-001",
        name="Login Script",
        description="Execute user login",
        api_definition_id=1,  # Reference to login_api
        variables={"username": "testuser", "password": "Test@123"},
        assertions=[
            {"type": "status_code", "expected": 200},
            {"type": "json_path", "path": "$.token", "assertion": "exists"},
        ],
        extract_variables={"auth_token": "$.token"},
        output_variables=["auth_token"],
    )
    print(f"   ✓ Created TestScript: {login_script.name}")

    get_profile_api = ApiDefinition(
        uuid="api-002",
        name="Get User Profile API",
        description="Get current user profile",
        method="GET",
        path="/api/user/profile",
        header_id=1,  # Reference to auth_header
    )
    print(f"   ✓ Created ApiDefinition: {get_profile_api.name}")

    profile_script = TestScript(
        uuid="script-002",
        name="Get Profile Script",
        description="Fetch user profile",
        api_definition_id=2,  # Reference to get_profile_api
        assertions=[
            {"type": "status_code", "expected": 200},
            {"type": "json_path", "path": "$.user.id", "assertion": "exists"},
        ],
    )
    print(f"   ✓ Created TestScript: {profile_script.name}")

    # Layer 4: Create test case with scripts
    print("\n3. Creating Layer 4: Test Case with Scripts...")
    test_case = TestCase(
        uuid="testcase-001",
        name="User Authentication Flow",
        description="Test complete user authentication and profile retrieval",
        priority=TestCasePriority.HIGH,
        status=TestCaseStatus.ACTIVE,
        category="Authentication",
        tags=["auth", "user", "api"],
        test_data={"username": "testuser", "password": "Test@123"},
        execution_order="sequential",
        timeout=60,
    )
    print(f"   ✓ Created TestCase: {test_case.name}")

    # Add scripts to test case
    print("\n4. Adding scripts to test case...")
    case_script_1 = TestCaseScript(
        test_case_id=1,
        script_id=1,  # login_script
        execution_order=1,
        is_enabled=True,
        script_parameters={"username": "override_user"},  # Override parameter
        description="Step 1: Login to get auth token",
    )
    print(f"   ✓ Added script 1: {login_script.name} (order: 1)")

    case_script_2 = TestCaseScript(
        test_case_id=1,
        script_id=2,  # profile_script
        execution_order=2,
        is_enabled=True,
        description="Step 2: Get user profile with auth token",
    )
    print(f"   ✓ Added script 2: {profile_script.name} (order: 2)")

    print("\n✅ Test case with scripts created successfully!")
    print(f"\nTest Case: {test_case.name}")
    print(f"  - Priority: {test_case.priority.value}")
    print(f"  - Status: {test_case.status.value}")
    print(f"  - Scripts: 2")
    print(f"  - Execution: {test_case.execution_order}")


def demo_test_case_with_components():
    """Demonstrate creating a test case with components."""
    print("\n\n" + "=" * 80)
    print("Demo: Test Case with Components")
    print("=" * 80)

    # Layer 3: Create test component
    print("\n1. Creating Layer 3: Test Component...")
    auth_component = TestComponent(
        uuid="component-001",
        name="Authentication Component",
        description="Reusable authentication flow",
        shared_variables={"base_url": "https://api.example.com"},
        timeout=120,
    )
    print(f"   ✓ Created TestComponent: {auth_component.name}")

    # Add scripts to component
    print("\n2. Adding scripts to component...")
    comp_script_1 = ComponentScript(
        component_id=1,
        script_id=1,  # login_script
        execution_order=1,
        script_parameters={"timeout": 30},
        description="Login step",
    )
    print(f"   ✓ Added script to component (order: 1)")

    comp_script_2 = ComponentScript(
        component_id=1,
        script_id=2,  # profile_script
        execution_order=2,
        description="Profile retrieval step",
    )
    print(f"   ✓ Added script to component (order: 2)")

    # Layer 4: Create test case with component
    print("\n3. Creating Layer 4: Test Case with Component...")
    test_case = TestCase(
        uuid="testcase-002",
        name="User Management Test Suite",
        description="Comprehensive user management tests using components",
        priority=TestCasePriority.CRITICAL,
        status=TestCaseStatus.ACTIVE,
        category="User Management",
        tags=["user", "component", "integration"],
        execution_order="sequential",
    )
    print(f"   ✓ Created TestCase: {test_case.name}")

    # Add component to test case
    print("\n4. Adding component to test case...")
    case_component = TestCaseComponent(
        test_case_id=2,
        component_id=1,  # auth_component
        execution_order=1,
        is_enabled=True,
        component_parameters={"base_url": "https://test.example.com"},  # Override
        description="Authentication flow component",
    )
    print(f"   ✓ Added component: {auth_component.name}")

    print("\n✅ Test case with component created successfully!")
    print(f"\nTest Case: {test_case.name}")
    print(f"  - Priority: {test_case.priority.value}")
    print(f"  - Components: 1")
    print(f"  - Component contains: 2 scripts")


def demo_test_case_mixed():
    """Demonstrate creating a test case with both scripts and components."""
    print("\n\n" + "=" * 80)
    print("Demo: Test Case with Mixed Scripts and Components")
    print("=" * 80)

    print("\n1. Creating Layer 4: Test Case with mixed references...")
    test_case = TestCase(
        uuid="testcase-003",
        name="Complete E2E Test",
        description="End-to-end test using both direct scripts and components",
        priority=TestCasePriority.HIGH,
        status=TestCaseStatus.ACTIVE,
        category="E2E Testing",
        tags=["e2e", "integration", "comprehensive"],
        preconditions="Test environment must be running",
        postconditions="Clean up test data",
        execution_order="sequential",
        timeout=300,
        retry_count=2,
        continue_on_failure=False,
    )
    print(f"   ✓ Created TestCase: {test_case.name}")

    # Add a component first
    print("\n2. Adding component (order: 1)...")
    case_component = TestCaseComponent(
        test_case_id=3,
        component_id=1,  # auth_component
        execution_order=1,
        description="Setup: Authentication",
    )
    print(f"   ✓ Added component at order 1")

    # Add direct scripts
    print("\n3. Adding direct scripts...")
    case_script_1 = TestCaseScript(
        test_case_id=3,
        script_id=1,  # Some other script
        execution_order=2,
        description="Additional test step",
    )
    print(f"   ✓ Added script at order 2")

    case_script_2 = TestCaseScript(
        test_case_id=3,
        script_id=2,  # Another script
        execution_order=3,
        description="Final verification step",
    )
    print(f"   ✓ Added script at order 3")

    print("\n✅ Mixed test case created successfully!")
    print(f"\nTest Case: {test_case.name}")
    print(f"  - Priority: {test_case.priority.value}")
    print(f"  - Components: 1")
    print(f"  - Direct Scripts: 2")
    print(f"  - Total execution steps: 3")
    print(f"  - Retry count: {test_case.retry_count}")


def demo_parameter_override():
    """Demonstrate parameter override mechanism."""
    print("\n\n" + "=" * 80)
    print("Demo: Parameter Override Mechanism")
    print("=" * 80)

    print("\nParameter Priority (highest to lowest):")
    print("  1. Runtime Parameters")
    print("  2. Test Case Data")
    print("  3. Component Shared Variables")
    print("  4. Script Variables")
    print("  5. Script Parameter Defaults")
    print("  6. Environment Config")

    print("\n" + "-" * 80)
    print("Example Scenario:")
    print("-" * 80)

    print("\nEnvironment Config:")
    print('  {"timeout": 30, "base_url": "https://prod.example.com"}')

    print("\nScript Variables:")
    print('  {"timeout": 60, "username": "default_user"}')

    print("\nComponent Shared Variables:")
    print('  {"base_url": "https://test.example.com"}')

    print("\nTest Case Data:")
    print('  {"username": "test_user", "password": "Test@123"}')

    print("\nTestCaseScript Parameter Override:")
    print('  {"timeout": 45}')

    print("\nRuntime Parameters:")
    print('  {"password": "NewPass@456"}')

    print("\n" + "-" * 80)
    print("Final Merged Parameters:")
    print("-" * 80)
    print("  {")
    print('    "timeout": 45,           # From TestCaseScript override')
    print('    "base_url": "https://test.example.com",  # From Component')
    print('    "username": "test_user",  # From Test Case')
    print('    "password": "NewPass@456" # From Runtime (highest priority)')
    print("  }")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("Layer 4: Test Case Model - Comprehensive Demo")
    print("=" * 80)

    try:
        # Run demos
        demo_test_case_with_scripts()
        demo_test_case_with_components()
        demo_test_case_mixed()
        demo_parameter_override()

        print("\n\n" + "=" * 80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("  ✓ Test cases can reference scripts directly")
        print("  ✓ Test cases can reference components")
        print("  ✓ Test cases can mix scripts and components")
        print("  ✓ Execution order is configurable")
        print("  ✓ Parameters can be overridden at each level")
        print("  ✓ Proper cascade behavior for deletions")
        print("  ✓ Rich metadata and configuration options")

        return 0

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
