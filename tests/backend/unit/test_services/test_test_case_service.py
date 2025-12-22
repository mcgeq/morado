"""Unit tests for Test Case Service layer.

Tests business logic for TestCase management including script and component references.
"""

import pytest
from morado.models.test_case import TestCasePriority, TestCaseStatus
from morado.services.api_component import ApiDefinitionService
from morado.services.component import TestComponentService
from morado.services.script import TestScriptService
from morado.services.test_case import TestCaseService
from sqlalchemy.orm import Session


class TestTestCaseService:
    """Test TestCaseService business logic."""

    @pytest.fixture
    def service(self):
        """Create TestCaseService instance."""
        return TestCaseService()

    @pytest.fixture
    def script_service(self):
        """Create TestScriptService instance."""
        return TestScriptService()

    @pytest.fixture
    def component_service(self):
        """Create TestComponentService instance."""
        return TestComponentService()

    @pytest.fixture
    def api_def_service(self):
        """Create ApiDefinitionService instance."""
        return ApiDefinitionService()

    @pytest.fixture
    def sample_script(
        self,
        script_service: TestScriptService,
        api_def_service: ApiDefinitionService,
        db_session: Session
    ):
        """Create a sample script for testing."""
        api_def = api_def_service.create_api_definition(
            db_session,
            name="Test API",
            method="GET",
            path="/api/test"
        )
        return script_service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=api_def.id
        )

    @pytest.fixture
    def sample_component(
        self, component_service: TestComponentService, db_session: Session
    ):
        """Create a sample component for testing."""
        return component_service.create_component(
            db_session,
            name="Test Component"
        )

    def test_create_test_case_success(
        self, service: TestCaseService, db_session: Session
    ):
        """Test successful test case creation."""
        test_case = service.create_test_case(
            db_session,
            name="User Registration Flow",
            priority=TestCasePriority.HIGH,
            status=TestCaseStatus.ACTIVE
        )

        assert test_case.id is not None
        assert test_case.name == "User Registration Flow"
        assert test_case.priority == TestCasePriority.HIGH
        assert test_case.status == TestCaseStatus.ACTIVE
        assert test_case.is_automated is True

    def test_create_test_case_with_test_data(
        self, service: TestCaseService, db_session: Session
    ):
        """Test creating test case with test data."""
        test_case = service.create_test_case(
            db_session,
            name="Login Test",
            test_data={
                "username": "test_user",
                "password": "secret",
                "expected_role": "admin"
            }
        )

        assert test_case.test_data == {
            "username": "test_user",
            "password": "secret",
            "expected_role": "admin"
        }

    def test_create_test_case_with_preconditions_postconditions(
        self, service: TestCaseService, db_session: Session
    ):
        """Test creating test case with pre/post conditions."""
        test_case = service.create_test_case(
            db_session,
            name="Order Test",
            preconditions="User must be logged in",
            postconditions="Order should be created in database"
        )

        assert test_case.preconditions == "User must be logged in"
        assert test_case.postconditions == "Order should be created in database"

    def test_get_test_case_with_scripts(
        self,
        service: TestCaseService,
        sample_script,
        db_session: Session
    ):
        """Test retrieving test case with associated scripts."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=sample_script.id
        )

        retrieved = service.get_test_case(
            db_session,
            test_case.id,
            load_scripts=True
        )

        assert retrieved is not None
        assert len(retrieved.test_case_scripts) == 1

    def test_get_test_case_with_components(
        self,
        service: TestCaseService,
        sample_component,
        db_session: Session
    ):
        """Test retrieving test case with associated components."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        service.add_component_to_test_case(
            db_session,
            test_case_id=test_case.id,
            component_id=sample_component.id
        )

        retrieved = service.get_test_case(
            db_session,
            test_case.id,
            load_components=True
        )

        assert retrieved is not None
        assert len(retrieved.test_case_components) == 1

    def test_list_test_cases_by_status(
        self, service: TestCaseService, db_session: Session
    ):
        """Test listing test cases filtered by status."""
        service.create_test_case(
            db_session,
            name="Active Test",
            status=TestCaseStatus.ACTIVE
        )
        service.create_test_case(
            db_session,
            name="Draft Test",
            status=TestCaseStatus.DRAFT
        )

        active_cases = service.list_test_cases(
            db_session,
            status=TestCaseStatus.ACTIVE
        )
        assert len(active_cases) == 1
        assert active_cases[0].name == "Active Test"

    def test_list_test_cases_by_priority(
        self, service: TestCaseService, db_session: Session
    ):
        """Test listing test cases filtered by priority."""
        service.create_test_case(
            db_session,
            name="High Priority",
            priority=TestCasePriority.HIGH
        )
        service.create_test_case(
            db_session,
            name="Low Priority",
            priority=TestCasePriority.LOW
        )

        high_priority_cases = service.list_test_cases(
            db_session,
            priority=TestCasePriority.HIGH
        )
        assert len(high_priority_cases) == 1
        assert high_priority_cases[0].name == "High Priority"

    def test_list_automated_test_cases(
        self, service: TestCaseService, db_session: Session
    ):
        """Test listing only automated test cases."""
        service.create_test_case(
            db_session,
            name="Automated Test",
            is_automated=True
        )
        service.create_test_case(
            db_session,
            name="Manual Test",
            is_automated=False
        )

        automated_cases = service.list_test_cases(
            db_session,
            automated_only=True
        )
        assert len(automated_cases) == 1
        assert automated_cases[0].name == "Automated Test"

    def test_search_test_cases_by_name(
        self, service: TestCaseService, db_session: Session
    ):
        """Test searching test cases by name."""
        service.create_test_case(
            db_session,
            name="Login Test"
        )
        service.create_test_case(
            db_session,
            name="Logout Test"
        )

        results = service.search_test_cases(db_session, "Login")
        assert len(results) == 1
        assert results[0].name == "Login Test"

    def test_update_test_case(
        self, service: TestCaseService, db_session: Session
    ):
        """Test updating test case."""
        test_case = service.create_test_case(
            db_session,
            name="Original Name",
            priority=TestCasePriority.LOW
        )

        updated = service.update_test_case(
            db_session,
            test_case.id,
            name="Updated Name",
            priority=TestCasePriority.HIGH
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.priority == TestCasePriority.HIGH

    def test_delete_test_case(
        self, service: TestCaseService, db_session: Session
    ):
        """Test deleting test case."""
        test_case = service.create_test_case(
            db_session,
            name="To Delete"
        )

        result = service.delete_test_case(db_session, test_case.id)
        assert result is True

        retrieved = service.get_test_case(db_session, test_case.id)
        assert retrieved is None

    def test_add_script_to_test_case(
        self,
        service: TestCaseService,
        sample_script,
        db_session: Session
    ):
        """Test adding script to test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        test_case_script = service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=sample_script.id,
            execution_order=1,
            script_parameters={"username": "test_user"}
        )

        assert test_case_script.id is not None
        assert test_case_script.test_case_id == test_case.id
        assert test_case_script.script_id == sample_script.id
        assert test_case_script.execution_order == 1
        assert test_case_script.script_parameters == {"username": "test_user"}

    def test_add_component_to_test_case(
        self,
        service: TestCaseService,
        sample_component,
        db_session: Session
    ):
        """Test adding component to test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        test_case_component = service.add_component_to_test_case(
            db_session,
            test_case_id=test_case.id,
            component_id=sample_component.id,
            execution_order=1,
            component_parameters={"env": "test"}
        )

        assert test_case_component.id is not None
        assert test_case_component.test_case_id == test_case.id
        assert test_case_component.component_id == sample_component.id
        assert test_case_component.execution_order == 1
        assert test_case_component.component_parameters == {"env": "test"}

    def test_get_test_case_scripts_ordered(
        self,
        service: TestCaseService,
        script_service: TestScriptService,
        api_def_service: ApiDefinitionService,
        db_session: Session
    ):
        """Test retrieving test case scripts in execution order."""
        api_def = api_def_service.create_api_definition(
            db_session,
            name="Test API",
            method="GET",
            path="/api/test"
        )

        script1 = script_service.create_script(
            db_session,
            name="Script 1",
            api_definition_id=api_def.id
        )
        script2 = script_service.create_script(
            db_session,
            name="Script 2",
            api_definition_id=api_def.id
        )

        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        # Add scripts in non-sequential order
        service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=script2.id,
            execution_order=2
        )
        service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=script1.id,
            execution_order=1
        )

        scripts = service.get_test_case_scripts(db_session, test_case.id)
        assert len(scripts) == 2
        assert scripts[0].script.name == "Script 1"
        assert scripts[1].script.name == "Script 2"

    def test_update_test_case_script(
        self,
        service: TestCaseService,
        sample_script,
        db_session: Session
    ):
        """Test updating test case-script association."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        test_case_script = service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=sample_script.id
        )

        updated = service.update_test_case_script(
            db_session,
            test_case_script.id,
            execution_order=5,
            is_enabled=False
        )

        assert updated is not None
        assert updated.execution_order == 5
        assert updated.is_enabled is False

    def test_update_test_case_component(
        self,
        service: TestCaseService,
        sample_component,
        db_session: Session
    ):
        """Test updating test case-component association."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        test_case_component = service.add_component_to_test_case(
            db_session,
            test_case_id=test_case.id,
            component_id=sample_component.id
        )

        updated = service.update_test_case_component(
            db_session,
            test_case_component.id,
            execution_order=3,
            is_enabled=False
        )

        assert updated is not None
        assert updated.execution_order == 3
        assert updated.is_enabled is False

    def test_remove_script_from_test_case(
        self,
        service: TestCaseService,
        sample_script,
        db_session: Session
    ):
        """Test removing script from test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        test_case_script = service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=sample_script.id
        )

        result = service.remove_script_from_test_case(
            db_session,
            test_case_script.id
        )
        assert result is True

    def test_remove_component_from_test_case(
        self,
        service: TestCaseService,
        sample_component,
        db_session: Session
    ):
        """Test removing component from test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case"
        )

        test_case_component = service.add_component_to_test_case(
            db_session,
            test_case_id=test_case.id,
            component_id=sample_component.id
        )

        result = service.remove_component_from_test_case(
            db_session,
            test_case_component.id
        )
        assert result is True

    def test_activate_test_case(
        self, service: TestCaseService, db_session: Session
    ):
        """Test activating test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case",
            status=TestCaseStatus.DRAFT
        )

        activated = service.activate_test_case(db_session, test_case.id)
        assert activated is not None
        assert activated.status == TestCaseStatus.ACTIVE

    def test_archive_test_case(
        self, service: TestCaseService, db_session: Session
    ):
        """Test archiving test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case",
            status=TestCaseStatus.ACTIVE
        )

        archived = service.archive_test_case(db_session, test_case.id)
        assert archived is not None
        assert archived.status == TestCaseStatus.ARCHIVED

    def test_deprecate_test_case(
        self, service: TestCaseService, db_session: Session
    ):
        """Test deprecating test case."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case",
            status=TestCaseStatus.ACTIVE
        )

        deprecated = service.deprecate_test_case(db_session, test_case.id)
        assert deprecated is not None
        assert deprecated.status == TestCaseStatus.DEPRECATED

    def test_get_test_case_execution_plan(
        self,
        service: TestCaseService,
        sample_script,
        sample_component,
        db_session: Session
    ):
        """Test getting complete test case execution plan."""
        test_case = service.create_test_case(
            db_session,
            name="Test Case",
            test_data={"env": "test"}
        )

        service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=sample_script.id,
            execution_order=1
        )
        service.add_component_to_test_case(
            db_session,
            test_case_id=test_case.id,
            component_id=sample_component.id,
            execution_order=2
        )

        plan = service.get_test_case_execution_plan(db_session, test_case.id)

        assert plan is not None
        assert plan['test_case']['name'] == "Test Case"
        assert plan['test_case']['test_data'] == {"env": "test"}
        assert len(plan['execution_items']) == 2
        assert plan['execution_items'][0]['type'] == 'script'
        assert plan['execution_items'][1]['type'] == 'component'

    def test_clone_test_case(
        self,
        service: TestCaseService,
        sample_script,
        sample_component,
        db_session: Session
    ):
        """Test cloning test case."""
        original = service.create_test_case(
            db_session,
            name="Original Test Case",
            priority=TestCasePriority.HIGH,
            test_data={"env": "test"}
        )

        service.add_script_to_test_case(
            db_session,
            test_case_id=original.id,
            script_id=sample_script.id
        )
        service.add_component_to_test_case(
            db_session,
            test_case_id=original.id,
            component_id=sample_component.id
        )

        cloned = service.clone_test_case(
            db_session,
            original.id,
            "Cloned Test Case"
        )

        assert cloned is not None
        assert cloned.name == "Cloned Test Case"
        assert cloned.priority == TestCasePriority.HIGH
        assert cloned.test_data == {"env": "test"}
        assert cloned.status == TestCaseStatus.DRAFT
        assert len(cloned.test_case_scripts) == 1
        assert len(cloned.test_case_components) == 1

    def test_test_case_with_mixed_scripts_and_components(
        self,
        service: TestCaseService,
        script_service: TestScriptService,
        component_service: TestComponentService,
        api_def_service: ApiDefinitionService,
        db_session: Session
    ):
        """Test test case with both scripts and components in execution order."""
        api_def = api_def_service.create_api_definition(
            db_session,
            name="Test API",
            method="GET",
            path="/api/test"
        )

        script1 = script_service.create_script(
            db_session,
            name="Setup Script",
            api_definition_id=api_def.id
        )
        component1 = component_service.create_component(
            db_session,
            name="Main Component"
        )
        script2 = script_service.create_script(
            db_session,
            name="Teardown Script",
            api_definition_id=api_def.id
        )

        test_case = service.create_test_case(
            db_session,
            name="Complex Test Case"
        )

        # Add in specific order: script -> component -> script
        service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=script1.id,
            execution_order=1
        )
        service.add_component_to_test_case(
            db_session,
            test_case_id=test_case.id,
            component_id=component1.id,
            execution_order=2
        )
        service.add_script_to_test_case(
            db_session,
            test_case_id=test_case.id,
            script_id=script2.id,
            execution_order=3
        )

        plan = service.get_test_case_execution_plan(db_session, test_case.id)

        assert len(plan['execution_items']) == 3
        assert plan['execution_items'][0]['type'] == 'script'
        assert plan['execution_items'][0]['name'] == "Setup Script"
        assert plan['execution_items'][1]['type'] == 'component'
        assert plan['execution_items'][1]['name'] == "Main Component"
        assert plan['execution_items'][2]['type'] == 'script'
        assert plan['execution_items'][2]['name'] == "Teardown Script"
