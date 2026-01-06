"""Verification script for HTTP client utility functions.

This script tests the utility functions implemented in task 6.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.utils import (
    resolve_variables,
    build_url,
    encode_query_params,
    serialize_body,
    mask_sensitive_data,
    mask_sensitive_headers,
    truncate_for_logging,
)
from morado.common.http.exceptions import VariableResolutionError


def test_resolve_variables():
    """Test variable resolution in templates."""
    print("Testing resolve_variables...")
    
    # Test basic variable resolution
    result = resolve_variables("Hello ${name}!", {"name": "World"})
    assert result == "Hello World!", f"Expected 'Hello World!', got '{result}'"
    
    # Test multiple variables
    result = resolve_variables(
        "${protocol}://${host}:${port}",
        {"protocol": "https", "host": "api.example.com", "port": 443}
    )
    assert result == "https://api.example.com:443", f"Unexpected result: {result}"
    
    # Test missing variable
    try:
        resolve_variables("Hello ${name}!", {})
        assert False, "Should have raised VariableResolutionError"
    except VariableResolutionError as e:
        assert "name" in e.missing_vars
        print(f"  ✓ Correctly raised error for missing variable: {e}")
    
    # Test empty template
    result = resolve_variables("", {"name": "World"})
    assert result == "", "Empty template should return empty string"
    
    print("  ✓ resolve_variables tests passed")


def test_build_url():
    """Test URL building with path parameters."""
    print("Testing build_url...")
    
    # Test basic URL building
    result = build_url("https://api.example.com", "/users/{id}", {"id": 123})
    assert result == "https://api.example.com/users/123", f"Unexpected result: {result}"
    
    # Test colon-style parameters
    result = build_url(
        "https://api.example.com",
        "/users/:id/posts/:post_id",
        {"id": 123, "post_id": 456}
    )
    assert result == "https://api.example.com/users/123/posts/456", f"Unexpected result: {result}"
    
    # Test without path parameters
    result = build_url("https://api.example.com", "/users")
    assert result == "https://api.example.com/users", f"Unexpected result: {result}"
    
    # Test trailing slash handling
    result = build_url("https://api.example.com/", "/users", None)
    assert result == "https://api.example.com/users", f"Unexpected result: {result}"
    
    print("  ✓ build_url tests passed")


def test_encode_query_params():
    """Test query parameter encoding."""
    print("Testing encode_query_params...")
    
    # Test basic encoding
    result = encode_query_params({"name": "John Doe", "age": 30})
    assert "name=John" in result and "age=30" in result, f"Unexpected result: {result}"
    
    # Test list parameters
    result = encode_query_params({"tags": ["python", "http"], "active": True})
    assert "tags=python" in result and "tags=http" in result, f"Unexpected result: {result}"
    
    # Test None filtering
    result = encode_query_params({"name": "John", "age": None})
    assert "name=John" in result and "age" not in result, f"Unexpected result: {result}"
    
    # Test empty params
    result = encode_query_params({})
    assert result == "", f"Expected empty string, got '{result}'"
    
    print("  ✓ encode_query_params tests passed")


def test_serialize_body():
    """Test request body serialization."""
    print("Testing serialize_body...")
    
    # Test JSON serialization
    data, content_type = serialize_body({"name": "John"}, "application/json")
    assert '"name"' in data and '"John"' in data, f"Unexpected data: {data}"
    assert content_type == "application/json"
    
    # Test form data serialization
    data, content_type = serialize_body({"name": "John"}, "application/x-www-form-urlencoded")
    assert "name=John" in data, f"Unexpected data: {data}"
    assert content_type == "application/x-www-form-urlencoded"
    
    # Test auto-detection (dict -> JSON)
    data, content_type = serialize_body({"name": "John"})
    assert '"name"' in data, f"Unexpected data: {data}"
    assert content_type == "application/json"
    
    # Test string pass-through
    data, content_type = serialize_body("raw text")
    assert data == "raw text"
    
    # Test None
    data, content_type = serialize_body(None)
    assert data is None
    
    print("  ✓ serialize_body tests passed")


def test_mask_sensitive_data():
    """Test sensitive data masking."""
    print("Testing mask_sensitive_data...")
    
    # Test password masking
    result = mask_sensitive_data({"username": "john", "password": "secret123"})
    assert result["username"] == "john", f"Username should not be masked"
    assert result["password"] == "***", f"Password should be masked"
    
    # Test API key masking
    result = mask_sensitive_data({"api_key": "abc123", "data": "public"})
    assert result["api_key"] == "***", f"API key should be masked"
    assert result["data"] == "public", f"Public data should not be masked"
    
    # Test nested structures
    result = mask_sensitive_data({
        "user": {
            "name": "john",
            "password": "secret"
        }
    })
    assert result["user"]["name"] == "john"
    assert result["user"]["password"] == "***"
    
    # Test list handling
    result = mask_sensitive_data([
        {"username": "john", "password": "secret"},
        {"username": "jane", "token": "abc123"}
    ])
    assert result[0]["password"] == "***"
    assert result[1]["token"] == "***"
    
    # Test custom sensitive keys
    result = mask_sensitive_data(
        {"custom_field": "sensitive", "public": "data"},
        sensitive_keys=["custom_field"]
    )
    assert result["custom_field"] == "***"
    assert result["public"] == "data"
    
    print("  ✓ mask_sensitive_data tests passed")


def test_mask_sensitive_headers():
    """Test sensitive header masking."""
    print("Testing mask_sensitive_headers...")
    
    # Test authorization header masking
    result = mask_sensitive_headers({
        "Content-Type": "application/json",
        "Authorization": "Bearer token123"
    })
    assert result["Content-Type"] == "application/json"
    assert result["Authorization"] == "***"
    
    # Test cookie masking
    result = mask_sensitive_headers({
        "Cookie": "session=abc123",
        "User-Agent": "TestClient"
    })
    assert result["Cookie"] == "***"
    assert result["User-Agent"] == "TestClient"
    
    # Test case-insensitive matching
    result = mask_sensitive_headers({
        "authorization": "Bearer token",
        "COOKIE": "session=123"
    })
    assert result["authorization"] == "***"
    assert result["COOKIE"] == "***"
    
    print("  ✓ mask_sensitive_headers tests passed")


def test_truncate_for_logging():
    """Test data truncation for logging."""
    print("Testing truncate_for_logging...")
    
    # Test short text (no truncation)
    result = truncate_for_logging("short text", max_size=100)
    assert result == "short text", f"Short text should not be truncated"
    
    # Test long text (truncation)
    long_text = "x" * 2000
    result = truncate_for_logging(long_text, max_size=10)
    assert result.startswith("xxxxxxxxxx...")
    assert "truncated" in result
    assert "2000" in result
    
    # Test None
    result = truncate_for_logging(None)
    assert result == "None"
    
    # Test dict
    result = truncate_for_logging({"key": "value"}, max_size=100)
    assert "key" in result and "value" in result
    
    # Test bytes
    result = truncate_for_logging(b"binary data", max_size=100)
    assert "binary data" in result
    
    print("  ✓ truncate_for_logging tests passed")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("HTTP Client Utils Verification")
    print("=" * 60)
    
    try:
        test_resolve_variables()
        test_build_url()
        test_encode_query_params()
        test_serialize_body()
        test_mask_sensitive_data()
        test_mask_sensitive_headers()
        test_truncate_for_logging()
        
        print("\n" + "=" * 60)
        print("✓ All utility function tests passed!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
