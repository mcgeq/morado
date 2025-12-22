# 测试数据管理机制总结

## 核心概念

Morado测试平台实现了一套完整的数据管理和参数传递机制，确保测试数据在四层架构中灵活流动和复用。

## 参数优先级（从高到低）

参数从上层向下层传递，**上层参数覆盖下层参数**：

```
1. 运行时参数 (Runtime Parameters) ← 最高优先级
   ↓ 如果没有，则使用
2. 测试用例数据 (Test Case Data)
   ↓ 如果没有，则使用
3. 组件共享变量 (Component Shared Variables)
   ↓ 如果没有，则使用
4. 脚本变量 (Script Variables)
   ↓ 如果没有，则使用
5. 脚本参数默认值 (Script Parameter Defaults)
   ↓ 如果没有，则使用
6. 环境配置 (Environment Config) ← 最低优先级
```

**关键理解：**
- 上层的值会**覆盖**下层的值
- 如果上层没有提供某个参数，才会使用下层的值
- 这是一个**向下传递、向下覆盖**的过程

## 变量替换语法

### 基本语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `${variable}` | 简单变量引用 | `${user_name}` → "张三" |
| `${variable:default}` | 带默认值的变量 | `${role:tester}` → "tester" |
| `${env.path.to.value}` | 环境配置引用（点号路径） | `${env.api.base_url}` → "https://api.example.com" |

### 内置系统变量

| 变量 | 说明 | 示例值 |
|------|------|--------|
| `${timestamp}` | 当前时间戳 | 1703001234 |
| `${date}` | 当前日期 | 2025-12-22 |
| `${datetime}` | 当前日期时间 | 2025-12-22 21:44:01 |
| `${uuid}` | 随机UUID | 3734bdd0-b5a0-4f8b-bd08-1d0c3d0f6599 |
| `${random_int}` | 随机整数 | 41669 |
| `${random_string}` | 随机字符串 | 20251222 |
| `${environment}` | 当前环境名称 | test |

## 各层数据管理

### 第一层：API定义层

**Header变量替换：**
```python
header = Header(
    headers={
        "Authorization": "Bearer ${token}",
        "X-Environment": "${environment}"
    }
)
```

**Body变量替换：**
```python
body = Body(
    example_data={
        "name": "${user_name}",
        "email": "${user_email}",
        "age": "${user_age:25}"  # 默认值25
    }
)
```

**ApiDefinition路径参数：**
```python
api_def = ApiDefinition(
    path="/api/users/{id}",
    path_parameters={"id": {"type": "integer"}}
)
# 执行时: /api/users/123
```

### 第二层：脚本层

**脚本参数定义：**
```python
script = TestScript(
    variables={
        "timeout": 30,
        "retry_count": 3
    }
)

param = ScriptParameter(
    name="user_id",
    default_value="123",
    is_required=True
)
```

**参数使用：**
```python
# 脚本内容
user_id = params.get('user_id')
timeout = params.get('timeout', 30)
```

### 第三层：组件层

**组件共享变量：**
```python
component = TestComponent(
    shared_variables={
        "base_url": "https://api.example.com",
        "created_user_id": None  # 将在执行中填充
    }
)
```

**脚本间变量传递：**
```python
# 脚本1：创建用户
comp_script1 = ComponentScript(
    execution_order=1,
    script_parameters={"user_name": "测试用户"}
)
# 输出: created_user_id = 12345

# 脚本2：查询用户（使用脚本1的输出）
comp_script2 = ComponentScript(
    execution_order=2,
    script_parameters={"user_id": "${created_user_id}"}
)
```

### 第四层：测试用例层

**测试用例数据：**
```python
test_case = TestCase(
    environment="test",
    test_data={
        "base_url": "https://test.example.com",
        "user_name": "测试用户${timestamp}",
        "user_email": "test${timestamp}@example.com"
    }
)
```

**运行时参数覆盖：**
```python
# 执行测试用例时传入参数
execute_test_case(
    test_case,
    runtime_params={
        "user_password": "CustomPassword@456"  # 覆盖默认值
    }
)
```

## 数据流示例

### 场景：用户注册登录流程

**参数定义：**

```python
# 环境配置 (最低优先级)
env_config = {
    "api_base_url": "https://test.example.com",
    "timeout": 60,
    "retry_count": 5
}

# 测试用例数据 (覆盖环境配置)
test_case.test_data = {
    "timeout": 30,  # 覆盖环境的60
    "user_name": "测试用户",
    "user_email": "test@example.com"
}

# 组件共享变量 (覆盖测试用例)
component.shared_variables = {
    "retry_count": 3  # 覆盖环境的5
}

# 脚本变量 (覆盖组件)
script.variables = {
    "expected_status": 200
}

# 运行时参数 (最高优先级，覆盖所有)
runtime_params = {
    "timeout": 45,  # 覆盖测试用例的30
    "user_password": "Runtime@456"
}
```

**最终合并结果：**

```python
{
    "api_base_url": "https://test.example.com",  # 来自环境（无覆盖）
    "timeout": 45,  # 来自运行时（覆盖了测试用例和环境）
    "retry_count": 3,  # 来自组件（覆盖了环境）
    "user_name": "测试用户",  # 来自测试用例（无覆盖）
    "user_email": "test@example.com",  # 来自测试用例（无覆盖）
    "user_password": "Runtime@456",  # 来自运行时（无覆盖）
    "expected_status": 200  # 来自脚本（无覆盖）
}
```

**覆盖路径追踪：**

