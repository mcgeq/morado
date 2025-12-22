# Morado 测试平台四层架构设计

## 概述

Morado测试平台采用四层架构设计，从底层的接口定义到顶层的测试用例，每一层都有明确的职责和可复用性。

## 四层架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    第四层：测试用例层 (Test Case)                  │
│  - 用户直接操作的测试单元                                          │
│  - 可以引用脚本或联合组件                                          │
│  - 支持执行顺序配置和参数覆盖                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │ 引用
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  第三层：联合组件层 (Component)                    │
│  - 多个脚本的组合                                                 │
│  - 可以嵌套引用其他组件                                           │
│  - 支持独立调试执行                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │ 引用
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    第二层：脚本层 (Script)                        │
│  - 接口的实际实现和调试层                                         │
│  - 引用API定义并添加测试逻辑                                      │
│  - 支持前置/主/后置脚本                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │ 引用
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 第一层：接口定义层 (API Definition)                │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────┐        │
│  │  Header  │───▶│   Body   │───▶│  API Definition    │        │
│  │  组件    │    │   组件   │    │  (引用或内联)       │        │
│  └──────────┘    └──────────┘    └────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 第一层：接口定义层

### Header 组件
**职责：** 管理可复用的HTTP请求头

**特性：**
- 独立管理和存储
- 支持全局Header（所有接口可用）
- 支持项目级Header（特定项目可用）

**示例：**
```json
{
  "name": "认证Header",
  "headers": {
    "Authorization": "Bearer ${token}",
    "X-API-Key": "${api_key}"
  },
  "is_global": true
}
```

### Body 组件
**职责：** 管理可复用的请求/响应体模板

**特性：**
- 独立管理和存储
- 支持JSON Schema定义
- 支持示例数据
- 区分请求Body和响应Body

**示例：**
```json
{
  "name": "用户信息Body",
  "body_type": "request",
  "content_type": "application/json",
  "body_schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "age": {"type": "integer"}
    }
  },
  "example_data": {
    "name": "张三",
    "age": 25
  }
}
```

### API Definition
**职责：** 定义完整的API接口

**两种组合方式：**

#### 方式1：引用Header和Body组件
```json
{
  "name": "获取用户信息",
  "method": "GET",
  "path": "/api/users/{id}",
  "header_id": 1,           // 引用认证Header
  "response_body_id": 2     // 引用用户信息Body
}
```

#### 方式2：引用Header + 自定义Body
```json
{
  "name": "创建用户",
  "method": "POST",
  "path": "/api/users",
  "header_id": 1,           // 引用认证Header
  "inline_request_body": {  // 自定义请求体
    "name": "李四",
    "age": 30
  }
}
```

## 第二层：脚本层

### Test Script
**职责：** 接口的实际实现和测试逻辑

**特性：**
- 引用API Definition
- 支持多种脚本语言（Python、JavaScript、Groovy）
- 支持前置/主/后置脚本
- 支持断言和验证器
- 支持独立调试执行

**示例：**
```python
# 脚本内容
response = api.send_request(user_id=123)

# 断言
assert response.status_code == 200
assert response.json()["name"] == "张三"
```

**关联关系：**
```
TestScript
  ├─ api_definition_id → ApiDefinition
  ├─ script_content (实际代码)
  ├─ assertions (断言规则)
  └─ parameters (脚本参数)
```

## 第三层：联合组件层

### Test Component
**职责：** 多个脚本的组合，支持嵌套

**特性：**
- 包含多个脚本
- 可以引用其他组件（嵌套）
- 支持独立调试执行
- 支持执行顺序配置
- 支持变量共享

**示例：用户管理完整流程**
```
TestComponent: "用户管理完整流程"
  ├─ Script 1: 创建用户
  ├─ Script 2: 查询用户
  ├─ Script 3: 更新用户
  └─ Script 4: 删除用户
```

**嵌套示例：**
```
TestComponent: "完整业务流程"
  ├─ Component 1: 用户管理完整流程
  │   ├─ Script 1: 创建用户
  │   ├─ Script 2: 查询用户
  │   └─ ...
  ├─ Component 2: 订单管理完整流程
  │   ├─ Script 5: 创建订单
  │   ├─ Script 6: 查询订单
  │   └─ ...
  └─ Script 7: 生成报告
```

