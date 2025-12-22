"""Unit tests for API Component repositories.

Tests for HeaderRepository, BodyRepository, and ApiDefinitionRepository.
"""

import pytest
from morado.models.api_component import (
    ApiDefinition,
    Body,
    BodyType,
    Header,
    HeaderScope,
    HttpMethod,
)
from morado.repositories.api_component import (
    ApiDefinitionRepository,
    BodyRepository,
    HeaderRepository,
)


@pytest.fixture
def header_repo():
    """Create a HeaderRepository instance."""
    return HeaderRepository()


@pytest.fixture
def body_repo():
    """Create a BodyRepository instance."""
    return BodyRepository()


@pytest.fixture
def api_def_repo():
    """Create an ApiDefinitionRepository instance."""
    return ApiDefinitionRepository()


@pytest.fixture
def sample_headers(session):
    """Create sample header data."""
    headers = [
        Header(
            uuid="header-1",
            name="Auth Header",
            headers={"Authorization": "Bearer ${token}"},
            scope=HeaderScope.GLOBAL,
            is_active=True,
        ),
        Header(
            uuid="header-2",
            name="JSON Header",
            headers={"Content-Type": "application/json"},
            scope=HeaderScope.PROJECT,
            project_id=1,
            is_active=True,
        ),
        Header(
            uuid="header-3",
            name="Private Header",
            headers={"X-Custom": "value"},
            scope=HeaderScope.PRIVATE,
            is_active=False,
        ),
    ]
    for header in headers:
        session.add(header)
    session.commit()
    return headers


@pytest.fixture
def sample_bodies(session):
    """Create sample body data."""
    bodies = [
        Body(
            uuid="body-1",
            name="User Request Body",
            body_type=BodyType.REQUEST,
            content_type="application/json",
            body_schema={"type": "object", "properties": {"name": {"type": "string"}}},
            scope=HeaderScope.GLOBAL,
            is_active=True,
        ),
        Body(
            uuid="body-2",
            name="User Response Body",
            body_type=BodyType.RESPONSE,
            content_type="application/json",
            body_schema={"type": "object", "properties": {"id": {"type": "integer"}}},
            scope=HeaderScope.GLOBAL,
            is_active=True,
        ),
        Body(
            uuid="body-3",
            name="Generic Body",
            body_type=BodyType.BOTH,
            content_type="application/json",
            scope=HeaderScope.PRIVATE,
            is_active=False,
        ),
    ]
    for body in bodies:
        session.add(body)
    session.commit()
    return bodies


@pytest.fixture
def sample_api_definitions(session, sample_headers, sample_bodies):
    """Create sample API definition data."""
    api_defs = [
        ApiDefinition(
            uuid="api-1",
            name="Get User",
            method=HttpMethod.GET,
            path="/api/users/{id}",
            header_id=sample_headers[0].id,
            response_body_id=sample_bodies[1].id,
            is_active=True,
        ),
        ApiDefinition(
            uuid="api-2",
            name="Create User",
            method=HttpMethod.POST,
            path="/api/users",
            header_id=sample_headers[0].id,
            request_body_id=sample_bodies[0].id,
            is_active=True,
        ),
        ApiDefinition(
            uuid="api-3",
            name="Update User",
            method=HttpMethod.PUT,
            path="/api/users/{id}",
            header_id=sample_headers[1].id,
            inline_request_body={"name": "test"},
            is_active=False,
        ),
    ]
    for api_def in api_defs:
        session.add(api_def)
    session.commit()
    return api_defs


class TestHeaderRepository:
    """Test HeaderRepository operations."""

    def test_create_header(self, session, header_repo):
        """Test creating a header."""
        header = header_repo.create(
            session,
            uuid="new-header",
            name="New Header",
            headers={"X-Test": "value"},
            scope=HeaderScope.GLOBAL,
        )

        assert header.id is not None
        assert header.name == "New Header"
        assert header.scope == HeaderScope.GLOBAL

    def test_get_by_scope(self, session, header_repo, sample_headers):
        """Test getting headers by scope."""
        global_headers = header_repo.get_by_scope(session, HeaderScope.GLOBAL)

        assert len(global_headers) == 1
        assert global_headers[0].name == "Auth Header"

    def test_get_by_project(self, session, header_repo, sample_headers):
        """Test getting headers by project ID."""
        project_headers = header_repo.get_by_project(session, 1)

        assert len(project_headers) == 1
        assert project_headers[0].name == "JSON Header"

    def test_search_by_name(self, session, header_repo, sample_headers):
        """Test searching headers by name."""
        results = header_repo.search_by_name(session, "auth")

        assert len(results) == 1
        assert results[0].name == "Auth Header"

    def test_search_by_name_case_insensitive(self, session, header_repo, sample_headers):
        """Test that name search is case-insensitive."""
        results = header_repo.search_by_name(session, "AUTH")

        assert len(results) == 1
        assert results[0].name == "Auth Header"


