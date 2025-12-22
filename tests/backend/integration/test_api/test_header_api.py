"""Integration tests for Header API endpoints."""

from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)


class TestHeaderAPI:
    """Test Header API endpoints."""

    def test_create_header(self, client):
        """Test creating a new header."""
        response = client.post(
            "/headers/",
            json={
                "name": "Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global",
                "description": "Authentication header",
            },
        )
        assert response.status_code == HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Auth Header"
        assert data["headers"] == {"Authorization": "Bearer ${token}"}
        assert data["scope"] == "global"
        assert "id" in data
        assert "uuid" in data

    def test_list_headers(self, client):
        """Test listing headers."""
        # Create a few headers
        client.post(
            "/headers/",
            json={
                "name": "Header 1",
                "headers": {"X-Custom": "value1"},
                "scope": "global",
            },
        )
        client.post(
            "/headers/",
            json={
                "name": "Header 2",
                "headers": {"X-Custom": "value2"},
                "scope": "project",
                "project_id": 1,
            },
        )

        # List all headers
        response = client.get("/headers/")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_headers_with_filter(self, client):
        """Test listing headers with scope filter."""
        # Create headers with different scopes
        client.post(
            "/headers/",
            json={
                "name": "Global Header",
                "headers": {"X-Global": "value"},
                "scope": "global",
            },
        )
        client.post(
            "/headers/",
            json={
                "name": "Project Header",
                "headers": {"X-Project": "value"},
                "scope": "project",
                "project_id": 1,
            },
        )

        # Filter by scope
        response = client.get("/headers/?scope=global")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["scope"] == "global"

    def test_search_headers(self, client):
        """Test searching headers by name."""
        # Create headers
        client.post(
            "/headers/",
            json={
                "name": "Auth Header",
                "headers": {"Authorization": "Bearer token"},
                "scope": "global",
            },
        )
        client.post(
            "/headers/",
            json={
                "name": "Content Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )

        # Search by name
        response = client.get("/headers/search?name=Auth")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("Auth" in item["name"] for item in data["items"])

    def test_get_header_by_id(self, client):
        """Test getting a header by ID."""
        # Create a header
        create_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"X-Test": "value"},
                "scope": "global",
            },
        )
        header_id = create_response.json()["id"]

        # Get by ID
        response = client.get(f"/headers/{header_id}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["id"] == header_id
        assert data["name"] == "Test Header"

    def test_get_header_by_uuid(self, client):
        """Test getting a header by UUID."""
        # Create a header
        create_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"X-Test": "value"},
                "scope": "global",
            },
        )
        uuid = create_response.json()["uuid"]

        # Get by UUID
        response = client.get(f"/headers/uuid/{uuid}")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["uuid"] == uuid
        assert data["name"] == "Test Header"

    def test_get_nonexistent_header(self, client):
        """Test getting a header that doesn't exist."""
        response = client.get("/headers/99999")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_update_header(self, client):
        """Test updating a header."""
        # Create a header
        create_response = client.post(
            "/headers/",
            json={
                "name": "Original Name",
                "headers": {"X-Original": "value"},
                "scope": "global",
            },
        )
        header_id = create_response.json()["id"]

        # Update the header
        response = client.patch(
            f"/headers/{header_id}",
            json={
                "name": "Updated Name",
                "headers": {"X-Updated": "new_value"},
            },
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["headers"] == {"X-Updated": "new_value"}

    def test_delete_header(self, client):
        """Test deleting a header."""
        # Create a header
        create_response = client.post(
            "/headers/",
            json={
                "name": "To Delete",
                "headers": {"X-Delete": "value"},
                "scope": "global",
            },
        )
        header_id = create_response.json()["id"]

        # Delete the header
        response = client.delete(f"/headers/{header_id}")
        assert response.status_code == HTTP_200_OK

        # Verify it's deleted
        get_response = client.get(f"/headers/{header_id}")
        assert get_response.status_code == HTTP_404_NOT_FOUND

    def test_activate_header(self, client):
        """Test activating a header."""
        # Create a header
        create_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"X-Test": "value"},
                "scope": "global",
                "is_active": False,
            },
        )
        header_id = create_response.json()["id"]

        # Activate the header
        response = client.post(f"/headers/{header_id}/activate")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["is_active"] is True

    def test_deactivate_header(self, client):
        """Test deactivating a header."""
        # Create a header
        create_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"X-Test": "value"},
                "scope": "global",
                "is_active": True,
            },
        )
        header_id = create_response.json()["id"]

        # Deactivate the header
        response = client.post(f"/headers/{header_id}/deactivate")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False

    def test_header_reusability(self, client):
        """Test that headers can be reused across multiple API definitions."""
        # Create a reusable header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Shared Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create multiple API definitions using the same header
        for i in range(3):
            api_response = client.post(
                "/api-definitions/",
                json={
                    "name": f"API {i}",
                    "method": "GET",
                    "path": f"/api/endpoint{i}",
                    "header_id": header_id,
                },
            )
            assert api_response.status_code == HTTP_201_CREATED
            assert api_response.json()["header_id"] == header_id

        # Verify the header is still accessible
        get_response = client.get(f"/headers/{header_id}")
        assert get_response.status_code == HTTP_200_OK
