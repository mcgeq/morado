# Morado 四层架构使用指南

本指南详细介绍如何使用 Morado 测试平台的四层架构来创建和管理测试用例。

## 目录

1. [概述](#概述)
2. [第一层：接口定义层](#第一层接口定义层)
   - [创建和管理 Header 组件](#创建和管理-header-组件)
   - [创建和管理 Body 组件](#创建和管理-body-组件)
   - [创建 API 定义](#创建-api-定义)
3. [第二层：脚本层](#第二层脚本层)
   - [编写测试脚本](#编写测试脚本)
   - [调试脚本](#调试脚本)
4. [第三层：联合组件层](#第三层联合组件层)
   - [创建组件](#创建组件)
   - [组件嵌套](#组件嵌套)
5. [第四层：测试用例层](#第四层测试用例层)
   - [创建测试用例](#创建测试用例)
   - [引用脚本和组件](#引用脚本和组件)
6. [完整示例流程](#完整示例流程)
7. [最佳实践](#最佳实践)

## 概述

Morado 的四层架构从底层到顶层依次为：

1. **接口定义层** - Header、Body、API Definition
2. **脚本层** - TestScript
3. **联合组件层** - TestComponent
4. **测试用例层** - TestCase

每一层都可以独立管理和复用，上层可以引用下层的资源。

## 第一层：接口定义层

### 创建和管理 Header 组件

Header 组件用于管理可复用的 HTTP 请求头。

#### 创建 Header

**API 请求：**
```http
POST /api/v1/headers
Content-Type: application/json

{
  "name": "认证Header",
  "description": "包含 Bearer Token 的认证头",
  "headers": {
    "Authorization": "Bearer ${token}",
    "X-API-Key": "${api_key}"
  },
  "is_global": true
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | Header 组件名称 |
| description | string | 否 | 描述信息 |
| headers | object | 是 | HTTP 请求头键值对 |
| is_global | boolean | 否 | 是否全局可用，默认 false |
| project_id | uuid | 否 | 所属项目 ID |

#### Header 类型示例

**1. 认证 Header：**
```json
{
  "name": "JWT认证",
  "headers": {
    "Authorization": "Bearer ${jwt_token}"
  },
  "is_global": true
}
```

**2. 内容类型 Header：**
```json
{
  "name": "JSON内容类型",
  "headers": {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  "is_global": true
}
```

**3. 自定义 Header：**
```json
{
  "name": "追踪Header",
  "headers": {
    "X-Request-ID": "${request_id}",
    "X-Trace-ID": "${trace_id}"
  }
}
```

#### 查询 Header

```http
# 获取所有 Header
GET /api/v1/headers

# 获取单个 Header
GET /api/v1/headers/{id}

# 获取全局 Header
GET /api/v1/headers?is_global=true
```

### 创建和管理 Body 组件

Body 组件用于管理可复用的请求/响应体模板。

#### 创建 Body

**API 请求：**
```http
POST /api/v1/bodies
Content-Type: application/json

{
  "name": "用户信息Body",
  "description": "用户基本信息的请求体",
  "body_type": "request",
  "content_type": "application/json",
  "body_schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string", "description": "用户名"},
      "age": {"type": "integer", "minimum": 0},
      "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
  },
  "example_data": {
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com"
  }
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | Body 组件名称 |
| description | string | 否 | 描述信息 |
| body_type | string | 是 | 类型：request 或 response |
| content_type | string | 是 | 内容类型，如 application/json |
| body_schema | object | 否 | JSON Schema 定义 |
| example_data | object | 否 | 示例数据 |

#### Body 类型示例

**1. 请求 Body：**
```json
{
  "name": "创建订单请求",
  "body_type": "request",
  "content_type": "application/json",
  "body_schema": {
    "type": "object",
    "properties": {
      "items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "product_id": {"type": "string"},
            "quantity": {"type": "integer"}
          }
        }
      },
      "shipping_address": {"type": "string"}
    }
  },
  "example_data": {
    "items": [
      {"product_id": "P001", "quantity": 2}
    ],
    "shipping_address": "北京市朝阳区"
  }
}
```

**2. 响应 Body：**
```json
{
  "name": "用户列表响应",
  "body_type": "response",
  "content_type": "application/json",
  "body_schema": {
    "type": "object",
    "properties": {
      "total": {"type": "integer"},
      "items": {"type": "array"},
      "page": {"type": "integer"}
    }
  }
}
```

### 创建 API 定义

API 定义是完整的接口描述，可以引用 Header 和 Body 组件。

#### 方式一：引用 Header 和 Body 组件

```http
POST /api/v1/api-definitions
Content-Type: application/json

{
  "name": "获取用户信息",
  "description": "根据用户ID获取用户详细信息",
  "method": "GET",
  "path": "/api/users/{user_id}",
  "header_id": "uuid-of-auth-header",
  "response_body_id": "uuid-of-user-response-body",
  "path_parameters": {
    "user_id": {
      "type": "string",
      "description": "用户ID"
    }
  },
  "query_parameters": {
    "include_details": {
      "type": "boolean",
      "default": false
    }
  }
}
```

#### 方式二：引用 Header + 内联 Body

```http
POST /api/v1/api-definitions
Content-Type: application/json

{
  "name": "创建用户",
  "method": "POST",
  "path": "/api/users",
  "header_id": "uuid-of-auth-header",
  "inline_request_body": {
    "name": "${user_name}",
    "email": "${user_email}",
    "role": "user"
  },
  "inline_response_body": {
    "id": "${generated_id}",
    "name": "${user_name}",
    "created_at": "${timestamp}"
  }
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | API 名称 |
| method | string | 是 | HTTP 方法 |
| path | string | 是 | 请求路径 |
| header_id | uuid | 否 | 引用的 Header 组件 ID |
| request_body_id | uuid | 否 | 引用的请求 Body 组件 ID |
| response_body_id | uuid | 否 | 引用的响应 Body 组件 ID |
| inline_request_body | object | 否 | 内联请求体 |
| inline_response_body | object | 否 | 内联响应体 |

## 第二层：脚本层

### 编写测试脚本

脚本是接口的实际实现和测试逻辑。

#### 创建脚本

```http
POST /api/v1/scripts
Content-Type: application/json

{
  "name": "测试获取用户信息",
  "description": "验证获取用户信息接口的正确性",
  "api_definition_id": "uuid-of-api-definition",
  "script_type": "main",
  "script_language": "python",
  "script_content": "# 发送请求\nresponse = api.send_request(user_id=user_id)\n\n# 验证响应\nassert response.status_code == 200\nassert response.json()['name'] == expected_name",
  "assertions": [
    {
      "type": "status_code",
      "expected": 200
    },
    {
      "type": "json_path",
      "path": "$.name",
      "operator": "equals",
      "expected": "${expected_name}"
    }
  ],
  "parameters": [
    {
      "name": "user_id",
      "param_type": "string",
      "required": true,
      "description": "要查询的用户ID"
    },
    {
      "name": "expected_name",
      "param_type": "string",
      "required": true,
      "description": "期望的用户名"
    }
  ]
}
```

**脚本类型：**

| 类型 | 说明 |
|------|------|
| pre | 前置脚本，在主脚本之前执行 |
| main | 主脚本，核心测试逻辑 |
| post | 后置脚本，在主脚本之后执行 |

#### 断言类型

```json
{
  "assertions": [
    {
      "type": "status_code",
      "expected": 200
    },
    {
      "type": "json_path",
      "path": "$.data.id",
      "operator": "exists"
    },
    {
      "type": "json_path",
      "path": "$.data.name",
      "operator": "equals",
      "expected": "张三"
    },
    {
      "type": "json_path",
      "path": "$.data.age",
      "operator": "greater_than",
      "expected": 18
    },
    {
      "type": "response_time",
      "operator": "less_than",
      "expected": 1000
    },
    {
      "type": "header",
      "name": "Content-Type",
      "operator": "contains",
      "expected": "application/json"
    }
  ]
}
```

### 调试脚本

脚本支持独立调试执行。

#### 执行单个脚本

```http
POST /api/v1/scripts/{script_id}/execute
Content-Type: application/json

{
  "parameters": {
    "user_id": "12345",
    "expected_name": "张三"
  },
  "environment": "development"
}
```

**响应：**
```json
{
  "execution_id": "exec-uuid",
  "status": "success",
  "duration_ms": 156,
  "request": {
    "method": "GET",
    "url": "https://api.example.com/api/users/12345",
    "headers": {...}
  },
  "response": {
    "status_code": 200,
    "headers": {...},
    "body": {...}
  },
  "assertions_result": [
    {"type": "status_code", "passed": true},
    {"type": "json_path", "path": "$.name", "passed": true}
  ]
}
```

## 第三层：联合组件层

### 创建组件

组件是多个脚本的组合。

#### 创建组件

```http
POST /api/v1/components
Content-Type: application/json

{
  "name": "用户管理完整流程",
  "description": "包含用户CRUD的完整测试流程",
  "scripts": [
    {
      "script_id": "uuid-of-create-user-script",
      "execution_order": 1,
      "parameters": {
        "user_name": "测试用户"
      }
    },
    {
      "script_id": "uuid-of-get-user-script",
      "execution_order": 2,
      "parameters": {
        "user_id": "${created_user_id}"
      }
    },
    {
      "script_id": "uuid-of-update-user-script",
      "execution_order": 3
    },
    {
      "script_id": "uuid-of-delete-user-script",
      "execution_order": 4
    }
  ],
  "shared_variables": {
    "base_url": "https://api.example.com"
  }
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 组件名称 |
| description | string | 否 | 描述信息 |
| scripts | array | 是 | 包含的脚本列表 |
| shared_variables | object | 否 | 组件内共享变量 |
| parent_component_id | uuid | 否 | 父组件 ID（用于嵌套） |

### 组件嵌套

组件可以引用其他组件，实现复杂流程的组合。

#### 创建嵌套组件

```http
POST /api/v1/components
Content-Type: application/json

{
  "name": "完整业务流程测试",
  "description": "包含用户管理和订单管理的完整业务流程",
  "children": [
    {
      "component_id": "uuid-of-user-management-component",
      "execution_order": 1,
      "parameters": {
        "environment": "staging"
      }
    },
    {
      "component_id": "uuid-of-order-management-component",
      "execution_order": 2
    }
  ],
  "scripts": [
    {
      "script_id": "uuid-of-report-script",
      "execution_order": 3
    }
  ]
}
```

#### 执行组件

```http
POST /api/v1/components/{component_id}/execute
Content-Type: application/json

{
  "parameters": {
    "environment": "development"
  }
}
```

## 第四层：测试用例层

### 创建测试用例

测试用例是用户直接操作的测试单元。

#### 创建测试用例

```http
POST /api/v1/test-cases
Content-Type: application/json

{
  "name": "用户注册登录完整流程测试",
  "description": "验证用户从注册到登录的完整流程",
  "priority": "high",
  "tags": ["用户", "认证", "冒烟测试"],
  "test_data": {
    "user_name": "测试用户",
    "user_email": "test@example.com",
    "password": "Test123456"
  }
}
```

### 引用脚本和组件

测试用例可以引用脚本和组件。

#### 添加脚本引用

```http
POST /api/v1/test-cases/{test_case_id}/scripts
Content-Type: application/json

{
  "script_id": "uuid-of-register-script",
  "execution_order": 1,
  "parameters": {
    "user_name": "${test_data.user_name}"
  }
}
```

#### 添加组件引用

```http
POST /api/v1/test-cases/{test_case_id}/components
Content-Type: application/json

{
  "component_id": "uuid-of-user-verification-component",
  "execution_order": 2,
  "parameters": {
    "user_id": "${registered_user_id}"
  }
}
```

#### 执行测试用例

```http
POST /api/v1/test-cases/{test_case_id}/execute
Content-Type: application/json

{
  "runtime_parameters": {
    "environment": "staging",
    "timeout": 30000
  }
}
```

## 完整示例流程

以下是创建一个完整测试用例的步骤示例：

### 步骤 1：创建 Header 组件

```http
POST /api/v1/headers
{
  "name": "API认证Header",
  "headers": {
    "Authorization": "Bearer ${token}",
    "Content-Type": "application/json"
  },
  "is_global": true
}
```

### 步骤 2：创建 Body 组件

```http
POST /api/v1/bodies
{
  "name": "用户注册请求Body",
  "body_type": "request",
  "content_type": "application/json",
  "body_schema": {
    "type": "object",
    "properties": {
      "username": {"type": "string"},
      "email": {"type": "string"},
      "password": {"type": "string"}
    }
  }
}
```

### 步骤 3：创建 API 定义

```http
POST /api/v1/api-definitions
{
  "name": "用户注册API",
  "method": "POST",
  "path": "/api/auth/register",
  "header_id": "header-uuid",
  "request_body_id": "body-uuid"
}
```

### 步骤 4：创建测试脚本

```http
POST /api/v1/scripts
{
  "name": "用户注册测试",
  "api_definition_id": "api-def-uuid",
  "script_type": "main",
  "script_content": "response = api.send_request()\nassert response.status_code == 201",
  "assertions": [
    {"type": "status_code", "expected": 201}
  ],
  "parameters": [
    {"name": "username", "param_type": "string", "required": true},
    {"name": "email", "param_type": "string", "required": true},
    {"name": "password", "param_type": "string", "required": true}
  ]
}
```

### 步骤 5：创建组件

```http
POST /api/v1/components
{
  "name": "用户注册流程",
  "scripts": [
    {"script_id": "register-script-uuid", "execution_order": 1}
  ]
}
```

### 步骤 6：创建测试用例

```http
POST /api/v1/test-cases
{
  "name": "用户注册功能测试",
  "priority": "high",
  "test_data": {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123"
  }
}

# 添加组件引用
POST /api/v1/test-cases/{id}/components
{
  "component_id": "component-uuid",
  "execution_order": 1
}
```

### 步骤 7：执行测试

```http
POST /api/v1/test-cases/{id}/execute
{
  "runtime_parameters": {
    "environment": "development"
  }
}
```

## 最佳实践

### 1. Header 和 Body 复用

- 创建全局通用的 Header（如认证、内容类型）
- 按业务领域组织 Body 组件
- 使用变量替换实现动态值

### 2. 脚本设计

- 保持脚本单一职责
- 使用参数化提高复用性
- 合理使用前置/后置脚本

### 3. 组件组织

- 按业务流程组织组件
- 控制嵌套层级（建议不超过 3 层）
- 使用共享变量传递数据

### 4. 测试用例管理

- 使用标签分类测试用例
- 设置合理的优先级
- 维护测试数据的独立性

### 5. 变量使用

```
# 变量语法
${variable}              # 简单变量
${variable:default}      # 带默认值
${env.api.base_url}      # 环境配置

# 内置变量
${timestamp}             # 当前时间戳
${uuid}                  # 随机 UUID
${date}                  # 当前日期
${random_int}            # 随机整数
```

### 6. 参数优先级

参数从上层向下层传递，上层覆盖下层：

1. 运行时参数（最高优先级）
2. 测试用例数据
3. 组件共享变量
4. 脚本变量
5. 脚本参数默认值
6. 环境配置（最低优先级）

## 相关文档

- [架构设计](architecture.md)
- [四层架构详细设计](four-layer-architecture.md)
- [数据管理与执行机制](data-management-and-execution.md)
- [API 文档](api/)
