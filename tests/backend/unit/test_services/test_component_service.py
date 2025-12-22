"""Unit tests for Test Component Service layer.

Tests business logic for TestComponent including nesting and script management.
"""

import pytest
from morado.models.component import ComponentType
from morado.services.api_component import ApiDefinitionService
from morado.services.component import TestComponentService
from morado.services.script import TestScriptService
from sqlalchemy.orm import Session


class TestTestComponentService:
    """Test TestComponentService business logic."""

    @pytest.fixture
    def service(self):
        """Create TestComponentService instance."""
        return TestComponentService()

    @pytest.fixture
    def script_service(self):
        """Create TestScriptService instance."""
        return TestScriptService()

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

    def test_create_component_success(
        self, service: TestComponentService, db_session: Session
    ):
        """Test successful component creation."""
        component = service.create_component(
            db_session,
            name="User Login Flow",
            component_type=ComponentType.SIMPLE
        )

        assert component.id is not None
        assert component.name == "User Login Flow"
        assert component.component_type == ComponentType.SIMPLE
        assert component.execution_mode == "sequential"
        assert component.parent_component_id is None

    def test_create_nested_component(
        self, service: TestComponentService, db_session: Session
    ):
        """Test creating nested component."""
        parent = service.create_component(
            db_session,
            name="Parent Component"
        )

        child = service.create_component(
            db_session,
            name="Child Component",
            parent_component_id=parent.id
        )

        assert child.parent_component_id == parent.id

    def test_create_component_prevents_circular_reference(
        self, service: TestComponentService, db_session: Session
    ):
        """Test that circular references are prevented."""
        component = service.create_component(
            db_session,
            name="Test Component"
        )

        # Try to set itself as parent
        with pytest.raises(ValueError, match="circular reference"):
            service.create_component(
                db_session,
                name="Self Reference",
                parent_component_id=component.id
            )

    def test_update_component_prevents_circular_reference(
        self, service: TestComponentService, db_session: Session
    ):
        """Test that updating parent prevents circular references."""
        parent = service.create_component(
            db_session,
            name="Parent"
        )

        child = service.create_component(
            db_session,
            name="Child",
            parent_component_id=parent.id
        )

        # Try to make parent a child of child (circular)
        with pytest.raises(ValueError, match="circular reference"):
            service.update_component(
                db_session,
                parent.id,
                parent_component_id=child.id
            )

    def test_get_component_with_scripts(
        self,
        service: TestComponentService,
        sample_script,
        db_session: Session
    ):
        """Test retrieving component with associated scripts."""
        component = service.create_component(
            db_session,
            name="Test Component"
        )

        service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=sample_script.id
        )

        retrieved = service.get_component(
            db_session,
            component.id,
            load_scripts=True
        )

        assert retrieved is not None
        assert len(retrieved.component_scripts) == 1

    def test_get_component_with_children(
        self, service: TestComponentService, db_session: Session
    ):
        """Test retrieving component with child components."""
        parent = service.create_component(
            db_session,
            name="Parent"
        )

        service.create_component(
            db_session,
            name="Child 1",
            parent_component_id=parent.id
        )
        service.create_component(
            db_session,
            name="Child 2",
            parent_component_id=parent.id
        )

        retrieved = service.get_component(
            db_session,
            parent.id,
            load_children=True
        )

        assert retrieved is not None
        assert len(retrieved.child_components) == 2

    def test_list_root_components(
        self, service: TestComponentService, db_session: Session
    ):
        """Test listing only root components."""
        root1 = service.create_component(
            db_session,
            name="Root 1"
        )
        service.create_component(
            db_session,
            name="Root 2"
        )

        service.create_component(
            db_session,
            name="Child",
            parent_component_id=root1.id
        )

        roots = service.list_components(db_session, root_only=True)
        assert len(roots) == 2
        assert all(c.parent_component_id is None for c in roots)

    def test_list_components_by_parent(
        self, service: TestComponentService, db_session: Session
    ):
        """Test listing components by parent."""
        parent = service.create_component(
            db_session,
            name="Parent"
        )

        service.create_component(
            db_session,
            name="Child 1",
            parent_component_id=parent.id
        )
        service.create_component(
            db_session,
            name="Child 2",
            parent_component_id=parent.id
        )

        children = service.list_components(db_session, parent_id=parent.id)
        assert len(children) == 2

    def test_list_components_by_type(
        self, service: TestComponentService, db_session: Session
    ):
        """Test listing components filtered by type."""
        service.create_component(
            db_session,
            name="Simple Component",
            component_type=ComponentType.SIMPLE
        )
        service.create_component(
            db_session,
            name="Composite Component",
            component_type=ComponentType.COMPOSITE
        )

        simple_components = service.list_components(
            db_session,
            component_type=ComponentType.SIMPLE
        )
        assert len(simple_components) == 1
        assert simple_components[0].name == "Simple Component"

    def test_search_components_by_name(
        self, service: TestComponentService, db_session: Session
    ):
        """Test searching components by name."""
        service.create_component(
            db_session,
            name="Login Flow"
        )
        service.create_component(
            db_session,
            name="Logout Flow"
        )

        results = service.search_components(db_session, "Login")
        assert len(results) == 1
        assert results[0].name == "Login Flow"

    def test_update_component(
        self, service: TestComponentService, db_session: Session
    ):
        """Test updating component."""
        component = service.create_component(
            db_session,
            name="Original Name"
        )

        updated = service.update_component(
            db_session,
            component.id,
            name="Updated Name",
            timeout=600
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.timeout == 600

    def test_delete_component(
        self, service: TestComponentService, db_session: Session
    ):
        """Test deleting component."""
        component = service.create_component(
            db_session,
            name="To Delete"
        )

        result = service.delete_component(db_session, component.id)
        assert result is True

        retrieved = service.get_component(db_session, component.id)
        assert retrieved is None

    def test_add_script_to_component(
        self,
        service: TestComponentService,
        sample_script,
        db_session: Session
    ):
        """Test adding script to component."""
        component = service.create_component(
            db_session,
            name="Test Component"
        )

        component_script = service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=sample_script.id,
            execution_order=1,
            script_parameters={"username": "test_user"}
        )

        assert component_script.id is not None
        assert component_script.component_id == component.id
        assert component_script.script_id == sample_script.id
        assert component_script.execution_order == 1
        assert component_script.script_parameters == {"username": "test_user"}

    def test_get_component_scripts_ordered(
        self,
        service: TestComponentService,
        script_service: TestScriptService,
        api_def_service: ApiDefinitionService,
        db_session: Session
    ):
        """Test retrieving component scripts in execution order."""
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
        script3 = script_service.create_script(
            db_session,
            name="Script 3",
            api_definition_id=api_def.id
        )

        component = service.create_component(
            db_session,
            name="Test Component"
        )

        # Add scripts in non-sequential order
        service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=script2.id,
            execution_order=2
        )
        service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=script1.id,
            execution_order=1
        )
        service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=script3.id,
            execution_order=3
        )

        scripts = service.get_component_scripts(db_session, component.id)
        assert len(scripts) == 3
        assert scripts[0].script.name == "Script 1"
        assert scripts[1].script.name == "Script 2"
        assert scripts[2].script.name == "Script 3"

    def test_update_component_script(
        self,
        service: TestComponentService,
        sample_script,
        db_session: Session
    ):
        """Test updating component-script association."""
        component = service.create_component(
            db_session,
            name="Test Component"
        )

        component_script = service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=sample_script.id
        )

        updated = service.update_component_script(
            db_session,
            component_script.id,
            execution_order=5,
            is_enabled=False
        )

        assert updated is not None
        assert updated.execution_order == 5
        assert updated.is_enabled is False

    def test_remove_script_from_component(
        self,
        service: TestComponentService,
        sample_script,
        db_session: Session
    ):
        """Test removing script from component."""
        component = service.create_component(
            db_session,
            name="Test Component"
        )

        component_script = service.add_script_to_component(
            db_session,
            component_id=component.id,
            script_id=sample_script.id
        )

        result = service.remove_script_from_component(
            db_session,
            component_script.id
        )
        assert result is True

    def test_get_component_hierarchy(
        self,
        service: TestComponentService,
        sample_script,
        db_session: Session
    ):
        """Test getting complete component hierarchy."""
        parent = service.create_component(
            db_session,
            name="Parent Component"
        )

        service.create_component(
            db_session,
            name="Child Component",
            parent_component_id=parent.id
        )

        service.add_script_to_component(
            db_session,
            component_id=parent.id,
            script_id=sample_script.id
        )

        hierarchy = service.get_component_hierarchy(db_session, parent.id)

        assert hierarchy is not None
        assert hierarchy['name'] == "Parent Component"
        assert len(hierarchy['scripts']) == 1
        assert len(hierarchy['children']) == 1
        assert hierarchy['children'][0]['name'] == "Child Component"

    def test_clone_component_without_children(
        self,
        service: TestComponentService,
        sample_script,
        db_session: Session
    ):
        """Test cloning component without children."""
        original = service.create_component(
            db_session,
            name="Original Component",
            shared_variables={"env": "test"}
        )

        service.add_script_to_component(
            db_session,
            component_id=original.id,
            script_id=sample_script.id
        )

        cloned = service.clone_component(
            db_session,
            original.id,
            "Cloned Component",
            clone_children=False
        )

        assert cloned is not None
        assert cloned.name == "Cloned Component"
        assert cloned.shared_variables == {"env": "test"}
        assert len(cloned.component_scripts) == 1

    def test_clone_component_with_children(
        self,
        service: TestComponentService,
        db_session: Session
    ):
        """Test cloning component with children."""
        parent = service.create_component(
            db_session,
            name="Parent Component"
        )

        service.create_component(
            db_session,
            name="Child Component",
            parent_component_id=parent.id
        )

        cloned = service.clone_component(
            db_session,
            parent.id,
            "Cloned Parent",
            clone_children=True
        )

        assert cloned is not None
        assert cloned.name == "Cloned Parent"
        # Verify children were cloned
        children = service.list_components(db_session, parent_id=cloned.id)
        assert len(children) > 0

    def test_component_nesting_three_levels(
        self, service: TestComponentService, db_session: Session
    ):
        """Test three-level component nesting."""
        level1 = service.create_component(
            db_session,
            name="Level 1"
        )

        level2 = service.create_component(
            db_session,
            name="Level 2",
            parent_component_id=level1.id
        )

        level3 = service.create_component(
            db_session,
            name="Level 3",
            parent_component_id=level2.id
        )

        assert level3.parent_component_id == level2.id
        assert level2.parent_component_id == level1.id

        # Verify hierarchy
        hierarchy = service.get_component_hierarchy(db_session, level1.id)
        assert hierarchy is not None
        assert len(hierarchy['children']) == 1
        assert len(hierarchy['children'][0]['children']) == 1

    def test_would_create_cycle_detection(
        self, service: TestComponentService, db_session: Session
    ):
        """Test cycle detection in component hierarchy."""
        comp_a = service.create_component(db_session, name="Component A")
        comp_b = service.create_component(
            db_session, name="Component B", parent_component_id=comp_a.id
        )
        comp_c = service.create_component(
            db_session, name="Component C", parent_component_id=comp_b.id
        )

        # Try to make A a child of C (would create cycle: A -> B -> C -> A)
        with pytest.raises(ValueError, match="circular reference"):
            service.update_component(
                db_session,
                comp_a.id,
                parent_component_id=comp_c.id
            )
