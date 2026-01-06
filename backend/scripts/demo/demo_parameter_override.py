"""Demo script for parameter override logic.

This script clearly demonstrates how parameters are overridden
from top layer to bottom layer in the four-layer architecture.
"""

import sys

sys.path.insert(0, 'src')


def demo_parameter_override():
    """Demonstrate parameter override logic."""
    print("=" * 80)
    print("参数覆盖逻辑演示")
    print("=" * 80)
    print("\n核心原则: 上层参数覆盖下层参数")
    print("优先级: 运行时 > 测试用例 > 组件 > 脚本 > 环境配置")
    print("-" * 80)

    # 定义各层参数
    print("\n【第1步】定义各层参数\n")

    # 环境配置（最低优先级）
    env_config = {
        "api_base_url": "https://test.example.com",
        "timeout": 60,
        "retry_count": 5,
        "log_level": "INFO"
    }
    print("环境配置 (最低优先级):")
    for k, v in env_config.items():
        print(f"  {k}: {v}")

    # 测试用例数据
    test_case_data = {
        "timeout": 30,  # 覆盖环境的60
        "user_name": "测试用户",
        "user_email": "test@example.com"
    }
    print("\n测试用例数据 (覆盖环境配置):")
    for k, v in test_case_data.items():
        if k in env_config:
            print(f"  {k}: {v} ← 覆盖环境的 {env_config[k]}")
        else:
            print(f"  {k}: {v}")

    # 组件共享变量
    component_vars = {
        "retry_count": 3,  # 覆盖环境的5
        "component_id": "comp_001"
    }
    print("\n组件共享变量 (覆盖测试用例):")
    for k, v in component_vars.items():
        if k in env_config:
            print(f"  {k}: {v} ← 覆盖环境的 {env_config[k]}")
        else:
            print(f"  {k}: {v}")

    # 脚本变量
    script_vars = {
        "expected_status": 200,
        "script_id": "script_001"
    }
    print("\n脚本变量 (覆盖组件):")
    for k, v in script_vars.items():
        print(f"  {k}: {v}")

    # 运行时参数（最高优先级）
    runtime_params = {
        "timeout": 45,  # 覆盖测试用例的30
        "user_password": "Runtime@456",
        "log_level": "DEBUG"  # 覆盖环境的INFO
    }
    print("\n运行时参数 (最高优先级，覆盖所有):")
    for k, v in runtime_params.items():
        if k in test_case_data:
            print(f"  {k}: {v} ← 覆盖测试用例的 {test_case_data[k]}")
        elif k in env_config:
            print(f"  {k}: {v} ← 覆盖环境的 {env_config[k]}")
        else:
            print(f"  {k}: {v}")

    # 参数合并
    print("\n" + "=" * 80)
    print("【第2步】参数合并过程（从下往上，上层覆盖下层）")
    print("=" * 80)

    # 步骤1: 从环境配置开始
    merged = env_config.copy()
    print("\n步骤1: 从环境配置开始")
    print(f"  当前参数: {merged}")

    # 步骤2: 应用测试用例数据
    print("\n步骤2: 应用测试用例数据（覆盖环境配置）")
    for k, v in test_case_data.items():
        if k in merged:
            print(f"  {k}: {merged[k]} → {v} (覆盖)")
        else:
            print(f"  {k}: {v} (新增)")
        merged[k] = v
    print(f"  当前参数: {merged}")

    # 步骤3: 应用组件共享变量
    print("\n步骤3: 应用组件共享变量（覆盖测试用例）")
    for k, v in component_vars.items():
        if k in merged:
            print(f"  {k}: {merged[k]} → {v} (覆盖)")
        else:
            print(f"  {k}: {v} (新增)")
        merged[k] = v
    print(f"  当前参数: {merged}")

    # 步骤4: 应用脚本变量
    print("\n步骤4: 应用脚本变量（覆盖组件）")
    for k, v in script_vars.items():
        if k in merged:
            print(f"  {k}: {merged[k]} → {v} (覆盖)")
        else:
            print(f"  {k}: {v} (新增)")
        merged[k] = v
    print(f"  当前参数: {merged}")

    # 步骤5: 应用运行时参数
    print("\n步骤5: 应用运行时参数（最高优先级，覆盖所有）")
    for k, v in runtime_params.items():
        if k in merged:
            print(f"  {k}: {merged[k]} → {v} (覆盖)")
        else:
            print(f"  {k}: {v} (新增)")
        merged[k] = v
    print(f"  当前参数: {merged}")

    # 最终结果
    print("\n" + "=" * 80)
    print("【第3步】最终合并结果")
    print("=" * 80)

    print("\n最终参数:")
    for k, v in sorted(merged.items()):
        # 确定来源
        source = ""
        if k in runtime_params:
            source = "运行时"
        elif k in script_vars:
            source = "脚本"
        elif k in component_vars:
            source = "组件"
        elif k in test_case_data:
            source = "测试用例"
        elif k in env_config:
            source = "环境配置"

        print(f"  {k:20} = {v!s:30} (来自: {source})")

    # 覆盖追踪表
    print("\n" + "=" * 80)
    print("【第4步】覆盖追踪表")
    print("=" * 80)

    print("\n参数覆盖路径:")
    print(f"{'参数':<20} {'环境':<15} {'测试用例':<15} {'组件':<15} {'脚本':<15} {'运行时':<15} {'最终值':<15} {'来源':<10}")
    print("-" * 140)

    all_keys = set(env_config.keys()) | set(test_case_data.keys()) | set(component_vars.keys()) | set(script_vars.keys()) | set(runtime_params.keys())

    for key in sorted(all_keys):
        env_val = str(env_config.get(key, '-'))
        test_val = str(test_case_data.get(key, '-'))
        comp_val = str(component_vars.get(key, '-'))
        script_val = str(script_vars.get(key, '-'))
        runtime_val = str(runtime_params.get(key, '-'))
        final_val = str(merged[key])

        # 确定来源
        if key in runtime_params:
            source = "运行时"
        elif key in script_vars:
            source = "脚本"
        elif key in component_vars:
            source = "组件"
        elif key in test_case_data:
            source = "测试用例"
        else:
            source = "环境"

        print(f"{key:<20} {env_val:<15} {test_val:<15} {comp_val:<15} {script_val:<15} {runtime_val:<15} {final_val:<15} {source:<10}")

    print("\n" + "=" * 80)
    print("✓ 演示完成")
    print("=" * 80)

    print("\n关键要点:")
    print("  1. 参数从环境配置开始，逐层向上合并")
    print("  2. 上层的值会覆盖下层的值")
    print("  3. 如果上层没有提供某个参数，则保留下层的值")
    print("  4. 运行时参数具有最高优先级，可以覆盖任何层的值")
    print("  5. 这是一个向上覆盖的过程：环境 ← 测试用例 ← 组件 ← 脚本 ← 运行时")


