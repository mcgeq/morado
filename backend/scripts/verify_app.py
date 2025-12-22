"""Verification script for the Litestar application.

This script verifies that the Litestar application can be imported
and initialized correctly with all routes and middleware.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from morado.app import app
from morado.core.config import get_settings


def verify_application():
    """Verify the Litestar application configuration."""
    print("=" * 60)
    print("Morado Application Verification")
    print("=" * 60)

    # Get settings
    settings = get_settings()
    print(f"\n✓ Settings loaded successfully")
    print(f"  - Environment: {settings.environment}")
    print(f"  - Debug mode: {settings.debug}")
    print(f"  - App name: {settings.app_name}")
    print(f"  - Version: {settings.version}")

    # Verify application
    print(f"\n✓ Application created successfully")
    print(f"  - Type: {type(app).__name__}")
    print(f"  - Debug: {app.debug}")

    # Count routes
    print(f"\n✓ Routes registered: {len(app.routes)}")

    # List route handlers
    route_handlers = []
    for route in app.routes:
        if hasattr(route, "route_handler"):
            handler_name = route.route_handler.__class__.__name__
            if handler_name not in route_handlers:
                route_handlers.append(handler_name)

    print(f"\n✓ Route handlers ({len(route_handlers)}):")
    for handler in sorted(route_handlers):
        print(f"  - {handler}")

    # Verify middleware
    print(f"\n✓ Middleware configured: {len(app.middleware)}")

    # Verify CORS
    if app.cors_config:
        print(f"\n✓ CORS configured")
        print(f"  - Allowed origins: {app.cors_config.allow_origins}")

    # Verify exception handlers
    print(f"\n✓ Exception handlers: {len(app.exception_handlers)}")

    # Verify OpenAPI
    if app.openapi_config:
        print(f"\n✓ OpenAPI documentation configured")
        print(f"  - Title: {app.openapi_config.title}")
        print(f"  - Version: {app.openapi_config.version}")
        print(f"  - Path: {app.openapi_config.path}")

    print("\n" + "=" * 60)
    print("✓ All verifications passed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        verify_application()
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
