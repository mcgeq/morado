"""Integration tests for Body API endpoints."""

from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)


class TestBodyAPI:
    """Test Body API endpoints."""

    def test_create_body(self, client):
        """Test creating a new body."""
        response = client.post(
            "/bodies/",
            json={
                "name": "User Body",
                "body_type": "request",
                "example_data": {"name": "John", "email": "john@example.com"},
                "scope": "global",
                "description": "User request body",
            },
        )
        assert response.status_code == HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "User Body"
        assert data["body_type"] == "request"
        assert data["example_data"] == {"name": "John", "email": "john@example.com"}
        assert "id" in data
        assert "uuid" in data

    def test_list_bodies(self, client):
        """Test listing bodies."""
        # Create a few bodies
        client.post(
            "/bodies/",
            json={
                "name": "Request Body",
                "body_type": "request",
                "example_data": {"key": "value1"},
                "scope": "global",
            },
        )
        client.post(
            "/bodies/",
            json={
                "name": "Response Body",
                "body_type": "response",
                "example_data": {"key": "value2"},
                "scope": "global",
            },
        )

        # List all bodies
        response = client.get("/bodies/")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_bodies_with_type_filter(self, client):
        """Test listing bodies with body_type filter."""
        # Create bodies with different types
        client.post(
            "/bodies/",
            json={
                "name": "Request Body",
                "body_type": "request",
                "example_data": {"key": "value"},
                "scope": "global",
            },
        )
        client.post(
            "/bodies/",
            json={
                "name": "Response Body",
                "body_type": "response",
                "example_data": {"key": "value"},
                "scope": "global",
            },
        )

        # Filter by body_type
        response = client.get("/bodies/?body_type=request")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["body_type"] == "request"

    def test_search_bodies(self, client):
        """Test searching bodies by name."""
        # Create bodies
        client.post(
            "/bodies/",
            json={
                "name": "User Body",
                "body_type": "request",
                "example_data": {"user": "data"},
                "scope": "global",
            },
        )
        client.post(
            "/bodies/",
            json={
                "name": "Product Body",
                "body_type": "response",
                "example_data": {"product": "data"},
                "scope": "global",
            },
        )

        # Search by name
        response = client.get("/bodies/search?name=User")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("User" in item["name"] for item in data["items"])

    def test_get_body_by_id(self, client):
        """Test getting a body by ID."""
        # Create a body
        create_response = client.post(
            "/bodies/",
            json={
                "name": "Test Body",
                "body_type": "request",
                "example_data": {"test": "data"},
                "scope": "global",
            },
        )
        body_id = create_response.json()["id"]

        # Get by ID
        response = client.get(f"/bodies/{body_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["id"] == body_id
        assert data["name"] == "Test Body"

    def test_get_body_by_uuid(self, client):
        """Test getting a body by UUID."""
        # Create a body
        create_response = client.post(
            "/bodies/",
            json={
                "name": "Test Body",
                "body_type": "request",
                "example_data": {"test": "data"},
                "scope": "global",
            },
        )
        uuid = create_response.json()["uuid"]

        # Get by UUID
        response = client.get(f"/bodies/uuid/{uuid}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["uuid"] == uuid
        assert data["name"] == "Test Body"

    def test_get_nonexistent_body(self, client):
        """Test getting a body that doesn't exist."""
        response = client.get("/bodies/99999")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_update_body(self, client):
        """Test updating a body."""
        # Create a body
        create_response = client.post(
            "/bodies/",
            json={
                "name": "Original Body",
                "body_type": "request",
                "example_data": {"original": "data"},
                "scope": "global",
            },
        )
        body_id = create_response.json()["id"]

        # Update the body
        response = client.patch(
            f"/bodies/{body_id}",
            json={
                "name": "Updated Body",
                "example_data": {"updated": "data"},
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Body"
        assert data["example_data"] == {"updated": "data"}

    def test_delete_body(self, client):
        """Test deleting a body."""
        # Create a body
        create_response = client.post(
            "/bodies/",
            json={
                "name": "To Delete",
                "body_type": "request",
                "example_data": {"delete": "me"},
                "scope": "global",
            },
        )
        body_id = create_response.json()["id"]

        # Delete the body
        response = client.delete(f"/bodies/{body_id}")
        assert response.status_code == HTTP_200_OK

        # Verify it's deleted
        get_response = client.get(f"/bodies/{body_id}")
        assert get_response.status_code == HTTP_404_NOT_FOUND

    def test_body_reusability(self, client):
        """Test that bodies can be reused across multiple API definitions."""
        # Create a reusable body
        body_response = client.post(
            "/bodies/",
            json={
                "name": "Shared Response Body",
                "body_type": "response",
                "example_data": {"status": "success", "data": {}},
                "scope": "global",
            },
        )
        body_id = body_response.json()["id"]

        # Create a header for the API definitions
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create multiple API definitions using the same body
        for i in range(3):
            api_response = client.post(
                "/api-definitions/",
                json={
                    "name": f"API {i}",
                    "method": "GET",
                    "path": f"/api/endpoint{i}",
                    "header_id": header_id,
                    "response_body_id": body_id,
                },
            )
            assert api_response.status_code == HTTP_201_CREATED
            assert api_response.json()["response_body_id"] == body_id

        # Verify the body is still accessible
        get_response = client.get(f"/bodies/{body_id}")
        assert get_response.status_code == HTTP_200_OK
