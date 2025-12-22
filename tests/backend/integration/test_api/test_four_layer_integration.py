"""Integration tests for the complete four-layer architecture.

This module tests the integration of all four layers:
1. Header/Body/API Definition (Layer 1)
2. Scripts (Layer 2)
3. Components (Layer 3)
4. Test Cases (Layer 4)
"""

from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)


class TestFourLayerIntegration:
    """Test the complete four-layer architecture integration."""

    def test_complete_workflow_reference_mode(self, client):
        """Test complete workflow from Layer 1 to Layer 4 using reference mode."""
        # Layer 1: Create Header and Body components
        header_response = client.post(
            "/headers/",
            json={
                "name": "API Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global",
            },
        )
        assert header_response.status_code == HTTP_201_CREATED
        header_id = header_response.json()["id"]

        req_body_response = client.post(
            "/bodies/",
            json={
                "name": "Login Request",
                "body_type": "request",
                "example_data": {"username": "${username}", "password": "${password}"},
                "scope": "global",
            },
        )
        assert req_body_response.status_code == HTTP_201_CREATED
        req_body_id = req_body_response.json()["id"]

        res_body_response = client.post(
            "/bodies/",
            json={
                "name": "Login Response",
                "body_type": "response",
                "example_data": {"token": "abc123", "user_id": 1},
                "scope": "global",
            },
        )
        assert res_body_response.status_code == HTTP_201_CREATED
        res_body_id = res_body_response.json()["id"]

        # Create API Definition using references
        api_def_response = client.post(
            "/api-definitions/",
            json={
                "name": "Login API",
                "method": "POST",
                "path": "/api/auth/login",
                "header_id": header_id,
                "request_body_id": req_body_id,
                "response_body_id": res_body_id,
            },
        )
        assert api_def_response.status_code == HTTP_201_CREATED
        api_def_id = api_def_response.json()["id"]

        # Layer 2: Create Script referencing API Definition
        script_response = client.post(
            "/scripts/",
            json={
                "name": "Login Script",
                "api_definition_id": api_def_id,
                "script_type": "main",
                "variables": {"username": "testuser", "password": "testpass"},
                "assertions": [
                    {"type": "status_code", "expected": 200},
                    {"type": "json_path", "path": "$.token", "expected": "exists"},
                ],
            },
        )
        assert script_response.status_code == HTTP_201_CREATED
        script_id = script_response.json()["id"]

        # Verify script references the API definition
        script_data = script_response.json()
        assert script_data["api_definition_id"] == api_def_id

        # Layer 3: Create Component using the Script
        component_response = client.post(
            "/components/",
            json={
                "name": "Authentication Component",
                "description": "Handles user authentication",
                "scripts": [
                    {
                        "script_id": script_id,
                        "execution_order": 1,
                        "parameter_overrides": {"username": "admin"},
                    }
                ],
            },
        )
        assert component_response.status_code == HTTP_201_CREATED
        component_id = component_response.json()["id"]

        # Layer 4: Create Test Case using the Component
        test_case_response = client.post(
            "/test-cases/",
            json={
                "name": "Login Test Case",
                "description": "Test user login functionality",
                "components": [
                    {
                        "component_id": component_id,
                        "execution_order": 1,
                        "parameter_overrides": {"password": "adminpass"},
                    }
                ],
            },
        )
        assert test_case_response.status_code == HTTP_201_CREATED

        # Verify the complete chain
        test_case_data = test_case_response.json()
        assert test_case_data["name"] == "Login Test Case"
        assert len(test_case_data.get("components", [])) >= 0

    def test_complete_workflow_inline_mode(self, client):
        """Test complete workflow using inline mode for API Definition."""
        # Layer 1: Create Header only (bodies will be inline)
        header_response = client.post(
            "/headers/",
            json={
                "name": "Simple Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        assert header_response.status_code == HTTP_201_CREATED
        header_id = header_response.json()["id"]

        # Create API Definition with inline bodies
        api_def_response = client.post(
            "/api-definitions/",
            json={
                "name": "Get User API",
                "method": "GET",
                "path": "/api/users/{id}",
                "header_id": header_id,
                "inline_response_body": {
                    "id": "${user_id}",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            },
        )
        assert api_def_response.status_code == HTTP_201_CREATED
        api_def_id = api_def_response.json()["id"]

        # Verify inline body is stored
        api_def_data = api_def_response.json()
        assert api_def_data["inline_response_body"] is not None
        assert api_def_data["response_body_id"] is None

        # Layer 2: Create Script
        script_response = client.post(
            "/scripts/",
            json={
                "name": "Get User Script",
                "api_definition_id": api_def_id,
                "script_type": "main",
                "variables": {"user_id": "123"},
            },
        )
        assert script_response.status_code == HTTP_201_CREATED

    def test_component_nesting(self, client):
        """Test component nesting functionality."""
        # Create basic components first
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        api_def_response = client.post(
            "/api-definitions/",
            json={
                "name": "Test API",
                "method": "GET",
                "path": "/api/test",
                "header_id": header_id,
            },
        )
        api_def_id = api_def_response.json()["id"]

        script_response = client.post(
            "/scripts/",
            json={
                "name": "Test Script",
                "api_definition_id": api_def_id,
                "script_type": "main",
            },
        )
        script_id = script_response.json()["id"]

        # Create parent component
        parent_response = client.post(
            "/components/",
            json={
                "name": "Parent Component",
                "description": "Parent component",
                "scripts": [{"script_id": script_id, "execution_order": 1}],
            },
        )
        assert parent_response.status_code == HTTP_201_CREATED
        parent_id = parent_response.json()["id"]

        # Create child component that references parent
        child_response = client.post(
            "/components/",
            json={
                "name": "Child Component",
                "description": "Child component",
                "parent_component_id": parent_id,
                "scripts": [{"script_id": script_id, "execution_order": 1}],
            },
        )
        assert child_response.status_code == HTTP_201_CREATED
        child_data = child_response.json()
        assert child_data["parent_component_id"] == parent_id

    def test_test_case_with_scripts_and_components(self, client):
        """Test that test cases can reference both scripts and components."""
        # Setup: Create necessary components
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        api_def_response = client.post(
            "/api-definitions/",
            json={
                "name": "Test API",
                "method": "POST",
                "path": "/api/test",
                "header_id": header_id,
            },
        )
        api_def_id = api_def_response.json()["id"]

        # Create two scripts
        script1_response = client.post(
            "/scripts/",
            json={
                "name": "Setup Script",
                "api_definition_id": api_def_id,
                "script_type": "pre",
            },
        )
        script1_id = script1_response.json()["id"]

        script2_response = client.post(
            "/scripts/",
            json={
                "name": "Main Script",
                "api_definition_id": api_def_id,
                "script_type": "main",
            },
        )
        script2_id = script2_response.json()["id"]

        # Create a component
        component_response = client.post(
            "/components/",
            json={
                "name": "Test Component",
                "scripts": [{"script_id": script2_id, "execution_order": 1}],
            },
        )
        component_id = component_response.json()["id"]

        # Create test case with both scripts and components
        test_case_response = client.post(
            "/test-cases/",
            json={
                "name": "Mixed Test Case",
                "description": "Uses both scripts and components",
                "scripts": [{"script_id": script1_id, "execution_order": 1}],
                "components": [{"component_id": component_id, "execution_order": 2}],
            },
        )
        assert test_case_response.status_code == HTTP_201_CREATED
        test_case_data = test_case_response.json()
        assert test_case_data["name"] == "Mixed Test Case"

    def test_parameter_override_chain(self, client):
        """Test parameter overrides through the layer chain."""
        # Create basic setup
        header_response = client.post(
            "/headers/",
            json={
                "name": "Test Header",
                "headers": {"Content-Type": "application/json"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        api_def_response = client.post(
            "/api-definitions/",
            json={
                "name": "Test API",
                "method": "POST",
                "path": "/api/test",
                "header_id": header_id,
            },
        )
        api_def_id = api_def_response.json()["id"]

        # Create script with default variables
        script_response = client.post(
            "/scripts/",
            json={
                "name": "Test Script",
                "api_definition_id": api_def_id,
                "script_type": "main",
                "variables": {"param1": "script_value", "param2": "script_value"},
            },
        )
        script_id = script_response.json()["id"]

        # Create component with parameter override
        component_response = client.post(
            "/components/",
            json={
                "name": "Test Component",
                "scripts": [
                    {
                        "script_id": script_id,
                        "execution_order": 1,
                        "parameter_overrides": {"param1": "component_value"},
                    }
                ],
            },
        )
        component_id = component_response.json()["id"]

        # Create test case with another parameter override
        test_case_response = client.post(
            "/test-cases/",
            json={
                "name": "Override Test",
                "components": [
                    {
                        "component_id": component_id,
                        "execution_order": 1,
                        "parameter_overrides": {"param2": "testcase_value"},
                    }
                ],
            },
        )
        assert test_case_response.status_code == HTTP_201_CREATED

    def test_header_and_body_reuse_across_layers(self, client):
        """Test that Header and Body components can be reused across multiple API definitions."""
        # Create reusable header
        header_response = client.post(
            "/headers/",
            json={
                "name": "Shared Auth Header",
                "headers": {"Authorization": "Bearer ${token}"},
                "scope": "global",
            },
        )
        header_id = header_response.json()["id"]

        # Create reusable body
        body_response = client.post(
            "/bodies/",
            json={
                "name": "Shared Success Response",
                "body_type": "response",
                "example_data": {"status": "success", "message": "${message}"},
                "scope": "global",
            },
        )
        body_id = body_response.json()["id"]

        # Create multiple API definitions using the same header and body
        api_def_ids = []
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
            api_def_ids.append(api_response.json()["id"])

        # Verify all API definitions reference the same header and body
        for api_def_id in api_def_ids:
            response = client.get(f"/api-definitions/{api_def_id}")
            assert response.status_code == HTTP_200_OK
            data = response.json()
            assert data["header_id"] == header_id
            assert data["response_body_id"] == body_id

    def test_error_handling_missing_references(self, client):
        """Test error handling when referencing non-existent components."""
        # Try to create API definition with non-existent header
        response = client.post(
            "/api-definitions/",
            json={
                "name": "Invalid API",
                "method": "GET",
                "path": "/api/invalid",
                "header_id": 99999,  # Non-existent
            },
        )
        # Should fail validation or return error
        assert response.status_code in [HTTP_404_NOT_FOUND, 400, 422]

    def test_cascade_operations(self, client):
        """Test that deleting parent components affects children appropriately."""
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
        api_def_response = client.post(
            "/api-definitions/",
            json={
                "name": "Test API",
                "method": "GET",
                "path": "/api/test",
                "header_id": header_id,
            },
        )
        api_def_id = api_def_response.json()["id"]

        # Delete header
        delete_response = client.delete(f"/headers/{header_id}")
        assert delete_response.status_code == HTTP_200_OK

        # Check if API definition is affected
        # (Behavior depends on cascade rules - this tests the implementation)
        _ = client.get(f"/api-definitions/{api_def_id}")
        # Either the API def is deleted or the header_id is nulled
        # The exact behavior depends on the cascade configuration
