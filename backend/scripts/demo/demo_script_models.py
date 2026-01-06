"""Demo script for Layer 2: Script Models

This script demonstrates the usage of TestScript and ScriptParameter models
with realistic examples showing the four-layer architecture integration.
"""

import sys

sys.path.insert(0, 'src')

from morado.models.script import (
    AssertionType,
    ParameterType,
    ScriptParameter,
    ScriptType,
    TestScript,
)


def demo_script_models():
    """Demonstrate script model usage with realistic examples."""

    print("=" * 70)
    print("Layer 2: Script Models - Demonstration")
    print("=" * 70)

    # Example 1: Main test script with assertions
    print("\n📝 Example 1: Main Test Script with Assertions")
    print("-" * 70)

    login_script = TestScript(
        name="用户登录测试",
        description="测试用户登录功能，验证认证流程",
        api_definition_id=1,  # References Layer 1: ApiDefinition
        script_type=ScriptType.MAIN,
        execution_order=1,

        # Script variables
        variables={
            "username": "test_user",
            "password": "Test@123",
            "remember_me": True
        },

        # Assertions to validate response
        assertions=[
            {
                "type": AssertionType.STATUS_CODE.value,
                "expected": 200,
                "message": "登录应该返回200状态码"
            },
            {
                "type": AssertionType.JSON_PATH.value,
                "path": "$.data.token",
                "assertion": "exists",
                "message": "响应应该包含认证token"
            },
            {
                "type": AssertionType.JSON_PATH.value,
                "path": "$.data.user.username",
                "expected": "${username}",
                "message": "返回的用户名应该匹配"
            },
            {
                "type": AssertionType.RESPONSE_TIME.value,
                "max_time": 2000,
                "message": "响应时间应该小于2秒"
            }
        ],

        # Extract variables from response for next scripts
        extract_variables={
            "auth_token": "$.data.token",
            "user_id": "$.data.user.id",
            "session_id": "$.data.session_id"
        },

        # Output variables to pass to next script
        output_variables=["auth_token", "user_id", "session_id"],

        # Retry configuration
        retry_count=3,
        retry_interval=1.0,

        version="1.0.0",
        tags=["authentication", "login", "critical"]
    )

    print(f"Script Name: {login_script.name}")
    print(f"Type: {login_script.script_type.value}")
    print(f"Assertions: {len(login_script.assertions)}")
    print(f"Output Variables: {', '.join(login_script.output_variables)}")
    print(f"Retry Count: {login_script.retry_count}")

    # Example 2: Setup script with pre-script
    print("\n📝 Example 2: Setup Script with Pre-Script")
    print("-" * 70)

    setup_script = TestScript(
        name="准备测试环境",
        description="创建测试用户和初始化数据",
        api_definition_id=2,
        script_type=ScriptType.SETUP,
        execution_order=1,

        # Pre-script to run before API call
        pre_script="""
# Python code to prepare test data
import random
import string

# Generate random test data
test_user_id = ''.join(random.choices(string.digits, k=8))
test_email = f"test_{test_user_id}@example.com"

# Set variables for API call
context.set_variable('test_user_id', test_user_id)
context.set_variable('test_email', test_email)
print(f"Generated test user: {test_email}")
        """,

        variables={
            "user_role": "tester",
            "is_active": True
        },

        extract_variables={
            "created_user_id": "$.data.id",
            "created_at": "$.data.created_at"
        },

        output_variables=["created_user_id", "test_email"]
    )

    print(f"Script Name: {setup_script.name}")
    print(f"Type: {setup_script.script_type.value}")
    print(f"Has Pre-Script: {setup_script.pre_script is not None}")
    print(f"Output Variables: {', '.join(setup_script.output_variables)}")

    # Example 3: Teardown script with post-script
    print("\n📝 Example 3: Teardown Script with Post-Script")
    print("-" * 70)

    teardown_script = TestScript(
        name="清理测试数据",
        description="删除测试过程中创建的数据",
        api_definition_id=3,
        script_type=ScriptType.TEARDOWN,
        execution_order=99,

        variables={
            "user_id": "${created_user_id}",  # Use variable from setup
            "force_delete": True
        },

        # Post-script to run after API call
        post_script="""
# Python code to verify cleanup
if response.status_code == 200:
    print(f"Successfully deleted user: {context.get_variable('user_id')}")
    context.set_variable('cleanup_success', True)
else:
    print(f"Failed to delete user: {response.text}")
    context.set_variable('cleanup_success', False)
        """,

        assertions=[
            {
                "type": AssertionType.STATUS_CODE.value,
                "expected": 200,
                "message": "删除操作应该成功"
            }
        ]
    )

    print(f"Script Name: {teardown_script.name}")
    print(f"Type: {teardown_script.script_type.value}")
    print(f"Has Post-Script: {teardown_script.post_script is not None}")
    print(f"Execution Order: {teardown_script.execution_order}")

    # Example 4: Script with parameters
    print("\n📝 Example 4: Script Parameters")
    print("-" * 70)

    api_test_script = TestScript(
        name="API性能测试",
        description="测试API的性能和响应时间",
        api_definition_id=4,
        script_type=ScriptType.MAIN,
        debug_mode=True,
        debug_breakpoints=[
            {"line": 15, "condition": "response_time > 1000"},
            {"line": 30, "condition": "error_count > 0"}
        ]
    )

    # Define parameters for the script
    parameters = [
        ScriptParameter(
            script_id=api_test_script.id,
            name="endpoint_url",
            description="API端点URL",
            parameter_type=ParameterType.STRING,
            default_value="https://api.example.com/v1/users",
            is_required=True,
            validation_rules={
                "pattern": "^https?://.*",
                "message": "必须是有效的HTTP(S) URL"
            },
            order=1
        ),
        ScriptParameter(
            script_id=api_test_script.id,
            name="request_count",
            description="请求次数",
            parameter_type=ParameterType.INTEGER,
            default_value="100",
            is_required=False,
            validation_rules={
                "min": 1,
                "max": 1000,
                "message": "请求次数必须在1-1000之间"
            },
            order=2,
            group="Performance"
        ),
        ScriptParameter(
            script_id=api_test_script.id,
            name="concurrent_users",
            description="并发用户数",
            parameter_type=ParameterType.INTEGER,
            default_value="10",
            is_required=False,
            validation_rules={
                "min": 1,
                "max": 100
            },
            order=3,
            group="Performance"
        ),
        ScriptParameter(
            script_id=api_test_script.id,
            name="api_key",
            description="API密钥",
            parameter_type=ParameterType.STRING,
            is_required=True,
            is_sensitive=True,
            order=4,
            group="Authentication"
        ),
        ScriptParameter(
            script_id=api_test_script.id,
            name="test_data",
            description="测试数据（JSON格式）",
            parameter_type=ParameterType.JSON,
            default_value='{"name": "test", "age": 25}',
            is_required=False,
            order=5
        )
    ]

    print(f"Script Name: {api_test_script.name}")
    print(f"Debug Mode: {api_test_script.debug_mode}")
    print(f"Breakpoints: {len(api_test_script.debug_breakpoints)}")
    print(f"\nParameters ({len(parameters)}):")
    for param in parameters:
        sensitive = " [SENSITIVE]" if param.is_sensitive else ""
        required = " *" if param.is_required else ""
        print(f"  {param.order}. {param.name}{required}{sensitive}")
        print(f"     Type: {param.parameter_type.value}")
        if param.group:
            print(f"     Group: {param.group}")
        if param.default_value and not param.is_sensitive:
            print(f"     Default: {param.default_value}")

    # Example 5: Utility script
    print("\n📝 Example 5: Utility Script (Reusable)")
    print("-" * 70)

    utility_script = TestScript(
        name="生成测试报告",
        description="通用的测试报告生成工具",
        api_definition_id=5,
        script_type=ScriptType.UTILITY,

        variables={
            "report_format": "json",
            "include_screenshots": True,
            "include_logs": True
        },

        validators={
            "report_schema": {
                "type": "object",
                "required": ["test_name", "status", "duration"],
                "properties": {
                    "test_name": {"type": "string"},
                    "status": {"type": "string", "enum": ["pass", "fail", "skip"]},
                    "duration": {"type": "number"}
                }
            }
        },

        tags=["utility", "reporting", "reusable"]
    )

    print(f"Script Name: {utility_script.name}")
    print(f"Type: {utility_script.script_type.value}")
    print(f"Has Validators: {utility_script.validators is not None}")
    print(f"Tags: {', '.join(utility_script.tags)}")

    # Example 6: Script with complex assertions
    print("\n📝 Example 6: Complex Assertions and Validators")
    print("-" * 70)

    complex_script = TestScript(
        name="数据验证测试",
        description="验证API返回的数据结构和内容",
        api_definition_id=6,
        script_type=ScriptType.MAIN,

        assertions=[
            {
                "type": AssertionType.STATUS_CODE.value,
                "expected": 200
            },
            {
                "type": AssertionType.JSON_PATH.value,
                "path": "$.data.users[*].email",
                "assertion": "all_match",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
                "message": "所有邮箱格式应该正确"
            },
            {
                "type": AssertionType.JSON_PATH.value,
                "path": "$.data.users",
                "assertion": "count",
                "min": 1,
                "max": 100,
                "message": "用户数量应该在1-100之间"
            },
            {
                "type": AssertionType.CUSTOM.value,
                "script": """
def validate_response(response):
    data = response.json()
    users = data.get('data', {}).get('users', [])

    # Check all users have required fields
    for user in users:
        assert 'id' in user, "User must have id"
        assert 'email' in user, "User must have email"
        assert 'created_at' in user, "User must have created_at"

    return True
                """,
                "message": "自定义验证：所有用户必须包含必需字段"
            }
        ],

        validators={
            "response_schema": {
                "type": "object",
                "required": ["status", "data"],
                "properties": {
                    "status": {"type": "string"},
                    "data": {
                        "type": "object",
                        "required": ["users"],
                        "properties": {
                            "users": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["id", "email", "created_at"]
                                }
                            }
                        }
                    }
                }
            }
        }
    )

    print(f"Script Name: {complex_script.name}")
    print(f"Assertions: {len(complex_script.assertions)}")
    print("Assertion Types:")
    for i, assertion in enumerate(complex_script.assertions, 1):
        print(f"  {i}. {assertion['type']}")
    print(f"Has JSON Schema Validator: {complex_script.validators is not None}")

    # Summary
    print("\n" + "=" * 70)
    print("✓ Script Models Demonstration Complete")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Main, Setup, Teardown, and Utility script types")
    print("  ✓ Pre-script and post-script execution")
    print("  ✓ Variable extraction and output")
    print("  ✓ Multiple assertion types (status code, JSON path, custom)")
    print("  ✓ Script parameters with validation rules")
    print("  ✓ Sensitive parameter handling")
    print("  ✓ Debug mode with breakpoints")
    print("  ✓ Retry and timeout configuration")
    print("  ✓ JSON Schema validators")
    print("  ✓ Parameter grouping and ordering")
    print("=" * 70)


if __name__ == "__main__":
    demo_script_models()
