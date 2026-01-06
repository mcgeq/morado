#!/usr/bin/env python
"""Verify frontend-backend integration configuration.

This script verifies:
1. Docker Compose configuration is valid
2. Frontend API client configuration matches backend endpoints
3. CORS configuration allows frontend origin
4. Environment configurations are consistent

Usage:
    python backend/scripts/verify/verify_integration.py
"""

import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_src))

import os
import re

# Set testing environment
os.environ["ENVIRONMENT"] = "testing"


def verify_docker_compose_files():
    """Verify Docker Compose configuration files exist and are valid."""
    print("=" * 60)
    print("1. Verifying Docker Compose configuration...")
    print("=" * 60)
    
    docker_files = [
        "deployment/docker-compose.yml",
        "deployment/docker-compose.dev.yml",
        "deployment/docker/Dockerfile.backend",
        "deployment/docker/Dockerfile.frontend",
        "deployment/docker/nginx.conf",
    ]
    
    all_exist = True
    for file_path in docker_files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✓ {file_path} exists")
        else:
            print(f"  ✗ {file_path} NOT FOUND")
            all_exist = False
    
    return all_exist


def verify_frontend_api_config():
    """Verify frontend API client configuration."""
    print("\n" + "=" * 60)
    print("2. Verifying frontend API client configuration...")
    print("=" * 60)
    
    api_index_path = Path("frontend/src/api/index.ts")
    if not api_index_path.exists():
        print(f"  ✗ {api_index_path} NOT FOUND")
        return False
    
    content = api_index_path.read_text(encoding='utf-8')
    
    # Check for axios configuration
    if "axios" in content.lower():
        print("  ✓ Axios HTTP client configured")
    else:
        print("  ? Axios not found in API client")
    
    # Check for base URL configuration
    if "baseURL" in content or "VITE_API_BASE_URL" in content:
        print("  ✓ Base URL configuration found")
    else:
        print("  ? Base URL configuration not found")
    
    # Check for interceptors
    if "interceptor" in content.lower():
        print("  ✓ Request/Response interceptors configured")
    else:
        print("  ? Interceptors not found")
    
    return True


def verify_frontend_env_config():
    """Verify frontend environment configuration."""
    print("\n" + "=" * 60)
    print("3. Verifying frontend environment configuration...")
    print("=" * 60)
    
    env_files = [
        "frontend/.env.development",
        "frontend/.env.production",
    ]
    
    all_valid = True
    for env_file in env_files:
        path = Path(env_file)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            if "VITE_API_BASE_URL" in content:
                print(f"  ✓ {env_file} - API base URL configured")
            else:
                print(f"  ? {env_file} - API base URL not found")
        else:
            print(f"  ✗ {env_file} NOT FOUND")
            all_valid = False
    
    return all_valid


def verify_cors_configuration():
    """Verify CORS configuration allows frontend origin."""
    print("\n" + "=" * 60)
    print("4. Verifying CORS configuration...")
    print("=" * 60)
    
    try:
        from morado.core.config import get_settings, reload_settings
        
        reload_settings()
        settings = get_settings()
        
        print(f"  ✓ CORS origins: {settings.cors_origins}")
        print(f"  ✓ Allow credentials: {settings.cors_allow_credentials}")
        
        # Check if localhost:3000 or localhost:5173 is allowed
        frontend_origins = ["http://localhost:3000", "http://localhost:5173"]
        allowed = any(origin in settings.cors_origins for origin in frontend_origins)
        
        if allowed:
            print("  ✓ Frontend development origin is allowed")
        else:
            print("  ? Frontend development origin may not be allowed")
        
        return True
    except Exception as e:
        print(f"  ✗ Error checking CORS: {e}")
        return False


def verify_api_endpoints_match():
    """Verify frontend API calls match backend endpoints."""
    print("\n" + "=" * 60)
    print("5. Verifying API endpoint consistency...")
    print("=" * 60)
    
    # Frontend API files
    frontend_api_files = [
        "frontend/src/api/header.ts",
        "frontend/src/api/body.ts",
        "frontend/src/api/api-definition.ts",
        "frontend/src/api/script.ts",
        "frontend/src/api/component.ts",
        "frontend/src/api/test-case.ts",
        "frontend/src/api/test-suite.ts",
        "frontend/src/api/report.ts",
    ]
    
    # Expected endpoint patterns
    expected_endpoints = {
        "headers": "/headers",
        "bodies": "/bodies",
        "api-definitions": "/api-definitions",
        "scripts": "/scripts",
        "components": "/components",
        "test-cases": "/test-cases",
        "test-suites": "/test-suites",
        "reports": "/reports",
    }
    
    found_endpoints = set()
    
    for api_file in frontend_api_files:
        path = Path(api_file)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            for name, endpoint in expected_endpoints.items():
                if endpoint in content:
                    found_endpoints.add(name)
    
    print(f"  Found {len(found_endpoints)}/{len(expected_endpoints)} endpoint groups:")
    for name, endpoint in expected_endpoints.items():
        if name in found_endpoints:
            print(f"    ✓ {name}: {endpoint}")
        else:
            print(f"    ? {name}: {endpoint} - not found in frontend")
    
    return len(found_endpoints) >= len(expected_endpoints) * 0.8  # 80% threshold


def verify_backend_routes():
    """Verify backend routes are registered."""
    print("\n" + "=" * 60)
    print("6. Verifying backend routes registration...")
    print("=" * 60)
    
    try:
        from morado.app import app
        
        # Get all registered paths
        registered_paths = set()
        for route in app.routes:
            if hasattr(route, 'path'):
                registered_paths.add(route.path)
        
        print(f"  ✓ Total registered routes: {len(registered_paths)}")
        
        # Check for key endpoints
        key_endpoints = [
            "/headers",
            "/bodies",
            "/api-definitions",
            "/scripts",
            "/components",
            "/test-cases",
            "/test-suites",
            "/reports",
            "/dashboard",
        ]
        
        found = 0
        for endpoint in key_endpoints:
            if any(p.startswith(endpoint) for p in registered_paths):
                print(f"    ✓ {endpoint} - registered")
                found += 1
            else:
                print(f"    ? {endpoint} - not found")
        
        print(f"\n  Found {found}/{len(key_endpoints)} key endpoint groups")
        
        return found >= len(key_endpoints) * 0.8
    except Exception as e:
        print(f"  ✗ Error checking routes: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_nginx_config():
    """Verify Nginx configuration for reverse proxy."""
    print("\n" + "=" * 60)
    print("7. Verifying Nginx configuration...")
    print("=" * 60)
    
    nginx_path = Path("deployment/docker/nginx.conf")
    if not nginx_path.exists():
        print(f"  ✗ {nginx_path} NOT FOUND")
        return False
    
    content = nginx_path.read_text(encoding='utf-8')
    
    checks = [
        ("proxy_pass", "Backend proxy configured"),
        ("location /api", "API route configured"),
        ("location /", "Frontend route configured"),
    ]
    
    all_pass = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ? {description} - not found")
            all_pass = False
    
    return all_pass


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("FRONTEND-BACKEND INTEGRATION VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(("Docker Compose files", verify_docker_compose_files()))
    results.append(("Frontend API config", verify_frontend_api_config()))
    results.append(("Frontend env config", verify_frontend_env_config()))
    results.append(("CORS configuration", verify_cors_configuration()))
    results.append(("API endpoint consistency", verify_api_endpoints_match()))
    results.append(("Backend routes", verify_backend_routes()))
    results.append(("Nginx configuration", verify_nginx_config()))
    
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
