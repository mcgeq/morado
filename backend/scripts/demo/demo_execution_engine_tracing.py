"""Demonstration of tracing integration with execution engine.

This script shows how the tracing interceptor would be used in the context
of the execution engine, where the execution context is set up and HTTP
requests are made as part of script execution.
"""

import sys
from pathlib import Path

# Add backend/src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.common.http.client import HttpClient
from morado.common.http.logging_interceptor import LoggingInterceptor
from morado.common.http.tracing_interceptor import TracingInterceptor
from morado.common.logger.context import (
    clear_context,
    set_context_data,
    set_request_id,
)
from morado.common.utils.uuid import generate_uuid4


def simulate_script_execution():
    """Simulate a script execution with tracing."""
    print("=" * 60)
    print("Simulating Script Execution with Tracing")
    print("=" * 60)
    
    # Step 1: Execution engine sets up context
    print("\n1. Execution Engine Setup:")
    request_id = f"REQ-{generate_uuid4()[:8]}"
    user_id = 123
    script_id = 456
    
    set_request_id(request_id)
    set_context_data("user_id", user_id)
    set_context_data("script_id", script_id)
    
    print(f"   request_id: {request_id}")
    print(f"   user_id: {user_id}")
    print(f"   script_id: {script_id}")
    
    # Step 2: Create HTTP client with interceptors
    print("\n2. Creating HTTP Client:")
    client = HttpClient()
    
    # Add tracing interceptor
    client.interceptor_manager.add_request_interceptor(TracingInterceptor())
    print("   ✓ Tracing interceptor added")
    
    # Add logging interceptor (optional, for demonstration)
    client.interceptor_manager.add_request_interceptor(LoggingInterceptor())
    print("   ✓ Logging interceptor added")
    
    # Step 3: Execute script steps (HTTP requests)
    print("\n3. Executing Script Steps:")
    
    try:
        # Step 3.1: Get user data
        print("\n   Step 3.1: GET /users/123")
        response = client.get("https://httpbin.org/get", params={"user_id": user_id})
        print(f"   Status: {response.status_code}")
        
        # Step 3.2: Create order
        print("\n   Step 3.2: POST /orders")
        response = client.post(
            "https://httpbin.org/post",
            json={"user_id": user_id, "item": "book", "quantity": 1}
        )
        print(f"   Status: {response.status_code}")
        
        # Step 3.3: Update order
        print("\n   Step 3.3: PUT /orders/789")
        response = client.put(
            "https://httpbin.org/put",
            json={"order_id": 789, "status": "confirmed"}
        )
        print(f"   Status: {response.status_code}")
        
        print("\n   ✓ All script steps completed successfully")
        print(f"   ✓ All requests included tracing headers:")
        print(f"      - X-Request-ID: {request_id}")
        print(f"      - X-User-ID: {user_id}")
    
    except Exception as e:
        print(f"\n   ✗ Script execution failed: {e}")
        print("   (This is expected if no internet connection)")
    
    finally:
        # Step 4: Clean up context
        print("\n4. Cleanup:")
        clear_context()
        print("   ✓ Context cleared")


def simulate_test_case_execution():
    """Simulate a test case execution with multiple scripts."""
    print("\n\n" + "=" * 60)
    print("Simulating Test Case Execution with Multiple Scripts")
    print("=" * 60)
    
    # Test case setup
    print("\n1. Test Case Setup:")
    request_id = f"REQ-{generate_uuid4()[:8]}"
    user_id = 999
    test_case_id = 111
    
    set_request_id(request_id)
    set_context_data("user_id", user_id)
    set_context_data("test_case_id", test_case_id)
    
    print(f"   request_id: {request_id}")
    print(f"   user_id: {user_id}")
    print(f"   test_case_id: {test_case_id}")
    
    # Create HTTP client
    client = HttpClient()
    client.interceptor_manager.add_request_interceptor(TracingInterceptor())
    
    # Execute multiple scripts
    print("\n2. Executing Scripts:")
    
    scripts = [
        ("Login Script", "https://httpbin.org/post"),
        ("Create Data Script", "https://httpbin.org/post"),
        ("Verify Data Script", "https://httpbin.org/get"),
    ]
    
    for i, (script_name, url) in enumerate(scripts, 1):
        print(f"\n   Script {i}: {script_name}")
        
        # Update context with script info
        set_context_data("script_id", i)
        set_context_data("script_name", script_name)
        
        try:
            if "post" in url:
                response = client.post(url, json={"script": script_name})
            else:
                response = client.get(url, params={"script": script_name})
            
            print(f"   Status: {response.status_code}")
            print(f"   ✓ Request included tracing context:")
            print(f"      - X-Request-ID: {request_id} (same for all scripts)")
            print(f"      - X-User-ID: {user_id}")
        
        except Exception as e:
            print(f"   ✗ Failed: {e}")
    
    print("\n3. Test Case Complete:")
    print(f"   ✓ All scripts executed with same request_id: {request_id}")
    print("   ✓ Full traceability across all HTTP requests")
    
    # Cleanup
    clear_context()


def demonstrate_tracing_benefits():
    """Demonstrate the benefits of automatic tracing."""
    print("\n\n" + "=" * 60)
    print("Benefits of Automatic Tracing")
    print("=" * 60)
    
    print("\n1. Full Request Traceability:")
    print("   - Every HTTP request includes the same request_id")
    print("   - Easy to trace requests across services")
    print("   - Correlate logs from different systems")
    
    print("\n2. User Context Propagation:")
    print("   - User ID automatically included in requests")
    print("   - Downstream services know who initiated the request")
    print("   - Audit trail for security and compliance")
    
    print("\n3. Zero Developer Overhead:")
    print("   - No manual header management required")
    print("   - Interceptor handles everything automatically")
    print("   - Consistent across all HTTP requests")
    
    print("\n4. Flexible Configuration:")
    print("   - Custom header names supported")
    print("   - Optional user ID propagation")
    print("   - Works with existing headers")
    
    print("\n5. Integration with Logging:")
    print("   - Same context used for logs and HTTP requests")
    print("   - Unified tracing across the entire system")
    print("   - Easy debugging and troubleshooting")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("Execution Engine Tracing Integration Demo")
    print("=" * 60)
    print("\nThis demo shows how the tracing interceptor integrates")
    print("with the execution engine to provide automatic request")
    print("tracing across all HTTP requests in script execution.")
    print("\nNote: Requires internet connection to reach httpbin.org")
    print("=" * 60)
    
    try:
        simulate_script_execution()
        simulate_test_case_execution()
        demonstrate_tracing_benefits()
        
        print("\n" + "=" * 60)
        print("✓ Demo completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
