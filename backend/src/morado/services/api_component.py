"""Service layer for Layer 1: API Component management.

This module provides business logic for managing Header, Body, and ApiDefinition components.
"""

from typing import Any

from sqlalchemy.orm import Session

from morado.common.logger import get_logger
from morado.common.logger.context import get_log_context
from morado.models.api_component import ApiDefinition, Body, Header, HeaderScope
from morado.repositories.api_component import (
    ApiDefinitionRepository,
    BodyRepository,
    HeaderRepository,
)

logger = get_logger(__name__)


class HeaderService:
    """Service for managing HTTP header components.

    Provides business logic for creating, updating, and managing header components.

    Example:
        >>> service = HeaderService()
        >>> header = service.create_header(
        ...     session,
        ...     name="Auth Header",
        ...     headers={"Authorization": "Bearer ${token}"},
        ...     scope=HeaderScope.GLOBAL
        ... )
    """

    def __init__(self):
        """Initialize Header service."""
        self.repository = HeaderRepository()

    def create_header(
        self,
        session: Session,
        name: str,
        headers: dict[str, str],
        description: str | None = None,
        scope: HeaderScope = HeaderScope.PRIVATE,
        project_id: int | None = None,
        tags: list[str] | None = None,
        created_by: int | None = None,
        **kwargs: Any,
    ) -> Header:
        """Create a new header component.

        Args:
            session: Database session
            name: Header name
            headers: Header key-value pairs
            description: Header description
            scope: Header scope (global/project/private)
            project_id: Project ID (required if scope is project)
            tags: Tags for categorization
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created Header instance

        Raises:
            ValueError: If scope is project but project_id is not provided

        Example:
            >>> header = service.create_header(
            ...     session,
            ...     name="JSON Content-Type",
            ...     headers={"Content-Type": "application/json"},
            ...     scope=HeaderScope.GLOBAL
            ... )
        """
        logger.info(
            "Creating header component",
            extra={
                **get_log_context(),  # Include request_id and other context
                "header_name": name,
                "scope": scope.value,
                "project_id": project_id,
                "header_count": len(headers),
            },
        )

        # Validate scope and project_id
        if scope == HeaderScope.PROJECT and not project_id:
            logger.error(
                "Validation failed: project_id required for PROJECT scope",
                extra={
                    **get_log_context(),
                    "header_name": name,
                    "scope": scope.value,
                },
            )
            raise ValueError("project_id is required when scope is PROJECT")

        try:
            # Create header
            header = self.repository.create(
                session,
                name=name,
                description=description,
                headers=headers,
                scope=scope,
                project_id=project_id,
                tags=tags,
                created_by=created_by,
                **kwargs,
            )

            session.commit()

            logger.info(
                "Header component created successfully",
                extra={
                    **get_log_context(),
                    "header_id": header.id,
                    "header_uuid": str(header.uuid),
                    "header_name": name,
                },
            )

            return header

        except Exception as e:
            logger.exception(
                "Failed to create header component",
                extra={
                    **get_log_context(),
                    "header_name": name,
                    "error": str(e),
                },
            )
            session.rollback()
            raise

    def get_header(self, session: Session, header_id: int) -> Header | None:
        """Get header by ID.

        Args:
            session: Database session
            header_id: Header ID

        Returns:
            Header instance or None if not found
        """
        return self.repository.get_by_id(session, header_id)

    def get_header_by_uuid(self, session: Session, uuid: str) -> Header | None:
        """Get header by UUID.

        Args:
            session: Database session
            uuid: Header UUID

        Returns:
            Header instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_headers(
        self,
        session: Session,
        scope: HeaderScope | None = None,
        project_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Header]:
        """List headers with optional filtering.

        Args:
            session: Database session
            scope: Filter by scope
            project_id: Filter by project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances
        """
        if scope:
            return self.repository.get_by_scope(session, scope, skip, limit)
        elif project_id:
            return self.repository.get_by_project(session, project_id, skip, limit)
        else:
            return self.repository.get_all(session, skip, limit)

    def search_headers(
        self, session: Session, name: str, skip: int = 0, limit: int = 100
    ) -> list[Header]:
        """Search headers by name.

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Header instances
        """
        return self.repository.search_by_name(session, name, skip, limit)

    def update_header(
        self, session: Session, header_id: int, **kwargs: Any
    ) -> Header | None:
        """Update header.

        Args:
            session: Database session
            header_id: Header ID
            **kwargs: Fields to update

        Returns:
            Updated Header instance or None if not found
        """
        header = self.repository.get_by_id(session, header_id)
        if not header:
            return None

        updated_header = self.repository.update(session, header, **kwargs)
        session.commit()
        return updated_header

    def delete_header(self, session: Session, header_id: int) -> bool:
        """Delete header.

        Args:
            session: Database session
            header_id: Header ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, header_id)
        if result:
            session.commit()
        return result

    def activate_header(self, session: Session, header_id: int) -> Header | None:
        """Activate header.

        Args:
            session: Database session
            header_id: Header ID

        Returns:
            Updated Header instance or None if not found
        """
        return self.update_header(session, header_id, is_active=True)

    def deactivate_header(self, session: Session, header_id: int) -> Header | None:
        """Deactivate header.

        Args:
            session: Database session
            header_id: Header ID

        Returns:
            Updated Header instance or None if not found
        """
        return self.update_header(session, header_id, is_active=False)


