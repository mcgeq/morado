# Morado API 文档

## 概述

Morado 测试平台提供 RESTful API 用于管理测试资源和执行测试。

## 访问 API 文档

### 自动生成的交互式文档

Litestar 框架自动生成交互式 API 文档，启动后端服务后可访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/schema

### 静态 OpenAPI 规范

本目录包含静态 OpenAPI 规范文件：

- `openapi.yaml` - OpenAPI 3.1 规范文件

## API 版本

当前 API 版本：`v1`

所有 API 端点都以 `/api/v1` 为前缀（在实际实现中可能省略前缀）。

## 认证

大多数 API 端点需要认证。使用 Bearer Token 进行认证：

```http
Authorization: Bearer <your-token>
```

## API 分组

### Layer 1 - 接口定义层

| 端点 | 说明 |
|------|------|
| `/headers` | Header 组件管理 |
| `/bodies` | Body 组件管理 |
| `/api-definitions` | API 定义管理 |

### Layer 2 - 脚本层

| 端点 | 说明 |
|------|------|
| `/scripts` | 测试脚本管理 |
| `/scripts/{id}/execute` | 脚本执行 |

### Layer 3 - 组件层

| 端点 | 说明 |
|------|------|
| `/components` | 测试组件管理 |
| `/components/{id}/execute` | 组件执行 |

### Layer 4 - 测试用例层

| 端点 | 说明 |
|------|------|
| `/test-cases` | 测试用例管理 |
| `/test-cases/{id}/execute` | 测试用例执行 |

### 其他

| 端点 | 说明 |
|------|------|
| `/test-suites` | 测试套件管理 |
| `/test-executions` | 测试执行记录 |
| `/reports` | 测试报告 |
| `/dashboard` | 仪表板统计 |

## 通用响应格式

### 成功响应

```json
{
  "id": 1,
  "name": "Example",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 列表响应

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 错误响应

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found",
    "details": {},
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req-uuid"
  }
}
```

## HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

## 相关文档

- [四层架构使用指南](../four-layer-guide.md)
- [架构设计](../architecture.md)
