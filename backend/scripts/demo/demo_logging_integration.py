"""Demo script showing logging interceptor integration with HTTP client.

This script demonstrates how the logging interceptor integrates with the
HTTP client to provide comprehensive request/response logging.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http import (
    HttpClient,
    HttpClientConfig,
    InterceptorManager,
    SessionManager,
)
from morado.common.http.logging_interceptor import (
    ErrorLoggingInterceptor,
    LoggingInterceptor,
)
from morado.common.logger.logger import configure_logger, LoggerConfig


def demo_basic_logging():
    """Demo basic request/response logging."""
    print("=" * 60)
    print("Demo: Basic Request/Response Logging")
    print("=" * 60)
    
    # Configure logger
    configure_logger(
        config=LoggerConfig(
            level="INFO",
            format="console"
        )
    )
    
    # Create HTTP client with logging interceptor
    config = HttpClientConfig(
        enable_logging=True,
        log_request_body=True,
        log_response_body=True,
        max_log_body_size=1024
    )
    
    session_manager = SessionManager()
    interceptor_manager = InterceptorManager()
    
    # Add logging interceptor
    logging_interceptor = LoggingInterceptor(config=config)
    interceptor_manager.add_request_interceptor(logging_interceptor)
    interceptor_manager.add_response_interceptor(logging_interceptor)
    
    # Create client
    client = HttpClient(
        session_manager=session_manager,
        interceptor_manager=interceptor_manager,
        config=config
    )
    
    print("\nMaking a GET request to httpbin.org...")
    try:
        response = client.get(
            "https://httpbin.org/get",
            params={"key": "value", "test": "demo"}
        )
        print(f"Response status: {response.status_code}")
        print(f"Response time: {response.request_time:.3f}s")
    except Exception as e:
        print(f"Request failed: {e}")
    
    print("\nMaking a POST request with JSON body...")
    try:
        response = client.post(
            "https://httpbin.org/post",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secret123"  # This will be masked in logs
            }
        )
        print(f"Response status: {response.status_code}")
        print(f"Response time: {response.request_time:.3f}s")
    except Exception as e:
        print(f"Request failed: {e}")


def demo_error_logging():
    """Demo error logging with ErrorLoggingInterceptor."""
    print("\n" + "=" * 60)
    print("Demo: Error Logging")
    print("=" * 60)
    
    # Create HTTP client with both logging interceptors
    config = HttpClientConfig(enable_logging=True)
    
    session_manager = SessionManager()
    interceptor_manager = InterceptorManager()
    
    # Add both interceptors
    logging_interceptor = LoggingInterceptor(config=config)
    error_interceptor = ErrorLoggingInterceptor()
    
    interceptor_manager.add_request_interceptor(logging_interceptor)
    interceptor_manager.add_response_interceptor(logging_interceptor)
    interceptor_manager.add_response_interceptor(error_interceptor)
    
    client = HttpClient(
        session_manager=session_manager,
        interceptor_manager=interceptor_manager,
        config=config
    )
    
    print("\nMaking a request that returns 404...")
    try:
        response = client.get("https://httpbin.org/status/404")
        print(f"Response status: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")
    
    print("\nMaking a request that returns 500...")
    try:
        response = client.get("https://httpbin.org/status/500")
        print(f"Response status: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")


def demo_sensitive_data_masking():
    """Demo sensitive data masking in logs."""
    print("\n" + "=" * 60)
    print("Demo: Sensitive Data Masking")
    print("=" * 60)
    
    config = HttpClientConfig(
        enable_logging=True,
        log_request_body=True,
        log_response_body=True
    )
    
    session_manager = SessionManager()
    interceptor_manager = InterceptorManager()
    
    logging_interceptor = LoggingInterceptor(config=config)
    interceptor_manager.add_request_interceptor(logging_interceptor)
    interceptor_manager.add_response_interceptor(logging_interceptor)
    
    client = HttpClient(
        session_manager=session_manager,
        interceptor_manager=interceptor_manager,
        config=config
    )
    
    print("\nMaking a request with sensitive headers and body...")
    print("(Authorization header and password field will be masked in logs)")
    
    try:
        response = client.post(
            "https://httpbin.org/post",
            headers={
                "Authorization": "Bearer secret_token_12345",
                "X-API-Key": "api_key_67890"
            },
            json={
                "username": "admin",
                "password": "super_secret_password",
                "api_key": "another_secret_key",
                "public_data": "This is not sensitive"
            }
        )
        print(f"Response status: {response.status_code}")
        print("Check the logs above - sensitive data should be masked with '***'")
    except Exception as e:
        print(f"Request failed: {e}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("HTTP Client Logging Integration Demo")
    print("=" * 60)
    
    try:
        demo_basic_logging()
        demo_error_logging()
        demo_sensitive_data_masking()
        
        print("\n" + "=" * 60)
        print("✓ All demos completed successfully!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
