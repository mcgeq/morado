"""Demo script for execution context and variable resolution.

This script demonstrates how the execution context manages parameters,
resolves variables, and handles data flow across the four layers.
"""

import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_src))

from morado.services.execution_context import (
    ExecutionContext,
    ScriptExecutionContext,
    TestCaseExecutionContext,
    VariableResolver,
)


def demo_variable_resolver():
    """Demonstrate variable resolution."""
    print("=" * 70)
    print("1. Variable Resolver Demo")
    print("=" * 70)

    # Create context with variables
    context = {
        'user_name': '张三',
        'user_email': 'zhangsan@example.com',
        'user_age': 25,
        'env': {
            'api': {
                'base_url': 'https://test-api.example.com',
                'timeout': 30
            }
        }
    }

    resolver = VariableResolver(context)

    # Test simple variable
    print("\n简单变量替换:")
    result = resolver.resolve("用户名: ${user_name}")
    print("  输入: '用户名: ${user_name}'")
    print(f"  输出: '{result}'")

    # Test variable with default
    print("\n带默认值的变量:")
    result = resolver.resolve("角色: ${user_role:tester}")
    print("  输入: '角色: ${user_role:tester}'")
    print(f"  输出: '{result}'")

    # Test nested variable (dot notation)
    print("\n嵌套变量（点号路径）:")
    result = resolver.resolve("API地址: ${env.api.base_url}")
    print("  输入: 'API地址: ${env.api.base_url}'")
    print(f"  输出: '{result}'")

    # Test dictionary resolution
    print("\n字典变量替换:")
    data = {
        'name': '${user_name}',
        'email': '${user_email}',
        'age': '${user_age}',
        'role': '${user_role:tester}',
        'api_url': '${env.api.base_url}'
    }
    result = resolver.resolve(data)
    print(f"  输入: {data}")
    print(f"  输出: {result}")

    # Test built-in variables
    print("\n内置变量:")
    print(f"  时间戳: {resolver.resolve('${timestamp}')}")
    print(f"  日期: {resolver.resolve('${date}')}")
    print(f"  日期时间: {resolver.resolve('${datetime}')}")
    print(f"  UUID: {resolver.resolve('${uuid}')}")
    print(f"  随机整数: {resolver.resolve('${random_int}')}")
    print(f"  随机字符串: {resolver.resolve('${random_string}')}")


def demo_execution_context():
    """Demonstrate basic execution context."""
    print("\n" + "=" * 70)
    print("2. Execution Context Demo")
    print("=" * 70)

    # Create execution context
    context = ExecutionContext(environment="test")
    
    # Set initial parameters
    context.update_params({
        'user_name': '李四',
        'user_email': 'lisi@example.com'
    })

    print("\n初始参数:")
    print(f"  user_name: {context.get_param('user_name')}")
    print(f"  user_email: {context.get_param('user_email')}")

    # Update parameters with variable references
    print("\n更新参数（包含变量引用）:")
    context.update_params({
        'full_email': '${user_name} <${user_email}>',
        'greeting': 'Hello, ${user_name}!',
        'timestamp': '${timestamp}'
    })

    print(f"  full_email: {context.get_param('full_email')}")
    print(f"  greeting: {context.get_param('greeting')}")
    print(f"  timestamp: {context.get_param('timestamp')}")

    # Resolve complex data structure
    print("\n解析复杂数据结构:")
    api_request = {
        'url': '${base_url:https://api.example.com}/users',
        'method': 'POST',
        'headers': {
            'Authorization': 'Bearer ${token:default_token}',
            'Content-Type': 'application/json'
        },
        'body': {
            'name': '${user_name}',
            'email': '${user_email}',
            'timestamp': '${timestamp}'
        }
    }

    resolved = context.resolve_value(api_request)
    print(f"  原始: {api_request}")
    print(f"  解析后: {resolved}")


def demo_parameter_priority():
    """Demonstrate parameter priority and override."""
    print("\n" + "=" * 70)
    print("3. Parameter Priority Demo")
    print("=" * 70)

    # Simulate script with default parameters
    class MockScript:
        def __init__(self):
            self.name = "测试脚本"
            self.variables = {
                'timeout': 30,
                'retry_count': 3,
                'user_name': '脚本默认用户'
            }
            self.parameters = []

    class MockParameter:
        def __init__(self, name, default_value):
            self.name = name
            self.default_value = default_value

    script = MockScript()
    script.parameters = [
        MockParameter('expected_status', '200'),
        MockParameter('max_retries', '5')
    ]

    print("\n脚本默认参数:")
    print(f"  timeout: {script.variables['timeout']}")
    print(f"  retry_count: {script.variables['retry_count']}")
    print(f"  user_name: {script.variables['user_name']}")
    print("  expected_status: 200 (参数默认值)")
    print("  max_retries: 5 (参数默认值)")

    # Create script context with overrides
    print("\n应用覆盖参数:")
    override_params = {
        'user_name': '覆盖用户',  # 覆盖脚本变量
        'timeout': 60,  # 覆盖脚本变量
        'new_param': 'new_value'  # 新增参数
    }
    print(f"  覆盖: {override_params}")

    context = ScriptExecutionContext(
        script,
        override_params,
    )

    print("\n最终参数（按优先级合并）:")
    print(f"  timeout: {context.get_param('timeout')} (被覆盖)")
    print(f"  retry_count: {context.get_param('retry_count')} (保持脚本默认)")
    print(f"  user_name: {context.get_param('user_name')} (被覆盖)")
    print(f"  expected_status: {context.get_param('expected_status')} (参数默认值)")
    print(f"  max_retries: {context.get_param('max_retries')} (参数默认值)")
    print(f"  new_param: {context.get_param('new_param')} (新增)")


