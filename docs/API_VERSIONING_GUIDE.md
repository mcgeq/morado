# API 版本控制指南

本文档说明如何在 Morado 项目中添加和管理 API 版本。

## 当前架构

当前项目使用 v1 API 版本，所有端点都在 `/api/v1/` 路径下：

```
backend/src/morado/api/
├── v1/
│   ├── __init__.py
│   ├── header.py
│   ├── body.py
│   ├── api_definition.py
│   ├── script.py
│   ├── component.py
│   ├── test_case.py
│   ├── test_suite.py
│   ├── test_execution.py
│   └── report.py
```

## 何时需要新版本

考虑创建新 API 版本的情况：

1. **破坏性变更**：修改现有端点的请求/响应格式
2. **重大重构**：改变核心业务逻辑或数据模型
3. **移除功能**：删除现有端点或字段
4. **重命名**：更改端点路径或参数名称

## 添加 v2 版本的步骤

### 1. 创建 v2 目录结构

```bash
# 在 backend/src/morado/api/ 下创建 v2 目录
mkdir backend/src/morado/api/v2
```

### 2. 决定迁移策略

有三种常见策略：

#### 策略 A：完全复制（推荐用于大规模变更）

复制整个 v1 目录到 v2，然后进行修改：

```bash
# 复制所有文件
cp -r backend/src/morado/api/v1/* backend/src/morado/api/v2/
```

**优点**：
- v1 和 v2 完全独立
- 可以自由修改 v2 而不影响 v1
- 清晰的版本隔离

**缺点**：
- 代码重复
- 需要维护两套代码

#### 策略 B：选择性迁移（推荐用于部分变更）

只复制需要修改的端点到 v2：

```python
# backend/src/morado/api/v2/__init__.py
"""API v2 module - only changed endpoints."""

from morado.api.v2 import test_case  # v2 版本
from morado.api.v1 import (  # 继续使用 v1
    header,
    body,
    api_definition,
    script,
    component,
    test_suite,
    test_execution,
    report,
)

__all__ = [
    "test_case",  # v2
    "header",     # v1
    "body",       # v1
    # ...
]
```

**优点**：
- 减少代码重复
- 只维护变更的部分
- 渐进式迁移

**缺点**：
- 版本间有依赖关系
- 需要仔细管理导入

#### 策略 C：共享服务层（推荐用于小变更）

v1 和 v2 共享相同的服务层，只改变 API 接口：

```python
# backend/src/morado/api/v2/test_case.py
"""Test Case API v2 - with breaking changes."""

from morado.services.test_case import TestCaseService  # 共享服务
from morado.schemas.v2.test_case import (  # v2 专用 schema
    TestCaseCreateV2,
    TestCaseResponseV2,
)

class TestCaseControllerV2(Controller):
    path = "/test-cases"
    tags = ["Test Cases V2"]
    
    @post("/")
    async def create_test_case(
        self,
        data: TestCaseCreateV2,  # v2 schema
        # ...
    ) -> TestCaseResponseV2:
        # 转换 v2 schema 到内部模型
        internal_data = self._convert_v2_to_internal(data)
        test_case = service.create_test_case(db_session, **internal_data)
        # 转换内部模型到 v2 schema
        return self._convert_internal_to_v2(test_case)
```

**优点**：
- 最小化代码重复
- 业务逻辑只维护一份
- API 层灵活变化

**缺点**：
- 需要转换层
- 可能增加复杂度

### 3. 创建 v2 的 __init__.py

```python
# backend/src/morado/api/v2/__init__.py
"""API v2 module.

This module contains all v2 API endpoints with breaking changes from v1.
"""

from morado.api.v2 import (
    test_case,
    # 其他 v2 模块
)

__all__ = [
    "test_case",
    # ...
]
```

### 4. 更新 app.py 注册 v2 路由

