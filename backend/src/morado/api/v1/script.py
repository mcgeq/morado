"""Test Script management API endpoints.

This module provides REST API endpoints for managing test scripts (Layer 2).
"""

from typing import Annotated, Any

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.models.script import ScriptType
from morado.schemas.script import (
    ScriptParameterCreate,
    ScriptParameterListResponse,
    ScriptParameterResponse,
    ScriptParameterUpdate,
    TestScriptCreate,
    TestScriptListResponse,
    TestScriptResponse,
    TestScriptUpdate,
)
from morado.services.script import TestScriptService
from sqlalchemy.orm import Session


def provide_script_service() -> TestScriptService:
    """Provide TestScriptService instance."""
    return TestScriptService()


class TestScriptController(Controller):
    """Controller for Test Script management endpoints."""

    path = "/scripts"
    tags = ["Scripts"]
    dependencies = {"script_service": Provide(provide_script_service)}

    @post("/")
    async def create_script(
        self,
        data: TestScriptCreate,
        script_service: TestScriptService,
        db_session: Session,
    ) -> TestScriptResponse:
        """Create a new test script.

        Args:
            data: Script creation data
            script_service: Script service instance
            db_session: Database session

        Returns:
            Created script

        Example:
            ```json
            {
                "name": "Login Test",
                "api_definition_id": 1,
                "script_type": "main",
                "variables": {"username": "test"},
                "assertions": [{"type": "status_code", "expected": 200}]
            }
            ```
        """
        script = script_service.create_script(db_session, **data.model_dump())
        return TestScriptResponse.model_validate(script)

    @get("/")
    async def list_scripts(
        self,
        script_service: TestScriptService,
        db_session: Session,
        api_definition_id: Annotated[
            int | None, Parameter(query="api_definition_id")
        ] = None,
        script_type: Annotated[
            ScriptType | None, Parameter(query="script_type")
        ] = None,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestScriptListResponse:
        """List scripts with optional filtering.

        Args:
            script_service: Script service instance
            db_session: Database session
            api_definition_id: Filter by API definition ID
            script_type: Filter by script type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of scripts with pagination info
        """
        scripts = script_service.list_scripts(
            db_session,
            api_definition_id=api_definition_id,
            script_type=script_type,
            skip=skip,
            limit=limit,
        )

        # Calculate pagination values
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (len(scripts) + limit - 1) // limit if limit > 0 else 1

        return TestScriptListResponse(
            items=[TestScriptResponse.model_validate(s) for s in scripts],
            total=len(scripts),
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    @get("/search")
    async def search_scripts(
        self,
        script_service: TestScriptService,
        db_session: Session,
        name: Annotated[str, Parameter(query="name", min_length=1)],
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> TestScriptListResponse:
        """Search scripts by name.

        Args:
            script_service: Script service instance
            db_session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching scripts
        """
        scripts = script_service.search_scripts(
            db_session, name=name, skip=skip, limit=limit
        )

        # Calculate pagination values
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (len(scripts) + limit - 1) // limit if limit > 0 else 1

        return TestScriptListResponse(
            items=[TestScriptResponse.model_validate(s) for s in scripts],
            total=len(scripts),
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    @get("/{script_id:int}")
    async def get_script(
        self,
        script_id: int,
        script_service: TestScriptService,
        db_session: Session,
        with_relations: Annotated[bool, Parameter(query="with_relations")] = False,
    ) -> TestScriptResponse:
        """Get script by ID.

        Args:
            script_id: Script ID
            script_service: Script service instance
            db_session: Database session
            with_relations: Whether to load related API definition and parameters

        Returns:
            Script details

        Raises:
            NotFoundException: If script not found
        """
        script = script_service.get_script(
            db_session, script_id, with_relations=with_relations
        )
        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        return TestScriptResponse.model_validate(script)

    @get("/{script_id:int}/config")
    async def get_script_execution_config(
        self,
        script_id: int,
        script_service: TestScriptService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get complete script execution configuration.

        This endpoint returns all information needed to execute a script,
        including API definition, parameters, assertions, etc.

        Args:
            script_id: Script ID
            script_service: Script service instance
            db_session: Database session

        Returns:
            Complete execution configuration

        Raises:
            NotFoundException: If script not found
        """
        config = script_service.get_script_execution_config(db_session, script_id)
        if not config:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        return config

    @get("/uuid/{uuid:str}")
    async def get_script_by_uuid(
        self,
        uuid: str,
        script_service: TestScriptService,
        db_session: Session,
    ) -> TestScriptResponse:
        """Get script by UUID.

        Args:
            uuid: Script UUID
            script_service: Script service instance
            db_session: Database session

        Returns:
            Script details

        Raises:
            NotFoundException: If script not found
        """
        script = script_service.get_script_by_uuid(db_session, uuid)
        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with UUID {uuid} not found")

        return TestScriptResponse.model_validate(script)

    @patch("/{script_id:int}")
    async def update_script(
        self,
        script_id: int,
        data: TestScriptUpdate,
        script_service: TestScriptService,
        db_session: Session,
    ) -> TestScriptResponse:
        """Update script.

        Args:
            script_id: Script ID
            data: Script update data
            script_service: Script service instance
            db_session: Database session

        Returns:
            Updated script

        Raises:
            NotFoundException: If script not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        script = script_service.update_script(db_session, script_id, **update_data)

        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        return TestScriptResponse.model_validate(script)

    @delete("/{script_id:int}", status_code=200)
    async def delete_script(
        self,
        script_id: int,
        script_service: TestScriptService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete script.

        Args:
            script_id: Script ID
            script_service: Script service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If script not found
        """
        success = script_service.delete_script(db_session, script_id)

        if not success:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        return {"message": "Script deleted successfully"}

    @post("/{script_id:int}/debug/enable")
    async def enable_debug_mode(
        self,
        script_id: int,
        script_service: TestScriptService,
        db_session: Session,
    ) -> TestScriptResponse:
        """Enable debug mode for script.

        Args:
            script_id: Script ID
            script_service: Script service instance
            db_session: Database session

        Returns:
            Updated script

        Raises:
            NotFoundException: If script not found
        """
        script = script_service.enable_debug_mode(db_session, script_id)

        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        return TestScriptResponse.model_validate(script)

    @post("/{script_id:int}/debug/disable")
    async def disable_debug_mode(
        self,
        script_id: int,
        script_service: TestScriptService,
        db_session: Session,
    ) -> TestScriptResponse:
        """Disable debug mode for script.

        Args:
            script_id: Script ID
            script_service: Script service instance
            db_session: Database session

        Returns:
            Updated script

        Raises:
            NotFoundException: If script not found
        """
        script = script_service.disable_debug_mode(db_session, script_id)

        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        return TestScriptResponse.model_validate(script)

    # Parameter management endpoints

    @post("/{script_id:int}/parameters")
    async def add_parameter(
        self,
        script_id: int,
        data: ScriptParameterCreate,
        script_service: TestScriptService,
        db_session: Session,
    ) -> ScriptParameterResponse:
        """Add parameter to script.

        Args:
            script_id: Script ID
            data: Parameter creation data
            script_service: Script service instance
            db_session: Database session

        Returns:
            Created parameter

        Raises:
            NotFoundException: If script not found
        """
        # Verify script exists
        script = script_service.get_script(db_session, script_id)
        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        parameter = script_service.add_parameter(
            db_session, script_id=script_id, **data.model_dump(exclude={"script_id"})
        )

        return ScriptParameterResponse.model_validate(parameter)

    @get("/{script_id:int}/parameters")
    async def get_script_parameters(
        self,
        script_id: int,
        script_service: TestScriptService,
        db_session: Session,
        required_only: Annotated[bool, Parameter(query="required_only")] = False,
    ) -> ScriptParameterListResponse:
        """Get script parameters.

        Args:
            script_id: Script ID
            script_service: Script service instance
            db_session: Database session
            required_only: Whether to return only required parameters

        Returns:
            List of script parameters

        Raises:
            NotFoundException: If script not found
        """
        # Verify script exists
        script = script_service.get_script(db_session, script_id)
        if not script:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Script with ID {script_id} not found")

        parameters = script_service.get_script_parameters(
            db_session, script_id, required_only=required_only
        )

        # Calculate pagination values
        total = len(parameters)
        page = 1
        page_size = total
        total_pages = 1 if total > 0 else 0

        return ScriptParameterListResponse(
            items=[ScriptParameterResponse.model_validate(p) for p in parameters],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @patch("/parameters/{parameter_id:int}")
    async def update_parameter(
        self,
        parameter_id: int,
        data: ScriptParameterUpdate,
        script_service: TestScriptService,
        db_session: Session,
    ) -> ScriptParameterResponse:
        """Update script parameter.

        Args:
            parameter_id: Parameter ID
            data: Parameter update data
            script_service: Script service instance
            db_session: Database session

        Returns:
            Updated parameter

        Raises:
            NotFoundException: If parameter not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        parameter = script_service.update_parameter(
            db_session, parameter_id, **update_data
        )

        if not parameter:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(
                detail=f"Parameter with ID {parameter_id} not found"
            )

        return ScriptParameterResponse.model_validate(parameter)

    @delete("/parameters/{parameter_id:int}", status_code=200)
    async def delete_parameter(
        self,
        parameter_id: int,
        script_service: TestScriptService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete script parameter.

        Args:
            parameter_id: Parameter ID
            script_service: Script service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If parameter not found
        """
        success = script_service.delete_parameter(db_session, parameter_id)

        if not success:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(
                detail=f"Parameter with ID {parameter_id} not found"
            )

        return {"message": "Parameter deleted successfully"}