| 参数 | 环境 | 测试用例 | 组件 | 脚本 | 运行时 | 最终值 | 来源 |
|------|------|----------|------|------|--------|--------|------|
| api_base_url | "https://test.example.com" | - | - | - | - | "https://test.example.com" | 环境 |
| timeout | 60 | **30** | - | - | **45** | 45 | 运行时 |
| retry_count | 5 | - | **3** | - | - | 3 | 组件 |
| user_name | - | "测试用户" | - | - | - | "测试用户" | 测试用例 |
| user_email | - | "test@example.com" | - | - | - | "test@example.com" | 测试用例 |
| user_password | - | - | - | - | "Runtime@456" | "Runtime@456" | 运行时 |
| expected_status | - | - | - | 200 | - | 200 | 脚本 |

**执行流程：**

```
[测试用例] 初始参数合并
  环境配置 + 测试用例数据 + 运行时参数
  → timeout=45, user_name="测试用户", user_email="test@example.com"
         ↓
[脚本1] 用户注册
  输入: user_name, user_email, user_password (来自上层)
  输出: user_id=12345, token="abc123"
  → 输出变量添加到上下文
         ↓
[脚本2] 用户登录
  输入: user_email, user_password (来自上层)
  引用: ${user_id} → 12345 (来自脚本1输出)
  输出: session_id="xyz789", token="new456"
  → 输出变量添加到上下文
         ↓
[脚本3] 获取用户信息
  输入: ${user_id} → 12345, ${token} → "new456"
  引用: 脚本1的user_id, 脚本2的token
         ↓
[脚本4] 更新用户信息
  输入: ${user_id}, ${token}, ${session_id}
  引用: 所有前面脚本的输出
```

## 环境配置管理

### 配置文件结构

```toml
# config/test.toml
[api]
base_url = "https://test-api.example.com"
timeout = 30

[auth]
token_url = "https://test-auth.example.com/token"
client_id = "test_client_id"

[database]
host = "test-db.example.com"
port = 5432
```

### 配置引用

```python
# 在测试用例中引用环境配置
test_case = TestCase(
    test_data={
        "api_url": "${env.api.base_url}",
        "timeout": "${env.api.timeout:30}"
    }
)
```

## 实现类

### VariableResolver

负责解析和替换变量引用：

```python
resolver = VariableResolver(context)
result = resolver.resolve("用户: ${user_name}")
# 输出: "用户: 张三"
```

### ExecutionContext

基础执行上下文，管理参数和变量：

```python
context = ExecutionContext(environment="test")
context.update_params({"user_name": "张三"})
value = context.get_param("user_name")
```

### ScriptExecutionContext

脚本层执行上下文：

```python
context = ScriptExecutionContext(
    script,
    override_params={"timeout": 60}
)
```

### ComponentExecutionContext

组件层执行上下文，支持脚本间变量共享：

```python
context = ComponentExecutionContext(component)
result = context.execute_script(comp_script)
# 脚本输出自动添加到共享变量
```

### TestCaseExecutionContext

测试用例层执行上下文，管理整个测试流程：

```python
context = TestCaseExecutionContext(
    test_case,
    runtime_params={"password": "Custom@123"}
)
result = context.execute_script(case_script)
result = context.execute_component(case_component)
```

## 最佳实践

### 1. 参数命名规范

```python
# 好的命名
user_id, user_name, user_email
api_base_url, api_timeout
expected_status_code

# 避免的命名
id, name, url  # 太通用
x, y, temp     # 无意义
```

### 2. 使用环境配置

```python
# 将环境相关配置放在环境文件中
# config/test.toml
[api]
base_url = "https://test-api.example.com"

# 在测试中引用
test_data = {
    "base_url": "${env.api.base_url}"
}
```

### 3. 合理使用默认值

```python
# 在参数定义中提供默认值
param = ScriptParameter(
    name="timeout",
    default_value="30"
)

# 在变量引用中使用默认值
"timeout": "${timeout:30}"
```

### 4. 变量作用域管理

```python
# 测试用例级别：全局变量
test_case.test_data = {
    "environment": "test",
    "base_url": "https://test.example.com"
}

# 组件级别：组件内共享
component.shared_variables = {
    "created_user_id": None
}

# 脚本级别：脚本私有
script.variables = {
    "retry_count": 3
}
```

### 5. 输出变量传递

```python
# 脚本1输出
script1_result = {
    'output_variables': {
        'created_user_id': 12345
    }
}

# 脚本2引用
script2_params = {
    'user_id': '${created_user_id}'
}
```

## 关键特性

1. **灵活的变量替换**: 支持 `${variable}` 和 `${variable:default}` 语法
2. **多层参数优先级**: 运行时 > 用例 > 组件 > 脚本 > 环境
3. **点号路径访问**: 支持 `${env.api.base_url}` 访问嵌套配置
4. **内置系统变量**: 提供时间戳、UUID等常用变量
5. **层间数据流动**: 输出变量自动传递到下一层
6. **环境隔离**: 通过环境配置文件管理不同环境
7. **默认值机制**: 多层默认值保证系统健壮性
8. **运行时覆盖**: 支持执行时动态修改参数

## 演示脚本

运行以下命令查看完整演示：

```bash
cd backend
uv run python scripts/demo_execution_context.py
```

演示内容包括：
1. 变量解析器演示
2. 执行上下文演示
3. 参数优先级演示
4. 层间数据流演示
5. 完整工作流演示

## 相关文档

- [数据管理与执行机制详细文档](./data-management-and-execution.md)
- [四层架构设计](./four-layer-architecture.md)
- [API组件模型文档](../backend/docs/api_component_models.md)
