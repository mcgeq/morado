"""Verify that the component models can be imported and used correctly."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from morado.models.component import ComponentScript, ComponentType, ExecutionMode, TestComponent

print("✓ Successfully imported TestComponent and ComponentScript")

# Test creating a TestComponent instance
component = TestComponent(
    name="Test Component",
    description="A test component for verification",
    component_type=ComponentType.SIMPLE,
    execution_mode=ExecutionMode.SEQUENTIAL,
    shared_variables={"key": "value"},
    tags=["test", "verification"],
)

print(f"✓ Created TestComponent: {component.name}")
print(f"  - Type: {component.component_type}")
print(f"  - Execution Mode: {component.execution_mode}")
print(f"  - Shared Variables: {component.shared_variables}")
print(f"  - Tags: {component.tags}")

# Test creating a ComponentScript instance
component_script = ComponentScript(
    component_id=1,
    script_id=1,
    execution_order=1,
    is_enabled=True,
    script_parameters={"param1": "value1"},
    description="Test script association",
)

print(f"✓ Created ComponentScript")
print(f"  - Execution Order: {component_script.execution_order}")
print(f"  - Enabled: {component_script.is_enabled}")
print(f"  - Parameters: {component_script.script_parameters}")

# Test nested component
parent = TestComponent(
    name="Parent Component",
    component_type=ComponentType.COMPOSITE,
)

child = TestComponent(
    name="Child Component",
    component_type=ComponentType.SIMPLE,
    parent_component_id=1,  # Would reference parent.id in real usage
)

print(f"✓ Created nested components")
print(f"  - Parent: {parent.name} ({parent.component_type})")
print(f"  - Child: {child.name} (parent_id: {child.parent_component_id})")

print("\n✅ All component model verifications passed!")
