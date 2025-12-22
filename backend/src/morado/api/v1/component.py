"""Test Component management API endpoints.

This module provides REST API endpoints for managing test components (Layer 3).
"""

from typing import Annotated, Any

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.models.component import ComponentType
from morado.schemas.component import (
    ComponentScriptCreate,
    ComponentScriptListResponse,
    ComponentScriptResponse,
    ComponentScriptUpdate,
    TestComponentCreate,
    TestComponentListResponse,
    TestComponentResponse,
    TestComponentUpdate,
)
from morado.services.component import TestComponentService
from sqlalchemy.orm import Session


def provide_component_service() -> TestComponentService:
    """Provide TestComponentService instance."""
    return TestComponentService()


class TestComponentController(Controller):
    """Controller for Test Component management endpoints."""

    path = "/components"
    tags = ["Components"]
    dependencies = {"component_service": Provide(provide_component_service)}

    @post("/")
    async def create_component(
        self,
        data: TestComponentCreate,
        component_service: TestComponentService,
        db_session: Session,
    ) -> TestComponentResponse:
        """Create a new test component.

        Args:
            data: Component creation data
            component_service: Component service instance
            db_session: Database session

        Returns:
            Created component

        Raises:
            ValueError: If parent component creates a circular reference

        Example:
            ```json
            {
                "name": "User Login Flow",
                "component_type": "simple",
                "execution_mode": "sequential",
                "shared_variables": {"base_url": "https://api.example.com"}
            }
            ```
        """
        try:
            component = component_service.create_component(
                db_session,
                **data.model_dump()
            )
            return TestComponentResponse.model_validate(component)
        except ValueError as e:
            from litestar.exceptions import ValidationException
            raise ValidationException(detail=str(e))

    @get("/")
    async def list_components(
        self,
        component_service: TestComponentService,
        db_session: Session,
        component_type: Annotated[ComponentType | None, Parameter(query="component_type")] = None,
        parent_id: Annotated[int | None, Parameter(query="parent_id")] = None,
        root_only: Annotated[bool, Parameter(query="root_only")] = False,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestComponentListResponse:
        """List components with optional filtering.

        Args:
            component_service: Component service instance
            db_session: Database session
            component_type: Filter by component type
            parent_id: Filter by parent component ID
            root_only: Whether to return only root components
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of components with pagination info
        """
        components = component_service.list_components(
            db_session,
            component_type=component_type,
            parent_id=parent_id,
            root_only=root_only,
            skip=skip,
            limit=limit
        )

        return TestComponentListResponse(
            items=[TestComponentResponse.model_validate(c) for c in components],
            total=len(components),
            skip=skip,
            limit=limit
        )

    @get("/search")
    async def search_components(
        self,
        component_service: TestComponentService,
        db_session: Session,
        name: Annotated[str, Parameter(query="name", min_length=1)],
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestComponentListResponse:
        """Search components by name.

        Args:
            component_service: Component service instance
            db_session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching components
        """
        components = component_service.search_components(
            db_session,
            name=name,
            skip=skip,
            limit=limit
        )

        return TestComponentListResponse(
            items=[TestComponentResponse.model_validate(c) for c in components],
            total=len(components),
            skip=skip,
            limit=limit
        )

    @get("/{component_id:int}")
    async def get_component(
        self,
        component_id: int,
        component_service: TestComponentService,
        db_session: Session,
        load_scripts: Annotated[bool, Parameter(query="load_scripts")] = False,
        load_children: Annotated[bool, Parameter(query="load_children")] = False,
        load_full_hierarchy: Annotated[bool, Parameter(query="load_full_hierarchy")] = False,
    ) -> TestComponentResponse:
        """Get component by ID.

        Args:
            component_id: Component ID
            component_service: Component service instance
            db_session: Database session
            load_scripts: Whether to load associated scripts
            load_children: Whether to load child components
            load_full_hierarchy: Whether to load full hierarchy

        Returns:
            Component details

        Raises:
            NotFoundException: If component not found
        """
        component = component_service.get_component(
            db_session,
            component_id,
            load_scripts=load_scripts,
            load_children=load_children,
            load_full_hierarchy=load_full_hierarchy
        )
        if not component:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with ID {component_id} not found")

        return TestComponentResponse.model_validate(component)

    @get("/{component_id:int}/hierarchy")
    async def get_component_hierarchy(
        self,
        component_id: int,
        component_service: TestComponentService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get complete component hierarchy.

        This endpoint returns the component with all its scripts and child components,
        recursively loading the entire hierarchy.

        Args:
            component_id: Component ID
            component_service: Component service instance
            db_session: Database session

        Returns:
            Complete component hierarchy

        Raises:
            NotFoundException: If component not found
        """
        hierarchy = component_service.get_component_hierarchy(db_session, component_id)
        if not hierarchy:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with ID {component_id} not found")

        return hierarchy

    @get("/uuid/{uuid:str}")
    async def get_component_by_uuid(
        self,
        uuid: str,
        component_service: TestComponentService,
        db_session: Session,
    ) -> TestComponentResponse:
        """Get component by UUID.

        Args:
            uuid: Component UUID
            component_service: Component service instance
            db_session: Database session

        Returns:
            Component details

        Raises:
            NotFoundException: If component not found
        """
        component = component_service.get_component_by_uuid(db_session, uuid)
        if not component:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with UUID {uuid} not found")

        return TestComponentResponse.model_validate(component)

    @patch("/{component_id:int}")
    async def update_component(
        self,
        component_id: int,
        data: TestComponentUpdate,
        component_service: TestComponentService,
        db_session: Session,
    ) -> TestComponentResponse:
        """Update component.

        Args:
            component_id: Component ID
            data: Component update data
            component_service: Component service instance
            db_session: Database session

        Returns:
            Updated component

        Raises:
            NotFoundException: If component not found
            ValueError: If update would create a circular reference
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        try:
            component = component_service.update_component(
                db_session,
                component_id,
                **update_data
            )

            if not component:
                from litestar.exceptions import NotFoundException
                raise NotFoundException(detail=f"Component with ID {component_id} not found")

            return TestComponentResponse.model_validate(component)
        except ValueError as e:
            from litestar.exceptions import ValidationException
            raise ValidationException(detail=str(e))

    @delete("/{component_id:int}", status_code=200)
    async def delete_component(
        self,
        component_id: int,
        component_service: TestComponentService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete component.

        Args:
            component_id: Component ID
            component_service: Component service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If component not found
        """
        success = component_service.delete_component(db_session, component_id)

        if not success:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with ID {component_id} not found")

        return {"message": "Component deleted successfully"}

    @post("/{component_id:int}/clone")
    async def clone_component(
        self,
        component_id: int,
        component_service: TestComponentService,
        db_session: Session,
        new_name: Annotated[str, Parameter(query="new_name", min_length=1)],
        clone_children: Annotated[bool, Parameter(query="clone_children")] = False,
    ) -> TestComponentResponse:
        """Clone a component.

        Args:
            component_id: Component ID to clone
            component_service: Component service instance
            db_session: Database session
            new_name: Name for the cloned component
            clone_children: Whether to clone child components

        Returns:
            Cloned component

        Raises:
            NotFoundException: If component not found
        """
        cloned = component_service.clone_component(
            db_session,
            component_id,
            new_name,
            clone_children=clone_children
        )

        if not cloned:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with ID {component_id} not found")

        return TestComponentResponse.model_validate(cloned)

    # Script management endpoints

    @post("/{component_id:int}/scripts")
    async def add_script_to_component(
        self,
        component_id: int,
        data: ComponentScriptCreate,
        component_service: TestComponentService,
        db_session: Session,
    ) -> ComponentScriptResponse:
        """Add script to component.

        Args:
            component_id: Component ID
            data: Component-script association data
            component_service: Component service instance
            db_session: Database session

        Returns:
            Created component-script association

        Raises:
            NotFoundException: If component not found
        """
        # Verify component exists
        component = component_service.get_component(db_session, component_id)
        if not component:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with ID {component_id} not found")

        component_script = component_service.add_script_to_component(
            db_session,
            component_id=component_id,
            **data.model_dump(exclude={"component_id"})
        )

        return ComponentScriptResponse.model_validate(component_script)

    @get("/{component_id:int}/scripts")
    async def get_component_scripts(
        self,
        component_id: int,
        component_service: TestComponentService,
        db_session: Session,
    ) -> ComponentScriptListResponse:
        """Get scripts associated with component.

        Args:
            component_id: Component ID
            component_service: Component service instance
            db_session: Database session

        Returns:
            List of component-script associations

        Raises:
            NotFoundException: If component not found
        """
        # Verify component exists
        component = component_service.get_component(db_session, component_id)
        if not component:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"Component with ID {component_id} not found")

        component_scripts = component_service.get_component_scripts(
            db_session,
            component_id
        )

        return ComponentScriptListResponse(
            items=[ComponentScriptResponse.model_validate(cs) for cs in component_scripts],
            total=len(component_scripts),
            skip=0,
            limit=len(component_scripts)
        )

    @patch("/scripts/{component_script_id:int}")
    async def update_component_script(
        self,
        component_script_id: int,
        data: ComponentScriptUpdate,
        component_service: TestComponentService,
        db_session: Session,
    ) -> ComponentScriptResponse:
        """Update component-script association.

        Args:
            component_script_id: ComponentScript ID
            data: Update data
            component_service: Component service instance
            db_session: Database session

        Returns:
            Updated component-script association

        Raises:
            NotFoundException: If association not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        component_script = component_service.update_component_script(
            db_session,
            component_script_id,
            **update_data
        )

        if not component_script:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(
                detail=f"Component-script association with ID {component_script_id} not found"
            )

        return ComponentScriptResponse.model_validate(component_script)

    @delete("/scripts/{component_script_id:int}", status_code=200)
    async def remove_script_from_component(
        self,
        component_script_id: int,
        component_service: TestComponentService,
        db_session: Session,
    ) -> dict[str, str]:
        """Remove script from component.

        Args:
            component_script_id: ComponentScript ID
            component_service: Component service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If association not found
        """
        success = component_service.remove_script_from_component(
            db_session,
            component_script_id
        )

        if not success:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(
                detail=f"Component-script association with ID {component_script_id} not found"
            )

        return {"message": "Script removed from component successfully"}
