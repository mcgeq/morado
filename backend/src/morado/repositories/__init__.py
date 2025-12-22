"""Data access layer repositories.

This module provides repository classes for all models in the four-layer
architecture of the Morado test platform.

Layer 1 - API Components:
    - HeaderRepository: Manages HTTP header components
    - BodyRepository: Manages request/response body components
    - ApiDefinitionRepository: Manages API definitions

Layer 2 - Test Scripts:
    - TestScriptRepository: Manages test scripts
    - ScriptParameterRepository: Manages script parameters

Layer 3 - Test Components:
    - TestComponentRepository: Manages test components
    - ComponentScriptRepository: Manages component-script associations

Layer 4 - Test Cases:
    - TestCaseRepository: Manages test cases
    - TestCaseScriptRepository: Manages test case-script associations
    - TestCaseComponentRepository: Manages test case-component associations

Test Suites:
    - TestSuiteRepository: Manages test suites
    - TestSuiteCaseRepository: Manages test suite-case associations

Example:
    >>> from morado.repositories import HeaderRepository, TestScriptRepository
    >>> from morado.core.database import get_db
    >>>
    >>> header_repo = HeaderRepository()
    >>> script_repo = TestScriptRepository()
    >>>
    >>> with get_db() as session:
    ...     header = header_repo.get_by_id(session, 1)
    ...     script = script_repo.get_by_id(session, 1)
"""

from morado.repositories.api_component import (
    ApiDefinitionRepository,
    BodyRepository,
    HeaderRepository,
)
from morado.repositories.base import BaseRepository
from morado.repositories.component import (
    ComponentScriptRepository,
    TestComponentRepository,
)
from morado.repositories.script import ScriptParameterRepository, TestScriptRepository
from morado.repositories.test_case import (
    TestCaseComponentRepository,
    TestCaseRepository,
    TestCaseScriptRepository,
)
from morado.repositories.test_suite import TestSuiteCaseRepository, TestSuiteRepository

__all__ = [
    # Base
    "BaseRepository",
    # Layer 1: API Components
    "HeaderRepository",
    "BodyRepository",
    "ApiDefinitionRepository",
    # Layer 2: Test Scripts
    "TestScriptRepository",
    "ScriptParameterRepository",
    # Layer 3: Test Components
    "TestComponentRepository",
    "ComponentScriptRepository",
    # Layer 4: Test Cases
    "TestCaseRepository",
    "TestCaseScriptRepository",
    "TestCaseComponentRepository",
    # Test Suites
    "TestSuiteRepository",
    "TestSuiteCaseRepository",
]
