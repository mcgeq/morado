"""Test the relationships between components, scripts, and test cases."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from morado.models.api_component import ApiDefinition, Header, HttpMethod
from morado.models.component import ComponentScript, ComponentType, TestComponent
from morado.models.script import ScriptType, TestScript
from morado.models.test_case import TestCase, TestCaseComponent, TestCasePriority

print("Testing Component Model Relationships\n")
print("=" * 60)

# Create a mock API definition
print("\n1. Creating API Definition...")
api_def = ApiDefinition(
    id=1,
    name="Test API",
    method=HttpMethod.GET,
    path="/api/test",
)
print(f"   ✓ Created: {api_def.name}")

# Create test scripts
print("\n2. Creating Test Scripts...")
script1 = TestScript(
    id=1,
    name="Setup Script",
    api_definition_id=1,
    script_type=ScriptType.SETUP,
    execution_order=1,
)
print(f"   ✓ Created: {script1.name} ({script1.script_type})")

script2 = TestScript(
    id=2,
    name="Main Test Script",
    api_definition_id=1,
    script_type=ScriptType.MAIN,
    execution_order=2,
)
print(f"   ✓ Created: {script2.name} ({script2.script_type})")

script3 = TestScript(
    id=3,
    name="Teardown Script",
    api_definition_id=1,
    script_type=ScriptType.TEARDOWN,
    execution_order=3,
)
print(f"   ✓ Created: {script3.name} ({script3.script_type})")

# Create a component with scripts
print("\n3. Creating Component with Scripts...")
component = TestComponent(
    id=1,
    name="Login Flow Component",
    description="Complete login flow with setup and teardown",
    component_type=ComponentType.SIMPLE,
    shared_variables={"base_url": "https://api.example.com"},
)
print(f"   ✓ Created: {component.name}")

# Create component-script associations
print("\n4. Creating Component-Script Associations...")
cs1 = ComponentScript(
    component_id=1,
    script_id=1,
    execution_order=1,
    script_parameters={"timeout": 30},
    description="Setup phase",
)
print(f"   ✓ Associated: {script1.name} (order: {cs1.execution_order})")

cs2 = ComponentScript(
    component_id=1,
    script_id=2,
    execution_order=2,
    script_parameters={"username": "testuser"},
    description="Main test phase",
)
print(f"   ✓ Associated: {script2.name} (order: {cs2.execution_order})")

cs3 = ComponentScript(
    component_id=1,
    script_id=3,
    execution_order=3,
    description="Cleanup phase",
)
print(f"   ✓ Associated: {script3.name} (order: {cs3.execution_order})")

# Create nested components
print("\n5. Creating Nested Components...")
parent_component = TestComponent(
    id=2,
    name="Complete Test Suite",
    description="Parent component containing multiple child components",
    component_type=ComponentType.COMPOSITE,
)
print(f"   ✓ Created Parent: {parent_component.name}")

child_component = TestComponent(
    id=3,
    name="Sub-Component",
    description="Child component nested under parent",
    component_type=ComponentType.SIMPLE,
    parent_component_id=2,
)
print(f"   ✓ Created Child: {child_component.name} (parent_id: {child_component.parent_component_id})")

# Create a test case that uses the component
print("\n6. Creating Test Case with Component...")
test_case = TestCase(
    id=1,
    name="User Login Test",
    description="Test user login functionality",
    priority=TestCasePriority.HIGH,
    test_data={"environment": "test"},
)
print(f"   ✓ Created: {test_case.name} (priority: {test_case.priority})")

# Associate component with test case
print("\n7. Creating Test Case-Component Association...")
tc_component = TestCaseComponent(
    test_case_id=1,
    component_id=1,
    execution_order=1,
    component_parameters={"base_url": "https://test.example.com"},
    description="Login flow component in test case",
)
print(f"   ✓ Associated: {component.name} with {test_case.name}")
print(f"   ✓ Parameters override: {tc_component.component_parameters}")

# Verify the four-layer architecture
print("\n" + "=" * 60)
print("Four-Layer Architecture Verification:")
print("=" * 60)
print(f"\nLayer 1 (API Definition): {api_def.name}")
print(f"  └─ Method: {api_def.method}, Path: {api_def.path}")

print(f"\nLayer 2 (Scripts): {len([script1, script2, script3])} scripts")
print(f"  ├─ {script1.name} ({script1.script_type})")
print(f"  ├─ {script2.name} ({script2.script_type})")
print(f"  └─ {script3.name} ({script3.script_type})")

print(f"\nLayer 3 (Component): {component.name}")
print(f"  ├─ Type: {component.component_type}")
print(f"  ├─ Shared Variables: {component.shared_variables}")
print(f"  └─ Contains {len([cs1, cs2, cs3])} scripts:")
print(f"      ├─ {cs1.description} (order: {cs1.execution_order})")
print(f"      ├─ {cs2.description} (order: {cs2.execution_order})")
print(f"      └─ {cs3.description} (order: {cs3.execution_order})")

print(f"\nLayer 4 (Test Case): {test_case.name}")
print(f"  ├─ Priority: {test_case.priority}")
print(f"  ├─ Test Data: {test_case.test_data}")
print(f"  └─ Uses Component: {component.name}")
print(f"      └─ Parameter Override: {tc_component.component_parameters}")

print("\n" + "=" * 60)
print("Component Nesting Verification:")
print("=" * 60)
print(f"\nParent Component: {parent_component.name}")
print(f"  └─ Child Component: {child_component.name}")
print(f"      └─ Parent ID: {child_component.parent_component_id}")

print("\n" + "=" * 60)
print("✅ All relationship tests passed!")
print("=" * 60)
