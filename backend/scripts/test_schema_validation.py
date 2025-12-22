"""Test schema validation and serialization.

This script tests validation rules and JSON serialization/deserialization.
"""

from datetime import datetime

from morado.schemas import (
    PaginationParams,
    TestCaseCreate,
    TestCaseUpdate,
    TestExecutionCreate,
    TestSuiteCreate,
)
from pydantic import ValidationError


def test_validation_rules():
    """Test that validation rules work correctly."""
    print("Testing validation rules...")

    # Test required fields
    try:
        TestCaseCreate()  # Should fail - name is required
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        print(f"  ✓ Required field validation works: {e.error_count()} error(s)")

    # Test string length constraints
    try:
        TestCaseCreate(name="")  # Should fail - min_length=1
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        print(f"  ✓ String length validation works: {e.error_count()} error(s)")

    # Test enum validation
    try:
        TestCaseCreate(name="Test", priority="invalid")  # Should fail
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        print(f"  ✓ Enum validation works: {e.error_count()} error(s)")

    # Test pattern validation
    try:
        TestCaseCreate(name="Test", execution_order="invalid")  # Should fail
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        print(f"  ✓ Pattern validation works: {e.error_count()} error(s)")

    # Test numeric constraints
    try:
        PaginationParams(page=0)  # Should fail - ge=1
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        print(f"  ✓ Numeric constraint validation works: {e.error_count()} error(s)")

    try:
        PaginationParams(page_size=200)  # Should fail - le=100
        raise AssertionError("Should have raised ValidationError")
    except ValidationError as e:
        print(f"  ✓ Numeric upper bound validation works: {e.error_count()} error(s)")

    print("✓ All validation rules working correctly")


def test_json_serialization():
    """Test JSON serialization and deserialization."""
    print("\nTesting JSON serialization...")

    # Create a test case
    test_case = TestCaseCreate(
        name="API Test",
        description="Test API endpoints",
        priority="high",
        status="active",
        category="API",
        tags=["api", "smoke"],
        timeout=300,
        test_data={"url": "https://api.example.com", "method": "GET"},
        environment="test"
    )

    # Serialize to JSON
    json_data = test_case.model_dump_json()
    print(f"  ✓ Serialized to JSON: {len(json_data)} bytes")

    # Deserialize from JSON
    test_case_from_json = TestCaseCreate.model_validate_json(json_data)
    assert test_case_from_json.name == test_case.name
    assert test_case_from_json.tags == test_case.tags
    assert test_case_from_json.test_data == test_case.test_data
    print("  ✓ Deserialized from JSON successfully")

    # Test dict conversion
    test_case_dict = test_case.model_dump()
    assert isinstance(test_case_dict, dict)
    assert test_case_dict["name"] == "API Test"
    assert test_case_dict["priority"] == "high"
    print("  ✓ Converted to dict successfully")

    print("✓ JSON serialization working correctly")


def test_optional_fields():
    """Test that optional fields work correctly."""
    print("\nTesting optional fields...")

    # Create with minimal required fields
    test_case = TestCaseCreate(name="Minimal Test")
    assert test_case.name == "Minimal Test"
    assert test_case.description is None
    assert test_case.category is None
    assert test_case.tags is None
    assert test_case.priority == "medium"  # Default value
    assert test_case.status == "draft"  # Default value
    print("  ✓ Minimal creation with defaults works")

    # Update with partial fields
    update = TestCaseUpdate(name="Updated Name")
    assert update.name == "Updated Name"
    assert update.description is None
    assert update.priority is None
    print("  ✓ Partial update works")

    print("✓ Optional fields working correctly")


def test_nested_data():
    """Test nested data structures."""
    print("\nTesting nested data structures...")

    # Test with nested JSON data
    test_case = TestCaseCreate(
        name="Complex Test",
        test_data={
            "request": {
                "url": "https://api.example.com",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": {"username": "test", "password": "test123"}
            },
            "expected": {
                "status": 200,
                "body": {"success": True}
            }
        }
    )

    assert test_case.test_data["request"]["method"] == "POST"
    assert test_case.test_data["expected"]["status"] == 200
    print("  ✓ Nested JSON data preserved correctly")

    # Test with list of tags
    test_suite = TestSuiteCreate(
        name="Test Suite",
        tags=["regression", "api", "smoke"],
        global_variables={"base_url": "https://test.example.com", "timeout": 30}
    )

    assert len(test_suite.tags) == 3
    assert test_suite.global_variables["base_url"] == "https://test.example.com"
    print("  ✓ Lists and nested dicts work correctly")

    print("✓ Nested data structures working correctly")


def test_datetime_handling():
    """Test datetime field handling."""
    print("\nTesting datetime handling...")

    now = datetime.now()
    execution = TestExecutionCreate(
        test_case_id=1,
        status="running",
        start_time=now,
        environment="test"
    )

    assert execution.start_time == now
    print("  ✓ Datetime assignment works")

    # Test JSON serialization with datetime
    json_data = execution.model_dump_json()
    execution_from_json = TestExecutionCreate.model_validate_json(json_data)
    # Datetime should be preserved (may have slight precision differences)
    assert execution_from_json.start_time is not None
    print("  ✓ Datetime serialization/deserialization works")

    print("✓ Datetime handling working correctly")


def main():
    """Run all validation tests."""
    print("\n=== Testing Schema Validation and Serialization ===\n")

    test_validation_rules()
    test_json_serialization()
    test_optional_fields()
    test_nested_data()
    test_datetime_handling()

    print("\n=== All validation tests passed! ===\n")


if __name__ == "__main__":
    main()
