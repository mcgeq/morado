# 数据库设置说明

## 概述

本文档说明如何设置和初始化 Morado 项目的 PostgreSQL 数据库。

## 前提条件

1. PostgreSQL 18 已安装（安装目录：D:\tools\PostgreSQL\18）
2. 数据库 `morado` 已创建
3. Python 环境已配置（使用 uv）

## 数据库迁移文件

已创建以下 Alembic 迁移文件：

- `backend/alembic/versions/001_initial_migration.py` - 初始迁移，创建所有四层架构表

### 包含的表

**Layer 1 - API 定义组件：**
- `headers` - HTTP 请求头组件
- `bodies` - 请求/响应体组件  
- `api_definitions` - API 接口定义

**Layer 2 - 脚本层：**
- `test_scripts` - 测试脚本
- `script_parameters` - 脚本参数

**Layer 3 - 组件层：**
- `test_components` - 测试组件
- `component_scripts` - 组件-脚本关联表

**Layer 4 - 测试用例层：**
- `test_cases` - 测试用例
- `test_case_scripts` - 测试用例-脚本关联表
- `test_case_components` - 测试用例-组件关联表

**其他表：**
- `users` - 用户表
- `test_suites` - 测试套件
- `test_suite_cases` - 测试套件-用例关联表
- `test_executions` - 测试执行记录
- `execution_results` - 执行结果详情

## 创建数据库表

### 方法 1：使用 SQLAlchemy 直接创建（推荐）

1. 更新 `backend/scripts/create_tables.py` 中的数据库连接信息：

```python
DATABASE_URL = "postgresql+psycopg://用户名:密码@localhost:5432/morado"
```

2. 运行脚本：

```bash
cd backend
uv run python scripts/create_tables.py
```

### 方法 2：使用 Alembic 迁移

1. 更新 `backend/alembic.ini` 中的数据库连接：

```ini
sqlalchemy.url = postgresql://用户名:密码@localhost:5432/morado
```

2. 运行迁移：

```bash
cd backend
uv run alembic upgrade head
```

### 方法 3：使用 psql 命令行

如果遇到编码问题，可以使用 psql 直接执行 SQL：

```bash
D:\tools\PostgreSQL\18\bin\psql.exe -U postgres -d morado -f alembic/versions/001_initial_migration.sql
```

## 常见问题

### 编码错误

如果遇到 `UnicodeDecodeError: 'utf-8' codec can't decode byte` 错误：

1. 确保使用 `psycopg` (psycopg3) 而不是 `psycopg2`
2. 在连接字符串中添加 `?client_encoding=utf8`
3. 设置环境变量：
   ```bash
   $env:PGCLIENTENCODING='UTF8'
   $env:PYTHONIOENCODING='utf-8'
   ```

### 密码认证失败

如果遇到密码认证失败：

1. 确认 PostgreSQL 用户名和密码
2. 检查 `pg_hba.conf` 配置文件
3. 尝试使用 psql 命令行测试连接：
   ```bash
   D:\tools\PostgreSQL\18\bin\psql.exe -U postgres -d morado
   ```

## 验证安装

创建表后，可以使用以下命令验证：

```bash
D:\tools\PostgreSQL\18\bin\psql.exe -U postgres -d morado -c "\dt"
```

应该看到所有创建的表列表。

## 下一步

完成数据库表创建后，可以：

1. 运行 `backend/scripts/seed_four_layer_data.py` 创建测试数据（任务 4.2）
2. 验证四层架构的数据完整性（任务 4.3）
