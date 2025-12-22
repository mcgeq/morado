"""Verification script for middleware components.

This script verifies that all middleware components can be imported
and instantiated correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def verify_cors_middleware():
    """Verify CORS middleware configuration."""
    print("Verifying CORS middleware...")
    
    from morado.core.config import Settings
    from morado.middleware.cors import create_cors_config
    
    # Create test settings
    settings = Settings(
        cors_origins=["http://localhost:3000", "http://localhost:8080"],
        cors_allow_credentials=True,
    )
    
    # Create CORS config
    cors_config = create_cors_config(settings)
    
    # Verify configuration
    assert cors_config.allow_origins == ["http://localhost:3000", "http://localhost:8080"]
    assert cors_config.allow_credentials is True
    assert "GET" in cors_config.allow_methods
    assert "POST" in cors_config.allow_methods
    
    print("✓ CORS middleware verified successfully")


def verify_logging_middleware():
    """Verify logging middleware."""
    print("Verifying logging middleware...")
    
    from morado.middleware.logging import LoggingMiddleware, create_logging_middleware
    
    # Verify middleware class exists
    assert LoggingMiddleware is not None
    
    # Verify factory function
    middleware_def = create_logging_middleware()
    assert middleware_def is not None
    
    print("✓ Logging middleware verified successfully")


def verify_error_handler_middleware():
    """Verify error handler middleware."""
    print("Verifying error handler middleware...")
    
    from morado.middleware.error_handler import (
        ErrorDetail,
        ErrorResponse,
        create_error_response,
        create_exception_handlers,
    )
    
    # Test error response creation
    error_response = create_error_response(
        code="TEST_ERROR",
        message="Test error message",
        details={"key": "value"},
        request_id="test-123",
        path="/test/path",
    )
    
    assert error_response.error.code == "TEST_ERROR"
    assert error_response.error.message == "Test error message"
    assert error_response.error.details == {"key": "value"}
    assert error_response.error.request_id == "test-123"
    assert error_response.error.path == "/test/path"
    
    # Verify exception handlers
    handlers = create_exception_handlers()
    assert handlers is not None
    assert len(handlers) > 0
    
    print("✓ Error handler middleware verified successfully")


def verify_middleware_exports():
    """Verify middleware package exports."""
    print("Verifying middleware package exports...")
    
    from morado.middleware import (
        LoggingMiddleware,
        create_cors_config,
        create_exception_handlers,
    )
    
    assert LoggingMiddleware is not None
    assert create_cors_config is not None
    assert create_exception_handlers is not None
    
    print("✓ Middleware package exports verified successfully")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Middleware Verification Script")
    print("=" * 60)
    print()
    
    try:
        verify_cors_middleware()
        verify_logging_middleware()
        verify_error_handler_middleware()
        verify_middleware_exports()
        
        print()
        print("=" * 60)
        print("All middleware components verified successfully! ✓")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"Verification failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