**关联关系：**
```
TestComponent
  ├─ parent_component_id → TestComponent (自引用，支持嵌套)
  └─ ComponentScript (关联表)
      ├─ component_id → TestComponent
      ├─ script_id → TestScript
      ├─ execution_order (执行顺序)
      └─ script_parameters (参数覆盖)
```

## 第四层：测试用例层

### Test Case
**职责：** 用户直接操作的测试单元

**特性：**
- 可以引用脚本
- 可以引用联合组件
- 支持混合引用（既有脚本又有组件）
- 支持执行顺序配置
- 支持参数覆盖

**示例：**
```
TestCase: "用户注册登录完整流程测试"
  ├─ Script 1: 用户注册
  ├─ Component 1: 用户管理完整流程
  │   ├─ Script 2: 创建用户
  │   ├─ Script 3: 查询用户
  │   └─ ...
  └─ Script 8: 用户登录
```

**关联关系：**
```
TestCase
  ├─ TestCaseScript (关联表)
  │   ├─ test_case_id → TestCase
  │   ├─ script_id → TestScript
  │   ├─ execution_order
  │   └─ script_parameters
  └─ TestCaseComponent (关联表)
      ├─ test_case_id → TestCase
      ├─ component_id → TestComponent
      ├─ execution_order
      └─ component_parameters
```

## 数据流示例

### 完整的测试流程

```
1. 创建Header组件
   └─ "认证Header" (Authorization: Bearer ${token})

2. 创建Body组件
   └─ "用户信息Body" (name, age, email)

3. 创建API定义
   └─ "获取用户API" (引用Header + Body)

4. 创建脚本
   └─ "测试获取用户" (引用API定义 + 添加断言)

5. 创建组件
   └─ "用户管理流程" (包含多个脚本)
       ├─ 创建用户脚本
       ├─ 获取用户脚本
       └─ 删除用户脚本

6. 创建测试用例
   └─ "用户完整测试" (引用组件 + 额外脚本)
       ├─ 用户管理流程组件
       └─ 用户登录脚本

7. 执行测试用例
   └─ 按顺序执行所有脚本和组件
```

## 复用机制

### Header和Body的复用
```
Header "认证Header"
  ├─ 被 API定义1 引用
  ├─ 被 API定义2 引用
  └─ 被 API定义3 引用

Body "用户信息Body"
  ├─ 被 API定义1 引用
  └─ 被 API定义4 引用
```

### 组件的嵌套复用
```
Component "基础用户操作"
  ├─ Script: 创建用户
  └─ Script: 删除用户

Component "完整用户流程" (引用基础组件)
  ├─ Component: 基础用户操作
  ├─ Script: 查询用户
  └─ Script: 更新用户

TestCase "用户测试" (引用完整流程)
  ├─ Component: 完整用户流程
  └─ Script: 验证结果
```

## 优势

1. **高度复用**：Header、Body、脚本、组件都可以复用
2. **灵活组合**：API定义支持引用或内联，组件支持嵌套
3. **独立调试**：每一层都可以独立调试执行
4. **清晰层次**：职责明确，易于维护
5. **参数覆盖**：每一层都支持参数覆盖，灵活性高

## 数据库表关系

```sql
-- 第一层
headers (id, name, headers, is_global)
bodies (id, name, body_type, body_schema, example_data)
api_definitions (id, name, method, path, header_id, request_body_id, response_body_id, inline_request_body, inline_response_body)

-- 第二层
test_scripts (id, name, api_definition_id, script_content, assertions)
script_parameters (id, script_id, name, param_type, default_value)

-- 第三层
test_components (id, name, parent_component_id, execution_order)
component_scripts (id, component_id, script_id, execution_order, script_parameters)

-- 第四层
test_cases (id, name, priority, status)
test_case_scripts (id, test_case_id, script_id, execution_order, script_parameters)
test_case_components (id, test_case_id, component_id, execution_order, component_parameters)
```

## 使用建议

1. **从底层开始**：先创建Header和Body组件，再创建API定义
2. **逐层构建**：先创建脚本，再组合成组件，最后创建测试用例
3. **充分复用**：尽量使用全局Header和Body，减少重复定义
4. **合理嵌套**：组件嵌套不要超过3层，保持结构清晰
5. **参数化**：使用参数和变量，提高脚本和组件的通用性
