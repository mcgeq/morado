"""Unit tests for Test Script Service layer.

Tests business logic for TestScript and ScriptParameter services.
"""

import pytest
from morado.models.script import ScriptType
from morado.services.api_component import ApiDefinitionService
from morado.services.script import TestScriptService
from sqlalchemy.orm import Session


class TestTestScriptService:
    """Test TestScriptService business logic."""

    @pytest.fixture
    def service(self):
        """Create TestScriptService instance."""
        return TestScriptService()

    @pytest.fixture
    def api_def_service(self):
        """Create ApiDefinitionService instance."""
        return ApiDefinitionService()

    @pytest.fixture
    def sample_api_def(self, api_def_service: ApiDefinitionService, db_session: Session):
        """Create a sample API definition for testing."""
        return api_def_service.create_api_definition(
            db_session,
            name="Test API",
            method="GET",
            path="/api/test"
        )

    def test_create_script_success(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test successful script creation."""
        script = service.create_script(
            db_session,
            name="Login Test",
            api_definition_id=sample_api_def.id,
            script_type=ScriptType.MAIN
        )

        assert script.id is not None
        assert script.name == "Login Test"
        assert script.api_definition_id == sample_api_def.id
        assert script.script_type == ScriptType.MAIN
        assert script.debug_mode is False

    def test_create_script_with_variables_and_assertions(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test creating script with variables and assertions."""
        script = service.create_script(
            db_session,
            name="Complex Test",
            api_definition_id=sample_api_def.id,
            variables={"user": "test_user", "password": "secret"},
            assertions=[
                {"type": "status_code", "expected": 200},
                {"type": "json_path", "path": "$.status", "expected": "success"}
            ],
            validators={"response_time": {"max": 1000}}
        )

        assert script.variables == {"user": "test_user", "password": "secret"}
        assert len(script.assertions) == 2
        assert script.validators == {"response_time": {"max": 1000}}

    def test_create_script_with_pre_post_scripts(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test creating script with pre and post execution scripts."""
        script = service.create_script(
            db_session,
            name="Test with Hooks",
            api_definition_id=sample_api_def.id,
            pre_script="console.log('Before test');",
            post_script="console.log('After test');"
        )

        assert script.pre_script == "console.log('Before test');"
        assert script.post_script == "console.log('After test');"

    def test_get_script_with_relations(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test retrieving script with related API definition."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        retrieved = service.get_script(db_session, script.id, with_relations=True)

        assert retrieved is not None
        assert retrieved.api_definition is not None
        assert retrieved.api_definition.name == "Test API"

    def test_list_scripts_by_api_definition(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test listing scripts filtered by API definition."""
        service.create_script(
            db_session,
            name="Script 1",
            api_definition_id=sample_api_def.id
        )
        service.create_script(
            db_session,
            name="Script 2",
            api_definition_id=sample_api_def.id
        )

        scripts = service.list_scripts(db_session, api_definition_id=sample_api_def.id)
        assert len(scripts) == 2

    def test_list_scripts_by_type(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test listing scripts filtered by type."""
        service.create_script(
            db_session,
            name="Setup Script",
            api_definition_id=sample_api_def.id,
            script_type=ScriptType.SETUP
        )
        service.create_script(
            db_session,
            name="Main Script",
            api_definition_id=sample_api_def.id,
            script_type=ScriptType.MAIN
        )

        setup_scripts = service.list_scripts(db_session, script_type=ScriptType.SETUP)
        assert len(setup_scripts) == 1
        assert setup_scripts[0].name == "Setup Script"

    def test_search_scripts_by_name(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test searching scripts by name."""
        service.create_script(
            db_session,
            name="Login Test",
            api_definition_id=sample_api_def.id
        )
        service.create_script(
            db_session,
            name="Logout Test",
            api_definition_id=sample_api_def.id
        )

        results = service.search_scripts(db_session, "Login")
        assert len(results) == 1
        assert results[0].name == "Login Test"

    def test_update_script(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test updating script."""
        script = service.create_script(
            db_session,
            name="Original Script",
            api_definition_id=sample_api_def.id
        )

        updated = service.update_script(
            db_session,
            script.id,
            name="Updated Script",
            retry_count=3
        )

        assert updated is not None
        assert updated.name == "Updated Script"
        assert updated.retry_count == 3

    def test_delete_script(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test deleting script."""
        script = service.create_script(
            db_session,
            name="To Delete",
            api_definition_id=sample_api_def.id
        )

        result = service.delete_script(db_session, script.id)
        assert result is True

        retrieved = service.get_script(db_session, script.id)
        assert retrieved is None

    def test_add_parameter_to_script(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test adding parameter to script."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        parameter = service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string",
            default_value="test_user",
            is_required=True
        )

        assert parameter.id is not None
        assert parameter.name == "username"
        assert parameter.parameter_type == "string"
        assert parameter.default_value == "test_user"
        assert parameter.is_required is True

    def test_get_script_parameters(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test retrieving script parameters."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string",
            is_required=True
        )
        service.add_parameter(
            db_session,
            script_id=script.id,
            name="timeout",
            parameter_type="integer",
            is_required=False
        )

        all_params = service.get_script_parameters(db_session, script.id)
        assert len(all_params) == 2

        required_params = service.get_script_parameters(
            db_session, script.id, required_only=True
        )
        assert len(required_params) == 1
        assert required_params[0].name == "username"

    def test_update_parameter(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test updating script parameter."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        parameter = service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string"
        )

        updated = service.update_parameter(
            db_session,
            parameter.id,
            default_value="new_default",
            is_required=True
        )

        assert updated is not None
        assert updated.default_value == "new_default"
        assert updated.is_required is True

    def test_delete_parameter(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test deleting script parameter."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        parameter = service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string"
        )

        result = service.delete_parameter(db_session, parameter.id)
        assert result is True

    def test_enable_disable_debug_mode(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test enabling and disabling debug mode."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        enabled = service.enable_debug_mode(db_session, script.id)
        assert enabled is not None
        assert enabled.debug_mode is True

        disabled = service.disable_debug_mode(db_session, script.id)
        assert disabled is not None
        assert disabled.debug_mode is False

    def test_validate_script_parameters_success(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test successful parameter validation."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string",
            is_required=True
        )
        service.add_parameter(
            db_session,
            script_id=script.id,
            name="timeout",
            parameter_type="integer",
            is_required=False
        )

        is_valid, errors = service.validate_script_parameters(
            db_session,
            script.id,
            {"username": "test_user", "timeout": 30}
        )

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_script_parameters_missing_required(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test parameter validation with missing required parameter."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id
        )

        service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string",
            is_required=True
        )

        is_valid, errors = service.validate_script_parameters(
            db_session,
            script.id,
            {}
        )

        assert is_valid is False
        assert len(errors) > 0
        assert "username" in errors[0]

    def test_get_script_execution_config(
        self,
        service: TestScriptService,
        sample_api_def,
        db_session: Session
    ):
        """Test getting complete script execution configuration."""
        script = service.create_script(
            db_session,
            name="Test Script",
            api_definition_id=sample_api_def.id,
            variables={"user": "test"},
            assertions=[{"type": "status_code", "expected": 200}]
        )

        service.add_parameter(
            db_session,
            script_id=script.id,
            name="username",
            parameter_type="string",
            default_value="test_user"
        )

        config = service.get_script_execution_config(db_session, script.id)

        assert config is not None
        assert config['script']['name'] == "Test Script"
        assert config['script']['variables'] == {"user": "test"}
        assert config['api_definition']['name'] == "Test API"
        assert len(config['parameters']) == 1
        assert config['parameters'][0]['name'] == "username"