class BodyService:
    """Service for managing request/response body components.

    Provides business logic for creating, updating, and managing body components.

    Example:
        >>> service = BodyService()
        >>> body = service.create_body(
        ...     session,
        ...     name="User Body",
        ...     body_type=BodyType.REQUEST,
        ...     example_data={"name": "John", "email": "john@example.com"}
        ... )
    """

    def __init__(self):
        """Initialize Body service."""
        self.repository = BodyRepository()

    def create_body(  # noqa: PLR0913
        self,
        session: Session,
        name: str,
        body_type: str,
        description: str | None = None,
        content_type: str = "application/json",
        body_schema: dict | None = None,
        example_data: dict | None = None,
        scope: HeaderScope = HeaderScope.PRIVATE,
        project_id: int | None = None,
        tags: list[str] | None = None,
        created_by: int | None = None,
        **kwargs: Any,
    ) -> Body:
        """Create a new body component.

        Args:
            session: Database session
            name: Body name
            body_type: Body type (request/response/both)
            description: Body description
            content_type: Content type
            body_schema: JSON Schema definition
            example_data: Example data
            scope: Body scope (global/project/private)
            project_id: Project ID (required if scope is project)
            tags: Tags for categorization
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created Body instance

        Raises:
            ValueError: If scope is project but project_id is not provided
        """
        # Validate scope and project_id
        if scope == HeaderScope.PROJECT and not project_id:
            raise ValueError("project_id is required when scope is PROJECT")

        # Create body
        body = self.repository.create(
            session,
            name=name,
            description=description,
            body_type=body_type,
            content_type=content_type,
            body_schema=body_schema,
            example_data=example_data,
            scope=scope,
            project_id=project_id,
            tags=tags,
            created_by=created_by,
            **kwargs,
        )

        session.commit()
        return body

    def get_body(self, session: Session, body_id: int) -> Body | None:
        """Get body by ID.

        Args:
            session: Database session
            body_id: Body ID

        Returns:
            Body instance or None if not found
        """
        return self.repository.get_by_id(session, body_id)

    def get_body_by_uuid(self, session: Session, uuid: str) -> Body | None:
        """Get body by UUID.

        Args:
            session: Database session
            uuid: Body UUID

        Returns:
            Body instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_bodies(
        self,
        session: Session,
        body_type: str | None = None,
        scope: HeaderScope | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Body]:
        """List bodies with optional filtering.

        Args:
            session: Database session
            body_type: Filter by body type
            scope: Filter by scope
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        if body_type:
            return self.repository.get_by_type(session, body_type, skip, limit)
        elif scope:
            return self.repository.get_by_scope(session, scope, skip, limit)
        else:
            return self.repository.get_all(session, skip, limit)

    def search_bodies(
        self, session: Session, name: str, skip: int = 0, limit: int = 100
    ) -> list[Body]:
        """Search bodies by name.

        Args:
            session: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Body instances
        """
        return self.repository.search_by_name(session, name, skip, limit)

    def update_body(self, session: Session, body_id: int, **kwargs: Any) -> Body | None:
        """Update body.

        Args:
            session: Database session
            body_id: Body ID
            **kwargs: Fields to update

        Returns:
            Updated Body instance or None if not found
        """
        body = self.repository.get_by_id(session, body_id)
        if not body:
            return None

        updated_body = self.repository.update(session, body, **kwargs)
        session.commit()
        return updated_body

    def delete_body(self, session: Session, body_id: int) -> bool:
        """Delete body.

        Args:
            session: Database session
            body_id: Body ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, body_id)
        if result:
            session.commit()
        return result


class ApiDefinitionService:
    """Service for managing API definitions.

    Provides business logic for creating, updating, and managing API definitions
    that combine headers and bodies.

    Example:
        >>> service = ApiDefinitionService()
        >>> api_def = service.create_api_definition(
        ...     session,
        ...     name="Get User",
        ...     method=HttpMethod.GET,
        ...     path="/api/users/{id}",
        ...     header_id=1,
        ...     response_body_id=2
        ... )
    """

    def __init__(self):
        """Initialize ApiDefinition service."""
        self.repository = ApiDefinitionRepository()

    def create_api_definition(  # noqa: PLR0913
        self,
        session: Session,
        name: str,
        method: str,
        path: str,
        description: str | None = None,
        base_url: str | None = None,
        header_id: int | None = None,
        request_body_id: int | None = None,
        response_body_id: int | None = None,
        inline_request_body: dict | None = None,
        inline_response_body: dict | None = None,
        query_parameters: dict | None = None,
        path_parameters: dict | None = None,
        timeout: int = 30,
        tags: list[str] | None = None,
        created_by: int | None = None,
        **kwargs: Any,
    ) -> ApiDefinition:
        """Create a new API definition.

        Supports two modes:
        1. Reference mode: Use header_id, request_body_id, response_body_id
        2. Inline mode: Use header_id with inline_request_body, inline_response_body

        Args:
            session: Database session
            name: API name
            method: HTTP method
            path: API path
            description: API description
            base_url: Base URL
            header_id: Header component ID
            request_body_id: Request body component ID
            response_body_id: Response body component ID
            inline_request_body: Inline request body
            inline_response_body: Inline response body
            query_parameters: Query parameter definitions
            path_parameters: Path parameter definitions
            timeout: Timeout in seconds
            tags: Tags for categorization
            created_by: Creator user ID
            **kwargs: Additional fields

        Returns:
            Created ApiDefinition instance
        """
        # Create API definition
        api_def = self.repository.create(
            session,
            name=name,
            description=description,
            method=method,
            path=path,
            base_url=base_url,
            header_id=header_id,
            request_body_id=request_body_id,
            response_body_id=response_body_id,
            inline_request_body=inline_request_body,
            inline_response_body=inline_response_body,
            query_parameters=query_parameters,
            path_parameters=path_parameters,
            timeout=timeout,
            tags=tags,
            created_by=created_by,
            **kwargs,
        )

        session.commit()
        return api_def

    def get_api_definition(
        self, session: Session, api_def_id: int, with_relations: bool = False
    ) -> ApiDefinition | None:
        """Get API definition by ID.

        Args:
            session: Database session
            api_def_id: API definition ID
            with_relations: Whether to load related header and body components

        Returns:
            ApiDefinition instance or None if not found
        """
        if with_relations:
            return self.repository.get_with_relations(session, api_def_id)
        else:
            return self.repository.get_by_id(session, api_def_id)

    def get_api_definition_by_uuid(
        self, session: Session, uuid: str
    ) -> ApiDefinition | None:
        """Get API definition by UUID.

        Args:
            session: Database session
            uuid: API definition UUID

        Returns:
            ApiDefinition instance or None if not found
        """
        return self.repository.get_by_uuid(session, uuid)

    def list_api_definitions(
        self,
        session: Session,
        method: str | None = None,
        header_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ApiDefinition]:
        """List API definitions with optional filtering.

        Args:
            session: Database session
            method: Filter by HTTP method
            header_id: Filter by header ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        if method:
            return self.repository.get_by_method(session, method, skip, limit)
        elif header_id:
            return self.repository.get_by_header(session, header_id, skip, limit)
        else:
            return self.repository.get_all(session, skip, limit)

    def search_api_definitions(
        self, session: Session, path: str, skip: int = 0, limit: int = 100
    ) -> list[ApiDefinition]:
        """Search API definitions by path.

        Args:
            session: Database session
            path: Path to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of ApiDefinition instances
        """
        return self.repository.search_by_path(session, path, skip, limit)

    def update_api_definition(
        self, session: Session, api_def_id: int, **kwargs: Any
    ) -> ApiDefinition | None:
        """Update API definition.

        Args:
            session: Database session
            api_def_id: API definition ID
            **kwargs: Fields to update

        Returns:
            Updated ApiDefinition instance or None if not found
        """
        api_def = self.repository.get_by_id(session, api_def_id)
        if not api_def:
            return None

        updated_api_def = self.repository.update(session, api_def, **kwargs)
        session.commit()
        return updated_api_def

    def delete_api_definition(self, session: Session, api_def_id: int) -> bool:
        """Delete API definition.

        Args:
            session: Database session
            api_def_id: API definition ID

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete_by_id(session, api_def_id)
        if result:
            session.commit()
        return result

    def get_full_api_definition(
        self, session: Session, api_def_id: int
    ) -> dict[str, Any] | None:
        """Get complete API definition with all components resolved.

        This method returns a dictionary with the API definition and all
        referenced components (header, request body, response body) fully loaded.

        Args:
            session: Database session
            api_def_id: API definition ID

        Returns:
            Dictionary with complete API definition or None if not found
        """
        api_def = self.repository.get_with_relations(session, api_def_id)
        if not api_def:
            return None

        result = {
            "id": api_def.id,
            "uuid": api_def.uuid,
            "name": api_def.name,
            "description": api_def.description,
            "method": api_def.method,
            "path": api_def.path,
            "base_url": api_def.base_url,
            "timeout": api_def.timeout,
            "query_parameters": api_def.query_parameters,
            "path_parameters": api_def.path_parameters,
            "header": None,
            "request_body": None,
            "response_body": None,
        }

        # Add header if present
        if api_def.header:
            result["header"] = {
                "id": api_def.header.id,
                "name": api_def.header.name,
                "headers": api_def.header.headers,
            }

        # Add request body (either referenced or inline)
        if api_def.request_body:
            result["request_body"] = {
                "id": api_def.request_body.id,
                "name": api_def.request_body.name,
                "content_type": api_def.request_body.content_type,
                "body_schema": api_def.request_body.body_schema,
                "example_data": api_def.request_body.example_data,
            }
        elif api_def.inline_request_body:
            result["request_body"] = {
                "inline": True,
                "data": api_def.inline_request_body,
            }

        # Add response body (either referenced or inline)
        if api_def.response_body:
            result["response_body"] = {
                "id": api_def.response_body.id,
                "name": api_def.response_body.name,
                "content_type": api_def.response_body.content_type,
                "body_schema": api_def.response_body.body_schema,
                "example_data": api_def.response_body.example_data,
            }
        elif api_def.inline_response_body:
            result["response_body"] = {
                "inline": True,
                "data": api_def.inline_response_body,
            }

        return result
