"""Verification script for execution engine HTTP client integration.

This script verifies that the execution engine correctly:
1. Creates HTTP client instances
2. Builds requests from API definitions
3. Applies parameter overrides
4. Validates responses
5. Extracts variables
"""

import asyncio
from unittest.mock import Mock, MagicMock, patch

# Mock the models
class MockHeader:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

class MockBody:
    def __init__(self):
        self.example_data = {
            "name": "test",
            "email": "test@example.com"
        }

class MockApiDefinition:
    def __init__(self):
        self.name = "Test API"
        self.method = Mock(value="POST")
        self.path = "/api/users/{id}"
        self.base_url = "https://api.example.com"
        self.timeout = 30
        self.header = MockHeader()
        self.request_body = MockBody()
        self.response_body = None
        self.inline_request_body = None
        self.query_parameters = {"page": 1}
        self.path_parameters = {"id": 123}

class MockScript:
    def __init__(self):
        self.name = "Test Script"
        self.api_definition = MockApiDefinition()
        self.timeout_override = None
        self.assertions = [
            {
                "type": "status_code",
                "expected": 200,
                "message": "Status should be 200"
            },
            {
                "type": "json_path",
                "path": "$.data.id",
                "assertion": "exists",
                "message": "Response should contain data.id"
            }
        ]
        self.extract_variables = {
            "user_id": "$.data.id",
            "user_name": "$.data.name"
        }
        self.output_variables = ["user_id", "user_name"]
        self.variables = {}
        self.parameters = []

class MockHttpResponse:
    def __init__(self):
        self.status_code = 200
        self.headers = {"content-type": "application/json"}
        self.request_time = 0.5
        self._json_data = {
            "data": {
                "id": 456,
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    
    def json(self):
        return self._json_data
    
    def jsonpath(self, path):
        """Simple JSONPath implementation for testing"""
        if path == "$.data.id":
            return self._json_data["data"]["id"]
        elif path == "$.data.name":
            return self._json_data["data"]["name"]
        elif path == "$.data":
            return self._json_data["data"]
        return None

async def test_execution_engine_integration():
    """Test the execution engine HTTP client integration."""
    from morado.services.execution_engine import ExecutionEngine
    from morado.services.execution_context import ScriptExecutionContext
    
    print("Testing Execution Engine HTTP Client Integration")
    print("=" * 60)
    
    # Create mock script and context
    script = MockScript()
    context = ScriptExecutionContext(script, override_params={
        "headers": {"Authorization": "Bearer token123"},
        "params": {"page": 2},  # Override query param
        "path_params": {"id": 999},  # Override path param
        "body": {"age": 30}  # Additional body field
    })
    
    # Create execution engine
    engine = ExecutionEngine()
    
    # Test 1: Build request from API definition
    print("\n1. Testing request building from API definition...")
    try:
        request_data = engine._build_request_from_api_definition(
            script.api_definition,
            context.params,
            context
        )
        
        print(f"   ✓ Method: {request_data['method']}")
        print(f"   ✓ URL: {request_data['url']}")
        print(f"   ✓ Headers: {request_data.get('headers', {})}")
        print(f"   ✓ Query Params: {request_data.get('params', {})}")
        print(f"   ✓ Body: {request_data.get('json', {})}")
        
        # Verify parameter override
        assert request_data['method'] == 'POST', "Method should be POST"
        assert '/999' in request_data['url'], "Path param should be overridden to 999"
        assert request_data['params']['page'] == 2, "Query param should be overridden to 2"
        assert 'Authorization' in request_data['headers'], "Authorization header should be present"
        assert request_data['json']['age'] == 30, "Body should include age field"
        
        print("   ✓ Request building: PASSED")
    except Exception as e:
        print(f"   ✗ Request building: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Validate response
    print("\n2. Testing response validation...")
    try:
        mock_response = MockHttpResponse()
        assertion_results = engine._validate_response(
            mock_response,
            script.assertions,
            context
        )
        
        print(f"   ✓ Assertions executed: {len(assertion_results)}")
        for result in assertion_results:
            status = "PASSED" if result['passed'] else "FAILED"
            print(f"   ✓ {result['type']}: {status}")
        
        # Verify all assertions passed
        all_passed = all(r['passed'] for r in assertion_results)
        assert all_passed, "All assertions should pass"
        
        print("   ✓ Response validation: PASSED")
    except Exception as e:
        print(f"   ✗ Response validation: FAILED - {e}")
        return False
    
    # Test 3: Extract variables
    print("\n3. Testing variable extraction...")
    try:
        mock_response = MockHttpResponse()
        extracted = engine._extract_variables(
            mock_response,
            script.extract_variables,
            context
        )
        
        print(f"   ✓ Variables extracted: {len(extracted)}")
        for var_name, var_value in extracted.items():
            print(f"   ✓ {var_name}: {var_value}")
        
        # Verify extracted variables
        assert extracted['user_id'] == 456, "user_id should be 456"
        assert extracted['user_name'] == "John Doe", "user_name should be John Doe"
        
        print("   ✓ Variable extraction: PASSED")
    except Exception as e:
        print(f"   ✗ Variable extraction: FAILED - {e}")
        return False
    
    # Test 4: Full script execution (with mocked HTTP client)
    print("\n4. Testing full script execution...")
    try:
        with patch('morado.common.http.create_default_client') as mock_client_factory:
            # Setup mock client
            mock_client = MagicMock()
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=None)
            mock_client.request = Mock(return_value=MockHttpResponse())
            mock_client_factory.return_value = mock_client
            
            # Execute script
            result = await engine.execute_script(script, context)
            
            print(f"   ✓ Execution status: {result.status.value}")
            print(f"   ✓ Success: {result.success}")
            print(f"   ✓ Duration: {result.duration:.3f}s")
            print(f"   ✓ Output variables: {result.output_variables}")
            
            # Verify execution result
            assert result.success, "Execution should succeed"
            assert result.output_variables['user_id'] == 456, "Output variable user_id should be 456"
            assert result.output_variables['user_name'] == "John Doe", "Output variable user_name should be John Doe"
            
            # Verify HTTP client was called correctly
            assert mock_client.request.called, "HTTP client request should be called"
            call_args = mock_client.request.call_args
            assert call_args[1]['method'] == 'POST', "Method should be POST"
            
            print("   ✓ Full script execution: PASSED")
    except Exception as e:
        print(f"   ✗ Full script execution: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("All tests PASSED! ✓")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_execution_engine_integration())
    exit(0 if success else 1)
