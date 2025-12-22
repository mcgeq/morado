# 测试数据管理与执行机制

## 概述

本文档详细说明Morado测试平台四层架构中的测试数据管理、参数传递、变量替换和环境配置机制。

## 数据流与参数优先级

### 参数优先级（从高到低）

参数从上层向下层传递，上层参数覆盖下层参数：

```
执行时传入参数（最高优先级）
    ↓ 覆盖
测试用例参数（第四层）
    ↓ 覆盖
组件参数（第三层）
    ↓ 覆盖
脚本参数（第二层）
    ↓ 覆盖
API定义默认值（第一层）
    ↓ 覆盖
环境配置（最低优先级）
```

**覆盖规则：**
- 如果上层提供了参数值，则使用上层的值
- 如果上层没有提供，则使用下层的值
- 如果所有层都没有提供，则使用环境配置
- 如果环境配置也没有，则使用变量引用的默认值（如 `${var:default}`）

### 数据流示意图

```
┌─────────────────────────────────────────────────────────────┐
│                    执行时传入参数                              │
│                  (Runtime Parameters)                        │
│              优先级最高，覆盖所有下层参数                        │
└────────────────────────┬────────────────────────────────────┘
                         │ 向下传递，覆盖下层
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              第四层：测试用例 (Test Case)                      │
│  test_data: {                                               │
│    "environment": "test",                                   │
│    "base_url": "https://test.example.com",                 │
│    "user_id": 123                                          │
│  }                                                          │
│  如果运行时没有提供，则使用这里的值                             │
└────────────────────────┬────────────────────────────────────┘
                         │ 向下传递，覆盖下层
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            第三层：联合组件 (Component)                        │
│  shared_variables: {                                        │
│    "timeout": 30,                                          │
│    "retry_count": 3                                        │
│  }                                                          │
│  component_parameters (from TestCaseComponent): {          │
│    "user_id": 456  // 如果测试用例没有提供，使用这个值         │
│  }                                                          │
│  如果上层没有提供，则使用这里的值                               │
└────────────────────────┬────────────────────────────────────┘
                         │ 向下传递，覆盖下层
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                第二层：脚本 (Script)                          │
│  variables: {                                               │
│    "expected_status": 200                                  │
│  }                                                          │
│  script_parameters (from ComponentScript): {               │
│    "user_id": 789  // 如果组件没有提供，使用这个值            │
│  }                                                          │
│  如果上层没有提供，则使用这里的值                               │
└────────────────────────┬────────────────────────────────────┘
                         │ 向下传递
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            第一层：API定义 (API Definition)                   │
│  path_parameters: {                                         │
│    "id": "${user_id}"  // 从上层获取                        │
│  }                                                          │
│  headers (from Header): {                                  │
│    "Authorization": "Bearer ${token}"  // 从上层或环境获取   │
│  }                                                          │
│  如果上层没有提供，则从环境配置获取                             │
└─────────────────────────────────────────────────────────────┘
```

## 第一层：API定义层的数据管理

### Header中的变量替换

```python
# Header定义
header = Header(
    name="认证Header",
    headers={
        "Authorization": "Bearer ${token}",
        "X-API-Key": "${api_key}",
        "X-Environment": "${environment}"
    }
)

# 执行时的变量上下文
context = {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "api_key": "sk_test_123456",
    "environment": "test"
}

# 替换后的实际Header
actual_headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "X-API-Key": "sk_test_123456",
    "X-Environment": "test"
}
```

### Body中的变量替换

```python
# Body定义
body = Body(
    name="用户信息Body",
    example_data={
        "name": "${user_name}",
        "email": "${user_email}",
        "age": "${user_age:25}",  # 默认值为25
        "role": "tester"  # 固定值
    }
)

# 执行时的变量上下文
context = {
    "user_name": "张三",
    "user_email": "zhangsan@example.com"
    # user_age 未提供，使用默认值
}

# 替换后的实际Body
actual_body = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25,  # 使用默认值
    "role": "tester"
}
```

### ApiDefinition中的路径参数

