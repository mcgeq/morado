"""Verification script for dashboard endpoints.

This script verifies that the dashboard API endpoints are properly
registered and accessible.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.app import create_app


def verify_dashboard_endpoints():
    """Verify dashboard endpoints are registered."""
    print("Creating Litestar application...")
    app = create_app()

    print("\nVerifying dashboard endpoints...")

    # Get all routes
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append(route.path)

    # Check for dashboard endpoints
    expected_endpoints = [
        "/dashboard/user-metrics",
        "/dashboard/step-statistics",
        "/dashboard/api-usage",
        "/dashboard/trends",
    ]

    print("\nExpected dashboard endpoints:")
    all_found = True
    for endpoint in expected_endpoints:
        found = any(endpoint in route for route in routes)
        status = "✓" if found else "✗"
        print(f"  {status} {endpoint}")
        if not found:
            all_found = False

    if all_found:
        print("\n✓ All dashboard endpoints are registered successfully!")
        return True
    else:
        print("\n✗ Some dashboard endpoints are missing!")
        return False


if __name__ == "__main__":
    try:
        success = verify_dashboard_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error verifying dashboard endpoints: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
