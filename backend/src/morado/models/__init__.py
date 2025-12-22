"""Morado Models - Database Models

This module provides SQLAlchemy ORM models for the Morado test platform.

Models are organized in a layered architecture:
- Layer 1: API Definition (Header, Body, ApiDefinition)
- Layer 2: Script (TestScript)
- Layer 3: Component (TestComponent - composite of scripts)
- Layer 4: Test Case (TestCase - uses scripts and components)

Example:
    >>> from morado.models import ApiDefinition, TestScript, TestCase
    >>>
    >>> # Create an API definition
    >>> api = ApiDefinition(name="Get User", method="GET", path="/api/users/{id}")
    >>>
    >>> # Create a test script
    >>> script = TestScript(name="Test Get User", api_definition=api)
    >>>
    >>> # Create a test case
    >>> test_case = TestCase(name="User API Test", scripts=[script])
"""

from morado.models.api_component import ApiDefinition, Body, Header
from morado.models.base import Base, TimestampMixin, UUIDMixin
from morado.models.component import ComponentScript, TestComponent
from morado.models.script import ScriptParameter, TestScript
from morado.models.test_case import TestCase, TestCaseComponent, TestCaseScript
from morado.models.test_execution import ExecutionResult, TestExecution
from morado.models.test_suite import TestSuite, TestSuiteCase
from morado.models.user import User, UserRole

__all__ = [
    "ApiDefinition",
    # Base classes
    "Base",
    "Body",
    "ComponentScript",
    "ExecutionResult",
    # Layer 1: API Components
    "Header",
    "ScriptParameter",
    # Layer 4: Test Cases
    "TestCase",
    "TestCaseComponent",
    "TestCaseScript",
    # Layer 3: Components
    "TestComponent",
    # Execution
    "TestExecution",
    # Layer 2: Scripts
    "TestScript",
    # Test Suite
    "TestSuite",
    "TestSuiteCase",
    "TimestampMixin",
    "UUIDMixin",
    # User
    "User",
    "UserRole",
]
