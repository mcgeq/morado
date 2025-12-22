# 全链路请求跟踪指南

## 概述

Morado 实现了完整的全链路请求跟踪系统，使用单一的 Request ID 跟踪从 HTTP 请求入口到数据库层的整个调用链。

## 核心特性

### ✅ 自动 Request ID 传播
- HTTP 请求进入时，中间件自动生成或提取 Request ID
- Request ID 存储在 Context Variable 中，自动在整个调用链中传播
- 无需手动传递 Request ID 参数

### ✅ 上下文数据共享
- 请求方法、路径、客户端 IP 等信息自动共享
- 服务层可以添加额外的上下文数据
- 所有日志自动包含完整的上下文信息

### ✅ 跨层级跟踪
- **HTTP 层**（Middleware）→ **服务层**（Services）→ **仓储层**（Repositories）→ **数据库层**（Database）
- 每一层的日志都包含相同的 Request ID
- 轻松追踪请求的完整生命周期

## 架构设计

### Context Variable 机制

使用 Python 的 `contextvars` 模块实现上下文传播：

```python
# backend/src/morado/common/logger/context.py

import contextvars

# 存储 Request ID
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

# 存储额外的上下文数据
context_data_var: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    "context_data", default=None
)
```

### 核心函数

```python
# 设置 Request ID
set_request_id(request_id: str)

# 获取 Request ID
get_request_id() -> str | None

# 设置上下文数据
set_context_data(key: str, value: Any)

# 获取上下文数据
get_context_data(key: str | None = None) -> Any

# 获取完整的日志上下文
get_log_context() -> dict[str, Any]

# 清除上下文
clear_context()
```

## 使用示例

### 1. HTTP 中间件（自动）

中间件自动设置 Request ID 和基础上下文：

```python
# backend/src/morado/middleware/logging.py

async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
    # 生成或提取 Request ID
    request_id = headers.get(b"x-request-id", b"").decode("utf-8")
    if not request_id:
        request_id = generate_uuid()
    
    # 设置到上下文中
    set_request_id(request_id)
    set_context_data("method", method)
    set_context_data("path", path)
    set_context_data("client_ip", client_ip)
    
    # 记录日志 - 自动包含所有上下文
    logger.info("Request started", extra=get_log_context())
    
    try:
        await self.app(scope, receive, send_wrapper)
    finally:
        # 请求结束后清除上下文
        clear_context()
```

### 2. 服务层使用

服务层无需手动传递 Request ID，直接使用上下文：

```python
# backend/src/morado/services/api_component.py

from morado.common.logger import get_logger
from morado.common.logger.context import get_log_context, set_context_data

logger = get_logger(__name__)

class HeaderService:
    def create_header(self, session, name, **kwargs):
        # 添加服务层特定的上下文
        set_context_data("service", "HeaderService")
        set_context_data("operation", "create_header")
        
        # 日志自动包含 request_id 和所有上下文
        logger.info(
            "Creating header component",
            extra={
                **get_log_context(),  # 包含 request_id, method, path 等
                "name": name,
                "scope": kwargs.get("scope"),
            },
        )
        
        try:
            header = self.repository.create(session, name=name, **kwargs)
            session.commit()
            
            logger.info(
                "Header created successfully",
                extra={
                    **get_log_context(),
                    "header_id": header.id,
                },
            )
            return header
            
        except Exception as e:
            logger.exception(
                "Failed to create header",
                extra={
                    **get_log_context(),
                    "error": str(e),
                },
            )
            raise
```

### 3. 仓储层使用

仓储层同样自动获得 Request ID：

```python
# backend/src/morado/repositories/api_component.py

from morado.common.logger import get_logger
from morado.common.logger.context import get_log_context

logger = get_logger(__name__)

class HeaderRepository:
    def create(self, session, **kwargs):
        logger.debug(
            "Creating header in database",
            extra={
                **get_log_context(),  # 自动包含 request_id
                "table": "headers",
            },
        )
        
        header = Header(**kwargs)
        session.add(header)
        session.flush()
        
        logger.debug(
            "Header created",
            extra={
                **get_log_context(),
                "header_id": header.id,
            },
        )
        return header
```

### 4. 数据库层使用