```python
# backend/src/morado/app.py

def create_app() -> Litestar:
    """Create and configure the Litestar application."""
    settings = get_settings()

    # 导入 v1 控制器
    from morado.api.v1.header import HeaderController
    from morado.api.v1.body import BodyController
    # ... 其他 v1 控制器

    # 导入 v2 控制器
    from morado.api.v2.test_case import TestCaseControllerV2
    # ... 其他 v2 控制器

    # 创建 OpenAPI 配置
    openapi_config = OpenAPIConfig(
        title=settings.app_name,
        version=settings.version,
        description="Morado Testing Platform API",
        path="/docs",
        tags=[
            # v1 tags
            {"name": "Headers", "description": "HTTP header management (v1)"},
            {"name": "Bodies", "description": "Body management (v1)"},
            # v2 tags
            {"name": "Test Cases V2", "description": "Test case management (v2)"},
        ],
    )

    # 创建应用
    app = Litestar(
        route_handlers=[
            # v1 路由
            HeaderController,
            BodyController,
            # ... 其他 v1 控制器
            
            # v2 路由
            TestCaseControllerV2,
            # ... 其他 v2 控制器
        ],
        # ... 其他配置
    )

    return app
```

### 5. 配置路由路径

确保 v2 控制器使用正确的路径前缀：

```python
# backend/src/morado/api/v2/test_case.py

class TestCaseControllerV2(Controller):
    path = "/v2/test-cases"  # 明确指定 v2 路径
    tags = ["Test Cases V2"]
    
    # ... 端点定义
```

或者使用 Router 来组织：

```python
# backend/src/morado/app.py

from litestar import Router

# 创建 v1 路由器
v1_router = Router(
    path="/v1",
    route_handlers=[
        HeaderController,
        BodyController,
        # ... 其他 v1 控制器
    ],
)

# 创建 v2 路由器
v2_router = Router(
    path="/v2",
    route_handlers=[
        TestCaseControllerV2,
        # ... 其他 v2 控制器
    ],
)

# 创建应用
app = Litestar(
    route_handlers=[v1_router, v2_router],
    # ... 其他配置
)
```

## 版本弃用策略

### 1. 标记弃用

在 v1 端点中添加弃用警告：

```python
from litestar import get
from litestar.response import Response

class TestCaseController(Controller):
    @get("/{test_case_id:int}")
    async def get_test_case(
        self,
        test_case_id: int,
        # ...
    ) -> Response[TestCaseResponse]:
        """Get test case by ID.
        
        .. deprecated:: 2.0.0
           This endpoint is deprecated. Use /v2/test-cases/{id} instead.
        """
        # 添加弃用响应头
        response = Response(
            content=TestCaseResponse.model_validate(test_case),
            headers={
                "X-API-Deprecated": "true",
                "X-API-Deprecation-Date": "2024-12-31",
                "X-API-Sunset-Date": "2025-06-30",
                "Link": '</v2/test-cases/{id}>; rel="successor-version"',
            },
        )
        return response
```

### 2. 设置弃用时间表

```
阶段 1（发布 v2）：
- v1 和 v2 同时可用
- v1 标记为弃用
- 文档更新推荐使用 v2

阶段 2（6 个月后）：
- v1 进入维护模式
- 只修复严重 bug
- 不再添加新功能

阶段 3（12 个月后）：
- 移除 v1 端点
- 只保留 v2
```

### 3. 通知客户端

在响应中添加弃用信息：

```python
# backend/src/morado/middleware/deprecation.py

from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

class DeprecationMiddleware:
    """Middleware to add deprecation warnings to v1 endpoints."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            path = scope.get("path", "")
            
            # 检查是否是 v1 端点
            if path.startswith("/v1/"):
                # 添加弃用警告头
                async def send_wrapper(message: dict) -> None:
                    if message["type"] == "http.response.start":
                        headers = list(message.get("headers", []))
                        headers.extend([
                            (b"x-api-deprecated", b"true"),
                            (b"x-api-deprecation-info", b"This API version is deprecated. Please migrate to v2."),
                        ])
                        message["headers"] = headers
                    await send(message)
                
                await self.app(scope, receive, send_wrapper)
                return
        
        await self.app(scope, receive, send)
```

## 前端配置

### 1. 环境变量配置

```env
# frontend/.env.development
VITE_API_BASE_URL_V1=http://localhost:8000/v1
VITE_API_BASE_URL_V2=http://localhost:8000/v2
VITE_API_DEFAULT_VERSION=v2
```

### 2. API 客户端配置

