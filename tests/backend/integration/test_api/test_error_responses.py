"""Integration tests for API error responses."""

from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)


class TestErrorResponses:
    """Test API error response formats and handling."""

    def test_404_not_found_format(self, client):
        """Test that 404 errors return proper format."""
        response = client.get("/headers/99999")
        assert response.status_code == HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data or "message" in data

    def test_validation_error_format(self, client):
        """Test that validation errors return proper format."""
        # Try to create header with invalid data
        response = client.post(
            "/headers/",
            json={
                "name": "",  # Empty name should fail validation
                "headers": {},
                "scope": "invalid_scope",  # Invalid scope
            },
        )
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]
        data = response.json()
        # Litestar returns validation errors in a specific format
        assert "detail" in data or "extra" in data

    def test_missing_required_fields(self, client):
        """Test error when required fields are missing."""
        response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                # Missing required 'headers' field
            },
        )
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_invalid_json_format(self, client):
        """Test error handling for invalid JSON."""
        response = client.post(
            "/headers/",
            content="invalid json{",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_invalid_query_parameters(self, client):
        """Test error handling for invalid query parameters."""
        # Try to list with invalid skip value
        response = client.get("/headers/?skip=-1")
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_update_nonexistent_resource(self, client):
        """Test updating a resource that doesn't exist."""
        response = client.patch(
            "/headers/99999",
            json={"name": "Updated Name"},
        )
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_delete_nonexistent_resource(self, client):
        """Test deleting a resource that doesn't exist."""
        response = client.delete("/headers/99999")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_invalid_uuid_format(self, client):
        """Test error handling for invalid UUID format."""
        response = client.get("/headers/uuid/invalid-uuid-format")
        # Should return 404 or validation error
        assert response.status_code in [HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_invalid_method_on_endpoint(self, client):
        """Test using wrong HTTP method on endpoint."""
        # Try to POST to a GET-only endpoint
        response = client.post("/headers/1")
        # Should return 405 Method Not Allowed
        assert response.status_code == 405

    def test_search_without_required_parameter(self, client):
        """Test search endpoint without required parameter."""
        response = client.get("/headers/search")
        # Should fail because 'name' parameter is required
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_invalid_filter_values(self, client):
        """Test filtering with invalid values."""
        response = client.get("/headers/?scope=invalid_scope_value")
        # Depending on implementation, might return 400 or just empty results
        # At minimum, should not crash
        assert response.status_code in [200, HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_pagination_limits(self, client):
        """Test pagination with out-of-range limits."""
        # Try to request more than max limit
        response = client.get("/headers/?limit=1000")
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_api_definition_without_header(self, client):
        """Test creating API definition without required header."""
        response = client.post(
            "/api-definitions/",
            json={
                "name": "Invalid API",
                "method": "GET",
                "path": "/api/test",
                # Missing required header_id
            },
        )
        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_create_script_with_invalid_api_definition(self, client):
        """Test creating script with non-existent API definition."""
        response = client.post(
            "/scripts/",
            json={
                "name": "Invalid Script",
                "api_definition_id": 99999,  # Non-existent
                "script_type": "main",
            },
        )
        # Should fail validation
        assert response.status_code in [HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]

    def test_error_response_consistency(self, client):
        """Test that all error responses follow consistent format."""
        # Test multiple error scenarios
        error_responses = []

        # 404 error
        response1 = client.get("/headers/99999")
        if response1.status_code == HTTP_404_NOT_FOUND:
            error_responses.append(response1.json())

        # Validation error
        response2 = client.post("/headers/", json={"name": ""})
        if response2.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]:
            error_responses.append(response2.json())

        # All error responses should have similar structure
        for error in error_responses:
            # Should have at least one of these fields
            assert any(key in error for key in ["detail", "message", "error", "extra"])
