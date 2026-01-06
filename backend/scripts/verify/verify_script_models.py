"""Verification script for Layer 2: Script Models

This script verifies that the TestScript and ScriptParameter models
are correctly implemented and can be used with the database.
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


def verify_script_models():
    """Verify that script models are correctly defined."""

    print("=" * 60)
    print("Verifying Layer 2: Script Models")
    print("=" * 60)

    # Test 1: Verify TestScript model attributes
    print("\n1. Verifying TestScript model attributes...")
    script_attrs = [
        'id', 'uuid', 'name', 'description',
        'api_definition_id', 'script_type', 'execution_order',
        'variables', 'assertions', 'validators',
        'pre_script', 'post_script',
        'extract_variables', 'output_variables',
        'debug_mode', 'debug_breakpoints',
        'retry_count', 'retry_interval', 'timeout_override',
        'is_active', 'version', 'tags',
        'created_by', 'created_at', 'updated_at'
    ]

    for attr in script_attrs:
        assert hasattr(TestScript, attr), f"TestScript missing attribute: {attr}"

    print(f"   ✓ All {len(script_attrs)} TestScript attributes present")

    # Test 2: Verify ScriptParameter model attributes
    print("\n2. Verifying ScriptParameter model attributes...")
    param_attrs = [
        'id', 'uuid', 'script_id',
        'name', 'description', 'parameter_type',
        'default_value', 'is_required', 'validation_rules',
        'order', 'group', 'is_sensitive',
        'created_at', 'updated_at'
    ]

    for attr in param_attrs:
        assert hasattr(ScriptParameter, attr), f"ScriptParameter missing attribute: {attr}"

    print(f"   ✓ All {len(param_attrs)} ScriptParameter attributes present")

    # Test 3: Verify Enums
    print("\n3. Verifying Enum types...")

    # ScriptType
    assert ScriptType.SETUP == "setup"
    assert ScriptType.MAIN == "main"
    assert ScriptType.TEARDOWN == "teardown"
    assert ScriptType.UTILITY == "utility"
    print("   ✓ ScriptType enum values correct")

    # AssertionType
    assert AssertionType.EQUALS == "equals"
    assert AssertionType.STATUS_CODE == "status_code"
    assert AssertionType.JSON_PATH == "json_path"
    print("   ✓ AssertionType enum values correct")

    # ParameterType
    assert ParameterType.STRING == "string"
    assert ParameterType.INTEGER == "integer"
    assert ParameterType.JSON == "json"
    print("   ✓ ParameterType enum values correct")

    # Test 4: Verify relationships
    print("\n4. Verifying model relationships...")

    # TestScript relationships
    assert hasattr(TestScript, 'creator'), "TestScript missing 'creator' relationship"
    assert hasattr(TestScript, 'api_definition'), "TestScript missing 'api_definition' relationship"
    assert hasattr(TestScript, 'parameters'), "TestScript missing 'parameters' relationship"
    assert hasattr(TestScript, 'component_scripts'), "TestScript missing 'component_scripts' relationship"
    assert hasattr(TestScript, 'test_case_scripts'), "TestScript missing 'test_case_scripts' relationship"
    print("   ✓ TestScript relationships defined")

    # ScriptParameter relationships
    assert hasattr(ScriptParameter, 'script'), "ScriptParameter missing 'script' relationship"
    print("   ✓ ScriptParameter relationships defined")

    # Test 5: Verify table names
    print("\n5. Verifying table names...")
    assert TestScript.__tablename__ == "test_scripts"
    assert ScriptParameter.__tablename__ == "script_parameters"
    print("   ✓ Table names correct")

    # Test 6: Create sample instances (without database)
    print("\n6. Creating sample model instances...")

    # Create a sample TestScript
    script = TestScript(
        name="测试用户登录",
        description="验证用户登录功能",
        api_definition_id=1,
        script_type=ScriptType.MAIN,
        execution_order=1,
        variables={
            "username": "testuser",
            "password": "testpass123"
        },
        assertions=[
            {
                "type": "status_code",
                "expected": 200,
                "message": "登录应该返回200状态码"
            },
            {
                "type": "json_path",
                "path": "$.data.token",
                "assertion": "exists",
                "message": "响应应该包含token"
            }
        ],
        extract_variables={
            "auth_token": "$.data.token",
            "user_id": "$.data.user.id"
        },
        output_variables=["auth_token", "user_id"],
        retry_count=3,
        retry_interval=1.0,
        is_active=True,
        version="1.0.0"
    )

    assert script.name == "测试用户登录"
    assert script.script_type == ScriptType.MAIN
    assert script.retry_count == 3
    assert len(script.assertions) == 2
    print("   ✓ TestScript instance created successfully")

    # Create a sample ScriptParameter
    param = ScriptParameter(
        script_id=1,
        name="username",
        description="用户名",
        parameter_type=ParameterType.STRING,
        default_value="testuser",
        is_required=True,
        validation_rules={
            "min_length": 3,
            "max_length": 50,
            "pattern": "^[a-zA-Z0-9_]+$"
        },
        order=1,
        is_sensitive=False
    )

    assert param.name == "username"
    assert param.parameter_type == ParameterType.STRING
    assert param.is_required
    print("   ✓ ScriptParameter instance created successfully")

    # Test 7: Verify script types
    print("\n7. Verifying script type configurations...")

    setup_script = TestScript(
        name="准备测试数据",
        api_definition_id=1,
        script_type=ScriptType.SETUP,
        execution_order=1
    )
    assert setup_script.script_type == ScriptType.SETUP

    teardown_script = TestScript(
        name="清理测试数据",
        api_definition_id=1,
        script_type=ScriptType.TEARDOWN,
        execution_order=99
    )
    assert teardown_script.script_type == ScriptType.TEARDOWN

    print("   ✓ Different script types work correctly")

    # Test 8: Verify debug configuration
    print("\n8. Verifying debug configuration...")

    debug_script = TestScript(
        name="调试脚本",
        api_definition_id=1,
        debug_mode=True,
        debug_breakpoints=[
            {"line": 10, "condition": "response.status_code != 200"},
            {"line": 20, "condition": "data is None"}
        ]
    )

    assert debug_script.debug_mode
    assert len(debug_script.debug_breakpoints) == 2
    print("   ✓ Debug configuration works correctly")

    # Test 9: Verify sensitive parameter handling
    print("\n9. Verifying sensitive parameter handling...")

    password_param = ScriptParameter(
        script_id=1,
        name="password",
        description="密码",
        parameter_type=ParameterType.STRING,
        is_required=True,
        is_sensitive=True
    )

    assert password_param.is_sensitive
    print("   ✓ Sensitive parameter handling works correctly")

    print("\n" + "=" * 60)
    print("✓ All verifications passed!")
    print("=" * 60)
    print("\nLayer 2 Script Models are correctly implemented:")
    print("  - TestScript model with all required attributes")
    print("  - ScriptParameter model with validation support")
    print("  - Support for setup/main/teardown/utility script types")
    print("  - Assertion and validator configuration")
    print("  - Debug mode and breakpoint support")
    print("  - Pre-script and post-script execution")
    print("  - Variable extraction and output")
    print("  - Retry and timeout configuration")
    print("  - Sensitive parameter handling")
    print("=" * 60)


if __name__ == "__main__":
    try:
        verify_script_models()
    except AssertionError as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