class TestBodyRepository:
    """Test BodyRepository operations."""

    def test_create_body(self, session, body_repo):
        """Test creating a body."""
        body = body_repo.create(
            session,
            uuid="new-body",
            name="New Body",
            body_type=BodyType.REQUEST,
            content_type="application/json",
            scope=HeaderScope.GLOBAL,
        )

        assert body.id is not None
        assert body.name == "New Body"
        assert body.body_type == BodyType.REQUEST

    def test_get_by_scope(self, session, body_repo, sample_bodies):
        """Test getting bodies by scope."""
        global_bodies = body_repo.get_by_scope(session, HeaderScope.GLOBAL)

        assert len(global_bodies) == 2
        assert all(body.scope == HeaderScope.GLOBAL for body in global_bodies)

    def test_get_by_type(self, session, body_repo, sample_bodies):
        """Test getting bodies by type."""
        request_bodies = body_repo.get_by_type(session, BodyType.REQUEST)

        assert len(request_bodies) == 1
        assert request_bodies[0].name == "User Request Body"

    def test_search_by_name(self, session, body_repo, sample_bodies):
        """Test searching bodies by name."""
        results = body_repo.search_by_name(session, "user")

        assert len(results) == 2
        assert all("User" in body.name for body in results)


class TestApiDefinitionRepository:
    """Test ApiDefinitionRepository operations."""

    def test_create_api_definition(self, session, api_def_repo, sample_headers):
        """Test creating an API definition."""
        api_def = api_def_repo.create(
            session,
            uuid="new-api",
            name="New API",
            method=HttpMethod.GET,
            path="/api/test",
            header_id=sample_headers[0].id,
        )

        assert api_def.id is not None
        assert api_def.name == "New API"
        assert api_def.method == HttpMethod.GET

    def test_get_with_relations(self, session, api_def_repo, sample_api_definitions):
        """Test getting API definition with related entities."""
        api_def = api_def_repo.get_with_relations(session, sample_api_definitions[0].id)

        assert api_def is not None
        assert api_def.header is not None
        assert api_def.header.name == "Auth Header"
        assert api_def.response_body is not None
        assert api_def.response_body.name == "User Response Body"

    def test_get_by_method(self, session, api_def_repo, sample_api_definitions):
        """Test getting API definitions by HTTP method."""
        get_apis = api_def_repo.get_by_method(session, HttpMethod.GET)

        assert len(get_apis) == 1
        assert get_apis[0].name == "Get User"

    def test_search_by_path(self, session, api_def_repo, sample_api_definitions):
        """Test searching API definitions by path."""
        results = api_def_repo.search_by_path(session, "users")

        # Only active API definitions are returned
        assert len(results) == 2
        assert all("/users" in api.path for api in results)
        assert all(api.is_active for api in results)

    def test_get_by_header(self, session, api_def_repo, sample_api_definitions, sample_headers):
        """Test getting API definitions by header."""
        apis = api_def_repo.get_by_header(session, sample_headers[0].id)

        assert len(apis) == 2
        assert all(api.header_id == sample_headers[0].id for api in apis)


class TestApiComponentRelationships:
    """Test relationships between API components."""

    def test_header_to_api_definition_relationship(
        self, session, header_repo, api_def_repo, sample_api_definitions, sample_headers
    ):
        """Test that header can access its API definitions."""
        header = header_repo.get_by_id(session, sample_headers[0].id)

        # Refresh to load relationships
        session.refresh(header)
        assert len(header.api_definitions) == 2

    def test_body_to_api_definition_relationship(
        self, session, body_repo, sample_api_definitions, sample_bodies
    ):
        """Test that body can access its API definitions."""
        body = body_repo.get_by_id(session, sample_bodies[0].id)

        # Refresh to load relationships
        session.refresh(body)
        assert len(body.api_definitions_request) == 1

    def test_api_definition_with_inline_body(self, session, api_def_repo):
        """Test API definition with inline body instead of reference."""
        api_def = api_def_repo.create(
            session,
            uuid="inline-api",
            name="Inline API",
            method=HttpMethod.POST,
            path="/api/inline",
            inline_request_body={"key": "value"},
        )

        assert api_def.request_body_id is None
        assert api_def.inline_request_body == {"key": "value"}

    def test_api_definition_with_both_bodies(
        self, session, api_def_repo, sample_headers, sample_bodies
    ):
        """Test API definition with both request and response bodies."""
        api_def = api_def_repo.create(
            session,
            uuid="both-bodies",
            name="Both Bodies API",
            method=HttpMethod.POST,
            path="/api/both",
            header_id=sample_headers[0].id,
            request_body_id=sample_bodies[0].id,
            response_body_id=sample_bodies[1].id,
        )

        loaded = api_def_repo.get_with_relations(session, api_def.id)
        assert loaded.request_body is not None
        assert loaded.response_body is not None
        assert loaded.request_body.name == "User Request Body"
        assert loaded.response_body.name == "User Response Body"