```python
# API定义
api_def = ApiDefinition(
    name="获取用户信息",
    method=HttpMethod.GET,
    path="/api/users/{id}/orders/{order_id}",
    path_parameters={
        "id": {"type": "integer", "description": "用户ID"},
        "order_id": {"type": "integer", "description": "订单ID"}
    }
)

# 执行时的参数
params = {
    "id": 123,
    "order_id": 456
}

# 替换后的实际路径
actual_path = "/api/users/123/orders/456"
```

## 第二层：脚本层的数据管理

### 脚本参数定义

```python
# 脚本定义
script = TestScript(
    name="测试获取用户信息",
    api_definition_id=1,
    script_content="""
# 使用参数
user_id = params.get('user_id')
expected_name = params.get('expected_name', '默认名称')

# 发送请求
response = api.send_request(user_id=user_id)

# 验证
assert response.status_code == 200
assert response.json()['name'] == expected_name
    """,
    variables={
        "default_timeout": 30,
        "max_retries": 3
    }
)

# 脚本参数定义
param1 = ScriptParameter(
    script_id=script.id,
    name="user_id",
    param_type="integer",
    is_required=True,
    validation_rule={"min": 1, "max": 999999}
)

param2 = ScriptParameter(
    script_id=script.id,
    name="expected_name",
    param_type="string",
    default_value="张三",
    is_required=False
)
```

### 脚本执行时的参数合并

```python
# 执行上下文构建
class ScriptExecutionContext:
    def __init__(self, script, override_params=None):
        self.params = {}
        
        # 1. 加载脚本默认参数
        for param in script.parameters:
            if param.default_value:
                self.params[param.name] = param.default_value
        
        # 2. 加载脚本变量
        if script.variables:
            self.params.update(script.variables)
        
        # 3. 应用覆盖参数（来自组件或测试用例）
        if override_params:
            self.params.update(override_params)
    
    def get(self, key, default=None):
        return self.params.get(key, default)
```

## 第三层：组件层的数据管理

### 组件共享变量

```python
# 组件定义
component = TestComponent(
    name="用户管理完整流程",
    shared_variables={
        "base_url": "https://api.example.com",
        "timeout": 30,
        "created_user_id": None  # 将在执行过程中填充
    }
)

# 组件包含的脚本
comp_script1 = ComponentScript(
    component_id=component.id,
    script_id=1,  # 创建用户脚本
    execution_order=1,
    script_parameters={
        "user_name": "测试用户",
        "user_email": "test@example.com"
    }
)

comp_script2 = ComponentScript(
    component_id=component.id,
    script_id=2,  # 查询用户脚本
    execution_order=2,
    script_parameters={
        "user_id": "${created_user_id}"  # 引用第一个脚本的结果
    }
)
```

### 组件执行时的变量共享

```python
class ComponentExecutionContext:
    def __init__(self, component, override_params=None):
        # 初始化共享变量
        self.shared_vars = component.shared_variables.copy() if component.shared_variables else {}
        
        # 应用覆盖参数
        if override_params:
            self.shared_vars.update(override_params)
        
        # 执行结果存储
        self.script_results = {}
    
    def execute_script(self, comp_script):
        # 构建脚本参数
        script_params = self.shared_vars.copy()
        
        # 应用脚本级别的参数覆盖
        if comp_script.script_parameters:
            # 替换变量引用
            resolved_params = self._resolve_variables(comp_script.script_parameters)
            script_params.update(resolved_params)
        
        # 执行脚本
        result = execute_script(comp_script.script, script_params)
        
        # 保存结果到共享变量
        self.script_results[comp_script.script.name] = result
        
        # 如果脚本返回了新变量，更新共享变量
        if result.get('output_variables'):
            self.shared_vars.update(result['output_variables'])
        
        return result
    
    def _resolve_variables(self, params):
        """解析参数中的变量引用"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                var_name = value[2:-1]
                resolved[key] = self.shared_vars.get(var_name, value)
            else:
                resolved[key] = value
        return resolved
```

## 第四层：测试用例层的数据管理

### 测试用例数据定义