数据库操作也包含 Request ID：

```python
# backend/src/morado/core/database.py

from morado.common.logger import get_logger
from morado.common.logger.context import get_log_context

logger = get_logger(__name__)

def get_db():
    session = db_manager.get_session()
    logger.debug("Database session created", extra=get_log_context())
    
    try:
        yield session
        session.commit()
        logger.debug("Database session committed", extra=get_log_context())
    except Exception as e:
        session.rollback()
        logger.warning(
            "Database session rolled back",
            extra={**get_log_context(), "error": str(e)},
        )
        raise
    finally:
        session.close()
        logger.debug("Database session closed", extra=get_log_context())
```

## 日志输出示例

### 完整的请求跟踪

```
2025-12-23 00:35:00 [info] Request started
  extra={
    'request_id': 'REQ-demo-12345',
    'method': 'POST',
    'path': '/v1/headers',
    'client_ip': '192.168.1.100'
  }

2025-12-23 00:35:00 [info] Creating header component
  extra={
    'request_id': 'REQ-demo-12345',  # 相同的 request_id
    'method': 'POST',
    'path': '/v1/headers',
    'client_ip': '192.168.1.100',
    'service': 'HeaderService',
    'operation': 'create_header',
    'name': 'Auth Header'
  }

2025-12-23 00:35:00 [debug] Creating header in database
  extra={
    'request_id': 'REQ-demo-12345',  # 相同的 request_id
    'method': 'POST',
    'path': '/v1/headers',
    'client_ip': '192.168.1.100',
    'service': 'HeaderService',
    'operation': 'create_header',
    'repository': 'HeaderRepository',
    'table': 'headers'
  }

2025-12-23 00:35:00 [debug] Executing SQL INSERT
  extra={
    'request_id': 'REQ-demo-12345',  # 相同的 request_id
    'method': 'POST',
    'path': '/v1/headers',
    'client_ip': '192.168.1.100',
    'service': 'HeaderService',
    'operation': 'create_header',
    'repository': 'HeaderRepository',
    'query': 'INSERT INTO headers (name, scope) VALUES (?, ?)'
  }

2025-12-23 00:35:00 [info] Request completed
  extra={
    'request_id': 'REQ-demo-12345',  # 相同的 request_id
    'method': 'POST',
    'path': '/v1/headers',
    'status_code': 200,
    'duration': 0.045
  }
```

### 多个并发请求

每个请求有独立的 Request ID：

```
# 请求 1
[info] User login attempt
  extra={'request_id': 'REQ-user-login-001', ...}

# 请求 2
[info] Creating order
  extra={'request_id': 'REQ-create-order-002', ...}

# 请求 3
[info] Fetching user profile
  extra={'request_id': 'REQ-get-profile-003', ...}
```

## 查询和分析

### 1. 使用 grep 查询特定请求

```bash
# 查找特定请求的所有日志
grep "REQ-demo-12345" logs/app.log

# 输出：
# 2025-12-23 00:35:00 [info] Request started extra={'request_id': 'REQ-demo-12345', ...}
# 2025-12-23 00:35:00 [info] Creating header component extra={'request_id': 'REQ-demo-12345', ...}
# 2025-12-23 00:35:00 [debug] Creating header in database extra={'request_id': 'REQ-demo-12345', ...}
# ...
```

### 2. 使用 jq 分析 JSON 日志

```bash
# 提取特定请求的所有日志
cat logs/app.log | jq 'select(.request_id == "REQ-demo-12345")'

# 统计请求的处理时间
cat logs/app.log | jq 'select(.request_id == "REQ-demo-12345" and .duration) | .duration'

# 查找特定请求的错误
cat logs/app.log | jq 'select(.request_id == "REQ-demo-12345" and .level == "error")'
```

### 3. 追踪请求流程

```bash
# 按时间顺序查看请求的完整流程
grep "REQ-demo-12345" logs/app.log | sort

# 查看请求经过的所有服务
grep "REQ-demo-12345" logs/app.log | grep -o '"service": "[^"]*"' | sort -u
```

## 测试和演示

### 运行演示脚本

```bash
cd backend
uv run python scripts/demo_request_tracing.py
```

