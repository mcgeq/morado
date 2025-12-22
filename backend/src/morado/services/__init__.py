"""Service layer for business logic.

This module exports all service classes for managing the four-layer architecture
and test execution.
"""

from morado.services.api_component import (
    ApiDefinitionService,
    BodyService,
    HeaderService,
)
from morado.services.component import TestComponentService
from morado.services.execution_context import (
    ComponentExecutionContext,
    ExecutionContext,
    ScriptExecutionContext,
    TestCaseExecutionContext,
    VariableResolver,
)
from morado.services.execution_engine import (
    ExecutionEngine,
    ExecutionResult,
    ExecutionStatus,
    execute_component,
    execute_script,
    execute_test_case,
)
from morado.services.report import ReportService
from morado.services.script import TestScriptService
from morado.services.test_case import TestCaseService
from morado.services.test_execution import TestExecutionService
from morado.services.test_suite import TestSuiteService

__all__ = [
    'ApiDefinitionService',
    'BodyService',
    'ComponentExecutionContext',
    # Execution Context
    'ExecutionContext',
    # Execution Engine
    'ExecutionEngine',
    'ExecutionResult',
    'ExecutionStatus',
    # Layer 1: API Components
    'HeaderService',
    # Reports
    'ReportService',
    'ScriptExecutionContext',
    'TestCaseExecutionContext',
    # Layer 4: Test Cases
    'TestCaseService',
    # Layer 3: Components
    'TestComponentService',
    # Test Execution
    'TestExecutionService',
    # Layer 2: Scripts
    'TestScriptService',
    # Test Suites
    'TestSuiteService',
    'VariableResolver',
    'execute_component',
    'execute_script',
    'execute_test_case',
]
