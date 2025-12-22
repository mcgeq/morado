"""API Definition management API endpoints.

This module provides REST API endpoints for managing API definitions (Layer 1).
"""

from typing import Annotated, Any

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.schemas.api_component import (
    ApiDefinitionCreate,
    ApiDefinitionListResponse,
    ApiDefinitionResponse,
    ApiDefinitionUpdate,
)
from morado.services.api_component import ApiDefinitionService
from sqlalchemy.orm import Session


def provide_api_definition_service() -> ApiDefinitionService:
    """Provide ApiDefinitionService instance."""
    return ApiDefinitionService()


class ApiDefinitionController(Controller):
    """Controller for API Definition management endpoints."""

    path = "/api-definitions"
    tags = ["API Definitions"]
    dependencies = {"api_definition_service": Provide(provide_api_definition_service)}

    @post("/")
    async def create_api_definition(
        self,
        data: ApiDefinitionCreate,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
    ) -> ApiDefinitionResponse:
        """Create a new API definition.

        Supports two modes:
        1. Reference mode: Use header_id, request_body_id, response_body_id
        2. Inline mode: Use header_id with inline_request_body, inline_response_body

        Args:
            data: API definition creation data
            api_definition_service: API definition service instance
            db_session: Database session

        Returns:
            Created API definition

        Example:
            ```json
            {
                "name": "Get User",
                "method": "GET",
                "path": "/api/users/{id}",
                "header_id": 1,
                "response_body_id": 2
            }
            ```
        """
        api_def = api_definition_service.create_api_definition(
            db_session,
            **data.model_dump()
        )
        return ApiDefinitionResponse.model_validate(api_def)

    @get("/")
    async def list_api_definitions(
        self,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
        method: Annotated[str | None, Parameter(query="method")] = None,
        header_id: Annotated[int | None, Parameter(query="header_id")] = None,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> ApiDefinitionListResponse:
        """List API definitions with optional filtering.

        Args:
            api_definition_service: API definition service instance
            db_session: Database session
            method: Filter by HTTP method
            header_id: Filter by header ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of API definitions with pagination info
        """
        api_defs = api_definition_service.list_api_definitions(
            db_session,
            method=method,
            header_id=header_id,
            skip=skip,
            limit=limit
        )

        return ApiDefinitionListResponse(
            items=[ApiDefinitionResponse.model_validate(a) for a in api_defs],
            total=len(api_defs),
            skip=skip,
            limit=limit
        )

    @get("/search")
    async def search_api_definitions(
        self,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
        path: Annotated[str, Parameter(query="path", min_length=1)],
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> ApiDefinitionListResponse:
        """Search API definitions by path.

        Args:
            api_definition_service: API definition service instance
            db_session: Database session
            path: Path to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching API definitions
        """
        api_defs = api_definition_service.search_api_definitions(
            db_session,
            path=path,
            skip=skip,
            limit=limit
        )

        return ApiDefinitionListResponse(
            items=[ApiDefinitionResponse.model_validate(a) for a in api_defs],
            total=len(api_defs),
            skip=skip,
            limit=limit
        )

    @get("/{api_def_id:int}")
    async def get_api_definition(
        self,
        api_def_id: int,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
        with_relations: Annotated[bool, Parameter(query="with_relations")] = False,
    ) -> ApiDefinitionResponse:
        """Get API definition by ID.

        Args:
            api_def_id: API definition ID
            api_definition_service: API definition service instance
            db_session: Database session
            with_relations: Whether to load related header and body components

        Returns:
            API definition details

        Raises:
            NotFoundException: If API definition not found
        """
        api_def = api_definition_service.get_api_definition(
            db_session,
            api_def_id,
            with_relations=with_relations
        )
        if not api_def:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"API definition with ID {api_def_id} not found")

        return ApiDefinitionResponse.model_validate(api_def)

    @get("/{api_def_id:int}/full")
    async def get_full_api_definition(
        self,
        api_def_id: int,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
    ) -> dict[str, Any]:
        """Get complete API definition with all components resolved.

        This endpoint returns the API definition with all referenced components
        (header, request body, response body) fully loaded.

        Args:
            api_def_id: API definition ID
            api_definition_service: API definition service instance
            db_session: Database session

        Returns:
            Complete API definition with all components

        Raises:
            NotFoundException: If API definition not found
        """
        full_api_def = api_definition_service.get_full_api_definition(
            db_session,
            api_def_id
        )
        if not full_api_def:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"API definition with ID {api_def_id} not found")

        return full_api_def

    @get("/uuid/{uuid:str}")
    async def get_api_definition_by_uuid(
        self,
        uuid: str,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
    ) -> ApiDefinitionResponse:
        """Get API definition by UUID.

        Args:
            uuid: API definition UUID
            api_definition_service: API definition service instance
            db_session: Database session

        Returns:
            API definition details

        Raises:
            NotFoundException: If API definition not found
        """
        api_def = api_definition_service.get_api_definition_by_uuid(db_session, uuid)
        if not api_def:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"API definition with UUID {uuid} not found")

        return ApiDefinitionResponse.model_validate(api_def)

    @patch("/{api_def_id:int}")
    async def update_api_definition(
        self,
        api_def_id: int,
        data: ApiDefinitionUpdate,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
    ) -> ApiDefinitionResponse:
        """Update API definition.

        Args:
            api_def_id: API definition ID
            data: API definition update data
            api_definition_service: API definition service instance
            db_session: Database session

        Returns:
            Updated API definition

        Raises:
            NotFoundException: If API definition not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        api_def = api_definition_service.update_api_definition(
            db_session,
            api_def_id,
            **update_data
        )

        if not api_def:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"API definition with ID {api_def_id} not found")

        return ApiDefinitionResponse.model_validate(api_def)

    @delete("/{api_def_id:int}", status_code=200)
    async def delete_api_definition(
        self,
        api_def_id: int,
        api_definition_service: ApiDefinitionService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete API definition.

        Args:
            api_def_id: API definition ID
            api_definition_service: API definition service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If API definition not found
        """
        success = api_definition_service.delete_api_definition(db_session, api_def_id)

        if not success:
            from litestar.exceptions import NotFoundException
            raise NotFoundException(detail=f"API definition with ID {api_def_id} not found")

        return {"message": "API definition deleted successfully"}
