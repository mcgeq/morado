"""Header management API endpoints.

This module provides REST API endpoints for managing HTTP header components (Layer 1).
"""

from typing import Annotated

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter
from morado.models.api_component import HeaderScope
from morado.schemas.api_component import (
    HeaderCreate,
    HeaderListResponse,
    HeaderResponse,
    HeaderUpdate,
)
from morado.services.api_component import HeaderService
from sqlalchemy.orm import Session


def provide_header_service() -> HeaderService:
    """Provide HeaderService instance."""
    return HeaderService()


class HeaderController(Controller):
    """Controller for Header management endpoints."""

    path = "/headers"
    tags = ["Headers"]
    dependencies = {"header_service": Provide(provide_header_service)}

    @post("/")
    async def create_header(
        self,
        data: HeaderCreate,
        header_service: HeaderService,
        db_session: Session,
    ) -> HeaderResponse:
        """Create a new header component.

        Args:
            data: Header creation data
            header_service: Header service instance
            db_session: Database session

        Returns:
            Created header

        Example:
            ```json
            {
                "name": "Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global"
            }
            ```
        """
        header = header_service.create_header(db_session, **data.model_dump())
        return HeaderResponse.model_validate(header)

    @get("/")
    async def list_headers(
        self,
        header_service: HeaderService,
        db_session: Session,
        header_scope: Annotated[HeaderScope | None, Parameter(query="scope")] = None,
        project_id: Annotated[int | None, Parameter(query="project_id")] = None,
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> HeaderListResponse:
        """List headers with optional filtering.

        Args:
            header_service: Header service instance
            db_session: Database session
            header_scope: Filter by scope
            project_id: Filter by project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of headers with pagination info
        """
        headers = header_service.list_headers(
            db_session,
            scope=header_scope,
            project_id=project_id,
            skip=skip,
            limit=limit,
        )

        # Calculate pagination values
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (len(headers) + limit - 1) // limit if limit > 0 else 1

        return HeaderListResponse(
            items=[HeaderResponse.model_validate(h) for h in headers],
            total=len(headers),
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    @get("/search")
    async def search_headers(
        self,
        header_service: HeaderService,
        db_session: Session,
        name: Annotated[str, Parameter(query="name", min_length=1)],
        skip: Annotated[int, Parameter(query="skip", ge=0)] = 0,
        limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 100,
    ) -> HeaderListResponse:
        """Search headers by name.

        Args:
            header_service: Header service instance
            db_session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching headers
        """
        headers = header_service.search_headers(
            db_session, name=name, skip=skip, limit=limit
        )

        # Calculate pagination values
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (len(headers) + limit - 1) // limit if limit > 0 else 1

        return HeaderListResponse(
            items=[HeaderResponse.model_validate(h) for h in headers],
            total=len(headers),
            page=page,
            page_size=limit,
            total_pages=total_pages,
        )

    @get("/{header_id:int}")
    async def get_header(
        self,
        header_id: int,
        header_service: HeaderService,
        db_session: Session,
    ) -> HeaderResponse:
        """Get header by ID.

        Args:
            header_id: Header ID
            header_service: Header service instance
            db_session: Database session

        Returns:
            Header details

        Raises:
            NotFoundException: If header not found
        """
        header = header_service.get_header(db_session, header_id)
        if not header:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Header with ID {header_id} not found")

        return HeaderResponse.model_validate(header)

    @get("/uuid/{uuid:str}")
    async def get_header_by_uuid(
        self,
        uuid: str,
        header_service: HeaderService,
        db_session: Session,
    ) -> HeaderResponse:
        """Get header by UUID.

        Args:
            uuid: Header UUID
            header_service: Header service instance
            db_session: Database session

        Returns:
            Header details

        Raises:
            NotFoundException: If header not found
        """
        header = header_service.get_header_by_uuid(db_session, uuid)
        if not header:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Header with UUID {uuid} not found")

        return HeaderResponse.model_validate(header)

    @patch("/{header_id:int}")
    async def update_header(
        self,
        header_id: int,
        data: HeaderUpdate,
        header_service: HeaderService,
        db_session: Session,
    ) -> HeaderResponse:
        """Update header.

        Args:
            header_id: Header ID
            data: Header update data
            header_service: Header service instance
            db_session: Database session

        Returns:
            Updated header

        Raises:
            NotFoundException: If header not found
        """
        # Only include fields that were actually provided
        update_data = data.model_dump(exclude_unset=True)

        header = header_service.update_header(db_session, header_id, **update_data)

        if not header:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Header with ID {header_id} not found")

        return HeaderResponse.model_validate(header)

    @delete("/{header_id:int}", status_code=200)
    async def delete_header(
        self,
        header_id: int,
        header_service: HeaderService,
        db_session: Session,
    ) -> dict[str, str]:
        """Delete header.

        Args:
            header_id: Header ID
            header_service: Header service instance
            db_session: Database session

        Returns:
            Success message

        Raises:
            NotFoundException: If header not found
        """
        success = header_service.delete_header(db_session, header_id)

        if not success:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Header with ID {header_id} not found")

        return {"message": "Header deleted successfully"}

    @post("/{header_id:int}/activate")
    async def activate_header(
        self,
        header_id: int,
        header_service: HeaderService,
        db_session: Session,
    ) -> HeaderResponse:
        """Activate header.

        Args:
            header_id: Header ID
            header_service: Header service instance
            db_session: Database session

        Returns:
            Updated header

        Raises:
            NotFoundException: If header not found
        """
        header = header_service.activate_header(db_session, header_id)

        if not header:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Header with ID {header_id} not found")

        return HeaderResponse.model_validate(header)

    @post("/{header_id:int}/deactivate")
    async def deactivate_header(
        self,
        header_id: int,
        header_service: HeaderService,
        db_session: Session,
    ) -> HeaderResponse:
        """Deactivate header.

        Args:
            header_id: Header ID
            header_service: Header service instance
            db_session: Database session

        Returns:
            Updated header

        Raises:
            NotFoundException: If header not found
        """
        header = header_service.deactivate_header(db_session, header_id)

        if not header:
            from litestar.exceptions import NotFoundException

            raise NotFoundException(detail=f"Header with ID {header_id} not found")

        return HeaderResponse.model_validate(header)
