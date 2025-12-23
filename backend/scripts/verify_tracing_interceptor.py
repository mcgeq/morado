"""Verification script for tracing interceptor.

This script verifies that the tracing interceptor correctly:
1. Retrieves request_id from context
2. Retrieves user_id from context data
3. Adds tracing headers to requests
4. Respects existing headers
5. Works with custom header names
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.tracing_interceptor import TracingInterceptor
from morado.common.logger.context import (
    clear_context,
    get_request_id,
    set_context_data,
    set_request_id,
)


def test_basic_tracing():
    """Test basic tracing with request_id."""
    print("Test 1: Basic tracing with request_id")
    
    # Clear any existing context
    clear_context()
    
    # Set up context
    set_request_id("REQ-12345")
    
    # Create interceptor
    interceptor = TracingInterceptor()
    
    # Process request
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/users",
        {},
        params={"key": "value"}
    )
    
    # Verify
    assert headers.get("X-Request-ID") == "REQ-12345", f"Expected X-Request-ID to be REQ-12345, got {headers.get('X-Request-ID')}"
    assert method == "GET", f"Method should not change, got {method}"
    assert url == "https://api.example.com/users", f"URL should not change, got {url}"
    
    print("✓ Request ID added to headers")
    print(f"  Headers: {headers}")
    
    # Clean up
    clear_context()


def test_tracing_with_user_id():
    """Test tracing with both request_id and user_id."""
    print("\nTest 2: Tracing with request_id and user_id")
    
    # Clear any existing context
    clear_context()
    
    # Set up context
    set_request_id("REQ-67890")
    set_context_data("user_id", 42)
    
    # Create interceptor
    interceptor = TracingInterceptor()
    
    # Process request
    method, url, headers, kwargs = interceptor.before_request(
        "POST",
        "https://api.example.com/orders",
        {},
        json={"item": "book"}
    )
    
    # Verify
    assert headers.get("X-Request-ID") == "REQ-67890", f"Expected X-Request-ID to be REQ-67890, got {headers.get('X-Request-ID')}"
    assert headers.get("X-User-ID") == "42", f"Expected X-User-ID to be 42, got {headers.get('X-User-ID')}"
    
    print("✓ Request ID and User ID added to headers")
    print(f"  Headers: {headers}")
    
    # Clean up
    clear_context()


def test_no_context():
    """Test behavior when no context is set."""
    print("\nTest 3: No context set")
    
    # Clear any existing context
    clear_context()
    
    # Create interceptor
    interceptor = TracingInterceptor()
    
    # Process request
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/status",
        {},
    )
    
    # Verify - headers should be empty when no context
    assert "X-Request-ID" not in headers, f"X-Request-ID should not be present, got {headers}"
    assert "X-User-ID" not in headers, f"X-User-ID should not be present, got {headers}"
    
    print("✓ No headers added when context is empty")
    print(f"  Headers: {headers}")


def test_existing_headers_not_overwritten():
    """Test that existing tracing headers are not overwritten."""
    print("\nTest 4: Existing headers not overwritten")
    
    # Clear any existing context
    clear_context()
    
    # Set up context
    set_request_id("REQ-CONTEXT")
    set_context_data("user_id", 100)
    
    # Create interceptor
    interceptor = TracingInterceptor()
    
    # Process request with existing headers
    existing_headers = {
        "X-Request-ID": "REQ-EXISTING",
        "X-User-ID": "999"
    }
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/data",
        existing_headers,
    )
    
    # Verify - existing headers should be preserved
    assert headers.get("X-Request-ID") == "REQ-EXISTING", f"Existing X-Request-ID should be preserved, got {headers.get('X-Request-ID')}"
    assert headers.get("X-User-ID") == "999", f"Existing X-User-ID should be preserved, got {headers.get('X-User-ID')}"
    
    print("✓ Existing headers preserved")
    print(f"  Headers: {headers}")
    
    # Clean up
    clear_context()


def test_custom_header_names():
    """Test using custom header names."""
    print("\nTest 5: Custom header names")
    
    # Clear any existing context
    clear_context()
    
    # Set up context
    set_request_id("REQ-CUSTOM")
    set_context_data("user_id", 777)
    
    # Create interceptor with custom header names
    interceptor = TracingInterceptor(
        trace_header_name="X-Trace-ID",
        user_header_name="X-User"
    )
    
    # Process request
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/custom",
        {},
    )
    
    # Verify
    assert headers.get("X-Trace-ID") == "REQ-CUSTOM", f"Expected X-Trace-ID to be REQ-CUSTOM, got {headers.get('X-Trace-ID')}"
    assert headers.get("X-User") == "777", f"Expected X-User to be 777, got {headers.get('X-User')}"
    assert "X-Request-ID" not in headers, f"X-Request-ID should not be present with custom names"
    assert "X-User-ID" not in headers, f"X-User-ID should not be present with custom names"
    
    print("✓ Custom header names work correctly")
    print(f"  Headers: {headers}")
    
    # Clean up
    clear_context()


def test_disable_user_id():
    """Test disabling user_id propagation."""
    print("\nTest 6: Disable user_id propagation")
    
    # Clear any existing context
    clear_context()
    
    # Set up context
    set_request_id("REQ-NO-USER")
    set_context_data("user_id", 555)
    
    # Create interceptor with user_id disabled
    interceptor = TracingInterceptor(include_user_id=False)
    
    # Process request
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/public",
        {},
    )
    
    # Verify
    assert headers.get("X-Request-ID") == "REQ-NO-USER", f"Expected X-Request-ID to be REQ-NO-USER, got {headers.get('X-Request-ID')}"
    assert "X-User-ID" not in headers, f"X-User-ID should not be present when disabled, got {headers}"
    
    print("✓ User ID not included when disabled")
    print(f"  Headers: {headers}")
    
    # Clean up
    clear_context()


def test_user_id_type_conversion():
    """Test that user_id is converted to string."""
    print("\nTest 7: User ID type conversion")
    
    # Clear any existing context
    clear_context()
    
    # Set up context with integer user_id
    set_request_id("REQ-TYPE")
    set_context_data("user_id", 12345)
    
    # Create interceptor
    interceptor = TracingInterceptor()
    
    # Process request
    method, url, headers, kwargs = interceptor.before_request(
        "GET",
        "https://api.example.com/test",
        {},
    )
    
    # Verify - user_id should be converted to string
    assert headers.get("X-User-ID") == "12345", f"Expected X-User-ID to be '12345' (string), got {headers.get('X-User-ID')}"
    assert isinstance(headers.get("X-User-ID"), str), f"X-User-ID should be a string, got {type(headers.get('X-User-ID'))}"
    
    print("✓ User ID converted to string")
    print(f"  Headers: {headers}")
    
    # Clean up
    clear_context()


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Tracing Interceptor Verification")
    print("=" * 60)
    
    try:
        test_basic_tracing()
        test_tracing_with_user_id()
        test_no_context()
        test_existing_headers_not_overwritten()
        test_custom_header_names()
        test_disable_user_id()
        test_user_id_type_conversion()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