def demo_practical_example():
    """Demonstrate a practical example."""
    print("\n\n" + "=" * 80)
    print("实际应用示例")
    print("=" * 80)

    print("\n场景: 在不同环境下执行相同的测试用例")
    print("-" * 80)

    # 测试环境
    print("\n【测试环境】")
    test_env = {
        "api_base_url": "https://test-api.example.com",
        "timeout": 60,
        "db_host": "test-db.example.com"
    }
    test_case = {
        "timeout": 30,  # 测试用例希望更短的超时
        "user_name": "测试用户"
    }

    merged_test = test_env.copy()
    merged_test.update(test_case)

    print("环境配置:", test_env)
    print("测试用例:", test_case)
    print("合并结果:", merged_test)
    print(f"  → timeout 使用测试用例的 {merged_test['timeout']} (覆盖了环境的 {test_env['timeout']})")

    # 生产环境
    print("\n【生产环境】")
    prod_env = {
        "api_base_url": "https://api.example.com",
        "timeout": 120,
        "db_host": "prod-db.example.com"
    }

    merged_prod = prod_env.copy()
    merged_prod.update(test_case)

    print("环境配置:", prod_env)
    print("测试用例:", test_case)
    print("合并结果:", merged_prod)
    print(f"  → timeout 使用测试用例的 {merged_prod['timeout']} (覆盖了环境的 {prod_env['timeout']})")

    print("\n结论:")
    print("  - 相同的测试用例在不同环境下执行")
    print("  - 环境特定的配置（如 api_base_url, db_host）来自环境配置")
    print("  - 测试用例特定的配置（如 timeout）覆盖环境配置")
    print("  - 这样既保证了环境隔离，又保证了测试的一致性")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "参数覆盖逻辑详细演示" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        demo_parameter_override()
        demo_practical_example()

        print("\n" + "=" * 80)
        print("✓ 所有演示完成!")
        print("=" * 80)

        return 0
    except Exception as e:
        print(f"\n✗ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
