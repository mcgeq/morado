"""Integration test for HTTP client implementation.

This script tests the HTTP client with a real HTTP server (httpbin.org)
to verify that all functionality works correctly.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http import (
    HttpClient,
    HttpClientConfig,
    RequestInterceptor,
    ResponseInterceptor,
    InterceptorManager,
    RetryConfig,
    RetryHandler,
    RetryStrategy,
)


class LoggingRequestInterceptor(RequestInterceptor):
    """Test interceptor that logs requests."""
    
    def __init__(self):
        self.requests = []
    
    def before_request(self, method, url, headers, **kwargs):
        self.requests.append({
            'method': method,
            'url': url,
            'headers': headers.copy()
        })
        # Add a custom header
        headers['X-Test-Interceptor'] = 'request'
        return method, url, headers, kwargs


class LoggingResponseInterceptor(ResponseInterceptor):
    """Test interceptor that logs responses."""
    
    def __init__(self):
        self.responses = []
    
    def after_response(self, response):
        self.responses.append({
            'status_code': response.status_code,
            'headers': response.headers.copy()
        })
        return response


def test_basic_get_request():
    """Test basic GET request."""
    print("Testing basic GET request...")
    
    client = HttpClient()
    response = client.get("https://httpbin.org/get")
    
    assert response.status_code == 200
    assert response.is_success()
    
    data = response.json()
    assert 'url' in data
    assert 'headers' in data
    
    print("✓ Basic GET request works")


def test_post_with_json():
    """Test POST request with JSON body."""
    print("\nTesting POST with JSON...")
    
    client = HttpClient()
    payload = {"name": "test", "value": 123}
    response = client.post("https://httpbin.org/post", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data['json'] == payload
    
    print("✓ POST with JSON works")


def test_headers_merging():
    """Test header merging."""
    print("\nTesting header merging...")
    
    client = HttpClient(
        default_headers={"User-Agent": "TestClient/1.0"}
    )
    
    response = client.get(
        "https://httpbin.org/headers",
        headers={"X-Custom": "custom-value"}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    headers = data['headers']
    assert 'User-Agent' in headers
    assert 'X-Custom' in headers
    
    print("✓ Header merging works")


def test_query_parameters():
    """Test query parameters."""
    print("\nTesting query parameters...")
    
    client = HttpClient()
    response = client.get(
        "https://httpbin.org/get",
        params={"key1": "value1", "key2": "value2"}
    )
    
    assert response.status_code == 200
    
    data = response.json()
    args = data['args']
    assert args['key1'] == 'value1'
    assert args['key2'] == 'value2'
    
    print("✓ Query parameters work")


def test_base_url():
    """Test base URL functionality."""
    print("\nTesting base URL...")
    
    client = HttpClient(base_url="https://httpbin.org")
    response = client.get("/get")
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'httpbin.org' in data['url']
    
    print("✓ Base URL works")


def test_interceptors():
    """Test request and response interceptors."""
    print("\nTesting interceptors...")
    
    request_interceptor = LoggingRequestInterceptor()
    response_interceptor = LoggingResponseInterceptor()
    
    interceptor_manager = InterceptorManager()
    interceptor_manager.add_request_interceptor(request_interceptor)
    interceptor_manager.add_response_interceptor(response_interceptor)
    
    client = HttpClient(interceptor_manager=interceptor_manager)
    response = client.get("https://httpbin.org/get")
    
    assert response.status_code == 200
    
    # Check that interceptors were called
    assert len(request_interceptor.requests) == 1
    assert len(response_interceptor.responses) == 1
    
    # Check that request interceptor modified headers
    data = response.json()
    assert 'X-Test-Interceptor' in data['headers']
    
    print("✓ Interceptors work")


def test_all_http_methods():
    """Test all HTTP methods."""
    print("\nTesting all HTTP methods...")
    
    client = HttpClient()
    
    # GET
    response = client.get("https://httpbin.org/get")
    assert response.status_code == 200
    print("  ✓ GET works")
    
    # POST
    response = client.post("https://httpbin.org/post", json={"test": "data"})
    assert response.status_code == 200
    print("  ✓ POST works")
    
    # PUT
    response = client.put("https://httpbin.org/put", json={"test": "data"})
    assert response.status_code == 200
    print("  ✓ PUT works")
    
    # PATCH
    response = client.patch("https://httpbin.org/patch", json={"test": "data"})
    assert response.status_code == 200
    print("  ✓ PATCH works")
    
    # DELETE
    response = client.delete("https://httpbin.org/delete")
    assert response.status_code == 200
    print("  ✓ DELETE works")
    
    print("✓ All HTTP methods work")


def test_context_manager():
    """Test context manager."""
    print("\nTesting context manager...")
    
    with HttpClient() as client:
        response = client.get("https://httpbin.org/get")
        assert response.status_code == 200
    
    print("✓ Context manager works")


def test_from_config():
    """Test creating client from config."""
    print("\nTesting from_config()...")
    
    config = HttpClientConfig(
        base_url="https://httpbin.org",
        connect_timeout=10,
        read_timeout=30,
        enable_retry=False
    )
    
    client = HttpClient.from_config(config)
    response = client.get("/get")
    
    assert response.status_code == 200
    
    print("✓ from_config() works")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("HTTP Client Integration Tests")
    print("=" * 60)
    print("\nNote: These tests require internet connection to httpbin.org")
    print()
    
    try:
        test_basic_get_request()
        test_post_with_json()
        test_headers_merging()
        test_query_parameters()
        test_base_url()
        test_interceptors()
        test_all_http_methods()
        test_context_manager()
        test_from_config()
        
        print("\n" + "=" * 60)
        print("✓ All integration tests passed!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