```python
# 测试用例定义
test_case = TestCase(
    name="用户注册登录完整流程测试",
    test_data={
        # 全局测试数据
        "base_url": "https://test.example.com",
        "environment": "test",
        
        # 用户数据
        "user_name": "测试用户",
        "user_email": "test@example.com",
        "user_password": "Test@123",
        
        # 预期结果
        "expected_status": "active",
        "expected_role": "tester"
    },
    environment="test"
)

# 测试用例引用脚本
case_script1 = TestCaseScript(
    test_case_id=test_case.id,
    script_id=1,
    execution_order=1,
    script_parameters={
        "user_name": "${user_name}",
        "user_email": "${user_email}"
    }
)

# 测试用例引用组件
case_component1 = TestCaseComponent(
    test_case_id=test_case.id,
    component_id=1,
    execution_order=2,
    component_parameters={
        "base_url": "${base_url}",
        "timeout": 60  # 覆盖组件的默认超时
    }
)
```

### 测试用例执行时的参数合并

```python
class TestCaseExecutionContext:
    def __init__(self, test_case, runtime_params=None):
        # 1. 加载环境配置（最低优先级）
        self.env_config = load_environment_config(test_case.environment)
        
        # 2. 初始化参数字典，从环境配置开始
        self.params = self.env_config.copy()
        
        # 3. 加载测试用例数据（覆盖环境配置）
        if test_case.test_data:
            self.params.update(test_case.test_data)
        
        # 4. 应用运行时参数（最高优先级，覆盖所有）
        if runtime_params:
            self.params.update(runtime_params)
        
        # 执行历史
        self.execution_history = []
    
    def execute_script(self, case_script):
        # 构建脚本参数：从测试用例参数开始
        script_params = self.params.copy()
        
        # 如果测试用例级别指定了脚本参数，覆盖上面的值
        if case_script.script_parameters:
            resolved_params = self._resolve_variables(case_script.script_parameters)
            # 只覆盖指定的参数，未指定的保持测试用例的值
            script_params.update(resolved_params)
        
        # 执行脚本
        result = execute_script(case_script.script, script_params)
        
        # 保存执行历史
        self.execution_history.append({
            'type': 'script',
            'name': case_script.script.name,
            'result': result
        })
        
        # 更新上下文变量（脚本输出的变量添加到上下文）
        if result.get('output_variables'):
            self.params.update(result['output_variables'])
        
        return result
    
    def execute_component(self, case_component):
        # 构建组件参数：从测试用例参数开始
        component_params = self.params.copy()
        
        # 如果测试用例级别指定了组件参数，覆盖上面的值
        if case_component.component_parameters:
            resolved_params = self._resolve_variables(case_component.component_parameters)
            # 只覆盖指定的参数，未指定的保持测试用例的值
            component_params.update(resolved_params)
        
        # 创建组件执行上下文
        comp_context = ComponentExecutionContext(
            case_component.component,
            component_params
        )
        
        # 执行组件
        result = comp_context.execute()
        
        # 保存执行历史
        self.execution_history.append({
            'type': 'component',
            'name': case_component.component.name,
            'result': result
        })
        
        # 更新上下文变量（组件输出的变量添加到上下文）
        if result.get('output_variables'):
            self.params.update(result['output_variables'])
        
        return result
```

## 环境配置管理

### 环境配置文件结构

```toml
# config/test.toml
[environment]
name = "test"
description = "测试环境"

[api]
base_url = "https://test-api.example.com"
timeout = 30
retry_count = 3

[auth]
token_url = "https://test-auth.example.com/token"
client_id = "test_client_id"
client_secret = "test_client_secret"

[database]
host = "test-db.example.com"
port = 5432
database = "morado_test"

[variables]
default_user_role = "tester"
max_upload_size = 10485760  # 10MB
```

```toml
# config/production.toml
[environment]
name = "production"
description = "生产环境"

[api]
base_url = "https://api.example.com"
timeout = 60
retry_count = 5

[auth]
token_url = "https://auth.example.com/token"
client_id = "prod_client_id"
client_secret = "prod_client_secret"

[database]
host = "prod-db.example.com"
port = 5432
database = "morado_prod"

[variables]
default_user_role = "viewer"
max_upload_size = 52428800  # 50MB
```

### 环境配置加载

