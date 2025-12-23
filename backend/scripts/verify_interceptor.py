"""Verification script for interceptor implementation.

This script verifies that the interceptor mechanism is correctly implemented
and can be used to modify requests and responses.
"""

import sys
from pathlib import Path

# Add the backend/src directory to the Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.interceptor import (
    InterceptorManager,
    RequestInterceptor,
    ResponseInterceptor,
)
from morado.common.http.response import HttpResponse
from unittest.mock import Mock


# Create sample interceptors for testing
class AuthRequestInterceptor(RequestInterceptor):
    """Sample request interceptor that adds authentication."""

    def before_request(self, method, url, headers, **kwargs):
        headers["Authorization"] = "Bearer test-token"
        return method, url, headers, kwargs


class LoggingRequestInterceptor(RequestInterceptor):
    """Sample request interceptor that logs requests."""

    def __init__(self):
        self.logged_requests = []

    def before_request(self, method, url, headers, **kwargs):
        self.logged_requests.append({"method": method, "url": url})
        return method, url, headers, kwargs


class StatusCheckResponseInterceptor(ResponseInterceptor):
    """Sample response interceptor that checks status."""

    def __init__(self):
        self.checked_responses = []

    def after_response(self, response):
        self.checked_responses.append(response.status_code)
        return response


class HeaderModifyResponseInterceptor(ResponseInterceptor):
    """Sample response interceptor that modifies response."""

    def after_response(self, response):
        # In a real scenario, we might modify the response object
        # For this test, we just return it as-is
        return response


def test_interceptor_manager_creation():
    """Test that InterceptorManager can be created."""
    print("Testing InterceptorManager creation...")
    manager = InterceptorManager()
    assert manager.request_interceptor_count == 0
    assert manager.response_interceptor_count == 0
    print("✓ InterceptorManager created successfully")


def test_request_interceptor_registration():
    """Test that request interceptors can be registered."""
    print("\nTesting request interceptor registration...")
    manager = InterceptorManager()
    
    auth_interceptor = AuthRequestInterceptor()
    logging_interceptor = LoggingRequestInterceptor()
    
    manager.add_request_interceptor(auth_interceptor)
    assert manager.request_interceptor_count == 1
    
    manager.add_request_interceptor(logging_interceptor)
    assert manager.request_interceptor_count == 2
    
    print("✓ Request interceptors registered successfully")


def test_response_interceptor_registration():
    """Test that response interceptors can be registered."""
    print("\nTesting response interceptor registration...")
    manager = InterceptorManager()
    
    status_interceptor = StatusCheckResponseInterceptor()
    header_interceptor = HeaderModifyResponseInterceptor()
    
    manager.add_response_interceptor(status_interceptor)
    assert manager.response_interceptor_count == 1
    
    manager.add_response_interceptor(header_interceptor)
    assert manager.response_interceptor_count == 2
    
    print("✓ Response interceptors registered successfully")


def test_request_interceptor_chain():
    """Test that request interceptors are executed in order."""
    print("\nTesting request interceptor chain...")
    manager = InterceptorManager()
    
    auth_interceptor = AuthRequestInterceptor()
    logging_interceptor = LoggingRequestInterceptor()
    
    manager.add_request_interceptor(auth_interceptor)
    manager.add_request_interceptor(logging_interceptor)
    
    # Process a request
    method, url, headers, kwargs = manager.process_request(
        "GET",
        "https://api.example.com/users",
        {},
        params={"page": 1}
    )
    
    # Verify the auth header was added
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test-token"
    
    # Verify the logging interceptor recorded the request
    assert len(logging_interceptor.logged_requests) == 1
    assert logging_interceptor.logged_requests[0]["method"] == "GET"
    assert logging_interceptor.logged_requests[0]["url"] == "https://api.example.com/users"
    
    # Verify other parameters are preserved
    assert method == "GET"
    assert url == "https://api.example.com/users"
    assert kwargs["params"]["page"] == 1
    
    print("✓ Request interceptor chain executed successfully")


def test_response_interceptor_chain():
    """Test that response interceptors are executed in order."""
    print("\nTesting response interceptor chain...")
    manager = InterceptorManager()
    
    status_interceptor = StatusCheckResponseInterceptor()
    header_interceptor = HeaderModifyResponseInterceptor()
    
    manager.add_response_interceptor(status_interceptor)
    manager.add_response_interceptor(header_interceptor)
    
    # Create a mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.text = '{"message": "success"}'
    mock_response.content = b'{"message": "success"}'
    mock_response.url = "https://api.example.com/users"
    
    http_response = HttpResponse(mock_response, 0.5)
    
    # Process the response
    result = manager.process_response(http_response)
    
    # Verify the status interceptor recorded the status
    assert len(status_interceptor.checked_responses) == 1
    assert status_interceptor.checked_responses[0] == 200
    
    # Verify the response is returned
    assert result.status_code == 200
    
    print("✓ Response interceptor chain executed successfully")


def test_interceptor_clearing():
    """Test that interceptors can be cleared."""
    print("\nTesting interceptor clearing...")
    manager = InterceptorManager()
    
    manager.add_request_interceptor(AuthRequestInterceptor())
    manager.add_request_interceptor(LoggingRequestInterceptor())
    manager.add_response_interceptor(StatusCheckResponseInterceptor())
    
    assert manager.request_interceptor_count == 2
    assert manager.response_interceptor_count == 1
    
    # Clear request interceptors
    manager.clear_request_interceptors()
    assert manager.request_interceptor_count == 0
    assert manager.response_interceptor_count == 1
    
    # Clear response interceptors
    manager.clear_response_interceptors()
    assert manager.response_interceptor_count == 0
    
    # Add interceptors again
    manager.add_request_interceptor(AuthRequestInterceptor())
    manager.add_response_interceptor(StatusCheckResponseInterceptor())
    assert manager.request_interceptor_count == 1
    assert manager.response_interceptor_count == 1
    
    # Clear all interceptors
    manager.clear_all_interceptors()
    assert manager.request_interceptor_count == 0
    assert manager.response_interceptor_count == 0
    
    print("✓ Interceptor clearing works correctly")


def test_request_parameter_modification():
    """Test that interceptors can modify request parameters."""
    print("\nTesting request parameter modification...")
    
    class UrlModifyInterceptor(RequestInterceptor):
        def before_request(self, method, url, headers, **kwargs):
            # Add query parameter
            if "params" not in kwargs:
                kwargs["params"] = {}
            kwargs["params"]["api_key"] = "secret123"
            return method, url, headers, kwargs
    
    manager = InterceptorManager()
    manager.add_request_interceptor(UrlModifyInterceptor())
    
    method, url, headers, kwargs = manager.process_request(
        "GET",
        "https://api.example.com/data",
        {},
        params={"page": 1}
    )
    
    assert kwargs["params"]["page"] == 1
    assert kwargs["params"]["api_key"] == "secret123"
    
    print("✓ Request parameters modified successfully")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Interceptor Implementation Verification")
    print("=" * 60)
    
    try:
        test_interceptor_manager_creation()
        test_request_interceptor_registration()
        test_response_interceptor_registration()
        test_request_interceptor_chain()
        test_response_interceptor_chain()
        test_interceptor_clearing()
        test_request_parameter_modification()
        
        print("\n" + "=" * 60)
        print("✓ All verification tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
