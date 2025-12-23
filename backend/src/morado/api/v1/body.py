"""Body management API endpoints.

This module provides REST API endpoints for managing request/response body components (Layer 1).
"""

from typing import Annotated

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.models.api_component import HeaderScope
from morado.schemas.api_component import (
    BodyCreate,
    BodyListResponse,
    BodyResponse,
    BodyUpdate,
)
from morado.services.api_component import BodyService
from sqlalchemy.orm import Session


def provide_body_service() -> BodyService:
    """Provide BodyService instance."""
    return BodyService()


class BodyController(Controller):
    """Controller for Body management endpoints."""

    path = "/bodies"
    tags = ["Bodies"]
    dependencies = {"body_service": Provide(provide_body_service)}

    @post("/")
    async def create_body(
        self,
        data: BodyCreate,
        body_service: BodyService,
        db_session: Session,
    ) -> BodyResponse:
        """Create a new body component.

        Args:
            data: Body creation data
            body_service: Body service instance
            db_session: Database session

        Returns:
            Created body

        Example:
            ```json
            {
                "name": "User Body",
                "body_type": "request",
                "example_data": {"name": "John", "email": "john@example.com"}
            }
            ```
        """
        body = body_service.create_body(db_session, **data.model_dump())
        return BodyResponse.model_validate(body)

    @get("/")
    async def list_bodies(
        self,
        body_service: BodyService,
        db_session: Session,
        body_type: Annotated[str | None, Parameter(query="body_type")] = None,
        body_scope: Annotated[HeaderScope | None, Parameter(query="scope")] = None,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> BodyListResponse:
        """List bodies with optional filtering.

        Args:
            body_service: Body service instance
            db_session: Database session
            body_type: Filter by body type (request/response/both)
            body_scope: Filter by scope
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bodies with pagination info
        """
        bodies = body_service.list_bodies(
            db_session, body_type=body_type, scope=body_scope, skip=skip, limit=limit
        )

        # Calculate pagination values
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (len(bodies) + limit - 1) // limit if limit > 0 else 1

        return BodyListResponse(
            items=[BodyResponse.model_validate(b) for b in bodies],
            total=len(bodies),
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    @get("/search")
    async def search_bodies(
        self,
        body_service: BodyService,
        db_session: Session,
        name: Annotated[str, Parameter(query="name", min_length=1)],
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> BodyListResponse:
        """Search bodies by name.

        Args:
            body_service: Body service instance
            db_session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching bodies
        """
        bodies = body_service.search_bodies(
            db_session, name=name, skip=skip, limit=limit
        )

        # Calculate pagination values
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (len(bodies) + limit - 1) // limit if limit > 0 else 1

        return BodyListResponse(
            items=[BodyResponse.model_validate(b) for b in bodies],
            total=len(bodies),
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    @get("/{body_id:int}")
    async def get_body(
        self,
        body_id: int,
        body_service: BodyService,
        db_session: Session,
    ) -> BodyResponse:
        """Get body by ID.

        Args:
            body_id: Body ID
            body_service: Body service instance
            db_session: Database session

        Returns:
            Body details

        Raises:
            NotFoundException: If body not found
        """
        body = body_service.get_body(db_session, body_id)
        if not body:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Body with ID {body_id} not found")

        return BodyResponse.model_validate(body)

    @get("/uuid/{uuid:str}")
    async def get_body_by_uuid(
        self,
        uuid: str,
        body_service: BodyService,
        db_session: Session,
    ) -> BodyResponse:
        """Get body by UUID.

        Args:
            uuid: Body UUID
            body_service: Body service instance
            db_session: Database session

        Returns:
            Body details

        Raises:
            NotFoundException: If body not found
        """
        body = body_service.get_body_by_uuid(db_session, uuid)
        if not body:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Body with UUID {uuid} not found")

        return BodyResponse.model_validate(body)

    @patch("/{body_id:int}")
    async def update_body(
        self,
        body_id: int,
        data: BodyUpdate,
        body_service: BodyService,
        db_session: Session,
    ) -> BodyResponse:
        """Update body.

        Args:
            body_id: Body ID
            data: Body update data
            body_service: Body service instance
            db_session: Database session

        Returns:
            Updated body

        Raises:
            NotFoundException: If body not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        body = body_service.update_body(db_session, body_id, **update_data)

        if not body:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Body with ID {body_id} not found")

        return BodyResponse.model_validate(body)

    @delete("/{body_id:int}", status_code=200)
    async def delete_body(
        self,
        body_id: int,
        body_service: BodyService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete body.

        Args:
            body_id: Body ID
            body_service: Body service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If body not found
        """
        success = body_service.delete_body(db_session, body_id)

        if not success:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Body with ID {body_id} not found")

        return {"message": "Body deleted successfully"}
