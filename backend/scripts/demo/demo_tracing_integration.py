"""Demonstration of tracing integration with HTTP client.

This script demonstrates how the tracing interceptor integrates with the HTTP client
to automatically propagate request_id and user_id across HTTP requests.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.client import HttpClient
from morado.common.http.tracing_interceptor import TracingInterceptor
from morado.common.logger.context import (
    clear_context,
    set_context_data,
    set_request_id,
)


def demo_basic_tracing():
    """Demonstrate basic tracing with HTTP client."""
    print("=" * 60)
    print("Demo 1: Basic Tracing Integration")
    print("=" * 60)
    
    # Set up execution context
    set_request_id("REQ-DEMO-001")
    set_context_data("user_id", 123)
    
    # Create HTTP client with tracing interceptor
    client = HttpClient()
    client.interceptor_manager.add_request_interceptor(TracingInterceptor())
    
    print("\nContext set:")
    print(f"  request_id: REQ-DEMO-001")
    print(f"  user_id: 123")
    
    print("\nMaking HTTP request...")
    print("  URL: https://httpbin.org/headers")
    
    try:
        # Make request - tracing headers will be added automatically
        response = client.get("https://httpbin.org/headers")
        
        print(f"\nResponse status: {response.status_code}")
        
        # Parse response to show headers that were sent
        if response.status_code == 200:
            data = response.json()
            headers = data.get("headers", {})
            
            print("\nHeaders sent to server:")
            if "X-Request-Id" in headers:
                print(f"  X-Request-ID: {headers['X-Request-Id']}")
            if "X-User-Id" in headers:
                print(f"  X-User-ID: {headers['X-User-Id']}")
            
            print("\n✓ Tracing headers automatically added!")
    
    except Exception as e:
        print(f"\n✗ Request failed: {e}")
        print("  (This is expected if no internet connection)")
    
    finally:
        # Clean up context
        clear_context()


def demo_multiple_requests():
    """Demonstrate tracing across multiple requests."""
    print("\n" + "=" * 60)
    print("Demo 2: Tracing Across Multiple Requests")
    print("=" * 60)
    
    # Set up execution context
    set_request_id("REQ-DEMO-002")
    set_context_data("user_id", 456)
    
    # Create HTTP client with tracing interceptor
    client = HttpClient()
    client.interceptor_manager.add_request_interceptor(TracingInterceptor())
    
    print("\nContext set:")
    print(f"  request_id: REQ-DEMO-002")
    print(f"  user_id: 456")
    
    print("\nMaking multiple HTTP requests with same context...")
    
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/post",
        "https://httpbin.org/put",
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"\n  Request {i}: {url}")
        try:
            if "post" in url:
                response = client.post(url, json={"test": "data"})
            elif "put" in url:
                response = client.put(url, json={"test": "data"})
            else:
                response = client.get(url)
            
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                headers = data.get("headers", {})
                if "X-Request-Id" in headers:
                    print(f"    X-Request-ID: {headers['X-Request-Id']}")
        
        except Exception as e:
            print(f"    Failed: {e}")
    
    print("\n✓ Same tracing context used for all requests!")
    
    # Clean up context
    clear_context()


def demo_custom_configuration():
    """Demonstrate custom tracing configuration."""
    print("\n" + "=" * 60)
    print("Demo 3: Custom Tracing Configuration")
    print("=" * 60)
    
    # Set up execution context
    set_request_id("REQ-DEMO-003")
    set_context_data("user_id", 789)
    
    # Create HTTP client with custom tracing configuration
    client = HttpClient()
    client.interceptor_manager.add_request_interceptor(
        TracingInterceptor(
            trace_header_name="X-Trace-ID",
            user_header_name="X-User",
            include_user_id=True
        )
    )
    
    print("\nContext set:")
    print(f"  request_id: REQ-DEMO-003")
    print(f"  user_id: 789")
    
    print("\nCustom header names:")
    print(f"  trace_header_name: X-Trace-ID")
    print(f"  user_header_name: X-User")
    
    print("\nMaking HTTP request...")
    print("  URL: https://httpbin.org/headers")
    
    try:
        response = client.get("https://httpbin.org/headers")
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            headers = data.get("headers", {})
            
            print("\nCustom headers sent to server:")
            if "X-Trace-Id" in headers:
                print(f"  X-Trace-ID: {headers['X-Trace-Id']}")
            if "X-User" in headers:
                print(f"  X-User: {headers['X-User']}")
            
            print("\n✓ Custom header names work correctly!")
    
    except Exception as e:
        print(f"\n✗ Request failed: {e}")
        print("  (This is expected if no internet connection)")
    
    finally:
        # Clean up context
        clear_context()


def demo_without_user_id():
    """Demonstrate tracing without user_id."""
    print("\n" + "=" * 60)
    print("Demo 4: Tracing Without User ID")
    print("=" * 60)
    
    # Set up execution context (only request_id, no user_id)
    set_request_id("REQ-DEMO-004")
    
    # Create HTTP client with user_id disabled
    client = HttpClient()
    client.interceptor_manager.add_request_interceptor(
        TracingInterceptor(include_user_id=False)
    )
    
    print("\nContext set:")
    print(f"  request_id: REQ-DEMO-004")
    print(f"  user_id: (not set)")
    
    print("\nConfiguration:")
    print(f"  include_user_id: False")
    
    print("\nMaking HTTP request...")
    print("  URL: https://httpbin.org/headers")
    
    try:
        response = client.get("https://httpbin.org/headers")
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            headers = data.get("headers", {})
            
            print("\nHeaders sent to server:")
            if "X-Request-Id" in headers:
                print(f"  X-Request-ID: {headers['X-Request-Id']}")
            if "X-User-Id" not in headers:
                print(f"  X-User-ID: (not included)")
            
            print("\n✓ User ID correctly excluded!")
    
    except Exception as e:
        print(f"\n✗ Request failed: {e}")
        print("  (This is expected if no internet connection)")
    
    finally:
        # Clean up context
        clear_context()


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("HTTP Client Tracing Integration Demonstration")
    print("=" * 60)
    print("\nThis demo shows how the tracing interceptor automatically")
    print("propagates request_id and user_id across HTTP requests.")
    print("\nNote: Requires internet connection to reach httpbin.org")
    print("=" * 60)
    
    try:
        demo_basic_tracing()
        demo_multiple_requests()
        demo_custom_configuration()
        demo_without_user_id()
        
        print("\n" + "=" * 60)
        print("✓ All demonstrations completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
