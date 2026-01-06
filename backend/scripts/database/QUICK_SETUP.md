# 快速配置指南 - 数据库设置

## 开发环境快速配置

### 1. 创建PostgreSQL数据库和用户

```bash
# 连接到PostgreSQL
psql -U postgres

# 创建用户
CREATE USER morado WITH PASSWORD 'morado';

# 创建开发数据库
CREATE DATABASE morado_dev OWNER morado;

# 创建测试数据库
CREATE DATABASE morado_test OWNER morado;

# 授予权限
GRANT ALL PRIVILEGES ON DATABASE morado_dev TO morado;
GRANT ALL PRIVILEGES ON DATABASE morado_test TO morado;

# 退出
\q
```

### 2. 配置开发环境

编辑 `backend/config/development.toml`:

```toml
# Database settings
database_url = "postgresql://morado:morado@localhost:5432/morado_dev"
database_pool_size = 5
database_echo = true
```

### 3. 配置测试环境

编辑 `backend/config/testing.toml`:

```toml
# Database settings
database_url = "postgresql://morado:morado@localhost:5432/morado_test"
database_pool_size = 5
database_echo = false
```

### 4. 运行数据库迁移

```bash
cd backend

# 运行迁移创建表结构
uv run alembic upgrade head
```

### 5. 填充测试数据

```bash
# 填充开发环境数据
uv run python scripts/database/seed_four_layer_data.py --env development

# 填充测试环境数据
uv run python scripts/database/seed_four_layer_data.py --env testing
```

## 使用不同的数据库配置

### 方式1: 修改配置文件（推荐用于本地开发）

**优点**: 配置持久化，团队成员可以共享相同的配置
**缺点**: 需要修改文件

```bash
# 编辑配置文件
code backend/config/development.toml

# 修改 database_url
database_url = "postgresql://your_user:your_password@your_host:5432/your_database"
```

### 方式2: 使用环境变量（推荐用于CI/CD和生产环境）

**优点**: 不需要修改代码，适合不同环境
**缺点**: 需要每次设置

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://user:pass@host:5432/db"
uv run python scripts/database/seed_four_layer_data.py

# Windows CMD
set DATABASE_URL=postgresql://user:pass@host:5432/db
uv run python scripts/database/seed_four_layer_data.py

# Linux/Mac
export DATABASE_URL="postgresql://user:pass@host:5432/db"
uv run python scripts/database/seed_four_layer_data.py

# 或者一行命令
DATABASE_URL="postgresql://user:pass@host:5432/db" uv run python scripts/database/seed_four_layer_data.py
```

### 方式3: 使用 .env 文件（推荐用于本地开发）

创建 `backend/.env` 文件:

```bash
DATABASE_URL=postgresql://morado:morado@localhost:5432/morado_dev
```

然后使用 python-dotenv 加载（需要在脚本中添加支持）。

## 常见配置场景

### 场景1: 本地开发使用Docker PostgreSQL

```toml
# backend/config/development.toml
database_url = "postgresql://postgres:postgres@localhost:5432/morado_dev"
```

### 场景2: 远程开发数据库

```toml
# backend/config/development.toml
database_url = "postgresql://dev_user:dev_pass@dev-db.example.com:5432/morado_dev"
```

### 场景3: 使用不同端口的PostgreSQL

```toml
# backend/config/development.toml
database_url = "postgresql://morado:morado@localhost:5433/morado_dev"
```

### 场景4: CI/CD环境

```yaml
# .github/workflows/test.yml
env:
  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

steps:
  - name: Run tests
    run: |
      uv run alembic upgrade head
      uv run python scripts/database/seed_four_layer_data.py --env testing
      uv run pytest
```

## 验证配置

### 测试数据库连接

```bash
# 使用 psql 测试连接
psql -U morado -d morado_dev -h localhost

# 如果成功，你会看到 PostgreSQL 提示符
morado_dev=>
```

### 查看当前配置

```bash
# 查看配置文件
cat backend/config/development.toml | grep database_url

# 查看环境变量
echo $DATABASE_URL  # Linux/Mac
echo $env:DATABASE_URL  # Windows PowerShell
```

### 测试seed脚本

```bash
cd backend

# 测试开发环境
uv run python scripts/database/seed_four_layer_data.py --env development

# 应该看到类似输出:
# Seeding data for environment: development
# ============================================================
#    Using database_url from development.toml
# Connecting to database: postgresql+psycopg://morado:****@localhost:5432/morado_dev
```

## 安全建议

### 开发环境
- ✅ 可以在配置文件中使用简单密码
- ✅ 可以提交配置文件到版本控制

### 测试环境
- ✅ 可以在配置文件中使用简单密码
- ✅ 可以提交配置文件到版本控制

### 生产环境
- ❌ **不要**在配置文件中存储生产密码
- ✅ **必须**使用环境变量
- ✅ **必须**使用强密码
- ✅ 使用密钥管理服务（如 AWS Secrets Manager, Azure Key Vault）

```bash
# 生产环境示例
export DATABASE_URL="postgresql://prod_user:$(cat /secrets/db_password)@prod-db:5432/morado_prod"
uv run python scripts/database/seed_four_layer_data.py --env production
```

## 故障排除

### 问题: "password authentication failed"

**解决方案**:
1. 检查用户名和密码是否正确
2. 检查 PostgreSQL 的 `pg_hba.conf` 配置
3. 确保用户有访问数据库的权限

```bash
# 重置用户密码
psql -U postgres -c "ALTER USER morado WITH PASSWORD 'new_password';"
```

### 问题: "database does not exist"

**解决方案**:
```bash
# 创建数据库
psql -U postgres -c "CREATE DATABASE morado_dev OWNER morado;"
```

### 问题: "could not connect to server"

**解决方案**:
1. 确保 PostgreSQL 服务正在运行
2. 检查主机名和端口是否正确
3. 检查防火墙设置

```bash
# 检查 PostgreSQL 状态
# Linux
sudo systemctl status postgresql

# Mac
brew services list | grep postgresql

# Windows
Get-Service -Name postgresql*
```

## 更多帮助

- 查看完整文档: `backend/scripts/database/README.md`
- PostgreSQL 文档: https://www.postgresql.org/docs/
- SQLAlchemy 文档: https://docs.sqlalchemy.org/
