# 验证脚本

本目录包含各种验证脚本，用于检查系统功能和数据完整性。

## 脚本列表

### verify_four_layer_integrity.py
验证四层架构的数据完整性。

**验证内容：**
- Header 和 Body 的独立性
- API Definition 的两种组合方式
- 脚本引用 API 定义
- 组件嵌套关系
- 测试用例引用脚本和组件
- 级联删除和更新规则

**使用方法：**
```bash
cd backend
uv run python scripts/verify/verify_four_layer_integrity.py
```

### verify_api_component_models.py
验证 API 组件模型。

**验证内容：**
- Header 模型
- Body 模型
- ApiDefinition 模型

### verify_app.py
验证应用启动和配置。

**验证内容：**
- 应用初始化
- 路由注册
- 中间件配置

### verify_component_models.py
验证组件模型。

**验证内容：**
- TestComponent 模型
- ComponentScript 关联

### verify_dashboard_endpoints.py
验证仪表板 API 端点。

**验证内容：**
- API 端点可访问性
- 响应格式
- 数据正确性

### verify_execution_engine_integration.py
验证执行引擎集成。

**验证内容：**
- 脚本执行
- 组件执行
- 测试用例执行

### verify_file_operations.py
验证文件操作功能。

**验证内容：**
- 文件读写
- 文件管理
- 权限控制

### verify_http_client.py / verify_http_client_complete.py
验证 HTTP 客户端功能。

**验证内容：**
- HTTP 请求
- 响应处理
- 错误处理

### verify_http_factory.py
验证 HTTP 工厂模式。

**验证内容：**
- 客户端创建
- 配置管理

### verify_imports.py
验证模块导入。

**验证内容：**
- 所有模块可正常导入
- 无循环依赖

### verify_interceptor.py
验证拦截器功能。

**验证内容：**
- 请求拦截
- 响应拦截
- 拦截器链

### verify_logging_interceptor.py
验证日志拦截器。

**验证内容：**
- 请求日志记录
- 响应日志记录

### verify_middleware.py
验证中间件。

**验证内容：**
- CORS 中间件
- 日志中间件
- 错误处理中间件

### verify_retry.py
验证重试机制。

**验证内容：**
- 自动重试
- 重试策略
- 重试次数

### verify_schemas.py
验证 Pydantic Schemas。

**验证内容：**
- Schema 定义
- 数据验证
- 序列化/反序列化

### verify_script_models.py
验证脚本模型。

**验证内容：**
- TestScript 模型
- ScriptParameter 模型

### verify_test_case_layer4.py
验证第四层测试用例。

**验证内容：**
- TestCase 模型
- 测试用例关联

### verify_tracing_interceptor.py
验证追踪拦截器。

**验证内容：**
- 请求追踪
- 追踪上下文传递

### verify_utils.py
验证工具函数。

**验证内容：**
- 时间工具
- UUID 工具
- 文件系统工具

## 使用方法

运行单个验证脚本：

```bash
cd backend
uv run python scripts/verify/<script_name>.py
```

运行所有验证脚本：

```bash
cd backend
# 依次运行所有验证脚本
for file in scripts/verify/*.py; do
    echo "Running $file..."
    uv run python "$file"
done
```

## 验证顺序建议

1. `verify_imports.py` - 首先验证所有模块可导入
2. `verify_utils.py` - 验证基础工具函数
3. `verify_schemas.py` - 验证数据结构
4. `verify_*_models.py` - 验证数据模型
5. `verify_four_layer_integrity.py` - 验证四层架构完整性
6. 其他功能验证脚本

## 注意事项

- 验证脚本通常需要数据库连接
- 建议在填充测试数据后运行验证脚本
- 验证脚本不会修改数据库数据
- 验证失败时会输出详细的错误信息
