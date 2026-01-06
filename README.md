# Morado 测试平台

Morado 是一个现代化的自动化测试平台，采用前后端分离的 BS 架构设计。平台实现了独特的四层架构，支持 API 接口定义、脚本编写、组件组合和测试用例管理的完整测试流程。

## 特性

- **四层架构设计**：从接口定义到测试用例的清晰层次结构
- **高度复用**：Header、Body、脚本、组件都可以独立管理和复用
- **灵活组合**：支持组件嵌套、参数覆盖、变量传递
- **独立调试**：每一层都可以独立调试执行
- **现代技术栈**：Vue 3 + Litestar + SQLAlchemy

## 技术栈

### 后端
- Python 3.13+
- Litestar (Web 框架)
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- PostgreSQL (数据库)
- Redis (缓存)

### 前端
- Vue 3 (Composition API)
- Vite 8 (构建工具)
- Tailwind CSS 4 (样式框架)
- Pinia (状态管理)
- Vue Router (路由)

## 快速启动

### 环境要求

- Python 3.13+
- Node.js 20+ 或 Bun 1.0+
- PostgreSQL 15+
- Redis 7+

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖 (使用 uv)
uv sync

# 初始化数据库
uv run alembic upgrade head

# 填充测试数据 (可选)
uv run python scripts/seed_data.py

# 启动开发服务器
uv run uvicorn src.morado.app:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖 (使用 Bun)
bun install

# 启动开发服务器
bun run dev
```

### Docker 启动

```bash
# 使用 Docker Compose 启动完整环境
cd deployment
docker-compose up -d

# 开发环境
docker-compose -f docker-compose.dev.yml up -d
```

## 目录结构

```
morado/
├── frontend/                 # 前端应用 (Vue 3)
│   ├── src/
│   │   ├── api/             # API 调用封装
│   │   ├── components/      # Vue 组件
│   │   │   ├── common/      # 通用组件
│   │   │   └── business/    # 业务组件
│   │   ├── composables/     # 组合式函数
│   │   ├── layouts/         # 布局组件
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── styles/          # 样式文件
│   │   ├── types/           # TypeScript 类型
│   │   ├── utils/           # 工具函数
│   │   └── views/           # 页面视图
│   └── ...
│
├── backend/                  # 后端应用 (Python)
│   ├── src/morado/
│   │   ├── api/             # API 路由层
│   │   │   └── v1/          # API v1 版本
│   │   ├── common/          # 公共模块
│   │   │   ├── http/        # HTTP 客户端
│   │   │   ├── logger/      # 日志模块
│   │   │   └── utils/       # 工具函数
│   │   ├── core/            # 核心配置
│   │   ├── middleware/      # 中间件
│   │   ├── models/          # 数据模型 (SQLAlchemy)
│   │   ├── repositories/    # 数据访问层
│   │   ├── schemas/         # Pydantic 数据结构
│   │   └── services/        # 业务逻辑层
│   ├── alembic/             # 数据库迁移
│   ├── config/              # 配置文件
│   └── scripts/             # 脚本工具
│
├── tests/                    # 测试代码
│   ├── backend/             # 后端测试
│   │   ├── unit/            # 单元测试
│   │   └── integration/     # 集成测试
│   └── frontend/            # 前端测试
│       ├── unit/            # 组件测试
│       └── e2e/             # 端到端测试
│
├── deployment/               # 部署配置
│   ├── docker/              # Docker 配置
│   └── k8s/                 # Kubernetes 配置
│
├── docs/                     # 项目文档
│   └── api/                 # API 文档
│
└── scripts/                  # 项目脚本
```

## 四层架构概述

Morado 采用独特的四层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│              第四层：测试用例层 (Test Case)                   │
│  用户直接操作的测试单元，可引用脚本或组件                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              第三层：联合组件层 (Component)                   │
│  多个脚本的组合，支持嵌套引用                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              第二层：脚本层 (Script)                          │
│  接口的实际实现和测试逻辑                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              第一层：接口定义层 (API Definition)              │
│  Header + Body + API Definition                              │
└─────────────────────────────────────────────────────────────┘
```

详细架构说明请参考 [四层架构文档](docs/four-layer-architecture.md)。

## 文档

- [架构设计](docs/architecture.md) - 系统架构和技术栈说明
- [四层架构指南](docs/four-layer-guide.md) - 四层架构使用指南
- [开发指南](docs/development.md) - 开发规范和工作流
- [部署指南](docs/deployment.md) - 部署步骤和配置说明
- [API 文档](docs/api/) - API 接口文档

## 开发

### 代码规范

后端使用 Ruff 进行代码检查和格式化：

```bash
# 检查代码
ruff check backend/

# 自动修复
ruff check --fix backend/

# 类型检查
ty check backend/src
```

前端使用 Biome 进行代码检查和格式化：

```bash
cd frontend

# 格式化代码
bun run format

# 检查代码
bun run lint

# 自动修复
bun run lint:fix
```

### 运行测试

```bash
# 后端测试
pytest tests/backend -v

# 前端测试
cd frontend && bun run test:run
```

## 许可证

[MIT License](LICENSE)