演示脚本展示：
1. ✅ 单个请求的完整跟踪（HTTP → Service → Repository → Database）
2. ✅ 多个并发请求的独立跟踪
3. ✅ 错误情况下的上下文保留

## 最佳实践

### ✅ 推荐做法

1. **始终使用 `get_log_context()`**
   ```python
   logger.info(
       "Operation completed",
       extra={
           **get_log_context(),  # 包含 request_id 和所有上下文
           "additional_data": value,
       },
   )
   ```

2. **添加层级特定的上下文**
   ```python
   # 服务层
   set_context_data("service", "OrderService")
   set_context_data("operation", "create_order")
   
   # 仓储层
   set_context_data("repository", "OrderRepository")
   ```

3. **在关键操作点记录日志**
   - 操作开始
   - 操作成功
   - 操作失败

### ❌ 避免的做法

1. **不要手动传递 Request ID**
   ```python
   # ❌ 错误
   def create_header(self, session, name, request_id):
       logger.info("Creating", extra={"request_id": request_id})
   
   # ✅ 正确
   def create_header(self, session, name):
       logger.info("Creating", extra=get_log_context())
   ```

2. **不要忘记使用 `get_log_context()`**
   ```python
   # ❌ 错误 - 缺少 request_id
   logger.info("Creating", extra={"name": name})
   
   # ✅ 正确
   logger.info("Creating", extra={**get_log_context(), "name": name})
   ```

3. **不要在中间件外清除上下文**
   ```python
   # ❌ 错误 - 会破坏上下文传播
   def some_service_method(self):
       clear_context()  # 不要这样做！
   
   # ✅ 正确 - 只在中间件的 finally 块中清除
   ```

## 故障排查

### 问题：日志中没有 Request ID

**原因：** 没有使用 `get_log_context()`

**解决：**
```python
# 确保使用 get_log_context()
logger.info("Message", extra=get_log_context())
```

### 问题：Request ID 在某一层丢失

**原因：** 可能使用了同步代码而非异步，或者上下文被意外清除

**解决：**
1. 检查是否正确使用了 `contextvars`
2. 确保没有在中间件外调用 `clear_context()`
3. 验证异步代码正确传播上下文

### 问题：多个请求的 Request ID 混淆

**原因：** 使用了全局变量而非 Context Variable

**解决：**
- 确保使用 `contextvars.ContextVar` 而非全局变量
- 每个请求在独立的上下文中运行

## 性能考虑

### Context Variable 的性能

- ✅ **高性能**：`contextvars` 是 Python 内置的高性能机制
- ✅ **线程安全**：自动处理并发请求
- ✅ **异步友好**：完美支持 async/await

### 日志性能

- 使用结构化日志（`extra` 字段）
- 避免在循环中过度日志
- 生产环境使用 JSON 格式便于解析

## 集成日志聚合工具

### ELK Stack

```json
{
  "timestamp": "2025-12-23T00:35:00Z",
  "level": "info",
  "message": "Creating header component",
  "request_id": "REQ-demo-12345",
  "method": "POST",
  "path": "/v1/headers",
  "service": "HeaderService"
}
```

在 Kibana 中按 `request_id` 过滤即可查看完整的请求链路。

### Grafana Loki

使用 LogQL 查询：
```
{app="morado"} |= "REQ-demo-12345"
```

### Datadog

自动提取 `request_id` 作为 trace ID，实现 APM 集成。

## 总结

Morado 的全链路请求跟踪系统提供了：

1. ✅ **自动化**：无需手动传递 Request ID
2. ✅ **完整性**：覆盖从 HTTP 到数据库的所有层级
3. ✅ **易用性**：简单的 API，最小化代码侵入
4. ✅ **高性能**：基于 Python 内置的 `contextvars`
5. ✅ **可追溯**：轻松追踪请求的完整生命周期

通过这个系统，你可以：
- 🔍 快速定位问题
- 📊 分析请求性能
- 🐛 调试复杂的调用链
- 📈 监控系统行为

---

**相关文档：**
- [日志系统使用指南](./LOGGING_GUIDE.md)
- [日志快速参考](./LOGGING_QUICK_REFERENCE.md)
- [日志实施总结](./LOGGING_IMPLEMENTATION_SUMMARY.md)
