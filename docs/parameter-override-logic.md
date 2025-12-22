# 参数覆盖逻辑详解

## 核心原则

**上层参数覆盖下层参数**

参数从底层（环境配置）开始，逐层向上合并。每一层都可以覆盖下层的参数值。

## 优先级顺序

```
运行时参数 (Runtime Parameters)        ← 最高优先级
    ↓ 如果没有，则使用
测试用例数据 (Test Case Data)
    ↓ 如果没有，则使用
组件共享变量 (Component Shared Variables)
    ↓ 如果没有，则使用
脚本变量 (Script Variables)
    ↓ 如果没有，则使用
脚本参数默认值 (Script Parameter Defaults)
    ↓ 如果没有，则使用
环境配置 (Environment Config)          ← 最低优先级
```

## 覆盖规则

1. **上层覆盖下层**: 如果上层提供了某个参数，则使用上层的值，忽略下层的值
2. **缺失则继承**: 如果上层没有提供某个参数，则使用下层的值
3. **新增参数**: 每一层都可以新增参数，不影响其他层
4. **完全覆盖**: 运行时参数可以覆盖任何层的任何参数

## 参数合并过程

### 步骤1: 从环境配置开始

```python
params = env_config.copy()
# params = {
#     "api_base_url": "https://test.example.com",
#     "timeout": 60,
#     "retry_count": 5
# }
```

### 步骤2: 应用测试用例数据

```python
params.update(test_case.test_data)
# 覆盖: timeout: 60 → 30
# 新增: user_name, user_email
# params = {
#     "api_base_url": "https://test.example.com",  # 保留
#     "timeout": 30,  # 覆盖
#     "retry_count": 5,  # 保留
#     "user_name": "测试用户",  # 新增
#     "user_email": "test@example.com"  # 新增
# }
```

### 步骤3: 应用组件共享变量

```python
params.update(component.shared_variables)
# 覆盖: retry_count: 5 → 3
# 新增: component_id
# params = {
#     "api_base_url": "https://test.example.com",  # 保留
#     "timeout": 30,  # 保留
#     "retry_count": 3,  # 覆盖
#     "user_name": "测试用户",  # 保留
#     "user_email": "test@example.com",  # 保留
#     "component_id": "comp_001"  # 新增
# }
```

### 步骤4: 应用脚本变量

```python
params.update(script.variables)
# 新增: expected_status, script_id
# params = {
#     "api_base_url": "https://test.example.com",  # 保留
#     "timeout": 30,  # 保留
#     "retry_count": 3,  # 保留
#     "user_name": "测试用户",  # 保留
#     "user_email": "test@example.com",  # 保留
#     "component_id": "comp_001",  # 保留
#     "expected_status": 200,  # 新增
#     "script_id": "script_001"  # 新增
# }
```

### 步骤5: 应用运行时参数

```python
params.update(runtime_params)
# 覆盖: timeout: 30 → 45, log_level: INFO → DEBUG
# 新增: user_password
# params = {
#     "api_base_url": "https://test.example.com",  # 保留
#     "timeout": 45,  # 覆盖
#     "retry_count": 3,  # 保留
#     "user_name": "测试用户",  # 保留
#     "user_email": "test@example.com",  # 保留
#     "component_id": "comp_001",  # 保留
#     "expected_status": 200,  # 保留
#     "script_id": "script_001",  # 保留
#     "log_level": "DEBUG",  # 覆盖
#     "user_password": "Runtime@456"  # 新增
# }
```

## 覆盖追踪表

| 参数 | 环境 | 测试用例 | 组件 | 脚本 | 运行时 | 最终值 | 来源 |
|------|------|----------|------|------|--------|--------|------|
| api_base_url | "https://test.example.com" | - | - | - | - | "https://test.example.com" | 环境 |
| timeout | 60 | **30** | - | - | **45** | 45 | 运行时 |
| retry_count | 5 | - | **3** | - | - | 3 | 组件 |
| user_name | - | "测试用户" | - | - | - | "测试用户" | 测试用例 |
| user_email | - | "test@example.com" | - | - | - | "test@example.com" | 测试用例 |
| component_id | - | - | "comp_001" | - | - | "comp_001" | 组件 |
| expected_status | - | - | - | 200 | - | 200 | 脚本 |
| script_id | - | - | - | "script_001" | - | "script_001" | 脚本 |
| log_level | "INFO" | - | - | - | **"DEBUG"** | "DEBUG" | 运行时 |
| user_password | - | - | - | - | "Runtime@456" | "Runtime@456" | 运行时 |

**说明:**
- **粗体**表示该层覆盖了下层的值
- `-` 表示该层没有提供该参数
- 最终值来自最上层提供该参数的层

## 实际应用场景

### 场景1: 不同环境使用相同测试用例

