# Backend Scripts

本目录包含 Morado 后端项目的各种脚本工具。

## 目录结构

```
scripts/
├── database/          # 数据库相关脚本
│   ├── create_tables.py
│   └── seed_four_layer_data.py
├── demo/             # 功能演示脚本
│   ├── demo_execution_context.py
│   ├── demo_execution_engine_tracing.py
│   ├── demo_logging_integration.py
│   ├── demo_parameter_override.py
│   ├── demo_request_tracing.py
│   ├── demo_script_models.py
│   ├── demo_test_case_layer4.py
│   └── demo_tracing_integration.py
├── test/             # 测试脚本
│   ├── test_api_component_integration.py
│   ├── test_component_relationships.py
│   ├── test_execution_context.py
│   ├── test_file_operations_comprehensive.py
│   ├── test_http_client_integration.py
│   ├── test_logging.py
│   ├── test_relationships.py
│   └── test_schema_validation.py
└── verify/           # 验证脚本
    ├── verify_four_layer_integrity.py
    ├── verify_api_component_models.py
    ├── verify_app.py
    ├── verify_component_models.py
    ├── verify_dashboard_endpoints.py
    ├── verify_execution_engine_integration.py
    ├── verify_file_operations.py
    ├── verify_http_client.py
    ├── verify_http_client_complete.py
    ├── verify_http_factory.py
    ├── verify_imports.py
    ├── verify_interceptor.py
    ├── verify_logging_interceptor.py
    ├── verify_middleware.py
    ├── verify_retry.py
    ├── verify_schemas.py
    ├── verify_script_models.py
    ├── verify_test_case_layer4.py
    ├── verify_tracing_interceptor.py
    └── verify_utils.py
```

## 快速开始

### 1. 初始化数据库

```bash
cd backend

# 创建数据库表
uv run python scripts/database/create_tables.py

# 填充测试数据
uv run python scripts/database/seed_four_layer_data.py

# 验证数据完整性
uv run python scripts/verify/verify_four_layer_integrity.py
```

### 2. 运行演示脚本

```bash
cd backend

# 演示执行上下文
uv run python scripts/demo/demo_execution_context.py

# 演示参数覆盖
uv run python scripts/demo/demo_parameter_override.py
```

### 3. 运行验证脚本

```bash
cd backend

# 验证模块导入
uv run python scripts/verify/verify_imports.py

# 验证应用配置
uv run python scripts/verify/verify_app.py
```

## 脚本分类说明

### 📁 database/ - 数据库脚本
用于数据库初始化和数据填充。

**主要脚本：**
- `create_tables.py` ⭐ - 创建所有数据库表（推荐）
- `seed_four_layer_data.py` ⭐ - 填充测试数据（必需）

**详细说明：** 查看 [database/README.md](database/README.md)

### 🎬 demo/ - 演示脚本
展示系统各个功能特性的使用方法。

**主要脚本：**
- `demo_execution_context.py` - 执行上下文演示
- `demo_parameter_override.py` - 参数覆盖演示
- `demo_test_case_layer4.py` - 测试用例演示

**详细说明：** 查看 [demo/README.md](demo/README.md)

### 🧪 test/ - 测试脚本
集成测试和功能测试脚本。

**主要脚本：**
- `test_api_component_integration.py` - API 组件集成测试
- `test_execution_context.py` - 执行上下文测试
- `test_http_client_integration.py` - HTTP 客户端测试

**详细说明：** 查看 [test/README.md](test/README.md)

### ✅ verify/ - 验证脚本
验证系统功能和数据完整性。

**主要脚本：**
- `verify_four_layer_integrity.py` - 四层架构完整性验证
- `verify_imports.py` - 模块导入验证
- `verify_app.py` - 应用配置验证

**详细说明：** 查看 [verify/README.md](verify/README.md)

## 使用建议

### 开发环境初始化流程

1. **数据库初始化**
   ```bash
   uv run python scripts/database/create_tables.py
   uv run python scripts/database/seed_four_layer_data.py
   ```

2. **验证安装**
   ```bash
   uv run python scripts/verify/verify_imports.py
   uv run python scripts/verify/verify_four_layer_integrity.py
   ```

3. **学习功能**
   ```bash
   # 运行演示脚本了解各个功能
   uv run python scripts/demo/demo_execution_context.py
   ```

### 测试流程

1. **运行单元测试**
   ```bash
   uv run pytest tests/backend/unit/
   ```

2. **运行集成测试脚本**
   ```bash
   uv run python scripts/test/test_api_component_integration.py
   ```

3. **运行验证脚本**
   ```bash
   uv run python scripts/verify/verify_four_layer_integrity.py
   ```

## 注意事项

1. **数据库连接**
   - 大多数脚本需要配置数据库连接
   - 默认连接：`postgresql+psycopg://postgres:postgres@localhost:5432/morado`
   - 根据实际情况修改脚本中的 `DATABASE_URL`

2. **执行顺序**
   - 先运行 database 脚本初始化数据库
   - 再运行 verify 脚本验证安装
   - 最后运行 demo 和 test 脚本

3. **环境要求**
   - Python 3.13+
   - PostgreSQL 18
   - 所有依赖已通过 `uv` 安装

## 常见问题

### Q: 数据库连接失败？
A: 检查 PostgreSQL 服务是否运行，确认用户名和密码正确。

### Q: 编码错误？
A: 使用 `psycopg` (psycopg3) 而不是 `psycopg2`，在连接字符串中使用 `postgresql+psycopg://` 前缀。

### Q: 如何清空数据库重新初始化？
A: 
```bash
# 删除所有表
uv run alembic downgrade base
# 或者直接删除数据库重新创建
# 然后重新运行初始化脚本
uv run python scripts/database/create_tables.py
uv run python scripts/database/seed_four_layer_data.py
```

## 贡献指南

添加新脚本时，请：

1. 将脚本放在正确的分类目录下
2. 在脚本开头添加清晰的文档字符串
3. 更新对应目录的 README.md
4. 确保脚本可以独立运行
5. 添加必要的错误处理和日志输出

## 相关文档

- [数据库设置说明](../README_DATABASE_SETUP.md)
- [数据库迁移总结](../DATABASE_MIGRATION_SUMMARY.md)
- [四层架构设计](../../docs/four-layer-architecture.md)
