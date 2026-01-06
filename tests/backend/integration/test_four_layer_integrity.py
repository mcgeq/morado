"""Test data integrity of the four-layer architecture.

This test module verifies:
1. Header and Body independence
2. ApiDefinition's two combination methods
3. Script references to API definitions
4. Component nesting relationships
5. Test case references to scripts and components
6. Cascade delete and update rules
"""

import pytest
from sqlalchemy import select

from morado.models.api_component import (
    ApiDefinition,
    Body,
    BodyType,
    Header,
    HeaderScope,
    HttpMethod,
)
from morado.models.component import (
    ComponentScript,
    ComponentType,
    ExecutionMode,
    TestComponent,
)
from morado.models.script import ParameterType, ScriptParameter, ScriptType, TestScript
from morado.models.test_case import (
    TestCase,
    TestCaseComponent,
    TestCasePriority,
    TestCaseScript,
    TestCaseStatus,
)
from morado.models.user import User, UserRole


@pytest.fixture
def sample_user(session):
    """Create a sample user for testing."""
    user = User(
        uuid="test-user-uuid-001",
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(user)
    session.flush()
    return user


@pytest.fixture
def sample_headers(session, sample_user):
    """Create sample Header components."""
    headers = [
        Header(
            uuid="header-uuid-001",
            name="Auth Header",
            description="Authentication header",
            headers={"Authorization": "Bearer ${token}"},
            scope=HeaderScope.GLOBAL,
            is_active=True,
            created_by=sample_user.id,
        ),
        Header(
            uuid="header-uuid-002",
            name="JSON Content-Type",
            description="JSON content type header",
            headers={"Content-Type": "application/json"},
            scope=HeaderScope.GLOBAL,
            is_active=True,
            created_by=sample_user.id,
        ),
    ]
    for header in headers:
        session.add(header)
    session.flush()
    return headers


@pytest.fixture
def sample_bodies(session, sample_user):
    """Create sample Body components."""
    bodies = [
        Body(
            uuid="body-uuid-001",
            name="User Body",
            description="User information body",
            body_type=BodyType.BOTH,
            content_type="application/json",
            body_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            example_data={"name": "Test User"},
            scope=HeaderScope.GLOBAL,
            is_active=True,
            created_by=sample_user.id,
        ),
        Body(
            uuid="body-uuid-002",
            name="Login Body",
            description="Login request body",
            body_type=BodyType.REQUEST,
            content_type="application/json",
            body_schema={
                "type": "object",
                "properties": {"username": {"type": "string"}},
            },
            is_active=True,
            created_by=sample_user.id,
        ),
    ]
    for body in bodies:
        session.add(body)
    session.flush()
    return bodies


@pytest.fixture
def sample_api_definitions(session, sample_user, sample_headers, sample_bodies):
    """Create sample API Definitions with both combination methods."""
    api_defs = [
        # Method 1: Header + Body reference
        ApiDefinition(
            uuid="api-uuid-001",
            name="Get User",
            description="Get user by ID",
            method=HttpMethod.GET,
            path="/api/users/{id}",
            header_id=sample_headers[0].id,
            response_body_id=sample_bodies[0].id,
            is_active=True,
            created_by=sample_user.id,
        ),
        # Method 2: Header + Inline Body
        ApiDefinition(
            uuid="api-uuid-002",
            name="Create User",
            description="Create a new user",
            method=HttpMethod.POST,
            path="/api/users",
            header_id=sample_headers[1].id,
            inline_request_body={"name": "New User", "email": "new@example.com"},
            inline_response_body={"id": 1, "name": "New User"},
            is_active=True,
            created_by=sample_user.id,
        ),
        # Method 1: Header + Request Body reference
        ApiDefinition(
            uuid="api-uuid-003",
            name="Login",
            description="User login",
            method=HttpMethod.POST,
            path="/api/auth/login",
            header_id=sample_headers[1].id,
            request_body_id=sample_bodies[1].id,
            inline_response_body={"token": "jwt_token"},
            is_active=True,
            created_by=sample_user.id,
        ),
    ]
    for api_def in api_defs:
        session.add(api_def)
    session.flush()
    return api_defs


@pytest.fixture
def sample_scripts(session, sample_user, sample_api_definitions):
    """Create sample Test Scripts."""
    scripts = [
        TestScript(
            uuid="script-uuid-001",
            name="Login Script",
            description="Test user login",
            api_definition_id=sample_api_definitions[2].id,
            script_type=ScriptType.MAIN,
            execution_order=1,
            variables={"username": "testuser"},
            assertions=[{"type": "status_code", "expected": 200}],
            is_active=True,
            created_by=sample_user.id,
        ),
        TestScript(
            uuid="script-uuid-002",
            name="Get User Script",
            description="Get user information",
            api_definition_id=sample_api_definitions[0].id,
            script_type=ScriptType.MAIN,
            execution_order=2,
            is_active=True,
            created_by=sample_user.id,
        ),
        TestScript(
            uuid="script-uuid-003",
            name="Setup Script",
            description="Setup test environment",
            api_definition_id=sample_api_definitions[1].id,
            script_type=ScriptType.SETUP,
            execution_order=0,
            is_active=True,
            created_by=sample_user.id,
        ),
    ]
    for script in scripts:
        session.add(script)
    session.flush()

    # Add script parameters
    params = [
        ScriptParameter(
            uuid="param-uuid-001",
            script_id=scripts[0].id,
            name="username",
            description="Username for login",
            parameter_type=ParameterType.STRING,
            default_value="testuser",
            is_required=True,
            order=1,
        ),
        ScriptParameter(
            uuid="param-uuid-002",
            script_id=scripts[0].id,
            name="password",
            description="Password for login",
            parameter_type=ParameterType.STRING,
            is_required=True,
            is_sensitive=True,
            order=2,
        ),
    ]
    for param in params:
        session.add(param)
    session.flush()

    return scripts


@pytest.fixture
def sample_components(session, sample_user, sample_scripts):
    """Create sample Test Components with nesting."""
    # Create parent component
    parent_component = TestComponent(
        uuid="component-uuid-001",
        name="User Management Suite",
        description="Complete user management test suite",
        component_type=ComponentType.COMPOSITE,
        execution_mode=ExecutionMode.SEQUENTIAL,
        shared_variables={"base_url": "https://api.example.com"},
        is_active=True,
        created_by=sample_user.id,
    )
    session.add(parent_component)
    session.flush()

    # Create child component (nested)
    child_component = TestComponent(
        uuid="component-uuid-002",
        name="Login Flow",
        description="Login flow component",
        component_type=ComponentType.SIMPLE,
        execution_mode=ExecutionMode.SEQUENTIAL,
        parent_component_id=parent_component.id,
        is_active=True,
        created_by=sample_user.id,
    )
    session.add(child_component)
    session.flush()

    # Create standalone component
    standalone_component = TestComponent(
        uuid="component-uuid-003",
        name="Standalone Component",
        description="A standalone component",
        component_type=ComponentType.SIMPLE,
        execution_mode=ExecutionMode.SEQUENTIAL,
        is_active=True,
        created_by=sample_user.id,
    )
    session.add(standalone_component)
    session.flush()

    # Add scripts to components
    component_scripts = [
        ComponentScript(
            component_id=child_component.id,
            script_id=sample_scripts[0].id,
            execution_order=1,
            is_enabled=True,
            script_parameters={"username": "component_user"},
            description="Login script in component",
        ),
        ComponentScript(
            component_id=child_component.id,
            script_id=sample_scripts[1].id,
            execution_order=2,
            is_enabled=True,
            description="Get user script in component",
        ),
        ComponentScript(
            component_id=standalone_component.id,
            script_id=sample_scripts[2].id,
            execution_order=1,
            is_enabled=True,
            description="Setup script in standalone component",
        ),
    ]
    for cs in component_scripts:
        session.add(cs)
    session.flush()

    return [parent_component, child_component, standalone_component]


@pytest.fixture
def sample_test_cases(session, sample_user, sample_scripts, sample_components):
    """Create sample Test Cases."""
    test_cases = [
        TestCase(
            uuid="testcase-uuid-001",
            name="User Registration Flow",
            description="Test complete user registration flow",
            priority=TestCasePriority.HIGH,
            status=TestCaseStatus.ACTIVE,
            category="User Management",
            test_data={"username": "test_user", "password": "Test@123"},
            is_automated=True,
            created_by=sample_user.id,
        ),
        TestCase(
            uuid="testcase-uuid-002",
            name="Login Test",
            description="Test user login functionality",
            priority=TestCasePriority.CRITICAL,
            status=TestCaseStatus.ACTIVE,
            category="Authentication",
            is_automated=True,
            created_by=sample_user.id,
        ),
    ]
    for tc in test_cases:
        session.add(tc)
    session.flush()

    # Add script references to test cases
    test_case_scripts = [
        TestCaseScript(
            test_case_id=test_cases[0].id,
            script_id=sample_scripts[2].id,
            execution_order=1,
            is_enabled=True,
            description="Setup script",
        ),
        TestCaseScript(
            test_case_id=test_cases[0].id,
            script_id=sample_scripts[0].id,
            execution_order=2,
            is_enabled=True,
            script_parameters={"username": "test_case_user"},
            description="Login script",
        ),
        TestCaseScript(
            test_case_id=test_cases[1].id,
            script_id=sample_scripts[0].id,
            execution_order=1,
            is_enabled=True,
            description="Login script for login test",
        ),
    ]
    for tcs in test_case_scripts:
        session.add(tcs)
    session.flush()

    # Add component references to test cases
    test_case_components = [
        TestCaseComponent(
            test_case_id=test_cases[0].id,
            component_id=sample_components[1].id,
            execution_order=3,
            is_enabled=True,
            component_parameters={"base_url": "https://test.example.com"},
            description="Login flow component",
        ),
    ]
    for tcc in test_case_components:
        session.add(tcc)
    session.flush()

    return test_cases


class TestHeaderBodyIndependence:
    """Test that Headers and Bodies are independent entities."""

    def test_headers_exist_independently(self, session, sample_headers):
        """Verify headers can exist without API definitions."""
        headers = session.execute(select(Header)).scalars().all()
        assert len(headers) == 2
        for header in headers:
            assert header.uuid is not None
            assert header.name is not None
            assert header.headers is not None

    def test_bodies_exist_independently(self, session, sample_bodies):
        """Verify bodies can exist without API definitions."""
        bodies = session.execute(select(Body)).scalars().all()
        assert len(bodies) == 2
        for body in bodies:
            assert body.uuid is not None
            assert body.name is not None

    def test_headers_and_bodies_are_separate(self, session, sample_headers, sample_bodies):
        """Verify headers and bodies are stored in separate tables."""
        headers = session.execute(select(Header)).scalars().all()
        bodies = session.execute(select(Body)).scalars().all()
        
        header_ids = {h.id for h in headers}
        body_ids = {b.id for b in bodies}
        
        # IDs can overlap since they're in different tables
        # But the entities should be distinct
        assert len(headers) == 2
        assert len(bodies) == 2


class TestApiDefinitionCombinations:
    """Test ApiDefinition's two combination methods."""

    def test_method1_header_plus_body_reference(
        self, session, sample_api_definitions, sample_headers, sample_bodies
    ):
        """Verify Method 1: Header + Body reference works."""
        api_def = session.get(ApiDefinition, sample_api_definitions[0].id)
        
        assert api_def.header_id == sample_headers[0].id
        assert api_def.response_body_id == sample_bodies[0].id
        assert api_def.inline_request_body is None
        assert api_def.inline_response_body is None

    def test_method2_header_plus_inline_body(
        self, session, sample_api_definitions, sample_headers
    ):
        """Verify Method 2: Header + Inline Body works."""
        api_def = session.get(ApiDefinition, sample_api_definitions[1].id)
        
        assert api_def.header_id == sample_headers[1].id
        assert api_def.request_body_id is None
        assert api_def.response_body_id is None
        assert api_def.inline_request_body is not None
        assert api_def.inline_response_body is not None

    def test_mixed_combination(self, session, sample_api_definitions, sample_bodies):
        """Verify mixed combination: Body reference + Inline response."""
        api_def = session.get(ApiDefinition, sample_api_definitions[2].id)
        
        assert api_def.request_body_id == sample_bodies[1].id
        assert api_def.response_body_id is None
        assert api_def.inline_response_body is not None

    def test_api_definition_relationships(self, session, sample_api_definitions):
        """Verify API definition relationships are loaded correctly."""
        for api_def in sample_api_definitions:
            loaded = session.get(ApiDefinition, api_def.id)
            if loaded.header_id:
                assert loaded.header is not None
            if loaded.request_body_id:
                assert loaded.request_body is not None
            if loaded.response_body_id:
                assert loaded.response_body is not None


class TestScriptApiReferences:
    """Test scripts reference API definitions correctly."""

    def test_scripts_have_api_definition_reference(self, session, sample_scripts):
        """Verify all scripts have API definition references."""
        scripts = session.execute(select(TestScript)).scalars().all()
        
        for script in scripts:
            assert script.api_definition_id is not None
            api_def = session.get(ApiDefinition, script.api_definition_id)
            assert api_def is not None

    def test_script_api_definition_relationship(self, session, sample_scripts):
        """Verify script-API definition relationship is loaded correctly."""
        for script in sample_scripts:
            loaded = session.get(TestScript, script.id)
            assert loaded.api_definition is not None
            assert loaded.api_definition.name is not None

    def test_script_parameters(self, session, sample_scripts):
        """Verify script parameters are associated correctly."""
        login_script = session.get(TestScript, sample_scripts[0].id)
        
        assert len(login_script.parameters) == 2
        param_names = {p.name for p in login_script.parameters}
        assert "username" in param_names
        assert "password" in param_names


class TestComponentNesting:
    """Test component nesting relationships."""

    def test_parent_component_exists(self, session, sample_components):
        """Verify parent component exists without parent."""
        parent = session.get(TestComponent, sample_components[0].id)
        
        assert parent.parent_component_id is None
        assert parent.component_type == ComponentType.COMPOSITE

    def test_child_component_references_parent(self, session, sample_components):
        """Verify child component references parent correctly."""
        child = session.get(TestComponent, sample_components[1].id)
        
        assert child.parent_component_id == sample_components[0].id
        assert child.parent_component is not None
        assert child.parent_component.name == "User Management Suite"

    def test_parent_has_child_components(self, session, sample_components):
        """Verify parent component has child components."""
        parent = session.get(TestComponent, sample_components[0].id)
        
        assert len(parent.child_components) == 1
        assert parent.child_components[0].name == "Login Flow"

    def test_standalone_component_has_no_parent(self, session, sample_components):
        """Verify standalone component has no parent."""
        standalone = session.get(TestComponent, sample_components[2].id)
        
        assert standalone.parent_component_id is None
        assert standalone.parent_component is None

    def test_component_scripts_association(self, session, sample_components):
        """Verify component-script associations."""
        child = session.get(TestComponent, sample_components[1].id)
        
        assert len(child.component_scripts) == 2
        for cs in child.component_scripts:
            assert cs.script is not None
            assert cs.script.name is not None


class TestTestCaseReferences:
    """Test test case references to scripts and components."""

    def test_test_case_script_references(self, session, sample_test_cases):
        """Verify test case script references."""
        tc1 = session.get(TestCase, sample_test_cases[0].id)
        
        assert len(tc1.test_case_scripts) == 2
        for tcs in tc1.test_case_scripts:
            assert tcs.script is not None
            assert tcs.script.name is not None

    def test_test_case_component_references(self, session, sample_test_cases):
        """Verify test case component references."""
        tc1 = session.get(TestCase, sample_test_cases[0].id)
        
        assert len(tc1.test_case_components) == 1
        tcc = tc1.test_case_components[0]
        assert tcc.component is not None
        assert tcc.component.name == "Login Flow"

    def test_test_case_with_only_scripts(self, session, sample_test_cases):
        """Verify test case can have only script references."""
        tc2 = session.get(TestCase, sample_test_cases[1].id)
        
        assert len(tc2.test_case_scripts) == 1
        assert len(tc2.test_case_components) == 0

    def test_execution_order_preserved(self, session, sample_test_cases):
        """Verify execution order is preserved in references."""
        tc1 = session.get(TestCase, sample_test_cases[0].id)
        
        script_orders = [tcs.execution_order for tcs in tc1.test_case_scripts]
        assert script_orders == sorted(script_orders)


class TestCascadeRules:
    """Test cascade delete and update rules."""

    def test_delete_api_definition_cascades_to_scripts(
        self, session, sample_user, sample_headers, sample_bodies
    ):
        """Verify deleting API definition cascades to scripts."""
        # Create a new API definition and script for this test
        api_def = ApiDefinition(
            uuid="cascade-test-api",
            name="Cascade Test API",
            method=HttpMethod.GET,
            path="/test",
            header_id=sample_headers[0].id,
            created_by=sample_user.id,
        )
        session.add(api_def)
        session.flush()

        script = TestScript(
            uuid="cascade-test-script",
            name="Cascade Test Script",
            api_definition_id=api_def.id,
            script_type=ScriptType.MAIN,
            created_by=sample_user.id,
        )
        session.add(script)
        session.flush()

        script_id = script.id

        # Delete API definition
        session.delete(api_def)
        session.flush()

        # Verify script is also deleted
        deleted_script = session.get(TestScript, script_id)
        assert deleted_script is None

    def test_delete_component_cascades_to_component_scripts(
        self, session, sample_user, sample_scripts
    ):
        """Verify deleting component cascades to component-script associations."""
        # Create a new component for this test
        component = TestComponent(
            uuid="cascade-test-component",
            name="Cascade Test Component",
            component_type=ComponentType.SIMPLE,
            execution_mode=ExecutionMode.SEQUENTIAL,
            created_by=sample_user.id,
        )
        session.add(component)
        session.flush()

        cs = ComponentScript(
            component_id=component.id,
            script_id=sample_scripts[0].id,
            execution_order=1,
        )
        session.add(cs)
        session.flush()

        cs_id = cs.id

        # Delete component
        session.delete(component)
        session.flush()

        # Verify component-script association is also deleted
        deleted_cs = session.get(ComponentScript, cs_id)
        assert deleted_cs is None

        # Verify script still exists
        script = session.get(TestScript, sample_scripts[0].id)
        assert script is not None


    def test_delete_test_case_cascades_to_associations(
        self, session, sample_user, sample_scripts, sample_components
    ):
        """Verify deleting test case cascades to script/component associations."""
        # Create a new test case for this test
        test_case = TestCase(
            uuid="cascade-test-case",
            name="Cascade Test Case",
            priority=TestCasePriority.MEDIUM,
            status=TestCaseStatus.DRAFT,
            created_by=sample_user.id,
        )
        session.add(test_case)
        session.flush()

        tcs = TestCaseScript(
            test_case_id=test_case.id,
            script_id=sample_scripts[0].id,
            execution_order=1,
        )
        session.add(tcs)
        session.flush()

        tcc = TestCaseComponent(
            test_case_id=test_case.id,
            component_id=sample_components[0].id,
            execution_order=2,
        )
        session.add(tcc)
        session.flush()

        tcs_id = tcs.id
        tcc_id = tcc.id

        # Delete test case
        session.delete(test_case)
        session.flush()

        # Verify associations are also deleted
        deleted_tcs = session.get(TestCaseScript, tcs_id)
        deleted_tcc = session.get(TestCaseComponent, tcc_id)
        assert deleted_tcs is None
        assert deleted_tcc is None

        # Verify script and component still exist
        script = session.get(TestScript, sample_scripts[0].id)
        component = session.get(TestComponent, sample_components[0].id)
        assert script is not None
        assert component is not None

    def test_delete_parent_component_cascades_to_children(
        self, session, sample_user
    ):
        """Verify deleting parent component cascades to child components."""
        # Create parent and child components for this test
        parent = TestComponent(
            uuid="cascade-parent",
            name="Cascade Parent",
            component_type=ComponentType.COMPOSITE,
            execution_mode=ExecutionMode.SEQUENTIAL,
            created_by=sample_user.id,
        )
        session.add(parent)
        session.flush()

        child = TestComponent(
            uuid="cascade-child",
            name="Cascade Child",
            component_type=ComponentType.SIMPLE,
            execution_mode=ExecutionMode.SEQUENTIAL,
            parent_component_id=parent.id,
            created_by=sample_user.id,
        )
        session.add(child)
        session.flush()

        child_id = child.id

        # Delete parent component
        session.delete(parent)
        session.flush()

        # Verify child is also deleted
        deleted_child = session.get(TestComponent, child_id)
        assert deleted_child is None

    def test_delete_user_sets_created_by_to_null(
        self, session, sample_headers
    ):
        """Verify deleting user sets created_by to NULL (SET NULL rule)."""
        # Create a new user and header for this test
        user = User(
            uuid="cascade-test-user",
            username="cascadeuser",
            email="cascade@example.com",
            password_hash="hashed",
            full_name="Cascade User",
            role=UserRole.TESTER,
            is_active=True,
        )
        session.add(user)
        session.flush()

        header = Header(
            uuid="cascade-user-header",
            name="Cascade User Header",
            headers={"X-Test": "value"},
            scope=HeaderScope.PRIVATE,
            created_by=user.id,
        )
        session.add(header)
        session.flush()

        header_id = header.id

        # Delete user
        session.delete(user)
        session.flush()

        # Verify header still exists but created_by is NULL
        remaining_header = session.get(Header, header_id)
        assert remaining_header is not None
        assert remaining_header.created_by is None
