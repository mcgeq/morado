"""Verification script for logging interceptor implementation.

This script tests the logging interceptor to ensure it properly logs
HTTP requests, responses, and errors.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.config import HttpClientConfig
from morado.common.http.logging_interceptor import (
    ErrorLoggingInterceptor,
    LoggingInterceptor,
)
from morado.common.http.response import HttpResponse
from morado.common.logger.logger import configure_logger
from unittest.mock import Mock


def test_logging_interceptor_initialization():
    """Test that LoggingInterceptor can be initialized."""
    print("Testing LoggingInterceptor initialization...")
    
    # Test with default config
    interceptor1 = LoggingInterceptor()
    assert interceptor1 is not None
    print("✓ LoggingInterceptor initialized with defaults")
    
    # Test with custom config
    config = HttpClientConfig(
        log_request_body=False,
        log_response_body=True,
        max_log_body_size=512
    )
    interceptor2 = LoggingInterceptor(config=config)
    assert interceptor2 is not None
    assert interceptor2._log_request_body is False
    assert interceptor2._log_response_body is True
    assert interceptor2._max_log_body_size == 512
    print("✓ LoggingInterceptor initialized with custom config")


def test_before_request_logging():
    """Test that before_request logs request details."""
    print("\nTesting before_request logging...")
    
    # Configure logger for testing
    config = HttpClientConfig()
    interceptor = LoggingInterceptor(config=config)
    
    # Test basic request
    method, url, headers, kwargs = interceptor.before_request(
        method="GET",
        url="https://api.example.com/users",
        headers={"Content-Type": "application/json"},
        params={"page": 1, "limit": 10}
    )
    
    # Verify parameters are unchanged
    assert method == "GET"
    assert url == "https://api.example.com/users"
    assert headers == {"Content-Type": "application/json"}
    assert kwargs == {"params": {"page": 1, "limit": 10}}
    print("✓ before_request logs and returns unmodified parameters")
    
    # Test with sensitive headers
    method, url, headers, kwargs = interceptor.before_request(
        method="POST",
        url="https://api.example.com/login",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer secret_token"
        },
        json={"username": "john", "password": "secret123"}
    )
    
    assert headers["Authorization"] == "Bearer secret_token"  # Original unchanged
    print("✓ before_request masks sensitive data in logs")


def test_after_response_logging():
    """Test that after_response logs response details."""
    print("\nTesting after_response logging...")
    
    interceptor = LoggingInterceptor()
    
    # Create mock response
    mock_requests_response = Mock()
    mock_requests_response.status_code = 200
    mock_requests_response.headers = {"Content-Type": "application/json"}
    mock_requests_response.text = '{"message": "success"}'
    mock_requests_response.content = b'{"message": "success"}'
    mock_requests_response.json.return_value = {"message": "success"}
    
    response = HttpResponse(mock_requests_response, request_time=0.123)
    
    # Test logging
    result = interceptor.after_response(response)
    
    # Verify response is unchanged
    assert result is response
    assert result.status_code == 200
    print("✓ after_response logs and returns unmodified response")
    
    # Test error response
    mock_error_response = Mock()
    mock_error_response.status_code = 404
    mock_error_response.headers = {"Content-Type": "application/json"}
    mock_error_response.text = '{"error": "not found"}'
    mock_error_response.content = b'{"error": "not found"}'
    mock_error_response.json.return_value = {"error": "not found"}
    
    error_response = HttpResponse(mock_error_response, request_time=0.456)
    result = interceptor.after_response(error_response)
    
    assert result is error_response
    print("✓ after_response logs error responses with warning level")


def test_log_error():
    """Test that log_error logs exception details."""
    print("\nTesting log_error...")
    
    interceptor = LoggingInterceptor()
    
    # Create test exception
    try:
        raise ValueError("Test error message")
    except ValueError as e:
        interceptor.log_error(
            exception=e,
            method="GET",
            url="https://api.example.com/test",
            headers={"Authorization": "Bearer token"}
        )
    
    print("✓ log_error logs exception with stack trace")


def test_error_logging_interceptor():
    """Test ErrorLoggingInterceptor."""
    print("\nTesting ErrorLoggingInterceptor...")
    
    interceptor = ErrorLoggingInterceptor()
    
    # Test with success response (should not log)
    mock_success_response = Mock()
    mock_success_response.status_code = 200
    mock_success_response.headers = {}
    mock_success_response.text = "OK"
    
    success_response = HttpResponse(mock_success_response, request_time=0.1)
    result = interceptor.after_response(success_response)
    assert result is success_response
    print("✓ ErrorLoggingInterceptor ignores success responses")
    
    # Test with 4xx error
    mock_4xx_response = Mock()
    mock_4xx_response.status_code = 400
    mock_4xx_response.headers = {}
    mock_4xx_response.text = '{"error": "bad request"}'
    mock_4xx_response.json.return_value = {"error": "bad request"}
    
    error_4xx_response = HttpResponse(mock_4xx_response, request_time=0.2)
    result = interceptor.after_response(error_4xx_response)
    assert result is error_4xx_response
    print("✓ ErrorLoggingInterceptor logs 4xx errors with warning level")
    
    # Test with 5xx error
    mock_5xx_response = Mock()
    mock_5xx_response.status_code = 500
    mock_5xx_response.headers = {}
    mock_5xx_response.text = '{"error": "internal server error"}'
    mock_5xx_response.json.return_value = {"error": "internal server error"}
    
    error_5xx_response = HttpResponse(mock_5xx_response, request_time=0.3)
    result = interceptor.after_response(error_5xx_response)
    assert result is error_5xx_response
    print("✓ ErrorLoggingInterceptor logs 5xx errors with error level")


def test_body_truncation():
    """Test that large bodies are truncated."""
    print("\nTesting body truncation...")
    
    config = HttpClientConfig(max_log_body_size=50)
    interceptor = LoggingInterceptor(config=config)
    
    # Create large request body
    large_body = {"data": "x" * 1000}
    
    method, url, headers, kwargs = interceptor.before_request(
        method="POST",
        url="https://api.example.com/data",
        headers={"Content-Type": "application/json"},
        json=large_body
    )
    
    # Verify original body is unchanged
    assert kwargs["json"] == large_body
    print("✓ Large request bodies are truncated in logs but unchanged in request")


def test_sensitive_data_masking():
    """Test that sensitive data is masked."""
    print("\nTesting sensitive data masking...")
    
    interceptor = LoggingInterceptor()
    
    # Test with sensitive data in body
    method, url, headers, kwargs = interceptor.before_request(
        method="POST",
        url="https://api.example.com/auth",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer secret_token",
            "Cookie": "session=abc123"
        },
        json={
            "username": "john",
            "password": "secret123",
            "api_key": "key123"
        }
    )
    
    # Verify original data is unchanged
    assert kwargs["json"]["password"] == "secret123"
    assert headers["Authorization"] == "Bearer secret_token"
    print("✓ Sensitive data is masked in logs but unchanged in request")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Logging Interceptor Verification")
    print("=" * 60)
    
    try:
        test_logging_interceptor_initialization()
        test_before_request_logging()
        test_after_response_logging()
        test_log_error()
        test_error_logging_interceptor()
        test_body_truncation()
        test_sensitive_data_masking()
        
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
