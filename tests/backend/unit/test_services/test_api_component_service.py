"""Unit tests for API Component Service layer.

Tests business logic for Header, Body, and ApiDefinition services.
"""

import pytest
from morado.models.api_component import HeaderScope, HttpMethod
from morado.services.api_component import (
    ApiDefinitionService,
    BodyService,
    HeaderService,
)
from sqlalchemy.orm import Session


class TestHeaderService:
    """Test HeaderService business logic."""

    @pytest.fixture
    def service(self):
        """Create HeaderService instance."""
        return HeaderService()

    def test_create_header_success(self, service: HeaderService, db_session: Session):
        """Test successful header creation."""
        header = service.create_header(
            db_session,
            name="Test Header",
            headers={"Authorization": "Bearer ${token}"},
            scope=HeaderScope.GLOBAL
        )

        assert header.id is not None
        assert header.name == "Test Header"
        assert header.headers == {"Authorization": "Bearer ${token}"}
        assert header.scope == HeaderScope.GLOBAL
        assert header.is_active is True

    def test_create_header_with_project_scope_requires_project_id(
        self, service: HeaderService, db_session: Session
    ):
        """Test that PROJECT scope requires project_id."""
        with pytest.raises(ValueError, match="project_id is required"):
            service.create_header(
                db_session,
                name="Project Header",
                headers={"Content-Type": "application/json"},
                scope=HeaderScope.PROJECT
            )

    def test_create_header_with_project_scope_success(
        self, service: HeaderService, db_session: Session
    ):
        """Test successful header creation with PROJECT scope."""
        header = service.create_header(
            db_session,
            name="Project Header",
            headers={"Content-Type": "application/json"},
            scope=HeaderScope.PROJECT,
            project_id=1
        )

        assert header.id is not None
        assert header.scope == HeaderScope.PROJECT
        assert header.project_id == 1

    def test_get_header_by_id(self, service: HeaderService, db_session: Session):
        """Test retrieving header by ID."""
        created = service.create_header(
            db_session,
            name="Test Header",
            headers={"X-Custom": "value"}
        )

        retrieved = service.get_header(db_session, created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Header"

    def test_get_header_by_uuid(self, service: HeaderService, db_session: Session):
        """Test retrieving header by UUID."""
        created = service.create_header(
            db_session,
            name="Test Header",
            headers={"X-Custom": "value"}
        )

        retrieved = service.get_header_by_uuid(db_session, created.uuid)
        assert retrieved is not None
        assert retrieved.uuid == created.uuid
        assert retrieved.name == "Test Header"

    def test_list_headers_by_scope(self, service: HeaderService, db_session: Session):
        """Test listing headers filtered by scope."""
        service.create_header(
            db_session,
            name="Global Header",
            headers={"X-Global": "value"},
            scope=HeaderScope.GLOBAL
        )
        service.create_header(
            db_session,
            name="Private Header",
            headers={"X-Private": "value"},
            scope=HeaderScope.PRIVATE
        )

        global_headers = service.list_headers(db_session, scope=HeaderScope.GLOBAL)
        assert len(global_headers) == 1
        assert global_headers[0].name == "Global Header"

    def test_search_headers_by_name(self, service: HeaderService, db_session: Session):
        """Test searching headers by name."""
        service.create_header(
            db_session,
            name="Auth Header",
            headers={"Authorization": "Bearer token"}
        )
        service.create_header(
            db_session,
            name="Content Header",
            headers={"Content-Type": "application/json"}
        )

        results = service.search_headers(db_session, "Auth")
        assert len(results) == 1
        assert results[0].name == "Auth Header"

    def test_update_header(self, service: HeaderService, db_session: Session):
        """Test updating header."""
        header = service.create_header(
            db_session,
            name="Original Name",
            headers={"X-Test": "value"}
        )

        updated = service.update_header(
            db_session,
            header.id,
            name="Updated Name",
            headers={"X-Test": "new_value"}
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.headers == {"X-Test": "new_value"}

    def test_delete_header(self, service: HeaderService, db_session: Session):
        """Test deleting header."""
        header = service.create_header(
            db_session,
            name="To Delete",
            headers={"X-Test": "value"}
        )

        result = service.delete_header(db_session, header.id)
        assert result is True

        retrieved = service.get_header(db_session, header.id)
        assert retrieved is None

    def test_activate_deactivate_header(
        self, service: HeaderService, db_session: Session
    ):
        """Test activating and deactivating header."""
        header = service.create_header(
            db_session,
            name="Test Header",
            headers={"X-Test": "value"}
        )

        deactivated = service.deactivate_header(db_session, header.id)
        assert deactivated is not None
        assert deactivated.is_active is False

        activated = service.activate_header(db_session, header.id)
        assert activated is not None
        assert activated.is_active is True


class TestBodyService:
    """Test BodyService business logic."""

    @pytest.fixture
    def service(self):
        """Create BodyService instance."""
        return BodyService()

    def test_create_body_success(self, service: BodyService, db_session: Session):
        """Test successful body creation."""
        body = service.create_body(
            db_session,
            name="User Body",
            body_type="request",
            example_data={"name": "John", "email": "john@example.com"}
        )

        assert body.id is not None
        assert body.name == "User Body"
        assert body.body_type == "request"
        assert body.example_data == {"name": "John", "email": "john@example.com"}

    def test_create_body_with_project_scope_requires_project_id(
        self, service: BodyService, db_session: Session
    ):
        """Test that PROJECT scope requires project_id."""
        with pytest.raises(ValueError, match="project_id is required"):
            service.create_body(
                db_session,
                name="Project Body",
                body_type="request",
                scope=HeaderScope.PROJECT
            )

    def test_list_bodies_by_type(self, service: BodyService, db_session: Session):
        """Test listing bodies filtered by type."""
        service.create_body(
            db_session,
            name="Request Body",
            body_type="request"
        )
        service.create_body(
            db_session,
            name="Response Body",
            body_type="response"
        )

        request_bodies = service.list_bodies(db_session, body_type="request")
        assert len(request_bodies) == 1
        assert request_bodies[0].name == "Request Body"

    def test_update_body(self, service: BodyService, db_session: Session):
        """Test updating body."""
        body = service.create_body(
            db_session,
            name="Original Body",
            body_type="request"
        )

        updated = service.update_body(
            db_session,
            body.id,
            name="Updated Body",
            example_data={"updated": True}
        )

        assert updated is not None
        assert updated.name == "Updated Body"
        assert updated.example_data == {"updated": True}


class TestApiDefinitionService:
    """Test ApiDefinitionService business logic."""

    @pytest.fixture
    def service(self):
        """Create ApiDefinitionService instance."""
        return ApiDefinitionService()

    @pytest.fixture
    def header_service(self):
        """Create HeaderService instance."""
        return HeaderService()

    @pytest.fixture
    def body_service(self):
        """Create BodyService instance."""
        return BodyService()

    def test_create_api_definition_with_references(
        self,
        service: ApiDefinitionService,
        header_service: HeaderService,
        body_service: BodyService,
        db_session: Session
    ):
        """Test creating API definition with referenced components."""
        # Create header and bodies
        header = header_service.create_header(
            db_session,
            name="Auth Header",
            headers={"Authorization": "Bearer ${token}"}
        )
        request_body = body_service.create_body(
            db_session,
            name="User Request",
            body_type="request"
        )
        response_body = body_service.create_body(
            db_session,
            name="User Response",
            body_type="response"
        )

        # Create API definition
        api_def = service.create_api_definition(
            db_session,
            name="Get User",
            method=HttpMethod.GET,
            path="/api/users/{id}",
            header_id=header.id,
            request_body_id=request_body.id,
            response_body_id=response_body.id
        )

        assert api_def.id is not None
        assert api_def.name == "Get User"
        assert api_def.method == HttpMethod.GET
        assert api_def.header_id == header.id
        assert api_def.request_body_id == request_body.id
        assert api_def.response_body_id == response_body.id

    def test_create_api_definition_with_inline_bodies(
        self,
        service: ApiDefinitionService,
        header_service: HeaderService,
        db_session: Session
    ):
        """Test creating API definition with inline bodies."""
        header = header_service.create_header(
            db_session,
            name="Auth Header",
            headers={"Authorization": "Bearer ${token}"}
        )

        api_def = service.create_api_definition(
            db_session,
            name="Create User",
            method=HttpMethod.POST,
            path="/api/users",
            header_id=header.id,
            inline_request_body={"name": "John", "email": "john@example.com"},
            inline_response_body={"id": 1, "status": "created"}
        )

        assert api_def.id is not None
        assert api_def.inline_request_body == {"name": "John", "email": "john@example.com"}
        assert api_def.inline_response_body == {"id": 1, "status": "created"}
        assert api_def.request_body_id is None
        assert api_def.response_body_id is None

    def test_get_api_definition_with_relations(
        self,
        service: ApiDefinitionService,
        header_service: HeaderService,
        db_session: Session
    ):
        """Test retrieving API definition with related components."""
        header = header_service.create_header(
            db_session,
            name="Auth Header",
            headers={"Authorization": "Bearer ${token}"}
        )

        api_def = service.create_api_definition(
            db_session,
            name="Get User",
            method=HttpMethod.GET,
            path="/api/users/{id}",
            header_id=header.id
        )

        retrieved = service.get_api_definition(
            db_session,
            api_def.id,
            with_relations=True
        )

        assert retrieved is not None
        assert retrieved.header is not None
        assert retrieved.header.name == "Auth Header"

    def test_get_full_api_definition(
        self,
        service: ApiDefinitionService,
        header_service: HeaderService,
        body_service: BodyService,
        db_session: Session
    ):
        """Test getting complete API definition with all components resolved."""
        header = header_service.create_header(
            db_session,
            name="Auth Header",
            headers={"Authorization": "Bearer ${token}"}
        )
        response_body = body_service.create_body(
            db_session,
            name="User Response",
            body_type="response",
            example_data={"id": 1, "name": "John"}
        )

        api_def = service.create_api_definition(
            db_session,
            name="Get User",
            method=HttpMethod.GET,
            path="/api/users/{id}",
            header_id=header.id,
            response_body_id=response_body.id,
            inline_request_body={"filter": "active"}
        )

        full_def = service.get_full_api_definition(db_session, api_def.id)

        assert full_def is not None
        assert full_def['name'] == "Get User"
        assert full_def['header'] is not None
        assert full_def['header']['name'] == "Auth Header"
        assert full_def['response_body'] is not None
        assert full_def['response_body']['name'] == "User Response"
        assert full_def['request_body'] is not None
        assert full_def['request_body']['inline'] is True

    def test_list_api_definitions_by_method(
        self, service: ApiDefinitionService, db_session: Session
    ):
        """Test listing API definitions filtered by HTTP method."""
        service.create_api_definition(
            db_session,
            name="Get User",
            method=HttpMethod.GET,
            path="/api/users/{id}"
        )
        service.create_api_definition(
            db_session,
            name="Create User",
            method=HttpMethod.POST,
            path="/api/users"
        )

        get_apis = service.list_api_definitions(db_session, method=HttpMethod.GET)
        assert len(get_apis) == 1
        assert get_apis[0].name == "Get User"

    def test_search_api_definitions_by_path(
        self, service: ApiDefinitionService, db_session: Session
    ):
        """Test searching API definitions by path."""
        service.create_api_definition(
            db_session,
            name="Get User",
            method=HttpMethod.GET,
            path="/api/users/{id}"
        )
        service.create_api_definition(
            db_session,
            name="Get Orders",
            method=HttpMethod.GET,
            path="/api/orders/{id}"
        )

        results = service.search_api_definitions(db_session, "users")
        assert len(results) == 1
        assert results[0].name == "Get User"

    def test_update_api_definition(
        self, service: ApiDefinitionService, db_session: Session
    ):
        """Test updating API definition."""
        api_def = service.create_api_definition(
            db_session,
            name="Original API",
            method=HttpMethod.GET,
            path="/api/test"
        )

        updated = service.update_api_definition(
            db_session,
            api_def.id,
            name="Updated API",
            timeout=60
        )

        assert updated is not None
        assert updated.name == "Updated API"
        assert updated.timeout == 60

    def test_delete_api_definition(
        self, service: ApiDefinitionService, db_session: Session
    ):
        """Test deleting API definition."""
        api_def = service.create_api_definition(
            db_session,
            name="To Delete",
            method=HttpMethod.GET,
            path="/api/test"
        )

        result = service.delete_api_definition(db_session, api_def.id)
        assert result is True

        retrieved = service.get_api_definition(db_session, api_def.id)
        assert retrieved is None
