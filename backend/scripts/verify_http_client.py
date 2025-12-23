"""Verification script for HTTP client implementation.

This script verifies that the HttpClient class is properly implemented
with all required methods and integrations.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.client import HttpClient
from morado.common.http.config import HttpClientConfig
from morado.common.http.session import SessionManager
from morado.common.http.retry import RetryConfig, RetryHandler, RetryStrategy
from morado.common.http.interceptor import InterceptorManager, RequestInterceptor, ResponseInterceptor
from morado.common.http.response import HttpResponse


def test_client_initialization():
    """Test that HttpClient can be initialized."""
    print("Testing HttpClient initialization...")
    
    # Test basic initialization
    client = HttpClient()
    assert client is not None
    print("✓ Basic initialization works")
    
    # Test initialization with parameters
    client = HttpClient(
        base_url="https://api.example.com",
        default_timeout=(5, 15),
        default_headers={"User-Agent": "TestClient/1.0"}
    )
    assert client._base_url == "https://api.example.com"
    assert client._default_timeout == (5, 15)
    assert client._default_headers["User-Agent"] == "TestClient/1.0"
    print("✓ Initialization with parameters works")
    
    # Test initialization with components
    session_manager = SessionManager()
    retry_handler = RetryHandler(RetryConfig(max_retries=3))
    interceptor_manager = InterceptorManager()
    
    client = HttpClient(
        session_manager=session_manager,
        retry_handler=retry_handler,
        interceptor_manager=interceptor_manager
    )
    assert client._session_manager is session_manager
    assert client._retry_handler is retry_handler
    assert client._interceptor_manager is interceptor_manager
    print("✓ Initialization with components works")


def test_from_config():
    """Test creating client from config."""
    print("\nTesting HttpClient.from_config()...")
    
    config = HttpClientConfig(
        base_url="https://api.example.com",
        connect_timeout=5,
        read_timeout=15,
        enable_retry=True,
        max_retries=3,
        retry_strategy="exponential"
    )
    
    client = HttpClient.from_config(config)
    assert client._base_url == "https://api.example.com"
    assert client._default_timeout == (5, 15)
    assert client._retry_handler is not None
    print("✓ from_config() works")


def test_http_methods():
    """Test that all HTTP method shortcuts exist."""
    print("\nTesting HTTP method shortcuts...")
    
    client = HttpClient()
    
    # Check that all methods exist
    assert hasattr(client, 'get')
    assert hasattr(client, 'post')
    assert hasattr(client, 'put')
    assert hasattr(client, 'patch')
    assert hasattr(client, 'delete')
    assert hasattr(client, 'head')
    assert hasattr(client, 'options')
    print("✓ All HTTP method shortcuts exist")
    
    # Check that they are callable
    assert callable(client.get)
    assert callable(client.post)
    assert callable(client.put)
    assert callable(client.patch)
    assert callable(client.delete)
    assert callable(client.head)
    assert callable(client.options)
    print("✓ All HTTP method shortcuts are callable")


def test_url_building():
    """Test URL building with base_url."""
    print("\nTesting URL building...")
    
    client = HttpClient(base_url="https://api.example.com")
    
    # Test relative URL
    url = client._build_url("/users")
    assert url == "https://api.example.com/users"
    print("✓ Relative URL building works")
    
    # Test absolute URL (should not be modified)
    url = client._build_url("https://other.example.com/data")
    assert url == "https://other.example.com/data"
    print("✓ Absolute URL is not modified")
    
    # Test without base_url
    client = HttpClient()
    url = client._build_url("/users")
    assert url == "/users"
    print("✓ URL building without base_url works")


def test_header_merging():
    """Test header merging."""
    print("\nTesting header merging...")
    
    client = HttpClient(default_headers={"User-Agent": "TestClient/1.0", "Accept": "application/json"})
    
    # Test with no request headers
    merged = client._merge_headers()
    assert merged["User-Agent"] == "TestClient/1.0"
    assert merged["Accept"] == "application/json"
    print("✓ Default headers are used")
    
    # Test with request headers (should override)
    merged = client._merge_headers({"Accept": "text/html", "Authorization": "Bearer token"})
    assert merged["User-Agent"] == "TestClient/1.0"
    assert merged["Accept"] == "text/html"  # Overridden
    assert merged["Authorization"] == "Bearer token"  # Added
    print("✓ Request headers override default headers")


def test_timeout_handling():
    """Test timeout handling."""
    print("\nTesting timeout handling...")
    
    client = HttpClient(default_timeout=(10, 30))
    
    # Test default timeout
    timeout = client._get_timeout()
    assert timeout == (10, 30)
    print("✓ Default timeout is used")
    
    # Test request-specific timeout
    timeout = client._get_timeout((5, 15))
    assert timeout == (5, 15)
    print("✓ Request-specific timeout overrides default")


def test_context_manager():
    """Test context manager support."""
    print("\nTesting context manager...")
    
    with HttpClient() as client:
        assert client is not None
    print("✓ Context manager works")


def test_interceptor_integration():
    """Test interceptor integration."""
    print("\nTesting interceptor integration...")
    
    class TestRequestInterceptor(RequestInterceptor):
        def before_request(self, method, url, headers, **kwargs):
            headers["X-Test"] = "test-value"
            return method, url, headers, kwargs
    
    class TestResponseInterceptor(ResponseInterceptor):
        def after_response(self, response):
            return response
    
    interceptor_manager = InterceptorManager()
    interceptor_manager.add_request_interceptor(TestRequestInterceptor())
    interceptor_manager.add_response_interceptor(TestResponseInterceptor())
    
    client = HttpClient(interceptor_manager=interceptor_manager)
    assert client._interceptor_manager.request_interceptor_count == 1
    assert client._interceptor_manager.response_interceptor_count == 1
    print("✓ Interceptor integration works")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("HTTP Client Implementation Verification")
    print("=" * 60)
    
    try:
        test_client_initialization()
        test_from_config()
        test_http_methods()
        test_url_building()
        test_header_merging()
        test_timeout_handling()
        test_context_manager()
        test_interceptor_integration()
        
        print("\n" + "=" * 60)
        print("✓ All verification tests passed!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
