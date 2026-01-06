"""Verification script for Pydantic schemas.

This script tests that all schemas can be instantiated and validated correctly.
"""

from datetime import datetime

from morado.schemas import (
    ErrorResponse,
    ExecutionResultCreate,
    MessageResponse,
    # Common
    PaginationParams,
    # Test Case
    TestCaseCreate,
    TestCaseResponse,
    TestCaseUpdate,
    # Test Execution
    TestExecutionCreate,
    TestExecutionResponse,
    TestExecutionUpdate,
    # Test Suite
    TestSuiteCreate,
    TestSuiteResponse,
    TestSuiteUpdate,
)


def test_common_schemas():
    """Test common schemas."""
    print("Testing common schemas...")

    # PaginationParams
    pagination = PaginationParams(page=1, page_size=20)
    assert pagination.page == 1
    assert pagination.page_size == 20

    # MessageResponse
    message = MessageResponse(message="Success", data={"id": 1})
    assert message.message == "Success"
    assert message.data == {"id": 1}

    # ErrorResponse
    error = ErrorResponse(
        error_code="TEST_ERROR",
        message="Test error message",
        details={"field": "test"}
    )
    assert error.error_code == "TEST_ERROR"

    print("✓ Common schemas validated")


def test_test_case_schemas():
    """Test test case schemas."""
    print("Testing test case schemas...")

    # TestCaseCreate
    test_case_create = TestCaseCreate(
        name="Test Case 1",
        description="Test description",
        priority="high",
        status="active",
        category="API Testing",
        tags=["api", "smoke"],
        timeout=300,
        environment="test"
    )
    assert test_case_create.name == "Test Case 1"
    assert test_case_create.priority == "high"

    # TestCaseUpdate
    test_case_update = TestCaseUpdate(
        name="Updated Test Case",
        status="deprecated"
    )
    assert test_case_update.name == "Updated Test Case"

    # TestCaseResponse
    test_case_response = TestCaseResponse(
        id=1,
        uuid="550e8400-e29b-41d4-a716-446655440000",
        name="Test Case 1",
        description="Test description",
        priority="high",
        status="active",
        category="API Testing",
        tags=["api", "smoke"],
        preconditions=None,
        postconditions=None,
        execution_order="sequential",
        timeout=300,
        retry_count=0,
        continue_on_failure=False,
        test_data=None,
        environment="test",
        version="1.0.0",
        is_automated=True,
        created_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    assert test_case_response.id == 1
    assert test_case_response.name == "Test Case 1"

    print("✓ Test case schemas validated")


def test_test_suite_schemas():
    """Test test suite schemas."""
    print("Testing test suite schemas...")

    # TestSuiteCreate
    test_suite_create = TestSuiteCreate(
        name="Test Suite 1",
        description="Test suite description",
        execution_order="sequential",
        parallel_execution=False,
        continue_on_failure=True,
        environment="test",
        tags=["regression"],
        version="1.0.0"
    )
    assert test_suite_create.name == "Test Suite 1"
    assert test_suite_create.parallel_execution is False

    # TestSuiteUpdate
    test_suite_update = TestSuiteUpdate(
        name="Updated Test Suite",
        parallel_execution=True
    )
    assert test_suite_update.name == "Updated Test Suite"

    # TestSuiteResponse
    test_suite_response = TestSuiteResponse(
        id=1,
        uuid="550e8400-e29b-41d4-a716-446655440000",
        name="Test Suite 1",
        description="Test suite description",
        execution_order="sequential",
        parallel_execution=False,
        continue_on_failure=True,
        schedule_config=None,
        is_scheduled=False,
        environment="test",
        global_variables=None,
        tags=["regression"],
        version="1.0.0",
        created_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    assert test_suite_response.id == 1
    assert test_suite_response.name == "Test Suite 1"

    print("✓ Test suite schemas validated")


def test_test_execution_schemas():
    """Test test execution schemas."""
    print("Testing test execution schemas...")

    # TestExecutionCreate
    test_execution_create = TestExecutionCreate(
        test_case_id=1,
        status="running",
        environment="test",
        executor="jenkins",
        total_count=10,
        passed_count=8,
        failed_count=2,
        error_count=0,
        skipped_count=0
    )
    assert test_execution_create.test_case_id == 1
    assert test_execution_create.status == "running"

    # TestExecutionUpdate
    test_execution_update = TestExecutionUpdate(
        status="passed",
        passed_count=10,
        failed_count=0
    )
    assert test_execution_update.status == "passed"

    # TestExecutionResponse
    test_execution_response = TestExecutionResponse(
        id=1,
        uuid="550e8400-e29b-41d4-a716-446655440000",
        test_case_id=1,
        test_suite_id=None,
        status="passed",
        start_time=datetime.now(),
        end_time=datetime.now(),
        duration=300.5,
        environment="test",
        executor="jenkins",
        execution_parameters=None,
        total_count=10,
        passed_count=10,
        failed_count=0,
        error_count=0,
        skipped_count=0,
        error_message=None,
        stack_trace=None,
        logs=None,
        created_by=1,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    assert test_execution_response.id == 1
    assert test_execution_response.status == "passed"

    # ExecutionResultCreate
    execution_result_create = ExecutionResultCreate(
        execution_id=1,
        script_id=1,
        status="passed",
        duration=30.5,
        request_data={"url": "https://api.example.com"},
        response_data={"status": 200}
    )
    assert execution_result_create.execution_id == 1
    assert execution_result_create.status == "passed"

    print("✓ Test execution schemas validated")


def main():
    """Run all schema validation tests."""
    print("\n=== Verifying Pydantic Schemas ===\n")

    test_common_schemas()
    test_test_case_schemas()
    test_test_suite_schemas()
    test_test_execution_schemas()

    print("\n=== All schemas validated successfully! ===\n")


if __name__ == "__main__":
    main()
