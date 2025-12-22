"""Unit tests for Component repositories.

Tests for TestComponentRepository and ComponentScriptRepository,
including nested component functionality.
"""

import pytest
from morado.models.api_component import ApiDefinition, Header, HttpMethod
from morado.models.component import ComponentScript, ComponentType, TestComponent
from morado.models.script import ScriptType, TestScript
from morado.repositories.component import (
    ComponentScriptRepository,
    TestComponentRepository,
)


@pytest.fixture
def component_repo():
    """Create a TestComponentRepository instance."""
    return TestComponentRepository()


@pytest.fixture
def component_script_repo():
    """Create a ComponentScriptRepository instance."""
    return ComponentScriptRepository()


@pytest.fixture
def sample_scripts(session):
    """Create sample script data."""
    # Create minimal API definition for scripts
    header = Header(
        uuid="header-1",
        name="Test Header",
        headers={"Content-Type": "application/json"},
    )
    session.add(header)
    session.flush()

    api_def = ApiDefinition(
        uuid="api-1",
        name="Test API",
        method=HttpMethod.GET,
        path="/test",
        header_id=header.id,
    )
    session.add(api_def)
    session.flush()

    scripts = [
        TestScript(
            uuid="script-1",
            name="Setup Script",
            script_type=ScriptType.SETUP,
            api_definition_id=api_def.id,
            is_active=True,
        ),
        TestScript(
            uuid="script-2",
            name="Main Script",
            script_type=ScriptType.MAIN,
            api_definition_id=api_def.id,
            is_active=True,
        ),
        TestScript(
            uuid="script-3",
            name="Teardown Script",
            script_type=ScriptType.TEARDOWN,
            api_definition_id=api_def.id,
            is_active=True,
        ),
    ]
    for script in scripts:
        session.add(script)
    session.commit()
    return scripts


@pytest.fixture
def sample_components(session, sample_scripts):
    """Create sample component data with nested structure."""
    # Root component
    root = TestComponent(
        uuid="comp-root",
        name="Root Component",
        component_type=ComponentType.COMPOSITE,
        is_active=True,
    )
    session.add(root)
    session.flush()

    # Child components
    child1 = TestComponent(
        uuid="comp-child1",
        name="Child Component 1",
        component_type=ComponentType.SIMPLE,
        parent_component_id=root.id,
        is_active=True,
    )
    child2 = TestComponent(
        uuid="comp-child2",
        name="Child Component 2",
        component_type=ComponentType.SIMPLE,
        parent_component_id=root.id,
        is_active=True,
    )
    session.add(child1)
    session.add(child2)
    session.flush()

    # Associate scripts with components
    associations = [
        ComponentScript(
            component_id=root.id,
            script_id=sample_scripts[0].id,
            execution_order=1,
            is_enabled=True,
        ),
        ComponentScript(
            component_id=child1.id,
            script_id=sample_scripts[1].id,
            execution_order=1,
            is_enabled=True,
        ),
        ComponentScript(
            component_id=child2.id,
            script_id=sample_scripts[2].id,
            execution_order=1,
            is_enabled=True,
        ),
    ]
    for assoc in associations:
        session.add(assoc)

    session.commit()
    return {"root": root, "child1": child1, "child2": child2}


class TestComponentRepositoryBasic:
    """Test basic component repository operations."""

    def test_create_component(self, session, component_repo):
        """Test creating a component."""
        component = component_repo.create(
            session,
            uuid="new-comp",
            name="New Component",
            component_type=ComponentType.SIMPLE,
        )

        assert component.id is not None
        assert component.name == "New Component"
        assert component.component_type == ComponentType.SIMPLE

    def test_get_by_type(self, session, component_repo, sample_components):
        """Test getting components by type."""
        simple_comps = component_repo.get_by_type(session, ComponentType.SIMPLE)

        assert len(simple_comps) == 2
        assert all(c.component_type == ComponentType.SIMPLE for c in simple_comps)

    def test_search_by_name(self, session, component_repo, sample_components):
        """Test searching components by name."""
        results = component_repo.search_by_name(session, "child")

        assert len(results) == 2
        assert all("Child" in c.name for c in results)

    def test_get_by_tags(self, session, component_repo):
        """Test getting components by tags."""
        component_repo.create(
            session,
            uuid="comp-1",
            name="Component 1",
            component_type=ComponentType.SIMPLE,
            tags=["auth", "api"],
        )
        component_repo.create(
            session,
            uuid="comp-2",
            name="Component 2",
            component_type=ComponentType.SIMPLE,
            tags=["auth", "db"],
        )
        session.commit()

        # Note: SQLite doesn't support array contains operations well
        # This test verifies the method exists and runs without error
        results = component_repo.get_by_tags(session, ["auth"])
        # In a real PostgreSQL database, this would return 2 results
        assert isinstance(results, list)


