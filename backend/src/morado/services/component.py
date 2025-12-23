"""Service layer for Layer 3: Test Component management.

This module provides business logic for managing test components and their execution.
"""

from typing import Any

from sqlalchemy.orm import Session

from morado.models.component import ComponentScript, ComponentType, TestComponent
from morado.repositories.component import (
    ComponentScriptRepository,
    TestComponentRepository,
)


class TestComponentService:
    """Service for managing test components.

    Provides business logic for creating, updating, and managing components
    that combine multiple scripts and support nesting.

    Example:
        >>> service = TestComponentService()
        >>> component = service.create_component(
        ...     session,
        ...     name="User Login Flow",
        ...     component_type=ComponentType.SIMPLE
        ... )
    """

    def __init__(self):
        """Initialize TestComponent service."""
        self.repository = TestComponentRepository()
        self.component_script_repository = ComponentScriptRepository()

    def create_component(  # noqa: PLR0913
        self,
        session: Session,
        name: str,
        description: str | None = None,
        component_type: ComponentType = ComponentType.SIMPLE,
        execution_mode: str = "sequential",
        parent_component_id: int | None = None,
        shared_variables: dict | None = None,
        timeout: int = 300,
        retry_count: int = 0,
        continue_on_failure: bool = False,
        execution_condition: str | None = None,
        tags: list[str] | None = None,
        created_by: int | None = None,
        **kwargs: Any,
    ) -> TestComponent:
        """Create a new test component.

        Args:
            session: Database session
            name: Component name
            description: Component description
            component_type: Component type (simple/composite/template)
            execution_mode: Execution mode (sequential/parallel/conditional)
            parent_component_id: Parent component ID for nesting
            shared_variables: Component-level shared variables
            timeout: Timeout in seconds
            retry_count: Number of retries
            continue_on_failure: Whether to continue on failure
            execution_condition: Execution condition expression
            tags: Tags for categorization
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created TestComponent instance

        Raises:
            ValueError: If parent component creates a circular reference
        """
        # Check for circular reference
        if parent_component_id:
            if self._would_create_cycle(session, parent_component_id, None):
                raise ValueError(
                    "Cannot create component: would create circular reference"
                )

        component = self.repository.create(
            session,
            name=name,
            description=description,
            component_type=component_type,
            execution_mode=execution_mode,
            parent_component_id=parent_component_id,
            shared_variables=shared_variables,
            timeout=timeout,
            retry_count=retry_count,
            continue_on_failure=continue_on_failure,
            execution_condition=execution_condition,
            tags=tags,
            created_by=created_by,
            **kwargs,
        )

        session.commit()
        return component

    def get_component(
        self,
        session: Session,
        component_id: int,
        load_scripts: bool = False,
        load_children: bool = False,
        load_full_hierarchy: bool = False,
    ) -> TestComponent | None:
        """Get component by ID.

        Args:
            session: Database session
            component_id: Component ID
            load_scripts: Whether to load associated scripts
            load_children: Whether to load child components
            load_full_hierarchy: Whether to load full hierarchy (scripts and children)

        Returns:
            TestComponent instance or None if not found
        """
        if load_full_hierarchy:
            return self.repository.get_with_full_hierarchy(session, component_id)
        elif load_scripts:
            return self.repository.get_with_scripts(session, component_id)
        elif load_children:
            return self.repository.get_with_children(session, component_id)
        else:
            return self.repository.get_by_id(session, component_id)

    def get_component_by_uuid(
        self, session: Session, uuid: str
    ) -> TestComponent | None:
        """Get component by UUID.

        Args:
            session: Database session
            uuid: Component UUID

        Returns:
            TestComponent instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_components(
        self,
        session: Session,
        component_type: ComponentType | None = None,
        parent_id: int | None = None,
        root_only: bool = False,
        tags: list[str] | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TestComponent]:
        """List components with optional filtering.

        Args:
            session: Database session
            component_type: Filter by component type
            parent_id: Filter by parent component ID
            root_only: Whether to return only root components
            tags: Filter by tags
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances
        """
        if root_only:
            return self.repository.get_root_components(session, skip, limit)
        elif parent_id is not None:
            return self.repository.get_children(session, parent_id, skip, limit)
        elif component_type:
            return self.repository.get_by_type(session, component_type, skip, limit)
        elif tags:
            return self.repository.get_by_tags(session, tags, skip, limit)
        else:
            return self.repository.get_all(session, skip, limit)

    def search_components(
        self, session: Session, name: str, skip: int = 0, limit: int = 100
    ) -> list[TestComponent]:
        """Search components by name.

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of TestComponent instances
        """
        return self.repository.search_by_name(session, name, skip, limit)

    def update_component(
        self, session: Session, component_id: int, **kwargs: Any
    ) -> TestComponent | None:
        """Update component.

        Args:
            session: Database session
            component_id: Component ID
            **kwargs: Fields to update

        Returns:
            Updated TestComponent instance or None if not found

        Raises:
            ValueError: If update would create a circular reference
        """
        component = self.repository.get_by_id(session, component_id)
        if not component:
            return None

        # Check for circular reference if parent is being updated
        if "parent_component_id" in kwargs:
            new_parent_id = kwargs["parent_component_id"]
            if new_parent_id and self._would_create_cycle(
                session, new_parent_id, component_id
            ):
                raise ValueError(
                    "Cannot update component: would create circular reference"
                )

        updated_component = self.repository.update(session, component, **kwargs)
        session.commit()
        return updated_component

    def delete_component(self, session: Session, component_id: int) -> bool:
        """Delete component.

        Args:
            session: Database session
            component_id: Component ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, component_id)
        if result:
            session.commit()
        return result

    def add_script_to_component(
        self,
        session: Session,
        component_id: int,
        script_id: int,
        execution_order: int = 0,
        is_enabled: bool = True,
        script_parameters: dict | None = None,
        execution_condition: str | None = None,
        skip_on_condition: bool = False,
        description: str | None = None,
    ) -> ComponentScript:
        """Add script to component.

        Args:
            session: Database session
            component_id: Component ID
            script_id: Script ID
            execution_order: Execution order
            is_enabled: Whether script is enabled
            script_parameters: Script parameter overrides
            execution_condition: Execution condition expression
            skip_on_condition: Whether to skip if condition not met
            description: Description

        Returns:
            Created ComponentScript instance
        """
        component_script = self.component_script_repository.create(
            session,
            component_id=component_id,
            script_id=script_id,
            execution_order=execution_order,
            is_enabled=is_enabled,
            script_parameters=script_parameters,
            execution_condition=execution_condition,
            skip_on_condition=skip_on_condition,
            description=description,
        )

        session.commit()
        return component_script

    def get_component_scripts(
        self, session: Session, component_id: int
    ) -> list[ComponentScript]:
        """Get scripts associated with component.

        Args:
            session: Database session
            component_id: Component ID

        Returns:
            List of ComponentScript instances ordered by execution_order
        """
        return self.component_script_repository.get_by_component(session, component_id)

    def update_component_script(
        self, session: Session, component_script_id: int, **kwargs: Any
    ) -> ComponentScript | None:
        """Update component-script association.

        Args:
            session: Database session
            component_script_id: ComponentScript ID
            **kwargs: Fields to update

        Returns:
            Updated ComponentScript instance or None if not found
        """
        component_script = self.component_script_repository.get_by_id(
            session, component_script_id
        )
        if not component_script:
            return None

        updated = self.component_script_repository.update(
            session, component_script, **kwargs
        )
        session.commit()
        return updated

    def remove_script_from_component(
        self, session: Session, component_script_id: int
    ) -> bool:
        """Remove script from component.

        Args:
            session: Database session
            component_script_id: ComponentScript ID

        Returns:
            True if removed, False if not found
        """
        result = self.component_script_repository.delete_by_id(
            session, component_script_id
        )
        if result:
            session.commit()
        return result

    def get_component_hierarchy(
        self, session: Session, component_id: int
    ) -> dict[str, Any] | None:
        """Get complete component hierarchy.

        This method returns the component with all its scripts and child components,
        recursively loading the entire hierarchy.

        Args:
            session: Database session
            component_id: Component ID

        Returns:
            Dictionary with complete component hierarchy or None if not found
        """
        component = self.repository.get_with_full_hierarchy(session, component_id)
        if not component:
            return None

        def build_hierarchy(comp: TestComponent) -> dict[str, Any]:
            result = {
                "id": comp.id,
                "uuid": comp.uuid,
                "name": comp.name,
                "description": comp.description,
                "component_type": comp.component_type,
                "execution_mode": comp.execution_mode,
                "shared_variables": comp.shared_variables,
                "timeout": comp.timeout,
                "scripts": [
                    {
                        "id": cs.id,
                        "script_id": cs.script_id,
                        "script_name": cs.script.name,
                        "execution_order": cs.execution_order,
                        "is_enabled": cs.is_enabled,
                        "script_parameters": cs.script_parameters,
                        "execution_condition": cs.execution_condition,
                    }
                    for cs in comp.component_scripts
                ],
                "children": [],
            }

            # Recursively load children
            for child in comp.child_components:
                child_full = self.repository.get_with_full_hierarchy(session, child.id)
                if child_full:
                    result["children"].append(build_hierarchy(child_full))

            return result

        return build_hierarchy(component)

    def _would_create_cycle(
        self, session: Session, parent_id: int, component_id: int | None
    ) -> bool:
        """Check if setting parent would create a circular reference.

        Args:
            session: Database session
            parent_id: Proposed parent component ID
            component_id: Component ID being updated (None for new component)

        Returns:
            True if would create cycle, False otherwise
        """
        if component_id is None:
            return False

        # If parent is the component itself, it's a cycle
        if parent_id == component_id:
            return True

        # Check if parent is a descendant of component
        visited = set()
        current_id = parent_id

        while current_id is not None:
            if current_id in visited:
                # Found a cycle in the existing hierarchy
                return True

            if current_id == component_id:
                # Parent is a descendant of component
                return True

            visited.add(current_id)

            # Get parent of current
            current = self.repository.get_by_id(session, current_id)
            if current:
                current_id = current.parent_component_id
            else:
                break

        return False

    def clone_component(
        self,
        session: Session,
        component_id: int,
        new_name: str,
        clone_children: bool = False,
    ) -> TestComponent | None:
        """Clone a component.

        Args:
            session: Database session
            component_id: Component ID to clone
            new_name: Name for the cloned component
            clone_children: Whether to clone child components

        Returns:
            Cloned TestComponent instance or None if source not found
        """
        source = self.repository.get_with_full_hierarchy(session, component_id)
        if not source:
            return None

        # Create new component
        cloned = self.repository.create(
            session,
            name=new_name,
            description=f"Cloned from: {source.name}",
            component_type=source.component_type,
            execution_mode=source.execution_mode,
            shared_variables=source.shared_variables,
            timeout=source.timeout,
            retry_count=source.retry_count,
            continue_on_failure=source.continue_on_failure,
            execution_condition=source.execution_condition,
            tags=source.tags,
            created_by=source.created_by,
        )

        # Clone scripts
        for cs in source.component_scripts:
            self.component_script_repository.create(
                session,
                component_id=cloned.id,
                script_id=cs.script_id,
                execution_order=cs.execution_order,
                is_enabled=cs.is_enabled,
                script_parameters=cs.script_parameters,
                execution_condition=cs.execution_condition,
                skip_on_condition=cs.skip_on_condition,
                description=cs.description,
            )

        # Clone children if requested
        if clone_children:
            for child in source.child_components:
                cloned_child = self.clone_component(
                    session, child.id, f"{child.name} (cloned)", clone_children=True
                )
                if cloned_child:
                    cloned_child.parent_component_id = cloned.id

        session.commit()
        return cloned
