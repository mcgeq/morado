"""Verification script for Layer 4: Test Case Model

This script verifies that the TestCase model and its associations
(TestCaseScript and TestCaseComponent) are correctly implemented.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.models import (
    TestCase,
    TestCaseComponent,
    TestCaseScript,
    TestComponent,
    TestScript,
)


def verify_test_case_model():
    """Verify TestCase model structure and relationships."""
    print("=" * 80)
    print("Verifying Layer 4: Test Case Model")
    print("=" * 80)

    # 1. Verify TestCase model attributes
    print("\n1. Verifying TestCase model attributes...")
    test_case_attrs = [
        "id",
        "uuid",
        "name",
        "description",
        "priority",
        "status",
        "category",
        "tags",
        "preconditions",
        "postconditions",
        "execution_order",
        "timeout",
        "retry_count",
        "continue_on_failure",
        "test_data",
        "environment",
        "version",
        "is_automated",
        "created_by",
        "created_at",
        "updated_at",
    ]

    for attr in test_case_attrs:
        if not hasattr(TestCase, attr):
            print(f"   ❌ Missing attribute: {attr}")
            return False
        print(f"   ✓ {attr}")

    # 2. Verify TestCase relationships
    print("\n2. Verifying TestCase relationships...")
    test_case_relationships = [
        "creator",
        "test_case_scripts",
        "test_case_components",
        "test_suite_cases",
        "executions",
    ]

    for rel in test_case_relationships:
        if not hasattr(TestCase, rel):
            print(f"   ❌ Missing relationship: {rel}")
            return False
        print(f"   ✓ {rel}")

    # 3. Verify TestCaseScript association table
    print("\n3. Verifying TestCaseScript association table...")
    test_case_script_attrs = [
        "id",
        "test_case_id",
        "script_id",
        "execution_order",
        "is_enabled",
        "script_parameters",
        "description",
        "created_at",
        "updated_at",
    ]

    for attr in test_case_script_attrs:
        if not hasattr(TestCaseScript, attr):
            print(f"   ❌ Missing attribute: {attr}")
            return False
        print(f"   ✓ {attr}")

    # 4. Verify TestCaseScript relationships
    print("\n4. Verifying TestCaseScript relationships...")
    test_case_script_relationships = ["test_case", "script"]

    for rel in test_case_script_relationships:
        if not hasattr(TestCaseScript, rel):
            print(f"   ❌ Missing relationship: {rel}")
            return False
        print(f"   ✓ {rel}")

    # 5. Verify TestCaseComponent association table
    print("\n5. Verifying TestCaseComponent association table...")
    test_case_component_attrs = [
        "id",
        "test_case_id",
        "component_id",
        "execution_order",
        "is_enabled",
        "component_parameters",
        "description",
        "created_at",
        "updated_at",
    ]

    for attr in test_case_component_attrs:
        if not hasattr(TestCaseComponent, attr):
            print(f"   ❌ Missing attribute: {attr}")
            return False
        print(f"   ✓ {attr}")

    # 6. Verify TestCaseComponent relationships
    print("\n6. Verifying TestCaseComponent relationships...")
    test_case_component_relationships = ["test_case", "component"]

    for rel in test_case_component_relationships:
        if not hasattr(TestCaseComponent, rel):
            print(f"   ❌ Missing relationship: {rel}")
            return False
        print(f"   ✓ {rel}")

    # 7. Verify enums
    print("\n7. Verifying TestCase enums...")
    from morado.models.test_case import TestCasePriority, TestCaseStatus

    priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    for priority in priorities:
        if not hasattr(TestCasePriority, priority):
            print(f"   ❌ Missing priority: {priority}")
            return False
        print(f"   ✓ TestCasePriority.{priority}")

    statuses = ["DRAFT", "ACTIVE", "DEPRECATED", "ARCHIVED"]
    for status in statuses:
        if not hasattr(TestCaseStatus, status):
            print(f"   ❌ Missing status: {status}")
            return False
        print(f"   ✓ TestCaseStatus.{status}")

    # 8. Verify table names
    print("\n8. Verifying table names...")
    if TestCase.__tablename__ != "test_cases":
        print(f"   ❌ Wrong table name: {TestCase.__tablename__}")
        return False
    print(f"   ✓ TestCase table: {TestCase.__tablename__}")

    if TestCaseScript.__tablename__ != "test_case_scripts":
        print(f"   ❌ Wrong table name: {TestCaseScript.__tablename__}")
        return False
    print(f"   ✓ TestCaseScript table: {TestCaseScript.__tablename__}")

    if TestCaseComponent.__tablename__ != "test_case_components":
        print(f"   ❌ Wrong table name: {TestCaseComponent.__tablename__}")
        return False
    print(f"   ✓ TestCaseComponent table: {TestCaseComponent.__tablename__}")

    # 9. Verify cascade behavior
    print("\n9. Verifying cascade behavior...")
    # Check that relationships have proper cascade settings
    test_case_scripts_rel = TestCase.test_case_scripts.property
    if "delete-orphan" not in str(test_case_scripts_rel.cascade):
        print("   ❌ test_case_scripts missing delete-orphan cascade")
        return False
    print("   ✓ test_case_scripts has proper cascade")

    test_case_components_rel = TestCase.test_case_components.property
    if "delete-orphan" not in str(test_case_components_rel.cascade):
        print("   ❌ test_case_components missing delete-orphan cascade")
        return False
    print("   ✓ test_case_components has proper cascade")

    print("\n" + "=" * 80)
    print("✅ All verifications passed!")
    print("=" * 80)
    return True


def verify_parameter_override_support():
    """Verify that parameter override is supported in associations."""
    print("\n" + "=" * 80)
    print("Verifying Parameter Override Support")
    print("=" * 80)

    # Check TestCaseScript has script_parameters field
    print("\n1. Checking TestCaseScript parameter override...")
    if not hasattr(TestCaseScript, "script_parameters"):
        print("   ❌ TestCaseScript missing script_parameters field")
        return False
    print("   ✓ TestCaseScript.script_parameters exists")

    # Check TestCaseComponent has component_parameters field
    print("\n2. Checking TestCaseComponent parameter override...")
    if not hasattr(TestCaseComponent, "component_parameters"):
        print("   ❌ TestCaseComponent missing component_parameters field")
        return False
    print("   ✓ TestCaseComponent.component_parameters exists")

    print("\n✅ Parameter override support verified!")
    return True


def verify_execution_order_support():
    """Verify that execution order is supported in associations."""
    print("\n" + "=" * 80)
    print("Verifying Execution Order Support")
    print("=" * 80)

    # Check TestCaseScript has execution_order field
    print("\n1. Checking TestCaseScript execution order...")
    if not hasattr(TestCaseScript, "execution_order"):
        print("   ❌ TestCaseScript missing execution_order field")
        return False
    print("   ✓ TestCaseScript.execution_order exists")

    # Check TestCaseComponent has execution_order field
    print("\n2. Checking TestCaseComponent execution order...")
    if not hasattr(TestCaseComponent, "execution_order"):
        print("   ❌ TestCaseComponent missing execution_order field")
        return False
    print("   ✓ TestCaseComponent.execution_order exists")

    # Check that relationships are ordered by execution_order
    print("\n3. Checking relationship ordering...")
    test_case_scripts_rel = TestCase.test_case_scripts.property
    if "execution_order" not in str(test_case_scripts_rel.order_by):
        print("   ❌ test_case_scripts not ordered by execution_order")
        return False
    print("   ✓ test_case_scripts ordered by execution_order")

    test_case_components_rel = TestCase.test_case_components.property
    if "execution_order" not in str(test_case_components_rel.order_by):
        print("   ❌ test_case_components not ordered by execution_order")
        return False
    print("   ✓ test_case_components ordered by execution_order")

    print("\n✅ Execution order support verified!")
    return True


def main():
    """Run all verification checks."""
    try:
        success = True

        # Run all verifications
        success = verify_test_case_model() and success
        success = verify_parameter_override_support() and success
        success = verify_execution_order_support() and success

        if success:
            print("\n" + "=" * 80)
            print("🎉 ALL VERIFICATIONS PASSED!")
            print("=" * 80)
            print("\nLayer 4 Test Case Model is correctly implemented with:")
            print("  ✓ TestCase model with all required attributes")
            print("  ✓ TestCaseScript association table")
            print("  ✓ TestCaseComponent association table")
            print("  ✓ Support for referencing scripts")
            print("  ✓ Support for referencing components")
            print("  ✓ Execution order configuration")
            print("  ✓ Parameter override support")
            print("  ✓ Proper relationships and cascade behavior")
            return 0
        else:
            print("\n❌ Some verifications failed!")
            return 1

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