```typescript
// frontend/src/api/index.ts

import axios from 'axios';

// 创建 v1 客户端
export const apiV1 = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL_V1,
  timeout: 10000,
});

// 创建 v2 客户端
export const apiV2 = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL_V2,
  timeout: 10000,
});

// 默认使用 v2
export const api = apiV2;
```

### 3. 渐进式迁移

```typescript
// frontend/src/api/test-case.ts

import { apiV1, apiV2 } from './index';

// 使用 v2 API
export const getTestCase = (id: number) => {
  return apiV2.get(`/test-cases/${id}`);
};

// 仍然使用 v1 API（待迁移）
export const getTestSuite = (id: number) => {
  return apiV1.get(`/test-suites/${id}`);
};
```

## 测试策略

### 1. 版本兼容性测试

```python
# tests/backend/integration/test_api_versioning.py

import pytest
from litestar.testing import TestClient

def test_v1_and_v2_coexist(test_client: TestClient):
    """Test that v1 and v2 APIs can coexist."""
    # 测试 v1 端点
    response_v1 = test_client.get("/v1/test-cases/1")
    assert response_v1.status_code == 200
    
    # 测试 v2 端点
    response_v2 = test_client.get("/v2/test-cases/1")
    assert response_v2.status_code == 200

def test_v1_deprecation_headers(test_client: TestClient):
    """Test that v1 endpoints include deprecation headers."""
    response = test_client.get("/v1/test-cases/1")
    assert "x-api-deprecated" in response.headers
    assert response.headers["x-api-deprecated"] == "true"
```

### 2. 向后兼容性测试

```python
def test_v1_backward_compatibility(test_client: TestClient):
    """Ensure v1 API maintains backward compatibility."""
    # 使用旧的请求格式
    old_format_data = {
        "name": "Test Case",
        "description": "Description"
    }
    
    response = test_client.post("/v1/test-cases", json=old_format_data)
    assert response.status_code == 200
```

## 文档管理

### 1. OpenAPI 文档分离

```python
# backend/src/morado/app.py

# 为 v1 创建单独的文档
openapi_v1_config = OpenAPIConfig(
    title=f"{settings.app_name} API v1",
    version="1.0.0",
    path="/docs/v1",
    description="Legacy API - Deprecated",
)

# 为 v2 创建单独的文档
openapi_v2_config = OpenAPIConfig(
    title=f"{settings.app_name} API v2",
    version="2.0.0",
    path="/docs/v2",
    description="Current API version",
)
```

### 2. 迁移指南

创建 `docs/API_V1_TO_V2_MIGRATION.md` 文档：

```markdown
# API v1 到 v2 迁移指南

## 主要变更

### 1. Test Case 端点变更

**v1:**
```
POST /v1/test-cases
{
  "name": "string",
  "description": "string"
}
```

**v2:**
```
POST /v2/test-cases
{
  "name": "string",
  "description": "string",
  "priority": "high|medium|low",  // 新增必填字段
  "tags": ["string"]              // 新增可选字段
}
```

### 2. 响应格式变更

**v1:** 直接返回对象
**v2:** 统一包装格式

```json
{
  "data": { ... },
  "meta": {
    "version": "2.0",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```
```

## 最佳实践

1. **版本号语义化**：使用语义化版本号（v1, v2, v3）
2. **保持向后兼容**：在同一大版本内保持向后兼容
3. **明确弃用时间**：提前至少 6 个月通知弃用
4. **完整的迁移文档**：提供详细的迁移指南
5. **渐进式迁移**：允许客户端逐步迁移
6. **监控使用情况**：跟踪各版本的使用率

## 总结

添加 v2 版本的关键步骤：

1. ✅ 创建 `backend/src/morado/api/v2/` 目录
2. ✅ 选择合适的迁移策略（完全复制/选择性迁移/共享服务）
3. ✅ 实现 v2 控制器和 schemas
4. ✅ 在 `app.py` 中注册 v2 路由
5. ✅ 添加弃用警告到 v1
6. ✅ 更新前端配置支持多版本
7. ✅ 编写迁移文档
8. ✅ 添加版本兼容性测试

这样就可以平滑地引入新版本，同时保持对现有客户端的支持！
