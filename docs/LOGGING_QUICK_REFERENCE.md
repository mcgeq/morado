# 日志系统快速参考

## 快速开始

```python
from morado.common.logger import get_logger

logger = get_logger(__name__)
```

## 常用日志方法

| 方法 | 用途 | 示例 |
|------|------|------|
| `logger.debug()` | 调试信息 | `logger.debug("Session created")` |
| `logger.info()` | 一般信息 | `logger.info("User logged in")` |
| `logger.warning()` | 警告信息 | `logger.warning("Cache miss")` |
| `logger.error()` | 错误信息 | `logger.error("Query failed")` |
| `logger.exception()` | 异常（含堆栈） | `logger.exception("Operation failed")` |

## 结构化日志

```python
# ✅ 推荐：使用 extra 字段
logger.info(
    "User created",
    extra={
        "user_id": 123,
        "username": "john",
        "email": "john@example.com",
    },
)

# ❌ 不推荐：字符串格式化
logger.info(f"User {user_id} created with name {username}")
```

## 异常日志

```python
try:
    risky_operation()
except Exception as e:
    logger.exception(
        "Operation failed",
        extra={"operation": "risky_operation", "error": str(e)},
    )
    raise
```

## 请求上下文

```python
from morado.common.logger import request_scope

with request_scope(user_id=123, action="create_order") as ctx:
    logger.info("Processing order", extra={"order_id": 456})
    # 日志会自动包含 user_id 和 action
```

## 配置

### 环境变量
```bash
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json         # json, console
```

### 代码配置
```python
from morado.common.logger import configure_logger
from morado.common.logger.config import LoggerConfig

configure_logger(LoggerConfig(level="DEBUG", format="console"))
```

## 日志级别选择

| 场景 | 级别 |
|------|------|
| 函数进入/退出 | DEBUG |
| 数据库会话创建 | DEBUG |
| 用户操作 | INFO |
| 订单创建 | INFO |
| 配置文件缺失 | WARNING |
| 缓存未命中 | WARNING |
| 数据库查询失败 | ERROR |
| API 调用失败 | ERROR |
| 数据库连接丢失 | CRITICAL |
| 内存不足 | CRITICAL |

## 常见模式

### 服务层
```python
class MyService:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_item(self, session, name):
        self.logger.info("Creating item", extra={"name": name})
        
        try:
            item = self.repository.create(session, name=name)
            session.commit()
            
            self.logger.info(
                "Item created",
                extra={"item_id": item.id, "name": name},
            )
            return item
            
        except Exception as e:
            self.logger.exception("Failed to create item", extra={"name": name})
            session.rollback()
            raise
```

### 数据库操作
```python
def get_db():
    session = db_manager.get_session()
    logger.debug("Database session created")
    try:
        yield session
        session.commit()
        logger.debug("Database session committed")
    except Exception as e:
        session.rollback()
        logger.warning("Database session rolled back", extra={"error": str(e)})
        raise
    finally:
        session.close()
        logger.debug("Database session closed")
```

### 配置加载
```python
def load_config():
    logger.info("Loading configuration", extra={"environment": env})
    
    try:
        config = load_from_file(config_path)
        logger.info("Configuration loaded", extra={"config_path": str(config_path)})
        return config
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults", extra={"path": str(config_path)})
        return default_config
    except Exception as e:
        logger.exception("Failed to load config", extra={"error": str(e)})
        raise
```

## 避免的做法

### ❌ 不要记录敏感信息
```python
# ❌ 错误
logger.info("User login", extra={"password": password})

# ✅ 正确
logger.info("User login", extra={"username": username})
```

### ❌ 不要在循环中过度日志
```python
# ❌ 错误
for item in items:
    logger.info("Processing item", extra={"item_id": item.id})

# ✅ 正确
logger.info("Processing items", extra={"count": len(items)})
for item in items:
    process(item)
logger.info("Items processed")
```

### ❌ 不要使用字符串格式化
```python
# ❌ 错误
logger.info(f"User {user_id} created order {order_id}")

# ✅ 正确
logger.info("User created order", extra={"user_id": user_id, "order_id": order_id})
```

## 测试日志

```bash
# 运行日志测试
cd backend
uv run python scripts/test_logging.py
```

## 查看日志

```bash
# 实时查看
tail -f logs/app.log

# 查找错误
grep "ERROR" logs/app.log

# 查找特定请求
grep "REQ-abc123" logs/app.log

# JSON 日志分析
cat logs/app.log | jq 'select(.level == "error")'
```

## 更多信息

详细文档：`docs/LOGGING_GUIDE.md`