```python
class EnvironmentConfig:
    def __init__(self, environment_name):
        self.name = environment_name
        self.config = self._load_config()
    
    def _load_config(self):
        """加载环境配置文件"""
        config_path = f"config/{self.name}.toml"
        with open(config_path, 'r') as f:
            return toml.load(f)
    
    def get(self, key, default=None):
        """获取配置值，支持点号路径"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def to_dict(self):
        """转换为扁平字典，用于变量替换"""
        flat_dict = {}
        
        def flatten(d, prefix=''):
            for k, v in d.items():
                key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    flatten(v, key)
                else:
                    flat_dict[key] = v
        
        flatten(self.config)
        return flat_dict
```

## 完整执行流程示例

### 场景：用户注册登录测试

```python
# 1. 定义测试用例
test_case = TestCase(
    name="用户注册登录测试",
    environment="test",
    test_data={
        "user_name": "测试用户${timestamp}",
        "user_email": "test${timestamp}@example.com",
        "user_password": "Test@123",
        "timeout": 30  # 测试用例级别的超时设置
    }
)

# 2. 执行测试用例
def execute_test_case(test_case, runtime_params=None):
    # 创建执行上下文
    context = TestCaseExecutionContext(test_case, runtime_params)
    
    # 参数合并顺序：
    # 1. 环境配置: {api.base_url: "https://test.example.com", timeout: 60}
    # 2. 测试用例数据覆盖: {timeout: 30}  # 覆盖环境的60
    # 3. 运行时参数覆盖: {user_password: "Runtime@456"}  # 覆盖测试用例的Test@123
    
    # 最终参数:
    # {
    #   api.base_url: "https://test.example.com",  # 来自环境
    #   timeout: 30,  # 来自测试用例（覆盖了环境的60）
    #   user_name: "测试用户1703001234",  # 来自测试用例
    #   user_email: "test1703001234@example.com",  # 来自测试用例
    #   user_password: "Runtime@456"  # 来自运行时（覆盖了测试用例的Test@123）
    # }
    
    # 添加时间戳
    context.params['timestamp'] = int(time.time())
    
    # 解析所有变量引用
    context.params = resolve_all_variables(context.params)
    
    print(f"执行环境: {test_case.environment}")
    print(f"基础URL: {context.params.get('api.base_url')}")
    print(f"超时时间: {context.params.get('timeout')} (来自测试用例，覆盖了环境配置)")
    print(f"用户名: {context.params.get('user_name')}")
    print(f"邮箱: {context.params.get('user_email')}")
    print(f"密码: {context.params.get('user_password')} (来自运行时，覆盖了测试用例)")
    
    # 按顺序执行脚本和组件
    items = []
    items.extend([(s.execution_order, 'script', s) for s in test_case.test_case_scripts])
    items.extend([(c.execution_order, 'component', c) for c in test_case.test_case_components])
    items.sort(key=lambda x: x[0])
    
    results = []
    for order, item_type, item in items:
        if item_type == 'script':
            result = context.execute_script(item)
        else:
            result = context.execute_component(item)
        
        results.append(result)
        
        # 如果失败且不继续执行，则停止
        if not result['success'] and not test_case.continue_on_failure:
            break
    
    return {
        'success': all(r['success'] for r in results),
        'results': results,
        'context': context.params
    }

# 3. 运行测试
result = execute_test_case(
    test_case,
    runtime_params={
        'user_password': 'CustomPassword@456'  # 覆盖测试用例的密码
    }
)
```

### 参数覆盖示例

假设有以下配置：

```python
# 环境配置 (config/test.toml)
{
    "api": {"base_url": "https://test.example.com"},
    "timeout": 60,
    "retry_count": 5
}

# 测试用例数据
test_case.test_data = {
    "timeout": 30,  # 覆盖环境的60
    "user_name": "张三"
}

# 组件共享变量
component.shared_variables = {
    "retry_count": 3,  # 覆盖环境的5
    "user_role": "tester"
}

# 脚本变量
script.variables = {
    "expected_status": 200
}

# 运行时参数
runtime_params = {
    "timeout": 45,  # 覆盖测试用例的30
    "user_name": "李四"  # 覆盖测试用例的"张三"
}
```

**最终参数（按优先级合并）：**

