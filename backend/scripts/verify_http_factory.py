"""Verification script for HTTP client factory functions.

This script tests the factory functions and public API of the HTTP client wrapper.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all public API imports work."""
    print("Testing imports...")
    
    try:
        from morado.common.http import (
            # Factory functions
            create_http_client,
            create_default_client,
            load_config_from_dict,
            load_config_from_toml,
            # Configuration
            HttpClientConfig,
            # Core Client
            HttpClient,
            # Exceptions
            HttpClientError,
            HttpConnectionError,
            HttpRequestError,
            HttpTimeoutError,
            RetryExhaustedError,
            JSONPathError,
            VariableResolutionError,
            # Response
            HttpResponse,
            # Session
            SessionManager,
            # Retry
            RetryConfig,
            RetryStrategy,
            RetryHandler,
            # Interceptor
            RequestInterceptor,
            ResponseInterceptor,
            InterceptorManager,
            LoggingInterceptor,
            ErrorLoggingInterceptor,
            TracingInterceptor,
            # Utils
            resolve_variables,
            build_url,
            encode_query_params,
            serialize_body,
            mask_sensitive_data,
            mask_sensitive_headers,
            truncate_for_logging,
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_create_default_client():
    """Test create_default_client factory function."""
    print("\nTesting create_default_client...")
    
    try:
        from morado.common.http import create_default_client
        
        # Create default client
        client = create_default_client()
        assert client is not None
        assert hasattr(client, 'get')
        assert hasattr(client, 'post')
        assert hasattr(client, 'interceptor_manager')
        
        # Create with base URL
        client = create_default_client(base_url="https://api.example.com")
        assert client._base_url == "https://api.example.com"
        
        # Create without logging
        client = create_default_client(enable_logging=False)
        assert client is not None
        
        # Create without retry
        client = create_default_client(enable_retry=False)
        assert client._retry_handler is None
        
        print("✓ create_default_client works correctly")
        return True
    except Exception as e:
        print(f"✗ create_default_client failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_http_client():
    """Test create_http_client factory function."""
    print("\nTesting create_http_client...")
    
    try:
        from morado.common.http import create_http_client, HttpClientConfig
        
        # Create with default config
        client = create_http_client()
        assert client is not None
        
        # Create with custom config
        config = HttpClientConfig(
            base_url="https://api.example.com",
            connect_timeout=15,
            read_timeout=60,
            max_retries=5,
            retry_strategy="exponential"
        )
        client = create_http_client(config)
        assert client._base_url == "https://api.example.com"
        assert client._default_timeout == (15, 60)
        
        # Create without logging
        client = create_http_client(enable_logging=False)
        assert client is not None
        
        # Create without tracing
        client = create_http_client(enable_tracing=False)
        assert client is not None
        
        print("✓ create_http_client works correctly")
        return True
    except Exception as e:
        print(f"✗ create_http_client failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_config_from_dict():
    """Test load_config_from_dict function."""
    print("\nTesting load_config_from_dict...")
    
    try:
        from morado.common.http import load_config_from_dict, create_http_client
        
        # Load from dictionary
        config_dict = {
            "base_url": "https://api.example.com",
            "connect_timeout": 15,
            "read_timeout": 60,
            "max_retries": 5,
            "retry_strategy": "exponential",
            "enable_logging": True,
            "enable_tracing": True
        }
        
        config = load_config_from_dict(config_dict)
        assert config.base_url == "https://api.example.com"
        assert config.connect_timeout == 15
        assert config.read_timeout == 60
        assert config.max_retries == 5
        assert config.retry_strategy == "exponential"
        
        # Create client from loaded config
        client = create_http_client(config)
        assert client is not None
        
        print("✓ load_config_from_dict works correctly")
        return True
    except Exception as e:
        print(f"✗ load_config_from_dict failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_http_client_config():
    """Test HttpClientConfig validation."""
    print("\nTesting HttpClientConfig...")
    
    try:
        from morado.common.http import HttpClientConfig
        from pydantic import ValidationError
        
        # Valid config
        config = HttpClientConfig(
            base_url="https://api.example.com",
            connect_timeout=10,
            read_timeout=30
        )
        assert config.base_url == "https://api.example.com"
        
        # Test validation - invalid base_url
        try:
            config = HttpClientConfig(base_url="not-a-url")
            print("✗ Should have raised validation error for invalid base_url")
            return False
        except ValidationError:
            pass  # Expected
        
        # Test validation - invalid retry_strategy
        try:
            config = HttpClientConfig(retry_strategy="invalid")
            print("✗ Should have raised validation error for invalid retry_strategy")
            return False
        except ValidationError:
            pass  # Expected
        
        # Test defaults
        config = HttpClientConfig()
        assert config.connect_timeout == 10
        assert config.read_timeout == 30
        assert config.max_retries == 3
        assert config.retry_strategy == "exponential"
        assert config.enable_retry is True
        assert config.enable_logging is True
        assert config.enable_tracing is True
        
        print("✓ HttpClientConfig validation works correctly")
        return True
    except Exception as e:
        print(f"✗ HttpClientConfig test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_manager():
    """Test client as context manager."""
    print("\nTesting context manager...")
    
    try:
        from morado.common.http import create_default_client
        
        # Test context manager
        with create_default_client() as client:
            assert client is not None
            assert hasattr(client, 'get')
        
        # Client should be closed after context
        # (We can't easily verify this without making a request)
        
        print("✓ Context manager works correctly")
        return True
    except Exception as e:
        print(f"✗ Context manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_interceptor_integration():
    """Test that interceptors are properly added."""
    print("\nTesting interceptor integration...")
    
    try:
        from morado.common.http import create_http_client, HttpClientConfig
        
        # Create client with logging and tracing enabled
        config = HttpClientConfig(
            enable_logging=True,
            enable_tracing=True
        )
        client = create_http_client(config, enable_logging=True, enable_tracing=True)
        
        # Check that interceptors were added
        assert client.interceptor_manager.request_interceptor_count > 0
        assert client.interceptor_manager.response_interceptor_count > 0
        
        # Create client without logging
        client = create_http_client(enable_logging=False, enable_tracing=False)
        assert client.interceptor_manager.request_interceptor_count == 0
        assert client.interceptor_manager.response_interceptor_count == 0
        
        print("✓ Interceptor integration works correctly")
        return True
    except Exception as e:
        print(f"✗ Interceptor integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_config_method():
    """Test HttpClient.from_config class method."""
    print("\nTesting HttpClient.from_config...")
    
    try:
        from morado.common.http import HttpClient, HttpClientConfig
        
        config = HttpClientConfig(
            base_url="https://api.example.com",
            connect_timeout=15,
            read_timeout=60,
            enable_retry=True,
            max_retries=5
        )
        
        client = HttpClient.from_config(config)
        assert client is not None
        assert client._base_url == "https://api.example.com"
        assert client._default_timeout == (15, 60)
        assert client._retry_handler is not None
        
        print("✓ HttpClient.from_config works correctly")
        return True
    except Exception as e:
        print(f"✗ HttpClient.from_config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("HTTP Client Factory Functions - Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_create_default_client,
        test_create_http_client,
        test_load_config_from_dict,
        test_http_client_config,
        test_context_manager,
        test_interceptor_integration,
        test_from_config_method,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All verification tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
