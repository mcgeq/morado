# 数据库迁移和初始化总结

## 完成的任务

### ✓ 任务 4.1: 创建数据库迁移脚本（四层架构）

已创建完整的 Alembic 迁移脚本，包含所有四层架构的表：

**文件位置：** `backend/alembic/versions/001_initial_migration.py`

**创建的表：**

1. **用户表**
   - `users` - 用户信息

2. **Layer 1 - API 定义组件**
   - `headers` - HTTP 请求头组件（可复用）
   - `bodies` - 请求/响应体组件（可复用）
   - `api_definitions` - API 接口定义（引用 Header 和 Body）

3. **Layer 2 - 脚本层**
   - `test_scripts` - 测试脚本（引用 API Definition）
   - `script_parameters` - 脚本参数定义

4. **Layer 3 - 组件层**
   - `test_components` - 测试组件（支持嵌套）
   - `component_scripts` - 组件-脚本关联表

5. **Layer 4 - 测试用例层**
   - `test_cases` - 测试用例
   - `test_case_scripts` - 测试用例-脚本关联表
   - `test_case_components` - 测试用例-组件关联表

6. **其他表**
   - `test_suites` - 测试套件
   - `test_suite_cases` - 测试套件-用例关联表
   - `test_executions` - 测试执行记录
   - `execution_results` - 执行结果详情

**特性：**
- ✓ 支持 Header 和 Body 的独立管理和复用
- ✓ 支持 API Definition 的两种组合方式（引用 Body 或内联 Body）
- ✓ 支持组件嵌套（parent_component_id 自引用）
- ✓ 支持级联删除和更新规则
- ✓ 包含完整的索引和外键约束
- ✓ 支持 upgrade 和 downgrade 操作

### ✓ 任务 4.2: 创建测试数据种子脚本（四层架构）

已创建完整的测试数据种子脚本，包含所有层的示例数据。

**文件位置：** `backend/scripts/database/seed_four_layer_data.py`

**创建的示例数据：**

1. **用户数据**
   - 1 个管理员用户（username: admin）

2. **Layer 1 示例数据**
   - 3 个 Header 组件（认证 Header、JSON Content-Type、XML Content-Type）
   - 3 个 Body 组件（用户信息、订单信息、登录请求）
   - 4 个 API Definition（展示两种组合方式）

3. **Layer 2 示例数据**
   - 4 个 Test Script（登录、获取用户信息、创建用户、准备环境）
   - 2 个 Script Parameter（用户名、密码参数）

4. **Layer 3 示例数据**
   - 3 个 Test Component（包含 1 个嵌套组件）
   - 4 个 Component-Script 关联

5. **Layer 4 示例数据**
   - 3 个 Test Case
   - 3 个 TestCase-Script 关联
   - 2 个 TestCase-Component 关联

**特性：**
- ✓ 展示 Header 和 Body 的复用
- ✓ 展示 API Definition 的两种组合方式
- ✓ 展示脚本引用 API Definition
- ✓ 展示组件嵌套关系
- ✓ 展示测试用例引用脚本和组件
- ✓ 包含参数覆盖示例

### ✓ 任务 4.3: 验证四层架构的数据完整性

已创建完整的数据完整性验证脚本。

**文件位置：** `backend/scripts/verify/verify_four_layer_integrity.py`

**验证项目：**

1. ✓ **Header 和 Body 的独立性**
   - 验证 Header 和 Body 可以独立存在
   - 验证它们不依赖于 API Definition

2. ✓ **API Definition 的两种组合方式**
   - 方式 1：引用 Header + 引用 Body
   - 方式 2：引用 Header + 内联 Body
   - 统计每种方式的使用情况

3. ✓ **脚本引用 API 定义**
   - 验证所有脚本都正确引用 API Definition
   - 验证引用的 API Definition 存在
   - 验证脚本参数

4. ✓ **组件嵌套关系**
   - 验证组件的父子关系
   - 验证嵌套组件引用的父组件存在
   - 验证组件-脚本关联

