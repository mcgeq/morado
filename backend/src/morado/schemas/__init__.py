"""Pydantic schemas for API request/response validation.

This module provides Pydantic models for data validation and serialization
across the API layer.
"""

from morado.schemas.common import (
    ErrorResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
)
from morado.schemas.test_case import (
    TestCaseBase,
    TestCaseComponentBase,
    TestCaseComponentCreate,
    TestCaseCreate,
    TestCaseListResponse,
    TestCaseResponse,
    TestCaseScriptBase,
    TestCaseScriptCreate,
    TestCaseUpdate,
)
from morado.schemas.test_execution import (
    ExecutionResultBase,
    ExecutionResultCreate,
    TestExecutionBase,
    TestExecutionCreate,
    TestExecutionListResponse,
    TestExecutionResponse,
    TestExecutionUpdate,
)
from morado.schemas.test_suite import (
    TestSuiteBase,
    TestSuiteCaseBase,
    TestSuiteCaseCreate,
    TestSuiteCreate,
    TestSuiteListResponse,
    TestSuiteResponse,
    TestSuiteUpdate,
)

__all__ = [
    "ErrorResponse",
    "ExecutionResultBase",
    "ExecutionResultCreate",
    "MessageResponse",
    "PaginatedResponse",
    # Common
    "PaginationParams",
    # Test Case
    "TestCaseBase",
    "TestCaseComponentBase",
    "TestCaseComponentCreate",
    "TestCaseCreate",
    "TestCaseListResponse",
    "TestCaseResponse",
    "TestCaseScriptBase",
    "TestCaseScriptCreate",
    "TestCaseUpdate",
    # Test Execution
    "TestExecutionBase",
    "TestExecutionCreate",
    "TestExecutionListResponse",
    "TestExecutionResponse",
    "TestExecutionUpdate",
    # Test Suite
    "TestSuiteBase",
    "TestSuiteCaseBase",
    "TestSuiteCaseCreate",
    "TestSuiteCreate",
    "TestSuiteListResponse",
    "TestSuiteResponse",
    "TestSuiteUpdate",
]
