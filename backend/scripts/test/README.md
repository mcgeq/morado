# 测试脚本

本目录包含各种集成测试和功能测试脚本。

## 脚本列表

### test_api_component_integration.py
测试 API 组件的集成。

**测试内容：**
- Header、Body、ApiDefinition 的创建和关联
- API 组件的复用

### test_component_relationships.py
测试组件之间的关系。

**测试内容：**
- 组件嵌套关系
- 组件-脚本关联
- 关系完整性

### test_execution_context.py
测试执行上下文功能。

**测试内容：**
- 变量解析
- 参数覆盖
- 上下文传递

### test_file_operations_comprehensive.py
测试文件操作功能。

**测试内容：**
- 文件读写
- 文件上传下载
- 文件管理

### test_http_client_integration.py
测试 HTTP 客户端集成。

**测试内容：**
- HTTP 请求发送
- 响应处理
- 拦截器功能

### test_logging.py
测试日志功能。

**测试内容：**
- 日志记录
- 日志格式化
- 日志输出

### test_relationships.py
测试数据模型关系。

**测试内容：**
- 外键关系
- 级联操作
- 关系查询

### test_schema_validation.py
测试 Schema 验证。

**测试内容：**
- Pydantic schema 验证
- 数据类型检查
- 必填字段验证

## 使用方法

运行单个测试脚本：

```bash
cd backend
uv run python scripts/test/<script_name>.py
```

运行所有测试：

```bash
cd backend
# 使用 pytest 运行所有测试
uv run pytest scripts/test/
```

## 注意事项

- 测试脚本可能需要数据库连接
- 建议在测试环境中运行
- 某些测试可能会修改数据库数据
- 测试前建议备份数据库
