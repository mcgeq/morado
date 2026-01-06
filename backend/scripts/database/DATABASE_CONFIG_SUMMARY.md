# 数据库配置总结

## 配置优先级

seed脚本按以下优先级读取数据库配置：

```
1. DATABASE_URL 环境变量 (最高优先级)
   ↓ 如果未设置
2. 配置文件 (backend/config/{environment}.toml)
   ↓ 如果未找到
3. 默认值 (postgresql://postgres:postgres@localhost:5432/morado)
```

## 三种配置方式对比

| 方式 | 优先级 | 适用场景 | 优点 | 缺点 |
|------|--------|----------|------|------|
| 环境变量 | 🥇 最高 | CI/CD、生产环境 | 安全、灵活、不修改代码 | 需要每次设置 |
| 配置文件 | 🥈 中等 | 本地开发、测试 | 持久化、团队共享 | 需要修改文件 |
| 默认值 | 🥉 最低 | 快速测试 | 无需配置 | 不灵活 |

## 快速使用指南

### 开发环境（推荐使用配置文件）

```bash
# 1. 编辑配置文件
# backend/config/development.toml
database_url = "postgresql://morado:morado@localhost:5432/morado_dev"

# 2. 运行seed脚本
cd backend
uv run python scripts/database/seed_four_layer_data.py --env development
```

### 测试环境（推荐使用配置文件）

```bash
# 1. 编辑配置文件
# backend/config/testing.toml
database_url = "postgresql://morado:morado@localhost:5432/morado_test"

# 2. 运行seed脚本
cd backend
uv run python scripts/database/seed_four_layer_data.py --env testing
```

### 生产环境（必须使用环境变量）

```bash
# 设置环境变量
export DATABASE_URL="postgresql://prod_user:secure_password@prod-db:5432/morado_prod"

# 运行seed脚本
cd backend
uv run python scripts/database/seed_four_layer_data.py --env production
```

### 临时使用不同数据库（使用环境变量）

```bash
# 一次性设置并运行
DATABASE_URL="postgresql://temp_user:temp_pass@temp-host:5432/temp_db" \
  uv run python scripts/database/seed_four_layer_data.py
```

## 命令行参数

```bash
# 查看帮助
uv run python scripts/database/seed_four_layer_data.py --help

# 指定环境
uv run python scripts/database/seed_four_layer_data.py --env development
uv run python scripts/database/seed_four_layer_data.py --env testing
uv run python scripts/database/seed_four_layer_data.py --env production

# 简写形式
uv run python scripts/database/seed_four_layer_data.py --environment testing
```

## 配置文件示例

### development.toml
```toml
# 开发环境 - 本地数据库
database_url = "postgresql://morado:morado@localhost:5432/morado_dev"
database_pool_size = 5
database_echo = true  # 显示SQL语句，便于调试
```

### testing.toml
```toml
# 测试环境 - 独立测试数据库
database_url = "postgresql://morado:morado@localhost:5432/morado_test"
database_pool_size = 5
database_echo = false  # 不显示SQL，保持测试输出清晰
```

### production.toml
```toml
# 生产环境 - 使用环境变量覆盖
database_url = "postgresql://morado:morado@db:5432/morado"  # 默认值
database_pool_size = 20
database_echo = false
```

## 环境变量示例

### Windows PowerShell
```powershell
# 临时设置（当前会话）
$env:DATABASE_URL="postgresql://user:pass@host:5432/db"

# 永久设置（当前用户）
[System.Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://user:pass@host:5432/db", "User")
```

### Windows CMD
```cmd
# 临时设置（当前会话）
set DATABASE_URL=postgresql://user:pass@host:5432/db

# 永久设置（系统级）
setx DATABASE_URL "postgresql://user:pass@host:5432/db"
```

### Linux/Mac
```bash
# 临时设置（当前会话）
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export DATABASE_URL="postgresql://user:pass@host:5432/db"' >> ~/.bashrc
source ~/.bashrc
```

## Docker Compose 示例

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://morado:morado@postgres:5432/morado_dev
    depends_on:
      - postgres
    command: |
      sh -c "
        uv run alembic upgrade head &&
        uv run python scripts/database/seed_four_layer_data.py --env development &&
        uv run uvicorn src.morado.app:app --host 0.0.0.0 --port 8000
      "
  
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=morado
      - POSTGRES_PASSWORD=morado
      - POSTGRES_DB=morado_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## GitHub Actions CI/CD 示例

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: |
          cd backend
          uv sync
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          cd backend
          uv run alembic upgrade head
      
      - name: Seed test data
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          cd backend
          uv run python scripts/database/seed_four_layer_data.py --env testing
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          cd backend
          uv run pytest
```

## 安全最佳实践

### ✅ 推荐做法

1. **开发/测试环境**: 使用配置文件，可以提交到版本控制
   ```toml
   database_url = "postgresql://morado:morado@localhost:5432/morado_dev"
   ```

2. **生产环境**: 使用环境变量，不要提交到版本控制
   ```bash
   export DATABASE_URL="postgresql://prod_user:${DB_PASSWORD}@prod-db:5432/morado_prod"
   ```

3. **密钥管理**: 使用密钥管理服务
   ```bash
   # AWS Secrets Manager
   export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id prod/db/url --query SecretString --output text)
   
   # Azure Key Vault
   export DATABASE_URL=$(az keyvault secret show --vault-name myvault --name db-url --query value -o tsv)
   ```

### ❌ 避免做法

1. ❌ 在生产配置文件中存储密码
2. ❌ 将生产密码提交到版本控制
3. ❌ 在代码中硬编码数据库连接
4. ❌ 使用弱密码（如 "password", "123456"）

## 验证配置

### 检查当前配置
```bash
# 查看将使用哪个数据库
cd backend
uv run python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('src')))
from scripts.database.seed_four_layer_data import get_database_url
print(get_database_url('development'))
"
```

### 测试数据库连接
```bash
# 使用 psql 测试
psql -U morado -d morado_dev -h localhost -c "SELECT version();"

# 使用 Python 测试
cd backend
uv run python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://morado:morado@localhost:5432/morado_dev')
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print(result.fetchone())
"
```

## 常见问题

**Q: 如何知道脚本使用了哪个数据库？**

A: 脚本会在输出中显示：
```
Seeding data for environment: development
============================================================
   Using database_url from development.toml
Connecting to database: postgresql+psycopg://morado:****@localhost:5432/morado_dev
```

**Q: 可以同时为多个环境填充数据吗？**

A: 可以，分别运行：
```bash
uv run python scripts/database/seed_four_layer_data.py --env development
uv run python scripts/database/seed_four_layer_data.py --env testing
```

**Q: 如何重置数据库？**

A: 删除并重新创建：
```bash
# 删除数据
psql -U postgres -c "DROP DATABASE morado_dev;"
psql -U postgres -c "CREATE DATABASE morado_dev OWNER morado;"

# 重新迁移和填充
cd backend
uv run alembic upgrade head
uv run python scripts/database/seed_four_layer_data.py --env development
```

**Q: 环境变量和配置文件可以同时使用吗？**

A: 可以，环境变量优先级更高，会覆盖配置文件的设置。

## 相关文档

- 📖 [完整文档](README.md) - 详细的使用说明和功能介绍
- 🚀 [快速配置指南](QUICK_SETUP.md) - 一步步配置数据库
- 🔧 [Alembic迁移文档](../../alembic/README) - 数据库迁移管理