```python
{
    "api.base_url": "https://test.example.com",  # 来自环境（无覆盖）
    "timeout": 45,  # 来自运行时（覆盖了测试用例的30和环境的60）
    "retry_count": 3,  # 来自组件（覆盖了环境的5）
    "user_name": "李四",  # 来自运行时（覆盖了测试用例的"张三"）
    "user_role": "tester",  # 来自组件（无覆盖）
    "expected_status": 200  # 来自脚本（无覆盖）
}
```

**覆盖路径：**
- `timeout`: 环境(60) → 测试用例(30) → 运行时(45) ✓
- `retry_count`: 环境(5) → 组件(3) ✓
- `user_name`: 测试用例("张三") → 运行时("李四") ✓
- `api.base_url`: 环境("https://test.example.com") ✓ (无覆盖)
- `user_role`: 组件("tester") ✓ (无覆盖)
- `expected_status`: 脚本(200) ✓ (无覆盖)

### 输出示例

```
执行环境: test
基础URL: https://test-api.example.com
用户名: 测试用户1703001234
邮箱: test1703001234@example.com

[脚本1] 用户注册
  参数: {user_name: "测试用户1703001234", user_email: "test1703001234@example.com", user_password: "CustomPassword@456"}
  结果: 成功
  输出变量: {user_id: 12345, token: "eyJhbGc..."}

[脚本2] 用户登录
  参数: {user_email: "test1703001234@example.com", user_password: "CustomPassword@456"}
  结果: 成功
  输出变量: {session_id: "sess_abc123"}

[组件1] 用户信息验证
  参数: {user_id: 12345, token: "eyJhbGc..."}
  结果: 成功
  
测试用例执行完成: 成功
```

## 变量替换规则

### 基本语法

```
${variable_name}              # 简单变量引用
${variable_name:default}      # 带默认值的变量引用
${env.api.base_url}          # 环境配置引用（点号路径）
${script.output.user_id}     # 脚本输出引用
```

### 替换优先级

1. **运行时参数**: 执行时传入的参数
2. **测试用例数据**: test_case.test_data
3. **组件共享变量**: component.shared_variables
4. **脚本变量**: script.variables
5. **环境配置**: 从环境配置文件加载
6. **默认值**: 变量定义中的默认值

### 特殊变量

```python
# 系统内置变量
${timestamp}           # 当前时间戳
${date}               # 当前日期 (YYYY-MM-DD)
${datetime}           # 当前日期时间 (YYYY-MM-DD HH:MM:SS)
${uuid}               # 随机UUID
${random_int}         # 随机整数
${random_string}      # 随机字符串
${environment}        # 当前环境名称
```

## 最佳实践

### 1. 参数命名规范

```python
# 好的命名
user_id, user_name, user_email
api_base_url, api_timeout
expected_status_code, expected_response_time

# 避免的命名
id, name, url  # 太通用
x, y, temp     # 无意义
```

### 2. 使用环境配置

```python
# 将环境相关的配置放在环境文件中
# config/test.toml
[api]
base_url = "https://test-api.example.com"

# 在测试用例中引用
test_case = TestCase(
    test_data={
        "base_url": "${env.api.base_url}"  # 从环境配置读取
    }
)
```

### 3. 合理使用默认值

```python
# 在脚本参数中定义默认值
param = ScriptParameter(
    name="timeout",
    default_value="30",
    description="请求超时时间（秒）"
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
    "created_user_id": None,
    "created_order_id": None
}

# 脚本级别：脚本私有
script.variables = {
    "retry_count": 3,
    "expected_status": 200
}
```

### 5. 输出变量传递

```python
# 脚本1：创建用户，输出user_id
script1_result = {
    'success': True,
    'output_variables': {
        'created_user_id': 12345
    }
}

# 脚本2：使用script1的输出
script2_params = {
    'user_id': '${created_user_id}'  # 引用上一个脚本的输出
}
```

## 总结

Morado测试平台的数据管理机制提供了：

1. **灵活的参数传递**: 支持多层参数覆盖和变量引用
2. **环境隔离**: 通过环境配置文件管理不同环境的差异
3. **变量共享**: 支持脚本间、组件间的变量传递
4. **默认值机制**: 多层默认值保证系统的健壮性
5. **运行时覆盖**: 支持执行时动态修改参数

这种设计确保了测试的灵活性、可维护性和可复用性。