5. ✓ **用例引用脚本和组件**
   - 验证测试用例引用的脚本存在
   - 验证测试用例引用的组件存在
   - 验证执行顺序配置

6. ✓ **级联删除和更新规则**
   - 验证外键关系配置
   - 检查 CASCADE 规则
   - 检查 SET NULL 规则

## 使用说明

### 1. 创建数据库表

**方法 A：使用 SQLAlchemy 直接创建（推荐）**

```bash
cd backend

# 更新 scripts/database/create_tables.py 中的数据库连接信息
# DATABASE_URL = "postgresql+psycopg://用户名:密码@localhost:5432/morado"

uv run python scripts/database/create_tables.py
```

**方法 B：使用 Alembic 迁移**

```bash
cd backend

# 更新 alembic.ini 中的数据库连接
# sqlalchemy.url = postgresql://用户名:密码@localhost:5432/morado

uv run alembic upgrade head
```

### 2. 填充测试数据

```bash
cd backend

# 更新 scripts/database/seed_four_layer_data.py 中的数据库连接信息
uv run python scripts/database/seed_four_layer_data.py
```

### 3. 验证数据完整性

```bash
cd backend

# 更新 scripts/verify/verify_four_layer_integrity.py 中的数据库连接信息
uv run python scripts/verify/verify_four_layer_integrity.py
```

## 注意事项

### 数据库连接

由于 Windows 系统和 PostgreSQL 配置可能存在编码问题，建议：

1. 使用 `psycopg` (psycopg3) 而不是 `psycopg2`
2. 在连接字符串中使用 `postgresql+psycopg://` 前缀
3. 确保 PostgreSQL 用户名和密码正确

### 密码配置

默认脚本使用以下连接信息：
- 用户名: postgres
- 密码: postgres
- 主机: localhost
- 端口: 5432
- 数据库: morado

请根据实际情况修改脚本中的 `DATABASE_URL`。

### 依赖包

确保已安装以下依赖：
```bash
uv add alembic psycopg[binary] psycopg2-binary
```

## 文件清单

### 迁移文件
- `backend/alembic.ini` - Alembic 配置文件
- `backend/alembic/env.py` - Alembic 环境配置
- `backend/alembic/versions/001_initial_migration.py` - 初始迁移脚本

### 脚本文件
- `backend/scripts/database/create_tables.py` - 直接创建表的脚本（推荐）
- `backend/scripts/database/seed_four_layer_data.py` - 测试数据种子脚本
- `backend/scripts/verify/verify_four_layer_integrity.py` - 数据完整性验证脚本

### 文档文件
- `backend/README_DATABASE_SETUP.md` - 数据库设置详细说明
- `backend/DATABASE_MIGRATION_SUMMARY.md` - 本文档

## 下一步

完成数据库迁移和初始化后，可以：

1. 启动后端服务测试 API 端点
2. 使用前端应用连接后端
3. 执行测试用例验证四层架构功能
4. 根据需要添加更多测试数据

## 四层架构关系图

```
Layer 1: API Definition Components
┌─────────┐     ┌──────┐     ┌────────────────┐
│ Header  │────▶│ API  │◀────│ Body           │
│ (复用)  │     │ Def  │     │ (复用/内联)    │
└─────────┘     └──┬───┘     └────────────────┘
                   │
                   ▼
Layer 2: Test Scripts
              ┌────────┐
              │ Script │
              │ + Params│
              └───┬────┘
                  │
                  ▼
Layer 3: Test Components
              ┌───────────┐
              │ Component │◀──┐ (嵌套)
              │ + Scripts │───┘
              └─────┬─────┘
                    │
                    ▼
Layer 4: Test Cases
              ┌───────────┐
              │ Test Case │
              │ + Scripts │
              │ + Components│
              └───────────┘
```

## 总结

✓ 所有任务已完成
✓ 数据库迁移脚本已创建
✓ 测试数据种子脚本已创建
✓ 数据完整性验证脚本已创建
✓ 支持四层架构的所有特性
✓ 包含完整的文档和使用说明