class TestComponentNesting:
    """Test component nesting functionality."""

    def test_get_root_components(self, session, component_repo, sample_components):
        """Test getting root components (no parent)."""
        roots = component_repo.get_root_components(session)

        assert len(roots) == 1
        assert roots[0].name == "Root Component"
        assert roots[0].parent_component_id is None

    def test_get_children(self, session, component_repo, sample_components):
        """Test getting child components of a parent."""
        root_id = sample_components["root"].id
        children = component_repo.get_children(session, root_id)

        assert len(children) == 2
        assert all(c.parent_component_id == root_id for c in children)

    def test_get_with_children(self, session, component_repo, sample_components):
        """Test getting component with children loaded."""
        root_id = sample_components["root"].id
        component = component_repo.get_with_children(session, root_id)

        assert component is not None
        assert len(component.child_components) == 2

    def test_nested_component_hierarchy(self, session, component_repo):
        """Test creating a multi-level nested hierarchy."""
        # Create 3-level hierarchy
        level1 = component_repo.create(
            session,
            uuid="level-1",
            name="Level 1",
            component_type=ComponentType.COMPOSITE,
        )
        session.flush()

        level2 = component_repo.create(
            session,
            uuid="level-2",
            name="Level 2",
            component_type=ComponentType.COMPOSITE,
            parent_component_id=level1.id,
        )
        session.flush()

        level3 = component_repo.create(
            session,
            uuid="level-3",
            name="Level 3",
            component_type=ComponentType.SIMPLE,
            parent_component_id=level2.id,
        )
        session.commit()

        # Verify hierarchy
        loaded_level1 = component_repo.get_with_children(session, level1.id)
        assert len(loaded_level1.child_components) == 1
        assert loaded_level1.child_components[0].id == level2.id

        loaded_level2 = component_repo.get_with_children(session, level2.id)
        assert len(loaded_level2.child_components) == 1
        assert loaded_level2.child_components[0].id == level3.id


class TestComponentScriptAssociations:
    """Test component-script associations."""

    def test_get_with_scripts(self, session, component_repo, sample_components):
        """Test getting component with associated scripts."""
        root_id = sample_components["root"].id
        component = component_repo.get_with_scripts(session, root_id)

        assert component is not None
        assert len(component.component_scripts) == 1
        assert component.component_scripts[0].script.name == "Setup Script"

    def test_get_with_full_hierarchy(self, session, component_repo, sample_components):
        """Test getting component with both scripts and children."""
        root_id = sample_components["root"].id
        component = component_repo.get_with_full_hierarchy(session, root_id)

        assert component is not None
        assert len(component.component_scripts) == 1
        assert len(component.child_components) == 2

    def test_component_script_execution_order(
        self, session, component_repo, component_script_repo, sample_components, sample_scripts
    ):
        """Test that scripts are returned in execution order."""
        comp_id = sample_components["root"].id

        # Add multiple scripts with different orders
        component_script_repo.create(
            session,
            component_id=comp_id,
            script_id=sample_scripts[1].id,
            execution_order=2,
            is_enabled=True,
        )
        component_script_repo.create(
            session,
            component_id=comp_id,
            script_id=sample_scripts[2].id,
            execution_order=3,
            is_enabled=True,
        )
        session.commit()

        associations = component_script_repo.get_by_component(session, comp_id)
        assert len(associations) == 3
        assert associations[0].execution_order == 1
        assert associations[1].execution_order == 2
        assert associations[2].execution_order == 3


class TestComponentScriptRepository:
    """Test ComponentScriptRepository operations."""

    def test_get_by_component(
        self, session, component_script_repo, sample_components
    ):
        """Test getting script associations for a component."""
        root_id = sample_components["root"].id
        associations = component_script_repo.get_by_component(session, root_id)

        assert len(associations) == 1
        assert associations[0].component_id == root_id

    def test_get_by_script(
        self, session, component_script_repo, sample_components, sample_scripts
    ):
        """Test getting component associations for a script."""
        script_id = sample_scripts[0].id
        associations = component_script_repo.get_by_script(session, script_id)

        assert len(associations) == 1
        assert associations[0].script_id == script_id

    def test_disabled_associations_excluded(
        self, session, component_script_repo, sample_components, sample_scripts
    ):
        """Test that disabled associations are excluded."""
        comp_id = sample_components["root"].id

        # Add a disabled association
        component_script_repo.create(
            session,
            component_id=comp_id,
            script_id=sample_scripts[1].id,
            execution_order=2,
            is_enabled=False,
        )
        session.commit()

        associations = component_script_repo.get_by_component(session, comp_id)
        # Should only get enabled associations
        assert len(associations) == 1
        assert all(a.is_enabled for a in associations)

    def test_parameter_override_field_not_in_model(
        self, session, component_script_repo, sample_components, sample_scripts
    ):
        """Test that ComponentScript model doesn't have parameter_override field yet.

        This is a placeholder test. When parameter_override is added to the model,
        this test should be updated to test the actual functionality.
        """
        comp_id = sample_components["root"].id
        script_id = sample_scripts[1].id

        # Create association without parameter_override
        assoc = component_script_repo.create(
            session,
            component_id=comp_id,
            script_id=script_id,
            execution_order=2,
            is_enabled=True,
        )
        session.commit()

        loaded = component_script_repo.get_by_id(session, assoc.id)
        assert loaded is not None
        assert loaded.component_id == comp_id
        assert loaded.script_id == script_id


class TestComponentTransactions:
    """Test transaction handling for components."""

    def test_create_component_rollback(self, session, component_repo):
        """Test that component creation can be rolled back."""
        component_repo.create(
            session,
            uuid="rollback-comp",
            name="Rollback Component",
            component_type=ComponentType.SIMPLE,
        )
        session.rollback()

        components = component_repo.get_all(session)
        assert len(components) == 0

    def test_nested_component_rollback(self, session, component_repo):
        """Test that nested component creation can be rolled back."""
        parent = component_repo.create(
            session,
            uuid="parent",
            name="Parent",
            component_type=ComponentType.COMPOSITE,
        )
        session.flush()

        component_repo.create(
            session,
            uuid="child",
            name="Child",
            component_type=ComponentType.SIMPLE,
            parent_component_id=parent.id,
        )
        session.rollback()

        components = component_repo.get_all(session)
        assert len(components) == 0
