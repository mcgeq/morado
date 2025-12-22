# 全链路跟踪快速开始

## 5 分钟上手

### 1. 导入必要的模块

```python
from morado.common.logger import get_logger
from morado.common.logger.context import get_log_context, set_context_data
```

### 2. 在代码中使用

```python
logger = get_logger(__name__)

def my_function():
    # 记录日志 - 自动包含 request_id
    logger.info("Operation started", extra=get_log_context())
    
    # 添加额外的上下文（可选）
    set_context_data("operation", "my_operation")
    
    # 再次记录 - 包含新的上下文
    logger.info("Processing", extra=get_log_context())
```

### 3. 查看日志

所有日志自动包含 `request_id`：

```
[info] Operation started
  request_id: REQ-abc123
  method: POST
  path: /v1/api

[info] Processing
  request_id: REQ-abc123
  method: POST
  path: /v1/api
  operation: my_operation
```

## 常用模式

### 服务层

```python
class MyService:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_item(self, session, name):
        self.logger.info(
            "Creating item",
            extra={**get_log_context(), "name": name},
        )
        
        try:
            item = self.repository.create(session, name=name)
            session.commit()
            
            self.logger.info(
                "Item created",
                extra={**get_log_context(), "item_id": item.id},
            )
            return item
            
        except Exception as e:
            self.logger.exception(
                "Failed to create item",
                extra={**get_log_context(), "error": str(e)},
            )
            raise
```

### 仓储层

```python
class MyRepository:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create(self, session, **kwargs):
        self.logger.debug(
            "Inserting into database",
            extra={**get_log_context(), "table": "items"},
        )
        
        item = Item(**kwargs)
        session.add(item)
        session.flush()
        
        self.logger.debug(
            "Insert completed",
            extra={**get_log_context(), "item_id": item.id},
        )
        return item
```

## 查询日志

### 按 Request ID 查询

```bash
# 查找特定请求的所有日志
grep "REQ-abc123" logs/app.log

# 使用 jq 查询 JSON 日志
cat logs/app.log | jq 'select(.request_id == "REQ-abc123")'
```

### 追踪请求流程

```bash
# 查看请求经过的所有层级
grep "REQ-abc123" logs/app.log | grep -o '"message": "[^"]*"'
```

## 核心 API

| 函数 | 用途 |
|------|------|
| `get_log_context()` | 获取完整的日志上下文（包含 request_id） |
| `set_context_data(key, value)` | 添加额外的上下文数据 |
| `get_request_id()` | 获取当前的 Request ID |
| `set_request_id(id)` | 设置 Request ID（通常由中间件自动完成） |

## 最佳实践

### ✅ 推荐

```python
# 始终使用 get_log_context()
logger.info("Message", extra=get_log_context())

# 添加额外数据时使用展开运算符
logger.info(
    "Message",
    extra={**get_log_context(), "additional": "data"},
)
```

### ❌ 避免

```python
# 不要忘记使用 get_log_context()
logger.info("Message", extra={"data": "value"})  # 缺少 request_id

# 不要手动传递 request_id
def my_function(request_id):  # 不需要！
    logger.info("Message", extra={"request_id": request_id})
```

## 测试

```bash
# 运行演示脚本
cd backend
uv run python scripts/demo_request_tracing.py
```

## 更多信息

- [完整指南](./REQUEST_TRACING_GUIDE.md)
- [日志系统文档](./LOGGING_GUIDE.md)
- [快速参考](./LOGGING_QUICK_REFERENCE.md)
