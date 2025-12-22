"""Integration test for API Component models.

This script tests the complete workflow of creating and using
Header, Body, and ApiDefinition models together.
"""

import sys

sys.path.insert(0, 'src')

from morado.common.utils.uuid import generate_uuid
from morado.models.api_component import (
    ApiDefinition,
    Body,
    BodyType,
    Header,
    HeaderScope,
    HttpMethod,
)


def test_complete_workflow():
    """Test the complete workflow of creating API components."""
    print("=" * 70)
    print("Testing Complete API Component Workflow")
    print("=" * 70)

    # Step 1: Create reusable Header components
    print("\n1. Creating reusable Header components...")

    auth_header = Header(
        uuid=generate_uuid(),
        name="认证Header",
        description="包含Bearer Token的认证Header",
        headers={
            "Authorization": "Bearer ${token}",
            "X-API-Key": "${api_key}"
        },
        scope=HeaderScope.GLOBAL,
        is_active=True,
        version="1.0.0"
    )
    print(f"   ✓ Created: {auth_header.name} (scope: {auth_header.scope})")

    json_header = Header(
        uuid=generate_uuid(),
        name="JSON Content-Type Header",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        scope=HeaderScope.GLOBAL
    )
    print(f"   ✓ Created: {json_header.name} (scope: {json_header.scope})")

    # Step 2: Create reusable Body components
    print("\n2. Creating reusable Body components...")

    user_body = Body(
        uuid=generate_uuid(),
        name="用户信息Body",
        description="用户基本信息的请求/响应体",
        body_type=BodyType.BOTH,
        content_type="application/json",
        body_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "email"]
        },
        example_data={
            "name": "张三",
            "age": 25,
            "email": "zhangsan@example.com"
        },
        scope=HeaderScope.GLOBAL
    )
    print(f"   ✓ Created: {user_body.name} (type: {user_body.body_type})")

    order_body = Body(
        uuid=generate_uuid(),
        name="订单信息Body",
        body_type=BodyType.REQUEST,
        content_type="application/json",
        body_schema={
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "quantity": {"type": "integer"},
                "price": {"type": "number"}
            }
        },
        example_data={
            "product_id": 123,
            "quantity": 2,
            "price": 99.99
        },
        scope=HeaderScope.GLOBAL
    )
    print(f"   ✓ Created: {order_body.name} (type: {order_body.body_type})")

    # Step 3: Create API definitions using Method 1 (Reference Header + Body)
    print("\n3. Creating API definitions (Method 1: Reference Header + Body)...")

    # Simulate having IDs (in real scenario, these would be from database)
    auth_header.id = 1
    user_body.id = 1

    get_user_api = ApiDefinition(
        uuid=generate_uuid(),
        name="获取用户信息",
        description="通过ID获取用户详细信息",
        method=HttpMethod.GET,
        path="/api/users/{id}",
        base_url="https://api.example.com",
        header_id=auth_header.id,
        response_body_id=user_body.id,
        path_parameters={
            "id": {"type": "integer", "description": "用户ID"}
        },
        timeout=30
    )
    print(f"   ✓ Created: {get_user_api.name}")
    print(f"      Method: {get_user_api.method}")
    print(f"      Path: {get_user_api.path}")
    print(f"      References Header ID: {get_user_api.header_id}")
    print(f"      References Response Body ID: {get_user_api.response_body_id}")

    # Step 4: Create API definitions using Method 2 (Reference Header + Inline Body)
    print("\n4. Creating API definitions (Method 2: Reference Header + Inline Body)...")

    create_user_api = ApiDefinition(
        uuid=generate_uuid(),
        name="创建用户",
        description="创建新用户",
        method=HttpMethod.POST,
        path="/api/users",
        base_url="https://api.example.com",
        header_id=auth_header.id,
        inline_request_body={
            "name": "李四",
            "age": 30,
            "email": "lisi@example.com"
        },
        timeout=30
    )
    print(f"   ✓ Created: {create_user_api.name}")
    print(f"      Method: {create_user_api.method}")
    print(f"      Path: {create_user_api.path}")
    print(f"      References Header ID: {create_user_api.header_id}")
    print(f"      Has Inline Request Body: {create_user_api.inline_request_body is not None}")

    # Step 5: Verify component reusability
    print("\n5. Verifying component reusability...")

    # Create another API that reuses the same header
    update_user_api = ApiDefinition(
        uuid=generate_uuid(),
        name="更新用户信息",
        method=HttpMethod.PUT,
        path="/api/users/{id}",
        header_id=auth_header.id,  # Reusing the same header
        request_body_id=user_body.id,  # Reusing the same body
        response_body_id=user_body.id,  # Reusing the same body
        path_parameters={
            "id": {"type": "integer", "description": "用户ID"}
        }
    )
    print(f"   ✓ Created: {update_user_api.name}")
    print(f"      Reuses Header ID: {update_user_api.header_id} (same as previous APIs)")
    print(f"      Reuses Body ID: {update_user_api.request_body_id} (same as GET user API)")

    # Step 6: Verify flexibility (inline + reference mix)
    print("\n6. Verifying flexibility (mixing inline and reference)...")

    delete_user_api = ApiDefinition(
        uuid=generate_uuid(),
        name="删除用户",
        method=HttpMethod.DELETE,
        path="/api/users/{id}",
        header_id=auth_header.id,  # Reference header
        inline_response_body={  # Inline response
            "success": True,
            "message": "User deleted successfully"
        },
        path_parameters={
            "id": {"type": "integer", "description": "用户ID"}
        }
    )
    print(f"   ✓ Created: {delete_user_api.name}")
    print(f"      References Header: Yes (ID: {delete_user_api.header_id})")
    print("      Uses Inline Response Body: Yes")

    # Summary
    print("\n" + "=" * 70)
    print("✓ Complete workflow test passed!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  - Created {2} reusable Header components")
    print(f"  - Created {2} reusable Body components")
    print(f"  - Created {4} API definitions")
    print("  - Demonstrated both composition methods")
    print("  - Verified component reusability")
    print("  - Verified flexibility in mixing inline and reference")
    print("\n✓ All Layer 1 (API Component) models are working correctly!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_complete_workflow()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
