"""Verification script for API Component models.

This script verifies that the Layer 1 API component models (Header, Body, ApiDefinition)
are correctly defined and can be instantiated.
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


def verify_header_model():
    """Verify Header model can be instantiated."""
    print("Testing Header model...")

    # Create a Header instance
    header = Header(
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

    assert header.name == "认证Header"
    assert header.scope == HeaderScope.GLOBAL
    assert "Authorization" in header.headers
    print("✓ Header model verified")


def verify_body_model():
    """Verify Body model can be instantiated."""
    print("Testing Body model...")

    # Create a Body instance
    body = Body(
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
        scope=HeaderScope.GLOBAL,
        is_active=True,
        version="1.0.0"
    )

    assert body.name == "用户信息Body"
    assert body.body_type == BodyType.BOTH
    assert body.content_type == "application/json"
    assert "name" in body.body_schema["properties"]
    print("✓ Body model verified")


def verify_api_definition_model():
    """Verify ApiDefinition model can be instantiated."""
    print("Testing ApiDefinition model...")

    # Test Method 1: Reference Header and Body
    api_def1 = ApiDefinition(
        uuid=generate_uuid(),
        name="获取用户信息",
        description="通过ID获取用户详细信息",
        method=HttpMethod.GET,
        path="/api/users/{id}",
        base_url="https://api.example.com",
        path_parameters={"id": {"type": "integer", "description": "用户ID"}},
        timeout=30,
        is_active=True,
        version="1.0.0"
    )

    assert api_def1.name == "获取用户信息"
    assert api_def1.method == HttpMethod.GET
    assert api_def1.path == "/api/users/{id}"
    print("✓ ApiDefinition model (Method 1: Reference) verified")

    # Test Method 2: Reference Header + Inline Body
    api_def2 = ApiDefinition(
        uuid=generate_uuid(),
        name="创建用户",
        description="创建新用户",
        method=HttpMethod.POST,
        path="/api/users",
        base_url="https://api.example.com",
        inline_request_body={
            "name": "李四",
            "age": 30,
            "email": "lisi@example.com"
        },
        timeout=30,
        is_active=True,
        version="1.0.0"
    )

    assert api_def2.name == "创建用户"
    assert api_def2.method == HttpMethod.POST
    assert api_def2.inline_request_body is not None
    assert api_def2.inline_request_body["name"] == "李四"
    print("✓ ApiDefinition model (Method 2: Inline) verified")


def verify_enums():
    """Verify all enums are correctly defined."""
    print("Testing Enums...")

    # Test HeaderScope
    assert HeaderScope.GLOBAL == "global"
    assert HeaderScope.PROJECT == "project"
    assert HeaderScope.PRIVATE == "private"
    print("✓ HeaderScope enum verified")

    # Test BodyType
    assert BodyType.REQUEST == "request"
    assert BodyType.RESPONSE == "response"
    assert BodyType.BOTH == "both"
    print("✓ BodyType enum verified")

    # Test HttpMethod
    assert HttpMethod.GET == "GET"
    assert HttpMethod.POST == "POST"
    assert HttpMethod.PUT == "PUT"
    assert HttpMethod.PATCH == "PATCH"
    assert HttpMethod.DELETE == "DELETE"
    print("✓ HttpMethod enum verified")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Verifying API Component Models (Layer 1)")
    print("=" * 60)

    try:
        verify_enums()
        print()
        verify_header_model()
        print()
        verify_body_model()
        print()
        verify_api_definition_model()
        print()
        print("=" * 60)
        print("✓ All API Component models verified successfully!")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
