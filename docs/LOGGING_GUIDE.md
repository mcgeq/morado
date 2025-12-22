# Morado 日志系统使用指南

本文档说明如何在 Morado 项目中使用日志系统。

## 日志系统概述

Morado 使用自定义的结构化日志系统，基于 Python 的 `structlog` 库，提供：

- ✅ 结构化日志输出（JSON/Console 格式）
- ✅ 请求上下文跟踪（Request ID）
- ✅ 多种日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- ✅ 自动日志装饰器
- ✅ 环境配置支持

## 基本使用

### 1. 导入日志器

```python
from morado.common.logger import get_logger

logger = get_logger(__name__)
```

### 2. 记录日志

```python
# 基本日志
logger.info("User logged in")
logger.warning("Rate limit approaching")
logger.error("Failed to connect to database")

# 带上下文的日志
logger.info(
    "Header component created",
    extra={
        "header_id": 123,
        "name": "Auth Header",
        "scope": "global",
    },
)

# 异常日志
try:
    # 某些操作
    pass
except Exception as e:
    logger.exception(
        "Operation failed",
        extra={"operation": "create_header", "error": str(e)},
    )
```

## 日志级别

### DEBUG
用于详细的调试信息，通常只在开发环境启用。

```python
logger.debug("Database session created")
logger.debug("Config loaded", extra={"config_path": "/path/to/config"})
```

### INFO
用于一般信息性消息，记录正常的业务流程。

```python
logger.info("Application started", extra={"version": "1.0.0"})
logger.info("User created", extra={"user_id": 123, "username": "john"})
```

### WARNING
用于警告信息，表示潜在问题但不影响正常运行。

```python
logger.warning("Config file not found, using defaults")
logger.warning("Rate limit exceeded", extra={"user_id": 123, "limit": 100})
```

### ERROR
用于错误信息，表示操作失败但应用仍可继续运行。

```python
logger.error("Failed to send email", extra={"recipient": "user@example.com"})
logger.error("Database query failed", extra={"query": "SELECT * FROM users"})
```

### CRITICAL
用于严重错误，可能导致应用无法继续运行。

```python
logger.critical("Database connection lost")
logger.critical("Out of memory", extra={"available_mb": 10})
```

## 在不同层级使用日志

### 1. 配置层 (core/)

记录配置加载、初始化等关键操作：

```python
# backend/src/morado/core/config.py
from morado.common.logger import get_logger

logger = get_logger(__name__)

def get_settings() -> Settings:
    logger.info("Loading application settings", extra={"environment": environment})
    # ... 加载配置
    logger.info("Settings loaded successfully", extra={"app_name": settings.app_name})
    return settings
```

### 2. 数据库层 (core/database.py)

记录数据库连接、会话管理：

```python
# backend/src/morado/core/database.py
from morado.common.logger import get_logger

logger = get_logger(__name__)

def initialize(self, database_url: str | None = None) -> None:
    logger.info("Initializing database", extra={"pool_size": settings.pool_size})
    # ... 初始化数据库
    logger.info("Database initialized successfully")
```

### 3. 服务层 (services/)

记录业务逻辑操作：

```python
# backend/src/morado/services/api_component.py
from morado.common.logger import get_logger

logger = get_logger(__name__)

class HeaderService:
    def create_header(self, session: Session, name: str, **kwargs) -> Header:
        logger.info("Creating header", extra={"name": name, "scope": kwargs.get("scope")})
        
        try:
            header = self.repository.create(session, name=name, **kwargs)
            session.commit()
            
            logger.info(
                "Header created successfully",
                extra={"header_id": header.id, "name": name},
            )
            return header
            
        except Exception as e:
            logger.exception("Failed to create header", extra={"name": name, "error": str(e)})
            session.rollback()
            raise
```

### 4. 仓储层 (repositories/)

记录数据访问操作（可选，通常只记录关键操作）：

```python
# backend/src/morado/repositories/api_component.py
from morado.common.logger import get_logger

logger = get_logger(__name__)

class HeaderRepository:
    def create(self, session: Session, **kwargs) -> Header:
        logger.debug("Creating header in database", extra={"name": kwargs.get("name")})
        header = Header(**kwargs)
        session.add(header)
        session.flush()
        logger.debug("Header created", extra={"header_id": header.id})
        return header
```

### 5. API 层 (api/v1/)

通常不需要手动添加日志，因为 `LoggingMiddleware` 会自动记录所有请求。

但可以在特殊情况下添加：

```python
# backend/src/morado/api/v1/header.py
from morado.common.logger import get_logger

logger = get_logger(__name__)

class HeaderController(Controller):
    @post("/")
    async def create_header(self, data: HeaderCreate, ...) -> HeaderResponse:
        # 中间件已经记录了请求，这里只在特殊情况下记录
        if data.scope == HeaderScope.GLOBAL:
            logger.info("Creating global header", extra={"name": data.name})
        
        header = header_service.create_header(db_session, **data.model_dump())
        return HeaderResponse.model_validate(header)
```

## 请求上下文跟踪

### 自动请求 ID

`LoggingMiddleware` 会自动为每个请求生成或提取 Request ID：

```python
# 自动添加到日志中
logger.info("Processing request")
# 输出: {"message": "Processing request", "request_id": "REQ-abc123...", ...}
```

### 手动使用请求上下文

