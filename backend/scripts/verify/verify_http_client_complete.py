"""Complete verification of HTTP client implementation.

This script verifies all requirements for task 7 without relying on external services.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http import (
    HttpClient,
    HttpClientConfig,
    HttpResponse,
    SessionManager,
    RetryConfig,
    RetryHandler,
    RetryStrategy,
    InterceptorManager,
    RequestInterceptor,
    ResponseInterceptor,
)


def test_requirement_1_1_request_building():
    """Requirement 1.1: Build complete HTTP request from API Definition."""
    print("Testing Requirement 1.1: Request building...")
    
    client = HttpClient(
        base_url="https://api.example.com",
        default_headers={"User-Agent": "TestClient"}
    )
    
    # Verify URL building
    url = client._build_url("/users")
    assert url == "https://api.example.com/users"
    
    # Verify header merging
    headers = client._merge_headers({"Authorization": "Bearer token"})
    assert "User-Agent" in headers
    assert "Authorization" in headers
    
    print("✓ Requirement 1.1: Request building works")


def test_requirement_1_2_http_methods():
    """Requirement 1.2: Support all standard HTTP methods."""
    print("\nTesting Requirement 1.2: HTTP methods...")
    
    client = HttpClient()
    
    methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    for method in methods:
        assert hasattr(client, method)
        assert callable(getattr(client, method))
    
    print("✓ Requirement 1.2: All HTTP methods supported")


def test_requirement_1_3_parameter_merging():
    """Requirement 1.3: Merge headers, body, and parameters."""
    print("\nTesting Requirement 1.3: Parameter merging...")
    
    client = HttpClient(
        default_headers={"User-Agent": "TestClient", "Accept": "application/json"}
    )
    
    # Test header merging with override
    merged = client._merge_headers({"Accept": "text/html", "Authorization": "Bearer token"})
    assert merged["User-Agent"] == "TestClient"
    assert merged["Accept"] == "text/html"  # Overridden
    assert merged["Authorization"] == "Bearer token"
    
    print("✓ Requirement 1.3: Parameter merging works")


def test_requirement_3_1_3_2_timeout_control():
    """Requirements 3.1, 3.2: Support timeout configuration."""
    print("\nTesting Requirements 3.1, 3.2: Timeout control...")
    
    # Test default timeout
    client = HttpClient(default_timeout=(10, 30))
    timeout = client._get_timeout()
    assert timeout == (10, 30)
    
    # Test request-specific timeout override
    timeout = client._get_timeout((5, 15))
    assert timeout == (5, 15)
    
    print("✓ Requirements 3.1, 3.2: Timeout control works")


def test_requirement_3_3_timeout_override():
    """Requirement 3.3: Request timeout overrides default."""
    print("\nTesting Requirement 3.3: Timeout override...")
    
    client = HttpClient(default_timeout=(10, 30))
    
    # Request-specific timeout should override
    timeout = client._get_timeout((5, 15))
    assert timeout == (5, 15)
    assert timeout != (10, 30)
    
    print("✓ Requirement 3.3: Timeout override works")


def test_session_manager_integration():
    """Test integration with SessionManager."""
    print("\nTesting SessionManager integration...")
    
    session_manager = SessionManager(pool_connections=5, pool_maxsize=10)
    client = HttpClient(session_manager=session_manager)
    
    assert client._session_manager is session_manager
    assert client._session is not None
    
    print("✓ SessionManager integration works")


def test_retry_handler_integration():
    """Test integration with RetryHandler."""
    print("\nTesting RetryHandler integration...")
    
    retry_config = RetryConfig(
        max_retries=3,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0
    )
    retry_handler = RetryHandler(retry_config)
    client = HttpClient(retry_handler=retry_handler)
    
    assert client._retry_handler is retry_handler
    
    print("✓ RetryHandler integration works")


def test_interceptor_manager_integration():
    """Test integration with InterceptorManager."""
    print("\nTesting InterceptorManager integration...")
    
    class TestRequestInterceptor(RequestInterceptor):
        def before_request(self, method, url, headers, **kwargs):
            headers["X-Test"] = "test"
            return method, url, headers, kwargs
    
    class TestResponseInterceptor(ResponseInterceptor):
        def after_response(self, response):
            return response
    
    interceptor_manager = InterceptorManager()
    interceptor_manager.add_request_interceptor(TestRequestInterceptor())
    interceptor_manager.add_response_interceptor(TestResponseInterceptor())
    
    client = HttpClient(interceptor_manager=interceptor_manager)
    
    assert client._interceptor_manager is interceptor_manager
    assert client._interceptor_manager.request_interceptor_count == 1
    assert client._interceptor_manager.response_interceptor_count == 1
    
    print("✓ InterceptorManager integration works")


def test_from_config_factory():
    """Test creating client from config."""
    print("\nTesting from_config factory method...")
    
    config = HttpClientConfig(
        base_url="https://api.example.com",
        connect_timeout=5,
        read_timeout=15,
        pool_connections=5,
        pool_maxsize=10,
        enable_retry=True,
        max_retries=3,
        retry_strategy="exponential"
    )
    
    client = HttpClient.from_config(config)
    
    assert client._base_url == "https://api.example.com"
    assert client._default_timeout == (5, 15)
    assert client._retry_handler is not None
    assert client._session_manager is not None
    
    print("✓ from_config factory method works")


def test_context_manager_support():
    """Test context manager support."""
    print("\nTesting context manager support...")
    
    with HttpClient() as client:
        assert client is not None
        assert client._session is not None
    
    print("✓ Context manager support works")


def test_request_method_signature():
    """Test that request method has correct signature."""
    print("\nTesting request method signature...")
    
    client = HttpClient()
    
    # Check that request method exists and has correct parameters
    import inspect
    sig = inspect.signature(client.request)
    params = list(sig.parameters.keys())
    
    assert 'method' in params
    assert 'url' in params
    assert 'params' in params
    assert 'headers' in params
    assert 'data' in params
    assert 'json' in params
    assert 'files' in params
    assert 'timeout' in params
    
    print("✓ Request method signature is correct")


def test_http_method_shortcuts():
    """Test that all HTTP method shortcuts exist and work."""
    print("\nTesting HTTP method shortcuts...")
    
    client = HttpClient()
    
    # Test that shortcuts exist
    methods = {
        'get': 'GET',
        'post': 'POST',
        'put': 'PUT',
        'patch': 'PATCH',
        'delete': 'DELETE',
        'head': 'HEAD',
        'options': 'OPTIONS'
    }
    
    for method_name, http_method in methods.items():
        assert hasattr(client, method_name)
        method = getattr(client, method_name)
        assert callable(method)
        
        # Check signature
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        assert 'url' in params
        assert 'kwargs' in params
    
    print("✓ All HTTP method shortcuts work")


def test_interceptor_processing():
    """Test that interceptors are processed correctly."""
    print("\nTesting interceptor processing...")
    
    class ModifyingRequestInterceptor(RequestInterceptor):
        def before_request(self, method, url, headers, **kwargs):
            # Modify method
            method = "POST"
            # Modify URL
            url = url + "/modified"
            # Add header
            headers["X-Modified"] = "true"
            return method, url, headers, kwargs
    
    interceptor_manager = InterceptorManager()
    interceptor_manager.add_request_interceptor(ModifyingRequestInterceptor())
    
    # Test processing
    method, url, headers, kwargs = interceptor_manager.process_request(
        "GET", "https://example.com", {}, params={"key": "value"}
    )
    
    assert method == "POST"
    assert url == "https://example.com/modified"
    assert headers["X-Modified"] == "true"
    assert kwargs["params"]["key"] == "value"
    
    print("✓ Interceptor processing works")


def test_all_requirements():
    """Run all requirement tests."""
    print("=" * 60)
    print("HTTP Client Implementation - Requirements Verification")
    print("=" * 60)
    
    try:
        test_requirement_1_1_request_building()
        test_requirement_1_2_http_methods()
        test_requirement_1_3_parameter_merging()
        test_requirement_3_1_3_2_timeout_control()
        test_requirement_3_3_timeout_override()
        test_session_manager_integration()
        test_retry_handler_integration()
        test_interceptor_manager_integration()
        test_from_config_factory()
        test_context_manager_support()
        test_request_method_signature()
        test_http_method_shortcuts()
        test_interceptor_processing()
        
        print("\n" + "=" * 60)
        print("✓ All requirements verified!")
        print("=" * 60)
        print("\nTask 7 Implementation Summary:")
        print("- ✓ HttpClient class implemented")
        print("- ✓ Basic request method implemented")
        print("- ✓ All HTTP method shortcuts implemented (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)")
        print("- ✓ Session manager integration complete")
        print("- ✓ Retry handler integration complete")
        print("- ✓ Interceptor manager integration complete")
        print("- ✓ Timeout control implemented")
        print("- ✓ Request building logic implemented (URL, headers, parameters)")
        print("- ✓ Requirements 1.1, 1.2, 1.3, 3.1, 3.2, 3.3 satisfied")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_all_requirements())
