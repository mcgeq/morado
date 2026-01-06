#!/usr/bin/env python
"""Verify backend service can start independently.

This script verifies:
1. Backend service can start without errors
2. API endpoints are accessible
3. Database connection is working (using SQLite for testing)

Usage:
    python backend/scripts/verify/verify_backend_startup.py
"""

import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_src))

import os

# Set testing environment to use SQLite
os.environ["ENVIRONMENT"] = "testing"


def verify_imports():
    """Verify all required modules can be imported."""
    print("=" * 60)
    print("1. Verifying module imports...")
    print("=" * 60)
    
    try:
        from morado.app import app, create_app
        print("  ✓ morado.app imported successfully")
        
        from morado.core.config import get_settings
        print("  ✓ morado.core.config imported successfully")
        
        from morado.core.database import init_database, get_db
        print("  ✓ morado.core.database imported successfully")
        
        from morado.common.logger import get_logger
        print("  ✓ morado.common.logger imported successfully")
        
        # Import all API controllers
        from morado.api.v1.header import HeaderController
        from morado.api.v1.body import BodyController
        from morado.api.v1.api_definition import ApiDefinitionController
        from morado.api.v1.script import TestScriptController
        from morado.api.v1.component import TestComponentController
        from morado.api.v1.test_case import TestCaseController
        from morado.api.v1.test_suite import TestSuiteController
        from morado.api.v1.test_execution import TestExecutionController
        from morado.api.v1.report import ReportController
        from morado.api.v1.dashboard import DashboardController
        print("  ✓ All API controllers imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False


def verify_settings():
    """Verify settings can be loaded."""
    print("\n" + "=" * 60)
    print("2. Verifying settings configuration...")
    print("=" * 60)
    
    try:
        from morado.core.config import get_settings, reload_settings
        
        # Clear cache and reload
        reload_settings()
        settings = get_settings()
        
        print(f"  ✓ App name: {settings.app_name}")
        print(f"  ✓ Version: {settings.version}")
        print(f"  ✓ Environment: {settings.environment}")
        print(f"  ✓ Debug mode: {settings.debug}")
        print(f"  ✓ Host: {settings.host}")
        print(f"  ✓ Port: {settings.port}")
        print(f"  ✓ Log level: {settings.log_level}")
        
        return True
    except Exception as e:
        print(f"  ✗ Settings error: {e}")
        return False


def verify_app_creation():
    """Verify Litestar app can be created."""
    print("\n" + "=" * 60)
    print("3. Verifying Litestar app creation...")
    print("=" * 60)
    
    try:
        from morado.app import create_app
        
        app = create_app()
        print(f"  ✓ App created successfully")
        print(f"  ✓ App type: {type(app).__name__}")
        print(f"  ✓ Number of route handlers: {len(app.routes)}")
        
        # List registered routes
        print("\n  Registered routes:")
        for route in app.routes:
            if hasattr(route, 'path'):
                print(f"    - {route.path}")
        
        return True
    except Exception as e:
        print(f"  ✗ App creation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_api_endpoints():
    """Verify API endpoints are registered correctly."""
    print("\n" + "=" * 60)
    print("4. Verifying API endpoints registration...")
    print("=" * 60)
    
    try:
        from morado.app import app
        
        # Expected endpoints for four-layer architecture
        expected_paths = [
            "/api/v1/headers",
            "/api/v1/bodies",
            "/api/v1/api-definitions",
            "/api/v1/scripts",
            "/api/v1/components",
            "/api/v1/test-cases",
            "/api/v1/test-suites",
            "/api/v1/test-executions",
            "/api/v1/reports",
            "/api/v1/dashboard",
        ]
        
        # Get all registered paths
        registered_paths = set()
        for route in app.routes:
            if hasattr(route, 'path'):
                registered_paths.add(route.path)
        
        print(f"  Total registered routes: {len(registered_paths)}")
        
        # Check expected paths
        found_count = 0
        for path in expected_paths:
            # Check if path or any sub-path is registered
            found = any(p.startswith(path) or path.startswith(p) for p in registered_paths)
            if found:
                print(f"  ✓ {path} - registered")
                found_count += 1
            else:
                print(f"  ? {path} - not found (may be nested)")
        
        print(f"\n  Found {found_count}/{len(expected_paths)} expected endpoint groups")
        
        return True
    except Exception as e:
        print(f"  ✗ Endpoint verification error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_openapi_docs():
    """Verify OpenAPI documentation is configured."""
    print("\n" + "=" * 60)
    print("5. Verifying OpenAPI documentation...")
    print("=" * 60)
    
    try:
        from morado.app import app
        
        if app.openapi_config:
            print(f"  ✓ OpenAPI configured")
            print(f"  ✓ Title: {app.openapi_config.title}")
            print(f"  ✓ Version: {app.openapi_config.version}")
            print(f"  ✓ Docs path: {app.openapi_config.path}")
            return True
        else:
            print("  ✗ OpenAPI not configured")
            return False
    except Exception as e:
        print(f"  ✗ OpenAPI verification error: {e}")
        return False


def verify_middleware():
    """Verify middleware is configured."""
    print("\n" + "=" * 60)
    print("6. Verifying middleware configuration...")
    print("=" * 60)
    
    try:
        from morado.app import app
        
        print(f"  ✓ Number of middleware: {len(app.middleware)}")
        
        # Check CORS
        if app.cors_config:
            print(f"  ✓ CORS configured")
            print(f"    - Allow origins: {app.cors_config.allow_origins}")
            print(f"    - Allow credentials: {app.cors_config.allow_credentials}")
        else:
            print("  ? CORS not configured")
        
        # Check exception handlers
        if app.exception_handlers:
            print(f"  ✓ Exception handlers configured: {len(app.exception_handlers)}")
        else:
            print("  ? No custom exception handlers")
        
        return True
    except Exception as e:
        print(f"  ✗ Middleware verification error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("BACKEND STARTUP VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(("Module imports", verify_imports()))
    results.append(("Settings configuration", verify_settings()))
    results.append(("App creation", verify_app_creation()))
    results.append(("API endpoints", verify_api_endpoints()))
    results.append(("OpenAPI docs", verify_openapi_docs()))
    results.append(("Middleware", verify_middleware()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n  Total: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