```python
from morado.common.logger import request_scope

with request_scope(user_id=123, action="create_header") as ctx:
    logger.info("User action", extra={"header_name": "Auth Header"})
    # 日志会包含 user_id 和 action
```

## 日志配置

### 1. 环境变量配置

```bash
# .env
LOG_LEVEL=INFO
LOG_FORMAT=json  # 或 console
```

### 2. 配置文件

```toml
# backend/config/development.toml
[logging]
level = "DEBUG"
format = "console"

# backend/config/production.toml
[logging]
level = "INFO"
format = "json"
```

### 3. 代码配置

```python
from morado.common.logger import configure_logger
from morado.common.logger.config import LoggerConfig

config = LoggerConfig(
    level="INFO",
    format="json",
)
configure_logger(config)
```

## 日志输出格式

### Console 格式（开发环境）

```
2024-12-22T16:30:45.123456Z [info     ] Header created successfully extra={'header_id': 123, 'name': 'Auth Header'}
```

### JSON 格式（生产环境）

```json
{
  "timestamp": "2024-12-22T16:30:45.123456Z",
  "level": "info",
  "message": "Header created successfully",
  "logger": "morado.services.api_component",
  "request_id": "REQ-abc123...",
  "extra": {
    "header_id": 123,
    "name": "Auth Header"
  }
}
```

## 最佳实践

### 1. 使用结构化日志

❌ **不好的做法：**
```python
logger.info(f"User {user_id} created header {header_name}")
```

✅ **好的做法：**
```python
logger.info(
    "User created header",
    extra={"user_id": user_id, "header_name": header_name},
)
```

### 2. 记录关键操作

记录以下操作：
- ✅ 创建、更新、删除操作
- ✅ 外部 API 调用
- ✅ 数据库事务
- ✅ 认证和授权
- ✅ 错误和异常

不要记录：
- ❌ 每个函数调用
- ❌ 循环内的重复日志
- ❌ 敏感信息（密码、令牌等）

### 3. 使用适当的日志级别

```python
# DEBUG: 详细的调试信息
logger.debug("Entering function", extra={"params": params})

# INFO: 正常的业务流程
logger.info("Order created", extra={"order_id": 123})

# WARNING: 潜在问题
logger.warning("Cache miss", extra={"key": cache_key})

# ERROR: 操作失败
logger.error("Payment failed", extra={"order_id": 123, "error": str(e)})

# CRITICAL: 严重错误
logger.critical("Database connection lost")
```

### 4. 包含上下文信息

```python
# 好的日志包含足够的上下文
logger.info(
    "Header component created",
    extra={
        "header_id": header.id,
        "header_uuid": str(header.uuid),
        "name": header.name,
        "scope": header.scope.value,
        "created_by": user_id,
    },
)
```

### 5. 使用异常日志

```python
try:
    result = risky_operation()
except Exception as e:
    # 使用 exception() 会自动包含堆栈跟踪
    logger.exception(
        "Operation failed",
        extra={"operation": "risky_operation", "error": str(e)},
    )
    raise
```

### 6. 避免敏感信息

```python
# ❌ 不要记录敏感信息
logger.info("User login", extra={"password": password})

# ✅ 只记录非敏感信息
logger.info("User login", extra={"username": username, "ip": ip_address})
```

## 日志查询和分析

### 1. 使用 grep 查询日志

```bash
# 查找特定请求的所有日志
grep "REQ-abc123" logs/app.log

# 查找错误日志
grep "ERROR" logs/app.log

# 查找特定用户的操作
grep "user_id.*123" logs/app.log
```

### 2. 使用 jq 分析 JSON 日志

```bash
# 提取所有错误消息
cat logs/app.log | jq 'select(.level == "error") | .message'

# 统计各级别日志数量
cat logs/app.log | jq -r '.level' | sort | uniq -c

# 查找特定操作的日志
cat logs/app.log | jq 'select(.extra.operation == "create_header")'
```

### 3. 集成日志聚合工具

生产环境建议使用：
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **Datadog**
- **CloudWatch Logs** (AWS)

## 性能考虑

### 1. 避免过度日志

```python
# ❌ 不好：在循环中记录每次迭代
for item in items:
    logger.debug("Processing item", extra={"item_id": item.id})
    process(item)

# ✅ 好：只记录摘要
logger.info("Processing items", extra={"count": len(items)})
for item in items:
    process(item)
logger.info("Items processed successfully")
```

### 2. 使用条件日志

```python
# 只在 DEBUG 级别启用时才构建复杂的日志数据
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Complex data", extra={"data": expensive_operation()})
```

## 故障排查

### 查看当前日志配置

```python
from morado.core.config import get_settings

settings = get_settings()
print(f"Log level: {settings.log_level}")
print(f"Log format: {settings.log_format}")
```

### 临时更改日志级别

```python
import logging

# 临时设置为 DEBUG
logging.getLogger("morado").setLevel(logging.DEBUG)
```

### 查看日志文件

```bash
# 实时查看日志
tail -f logs/app.log

# 查看最近的错误
tail -100 logs/app.log | grep ERROR
```

## 总结

Morado 的日志系统提供了强大的功能来跟踪应用程序的行为。遵循本指南的最佳实践，可以：

- ✅ 快速定位和解决问题
- ✅ 监控应用程序性能
- ✅ 审计用户操作
- ✅ 分析业务指标

记住：**好的日志是调试和监控的关键！**
