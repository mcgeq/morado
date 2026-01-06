# Database Scripts

This directory contains database management scripts for the Morado test platform.

## Scripts

### seed_four_layer_data.py

Seeds comprehensive test data for the four-layer architecture.

#### What it creates:

**Layer 1: API Definition Components**
- **Headers** (3 samples):
  - 认证Header (Authentication Header with Bearer Token)
  - JSON Content-Type Header
  - XML Content-Type Header

- **Bodies** (3 samples):
  - 用户信息Body (User information request/response body)
  - 订单信息Body (Order information body)
  - 登录请求Body (Login request body)

- **API Definitions** (4 samples):
  - 获取用户信息 (Get user info - references Header + Body)
  - 创建用户 (Create user - references Header + inline Body)
  - 用户登录 (User login - references Header + Body)
  - 获取订单列表 (Get order list - references Header + inline Body)

**Layer 2: Test Scripts**
- **Test Scripts** (4 samples):
  - 测试用户登录 (Test user login with assertions)
  - 获取用户信息 (Get user info with variable extraction)
  - 创建新用户 (Create new user with dynamic data)
  - 准备测试环境 (Setup script for test preparation)

- **Script Parameters** (2 samples):
  - username parameter with validation rules
  - password parameter (marked as sensitive)

**Layer 3: Test Components**
- **Test Components** (3 samples):
  - 用户登录流程 (User login flow - simple component)
  - 用户管理完整测试 (Complete user management - composite component)
  - 登录子流程 (Login sub-flow - nested component, child of composite)

- **Component Scripts** (4 associations):
  - Links scripts to components with execution order and parameter overrides

**Layer 4: Test Cases**
- **Test Cases** (3 samples):
  - 用户注册登录完整流程测试 (Complete user registration and login flow)
  - 用户信息查询测试 (User information query test)
  - 组件嵌套测试 (Component nesting test)

- **Test Case Scripts & Components**:
  - Links scripts and components to test cases with execution order

#### Prerequisites:

1. PostgreSQL database running
2. Database created (name depends on environment)
3. All database tables created (run migrations first)

#### Database Configuration:

The script supports three ways to configure the database connection (in priority order):

**1. Environment Variable (Highest Priority)**

Set the `DATABASE_URL` environment variable:

```bash
# Windows (PowerShell)
$env:DATABASE_URL="postgresql://username:password@host:port/database"
uv run python scripts/database/seed_four_layer_data.py

# Windows (CMD)
set DATABASE_URL=postgresql://username:password@host:port/database
uv run python scripts/database/seed_four_layer_data.py

# Linux/Mac
export DATABASE_URL="postgresql://username:password@host:port/database"
uv run python scripts/database/seed_four_layer_data.py
```

**2. Configuration File (Medium Priority)**

Edit the appropriate config file in `backend/config/`:

- `development.toml` - For development environment
- `testing.toml` - For testing environment  
- `production.toml` - For production environment

Example configuration:
```toml
# Database settings
database_url = "postgresql://morado:morado@localhost:5432/morado_dev"
database_pool_size = 5
database_echo = true
```

**3. Default Fallback (Lowest Priority)**

If neither environment variable nor config file is set, uses:
```
postgresql://postgres:postgres@localhost:5432/morado
```

#### Usage:

**Basic usage (development environment):**
```bash
cd backend
uv run python scripts/database/seed_four_layer_data.py
```

**Specify environment:**
```bash
# Seed development database
uv run python scripts/database/seed_four_layer_data.py --env development

# Seed testing database
uv run python scripts/database/seed_four_layer_data.py --env testing

# Seed production database (use with caution!)
uv run python scripts/database/seed_four_layer_data.py --env production
```

**Using environment variable:**
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://myuser:mypass@localhost:5432/mydb"
uv run python scripts/database/seed_four_layer_data.py

# Linux/Mac
DATABASE_URL="postgresql://myuser:mypass@localhost:5432/mydb" \
  uv run python scripts/database/seed_four_layer_data.py
```

#### Expected Output:

```
Seeding data for environment: development
============================================================
   Using database_url from development.toml
Connecting to database: postgresql+psycopg://morado:****@localhost:5432/morado_dev