```python
# 测试用例定义（环境无关）
test_case = TestCase(
    test_data={
        "timeout": 30,  # 测试用例希望30秒超时
        "user_name": "测试用户"
    }
)

# 测试环境
test_env = {
    "api_base_url": "https://test-api.example.com",
    "timeout": 60  # 环境默认60秒
}
# 合并结果: timeout=30 (测试用例覆盖环境)

# 生产环境
prod_env = {
    "api_base_url": "https://api.example.com",
    "timeout": 120  # 环境默认120秒
}
# 合并结果: timeout=30 (测试用例覆盖环境)
```

**优势:**
- 测试用例在不同环境下行为一致
- 环境特定配置（如URL）自动适配
- 测试特定配置（如超时）保持不变

### 场景2: 运行时动态调整参数

```python
# 正常执行
execute_test_case(test_case)
# 使用测试用例的默认密码

# 临时使用不同密码
execute_test_case(
    test_case,
    runtime_params={"user_password": "TempPassword@123"}
)
# 运行时参数覆盖测试用例的密码
```

**优势:**
- 无需修改测试用例定义
- 支持临时调整参数
- 适合调试和特殊场景

### 场景3: 组件复用与参数定制

```python
# 定义可复用组件
component = TestComponent(
    name="用户管理流程",
    shared_variables={
        "retry_count": 3,
        "timeout": 30
    }
)

# 测试用例1: 使用组件默认参数
case1 = TestCase(
    test_data={"user_name": "用户1"}
)
# retry_count=3, timeout=30 (来自组件)

# 测试用例2: 覆盖组件参数
case2 = TestCase(
    test_data={
        "user_name": "用户2",
        "timeout": 60  # 覆盖组件的30
    }
)
# retry_count=3 (来自组件), timeout=60 (覆盖组件)
```

**优势:**
- 组件提供合理默认值
- 测试用例可以按需定制
- 保持组件的可复用性

## 常见误区

### ❌ 误区1: 认为下层参数会覆盖上层

```python
# 错误理解
test_case.test_data = {"timeout": 30}
runtime_params = {"timeout": 45}
# 错误: 认为最终 timeout=30 (测试用例的值)
```

**正确理解:**
```python
# 正确: 运行时参数覆盖测试用例
# 最终 timeout=45 (运行时的值)
```

### ❌ 误区2: 认为必须在每一层都定义参数

```python
# 错误理解
# 必须在环境、测试用例、组件、脚本都定义 timeout
```

**正确理解:**
```python
# 只需在任意一层定义即可
# 如果多层定义，上层覆盖下层
env_config = {"timeout": 60}
test_case.test_data = {}  # 不定义 timeout
# 最终 timeout=60 (来自环境)
```

### ❌ 误区3: 认为参数会向下传递

```python
# 错误理解
runtime_params = {"timeout": 45}
# 错误: 认为这会修改测试用例的 test_data
```

**正确理解:**
```python
# 运行时参数只在执行时生效
# 不会修改测试用例的定义
# 每次执行都重新合并参数
```

## 最佳实践

### 1. 环境配置：放置环境特定的配置

```python
# config/test.toml
[api]
base_url = "https://test-api.example.com"
timeout = 60

[database]
host = "test-db.example.com"
```

### 2. 测试用例：放置测试特定的配置

```python
test_case = TestCase(
    test_data={
        "timeout": 30,  # 测试需要更短的超时
        "user_name": "测试用户",
        "expected_status": 200
    }
)
```

### 3. 组件：放置组件级别的默认值

```python
component = TestComponent(
    shared_variables={
        "retry_count": 3,
        "max_attempts": 5
    }
)
```

### 4. 脚本：放置脚本特定的配置

```python
script = TestScript(
    variables={
        "expected_response_time": 1000,
        "validation_rules": {...}
    }
)
```

### 5. 运行时：用于临时覆盖和调试

```python
# 正常执行
execute_test_case(test_case)

# 调试时使用不同参数
execute_test_case(
    test_case,
    runtime_params={
        "timeout": 300,  # 调试时需要更长超时
        "log_level": "DEBUG"
    }
)
```

## 演示脚本

运行以下命令查看详细演示：

```bash
cd backend
uv run python scripts/demo_parameter_override.py
```

演示内容包括：
1. 各层参数定义
2. 参数合并过程
3. 最终合并结果
4. 覆盖追踪表
5. 实际应用示例

## 总结

参数覆盖机制的核心是：

1. **从下往上合并**: 环境 → 测试用例 → 组件 → 脚本 → 运行时
2. **上层覆盖下层**: 上层的值会覆盖下层的值
3. **缺失则继承**: 上层没有的参数，使用下层的值
4. **灵活可控**: 每一层都可以按需定义参数

这种设计既保证了配置的灵活性，又保证了测试的可维护性和可复用性。