def demo_data_flow():
    """Demonstrate data flow between layers."""
    print("\n" + "=" * 70)
    print("4. Data Flow Between Layers Demo")
    print("=" * 70)

    # Simulate test case
    class MockTestCase:
        def __init__(self):
            self.name = "用户注册登录测试"
            self.environment = "test"
            self.test_data = {
                'base_url': 'https://test.example.com',
                'user_name': '测试用户${timestamp}',
                'user_email': 'test${timestamp}@example.com',
                'user_password': 'Test@123'
            }

    test_case = MockTestCase()

    print("\n第四层：测试用例数据")
    print(f"  {test_case.test_data}")

    # Create test case context
    context = TestCaseExecutionContext(
        test_case,
        runtime_params={
            'user_password': 'RuntimePassword@456'  # 运行时覆盖
        }
    )

    print("\n解析后的测试用例参数:")
    print(f"  base_url: {context.get_param('base_url')}")
    print(f"  user_name: {context.get_param('user_name')}")
    print(f"  user_email: {context.get_param('user_email')}")
    print(f"  user_password: {context.get_param('user_password')} (运行时覆盖)")

    # Simulate script execution that produces output
    print("\n第二层：脚本执行")
    print("  [脚本1] 用户注册")

    # Simulate script output
    script_output = {
        'created_user_id': 12345,
        'auth_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    }

    print(f"  输出变量: {script_output}")

    # Update context with script output
    context.params.update(script_output)

    print("\n第二层：下一个脚本使用上一个脚本的输出")
    print("  [脚本2] 用户登录")

    # Next script can reference previous output
    login_params = context.resolve_params({
        'user_id': '${created_user_id}',
        'email': '${user_email}',
        'password': '${user_password}'
    })

    print(f"  参数: {login_params}")
    print(f"  ✓ 成功引用了脚本1的输出 (user_id: {login_params['user_id']})")


def demo_complete_workflow():
    """Demonstrate complete workflow with all layers."""
    print("\n" + "=" * 70)
    print("5. Complete Workflow Demo")
    print("=" * 70)

    print("\n场景: 用户注册 -> 登录 -> 获取信息 -> 更新信息")
    print("-" * 70)

    # Test case level
    class MockTestCase:
        def __init__(self):
            self.environment = "test"
            self.test_data = {
                'user_name': '测试用户',
                'user_email': 'test@example.com',
                'user_password': 'Test@123'
            }

    test_case = MockTestCase()
    context = TestCaseExecutionContext(test_case)

    print("\n[测试用例] 初始参数:")
    print(f"  user_name: {context.get_param('user_name')}")
    print(f"  user_email: {context.get_param('user_email')}")

    # Step 1: Register user
    print("\n[步骤1] 用户注册")
    register_params = context.resolve_params({
        'name': '${user_name}',
        'email': '${user_email}',
        'password': '${user_password}'
    })
    print(f"  请求参数: {register_params}")

    # Simulate response
    register_output = {
        'user_id': 12345,
        'token': 'token_abc123'
    }
    context.params.update(register_output)
    print(f"  响应输出: {register_output}")

    # Step 2: Login
    print("\n[步骤2] 用户登录")
    login_params = context.resolve_params({
        'email': '${user_email}',
        'password': '${user_password}'
    })
    print(f"  请求参数: {login_params}")

    # Simulate response
    login_output = {
        'session_id': 'sess_xyz789',
        'token': 'token_new456'  # 更新token
    }
    context.params.update(login_output)
    print(f"  响应输出: {login_output}")

    # Step 3: Get user info
    print("\n[步骤3] 获取用户信息")
    get_params = context.resolve_params({
        'user_id': '${user_id}',
        'token': '${token}'
    })
    print(f"  请求参数: {get_params}")
    print("  ✓ 使用了步骤1的user_id和步骤2的token")

    # Step 4: Update user info
    print("\n[步骤4] 更新用户信息")
    update_params = context.resolve_params({
        'user_id': '${user_id}',
        'token': '${token}',
        'new_name': '${user_name}_updated',
        'session': '${session_id}'
    })
    print(f"  请求参数: {update_params}")
    print("  ✓ 使用了所有前面步骤的输出变量")

    print("\n" + "-" * 70)
    print("✓ 完整工作流演示完成")
    print("  - 参数从测试用例层向下传递")
    print("  - 每个步骤的输出成为下一步的输入")
    print("  - 变量自动解析和替换")
    print("  - 支持变量覆盖和默认值")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Morado 执行上下文与数据管理演示" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")

    try:
        demo_variable_resolver()
        demo_execution_context()
        demo_parameter_priority()
        demo_data_flow()
        demo_complete_workflow()

        print("\n" + "=" * 70)
        print("✓ 所有演示完成!")
        print("=" * 70)
        print("\n关键特性:")
        print("  1. 灵活的变量替换 (${variable}, ${variable:default})")
        print("  2. 多层参数优先级 (运行时 > 用例 > 组件 > 脚本 > 环境)")
        print("  3. 点号路径访问 (${env.api.base_url})")
        print("  4. 内置系统变量 (${timestamp}, ${uuid}, etc.)")
        print("  5. 层间数据流动 (输出变量自动传递)")
        print("=" * 70)

        return 0
    except Exception as e:
        print(f"\n✗ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