1. Creating sample user...
   ✓ Created user: admin

2. Creating sample Headers (Layer 1)...
   ✓ Created 3 headers

3. Creating sample Bodies (Layer 1)...
   ✓ Created 3 bodies

4. Creating sample API Definitions (Layer 1)...
   ✓ Created 4 API definitions

5. Creating sample Test Scripts (Layer 2)...
   ✓ Created 4 test scripts

6. Creating sample Test Components (Layer 3)...
   ✓ Created 3 test components (including nested)

7. Creating sample Test Cases (Layer 4)...
   ✓ Created 3 test cases

8. Committing all changes...
   ✓ All data committed successfully!

============================================================
✓ Test data seeding completed successfully!
============================================================

Summary:
  - Users: 1
  - Headers: 3
  - Bodies: 3
  - API Definitions: 4
  - Test Scripts: 4
  - Test Components: 3
  - Test Cases: 3
```

#### Sample User Credentials:

- **Username**: admin
- **Email**: admin@morado.com
- **Password**: admin123
- **Role**: ADMIN
- **Superuser**: Yes

#### Database Configuration:

To use a different database, you have three options:

**Option 1: Environment Variable (Recommended for CI/CD)**
```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
```

**Option 2: Edit Config File (Recommended for local development)**
Edit `backend/config/development.toml` or `backend/config/testing.toml`:
```toml
database_url = "postgresql://username:password@host:port/database"
```

**Option 3: Command Line with Environment Variable**
```bash
DATABASE_URL="postgresql://username:password@host:port/database" \
  uv run python scripts/database/seed_four_layer_data.py
```

#### Recommended Database Setup:

**Development:**
```toml
# backend/config/development.toml
database_url = "postgresql://morado:morado@localhost:5432/morado_dev"
```

**Testing:**
```toml
# backend/config/testing.toml
database_url = "postgresql://morado:morado@localhost:5432/morado_test"
```

**Production:**
```bash
# Use environment variable in production
export DATABASE_URL="postgresql://prod_user:secure_password@db-server:5432/morado_prod"
```

#### Features Demonstrated:

1. **Header and Body Reusability**: Shows how Headers and Bodies can be created once and referenced by multiple API definitions
2. **Two API Definition Patterns**:
   - Pattern 1: Reference both Header and Body components
   - Pattern 2: Reference Header + use inline Body
3. **Script Variable Extraction**: Scripts extract variables (like auth_token) and pass them to subsequent scripts
4. **Component Nesting**: Demonstrates parent-child component relationships
5. **Parameter Override Hierarchy**: Shows how parameters can be overridden at component and test case levels
6. **Script Types**: Includes SETUP, MAIN, and TEARDOWN script types
7. **Assertions and Validators**: Scripts include various assertion types (status_code, json_path, etc.)

#### Troubleshooting:

**Error: "No module named 'morado'"**
- Make sure you're running from the backend directory
- Use `uv run python` to ensure the virtual environment is activated

**Error: "No module named 'tomli'"**
- Install dependencies: `uv sync`
- The tomli package is required for reading TOML config files

**Error: "connection failed"**
- Ensure PostgreSQL is running
- Check database credentials in config file or environment variable
- Verify the database exists: `psql -U postgres -c "CREATE DATABASE morado_dev;"`
- Test connection: `psql -U morado -d morado_dev -h localhost`

**Error: "relation does not exist"**
- Run database migrations first: `uv run alembic upgrade head`
- Or create tables manually: `uv run python scripts/database/create_tables.py`

**Error: "password authentication failed"**
- Check username and password in config file
- Verify PostgreSQL user exists: `psql -U postgres -c "\du"`
- Create user if needed: `psql -U postgres -c "CREATE USER morado WITH PASSWORD 'morado';"`
- Grant permissions: `psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE morado_dev TO morado;"`

**Want to use different database for each environment?**
- Development: Edit `backend/config/development.toml`
- Testing: Edit `backend/config/testing.toml`
- Production: Set `DATABASE_URL` environment variable

#### Related Scripts:

- `create_tables.py` - Creates all database tables (if not using Alembic)
- See `backend/alembic/` for database migration scripts
