"""Integration tests for API Definition endpoints."""

from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)


class TestApiDefinitionAPI:
    """Test API Definition API endpoints."""

    def test_create_api_definition_reference_mode(self, client):
        """Test creating API definition using reference mode (header + body IDs)."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create request body
        req_body_response = client.post(
            "/bodies/",
            json={
                "name": "User Request",
                "body_type": "request",
                "example_data": {"name": "John"},
                "scope": "global",
            },
        )
        req_body_id = req_body_response.json()["id"]

        # Create response body
        res_body_response = client.post(
            "/bodies/",
            json={
                "name": "User Response",
                "body_type": "response",
                "example_data": {"id": 1, "name": "John"},
                "scope": "global",
            },
        )
        res_body_id = res_body_response.json()["id"]

        # Create API definition
        response = client.post(
            "/api-definitions/",
            json={
                "name": "Create User",
                "method": "POST",
                "path": "/api/users",
                "header_id": header_id,
                "request_body_id": req_body_id,
                "response_body_id": res_body_id,
                "description": "Create a new user",
            },
        )
        assert response.status_code == HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Create User"
        assert data["method"] == "POST"
        assert data["header_id"] == header_id
        assert data["request_body_id"] == req_body_id
        assert data["response_body_id"] == res_body_id

    def test_create_api_definition_inline_mode(self, client):
        """Test creating API definition using inline mode (header + inline bodies)."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definition with inline bodies
        response = client.post(
            "/api-definitions/",
            json={
                "name": "Get User",
                "method": "GET",
                "path": "/api/users/{id}",
                "header_id": header_id,
                "inline_request_body": None,
                "inline_response_body": {"id": 1, "name": "John", "email": "john@example.com"},
                "description": "Get user by ID",
            },
        )
        assert response.status_code == HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Get User"
        assert data["method"] == "GET"
        assert data["header_id"] == header_id
        assert data["inline_response_body"] == {"id": 1, "name": "John", "email": "john@example.com"}

    def test_list_api_definitions(self, client):
        """Test listing API definitions."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definitions
        client.post(
            "/api-definitions/",
            json={
                "name": "API 1",
                "method": "GET",
                "path": "/api/endpoint1",
                "header_id": header_id,
            },
        )
        client.post(
            "/api-definitions/",
            json={
                "name": "API 2",
                "method": "POST",
                "path": "/api/endpoint2",
                "header_id": header_id,
            },
        )

        # List all API definitions
        response = client.get("/api-definitions/")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_api_definitions_with_method_filter(self, client):
        """Test listing API definitions with method filter."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definitions with different methods
        client.post(
            "/api-definitions/",
            json={
                "name": "GET API",
                "method": "GET",
                "path": "/api/get",
                "header_id": header_id,
            },
        )
        client.post(
            "/api-definitions/",
            json={
                "name": "POST API",
                "method": "POST",
                "path": "/api/post",
                "header_id": header_id,
            },
        )

        # Filter by method
        response = client.get("/api-definitions/?method=GET")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["method"] == "GET"

    def test_search_api_definitions(self, client):
        """Test searching API definitions by path."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definitions
        client.post(
            "/api-definitions/",
            json={
                "name": "User API",
                "method": "GET",
                "path": "/api/users",
                "header_id": header_id,
            },
        )
        client.post(
            "/api-definitions/",
            json={
                "name": "Product API",
                "method": "GET",
                "path": "/api/products",
                "header_id": header_id,
            },
        )

        # Search by path
        response = client.get("/api-definitions/search?path=users")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("users" in item["path"] for item in data["items"])

    def test_get_api_definition_by_id(self, client):
        """Test getting an API definition by ID."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definition
        create_response = client.post(
            "/api-definitions/",
            json={
                "name": "Test API",
                "method": "GET",
                "path": "/api/test",
                "header_id": header_id,
            },
        )
        api_def_id = create_response.json()["id"]

        # Get by ID
        response = client.get(f"/api-definitions/{api_def_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["id"] == api_def_id
        assert data["name"] == "Test API"

    def test_get_full_api_definition(self, client):
        """Test getting complete API definition with all components."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Auth Header",
                "headers": {"Authorization": "Bearer token"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create bodies
        req_body_response = client.post(
            "/bodies/",
            json={
                "name": "Request Body",
                "body_type": "request",
                "example_data": {"key": "value"},
                "scope": "global",
            },
        )
        req_body_id = req_body_response.json()["id"]

        # Create API definition
        create_response = client.post(
            "/api-definitions/",
            json={
                "name": "Full API",
                "method": "POST",
                "path": "/api/full",
                "header_id": header_id,
                "request_body_id": req_body_id,
            },
        )
        api_def_id = create_response.json()["id"]

        # Get full API definition
        response = client.get(f"/api-definitions/{api_def_id}/full")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "api_definition" in data
        assert "header" in data
        assert "request_body" in data

    def test_update_api_definition(self, client):
        """Test updating an API definition."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definition
        create_response = client.post(
            "/api-definitions/",
            json={
                "name": "Original API",
                "method": "GET",
                "path": "/api/original",
                "header_id": header_id,
            },
        )
        api_def_id = create_response.json()["id"]

        # Update the API definition
        response = client.patch(
            f"/api-definitions/{api_def_id}",
            json={
                "name": "Updated API",
                "path": "/api/updated",
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated API"
        assert data["path"] == "/api/updated"

    def test_delete_api_definition(self, client):
        """Test deleting an API definition."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create API definition
        create_response = client.post(
            "/api-definitions/",
            json={
                "name": "To Delete",
                "method": "DELETE",
                "path": "/api/delete",
                "header_id": header_id,
            },
        )
        api_def_id = create_response.json()["id"]

        # Delete the API definition
        response = client.delete(f"/api-definitions/{api_def_id}")
        assert response.status_code == HTTP_200_OK

        # Verify it's deleted
        get_response = client.get(f"/api-definitions/{api_def_id}")
        assert get_response.status_code == HTTP_404_NOT_FOUND

    def test_two_combination_modes(self, client):
        """Test both combination modes: reference and inline."""
        # Create header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Shared Header",
                "headers": {"Authorization": "Bearer token"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create body for reference mode
        body_response = client.post(
            "/bodies/",
            json={
                "name": "Shared Body",
                "body_type": "response",
                "example_data": {"status": "ok"},
                "scope": "global",
            },
        )
        body_id = body_response.json()["id"]

        # Mode 1: Reference mode (header + body IDs)
        ref_response = client.post(
            "/api-definitions/",
            json={
                "name": "Reference Mode API",
                "method": "GET",
                "path": "/api/reference",
                "header_id": header_id,
                "response_body_id": body_id,
            },
        )
        assert ref_response.status_code == HTTP_201_CREATED
        ref_data = ref_response.json()
        assert ref_data["header_id"] == header_id
        assert ref_data["response_body_id"] == body_id
        assert ref_data["inline_response_body"] is None

        # Mode 2: Inline mode (header + inline body)
        inline_response = client.post(
            "/api-definitions/",
            json={
                "name": "Inline Mode API",
                "method": "POST",
                "path": "/api/inline",
                "header_id": header_id,
                "inline_request_body": {"data": "inline"},
                "inline_response_body": {"result": "success"},
            },
        )
        assert inline_response.status_code == HTTP_201_CREATED
        inline_data = inline_response.json()
        assert inline_data["header_id"] == header_id
        assert inline_data["request_body_id"] is None
        assert inline_data["inline_request_body"] == {"data": "inline"}
        assert inline_data["inline_response_body"] == {"result": "success"}
