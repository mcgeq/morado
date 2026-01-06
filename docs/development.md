# Morado 开发指南

本文档描述 Morado 项目的开发规范、工作流程和最佳实践。

## 目录

1. [开发环境设置](#开发环境设置)
2. [代码规范](#代码规范)
3. [Git 工作流](#git-工作流)
4. [测试要求](#测试要求)
5. [代码审查](#代码审查)
6. [发布流程](#发布流程)

## 开发环境设置

### 系统要求

- Python 3.13+
- Node.js 20+ 或 Bun 1.0+
- PostgreSQL 15+
- Redis 7+
- Git 2.40+

### 后端环境

```bash
# 克隆项目
git clone https://github.com/your-org/morado.git
cd morado

# 安装 uv (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv sync

# 安装开发依赖
uv sync --group dev --group test

# 配置环境变量
cp backend/config/development.toml.example backend/config/development.toml
# 编辑配置文件设置数据库连接等

# 初始化数据库
cd backend
uv run alembic upgrade head

# 启动开发服务器
uv run uvicorn src.morado.app:app --reload
```

### 前端环境

```bash
cd frontend

# 安装 Bun
curl -fsSL https://bun.sh/install | bash

# 安装依赖
bun install

# 配置环境变量
cp .env.development.example .env.development

# 启动开发服务器
bun run dev
```

### IDE 配置

推荐使用 VS Code，安装以下扩展：

- Python
- Pylance
- Vue - Official
- Tailwind CSS IntelliSense
- Biome

项目已包含 `.vscode/settings.json` 配置文件。

## 代码规范

### Python 代码规范

使用 Ruff 进行代码检查和格式化：

```bash
# 检查代码
ruff check backend/

# 自动修复
ruff check --fix backend/

# 格式化代码
ruff format backend/

# 类型检查
ty check backend/src
```

#### Python 代码风格

- 遵循 PEP 8 规范
- 使用类型注解
- 函数和类必须有 docstring
- 最大行长度 88 字符（由 Ruff 格式化器处理）

```python
# 示例代码风格
from typing import Optional

def create_user(
    name: str,
    email: str,
    age: Optional[int] = None,
) -> User:
    """创建新用户。

    Args:
        name: 用户名
        email: 邮箱地址
        age: 年龄（可选）

    Returns:
        创建的用户对象

    Raises:
        ValidationError: 如果数据验证失败
    """
    # 实现代码
    pass
```

#### 导入顺序

1. 标准库
2. 第三方库
3. 本地模块

```python
# 标准库
import os
from datetime import datetime
from typing import Optional

# 第三方库
from litestar import Controller, get, post
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 本地模块
from morado.models import User
from morado.services import UserService
```

### TypeScript/Vue 代码规范

使用 Biome 进行代码检查和格式化：

```bash
cd frontend

# 格式化代码
bun run format

# 检查代码
bun run lint

# 自动修复
bun run lint:fix

# 完整检查
bun run check
```

#### Vue 组件规范

- 使用 Composition API
- 使用 `<script setup>` 语法
- Props 必须定义类型
- 组件名使用 PascalCase

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
})

const emit = defineEmits<{
  (e: 'update', value: number): void
}>()

const localCount = ref(props.count)

const doubleCount = computed(() => localCount.value * 2)

function increment() {
  localCount.value++
  emit('update', localCount.value)
}
</script>

<template>
  <div class="component">
    <h2>{{ title }}</h2>
    <p>Count: {{ localCount }}</p>
    <p>Double: {{ doubleCount }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| Python 变量/函数 | snake_case | `user_name`, `get_user()` |
| Python 类 | PascalCase | `UserService`, `TestCase` |
| Python 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `API_VERSION` |
| TypeScript 变量/函数 | camelCase | `userName`, `getUser()` |
| TypeScript 类/接口 | PascalCase | `UserService`, `IUser` |
| Vue 组件 | PascalCase | `UserCard.vue`, `TestList.vue` |
| CSS 类 | kebab-case | `user-card`, `test-list` |
| 文件名 | snake_case (Python), kebab-case (TS) | `user_service.py`, `user-card.vue` |

## Git 工作流

### 分支策略

采用 Git Flow 工作流：

```
main          ─────────────────────────────────────────────►
                    │                           │
release       ──────┼───────────────────────────┼──────────►
                    │           │               │
develop       ──────┼───────────┼───────────────┼──────────►
                    │     │     │         │     │
feature/xxx   ──────┴─────┘     │         │     │
                                │         │     │
feature/yyy   ──────────────────┴─────────┘     │
                                                │
hotfix/zzz    ──────────────────────────────────┘
```

- `main`: 生产环境代码
- `release`: 预发布分支
- `develop`: 开发主分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 分支命名

```
feature/add-user-authentication
feature/JIRA-123-implement-test-execution
bugfix/fix-header-validation
hotfix/critical-security-patch
```

### 提交规范

使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型 (type)

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构（不是新功能或修复） |
| perf | 性能优化 |
| test | 测试相关 |
| chore | 构建/工具相关 |

#### 示例

```
feat(api): add header component CRUD endpoints

- Implement HeaderController with all CRUD operations
- Add HeaderService for business logic
- Add HeaderRepository for data access

Closes #123
```

```
fix(frontend): resolve header list pagination issue

The pagination was not updating correctly when changing page size.
Fixed by recalculating total pages on page size change.

Fixes #456
```

### Pull Request 流程

1. 从 `develop` 创建功能分支
2. 完成开发和测试
3. 提交 Pull Request
4. 通过代码审查
5. 合并到 `develop`

#### PR 模板

```markdown
## 描述
简要描述此 PR 的更改内容

## 更改类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 重构
- [ ] 其他

## 测试
- [ ] 添加了单元测试
- [ ] 添加了集成测试
- [ ] 所有测试通过

## 检查清单
- [ ] 代码符合项目规范
- [ ] 已更新相关文档
- [ ] 已自测功能正常

## 相关 Issue
Closes #xxx
```

## 测试要求

### 测试类型

1. **单元测试**: 测试单个函数/方法
2. **集成测试**: 测试组件间交互
3. **属性测试**: 使用 Hypothesis 进行属性测试
4. **端到端测试**: 测试完整用户流程

### 后端测试

```bash
# 运行所有测试
pytest tests/backend -v

# 运行单元测试
pytest tests/backend/unit -v

# 运行集成测试
pytest tests/backend/integration -v

# 运行带覆盖率
pytest tests/backend --cov=backend/src --cov-report=html

# 运行特定测试
pytest tests/backend/unit/test_services/test_header.py -v
```

#### 测试文件结构

```
tests/backend/
├── conftest.py           # 共享 fixtures
├── unit/
│   ├── test_services/
│   │   ├── test_header.py
│   │   └── test_script.py
│   ├── test_repositories/
│   └── test_utils/
└── integration/
    └── test_api/
        ├── test_header_api.py
        └── test_script_api.py
```

#### 测试示例

```python
import pytest
from hypothesis import given, strategies as st

from morado.services import HeaderService


class TestHeaderService:
    """HeaderService 单元测试"""

    def test_create_header_success(self, db_session):
        """测试成功创建 Header"""
        service = HeaderService()
        header = service.create_header(
            db_session,
            name="Test Header",
            headers={"Authorization": "Bearer token"},
        )
        
        assert header.id is not None
        assert header.name == "Test Header"

    def test_create_header_empty_name_fails(self, db_session):
        """测试空名称创建失败"""
        service = HeaderService()
        
        with pytest.raises(ValidationError):
            service.create_header(
                db_session,
                name="",
                headers={},
            )

    # 属性测试示例
    @given(name=st.text(min_size=1, max_size=100))
    def test_header_name_preserved(self, db_session, name):
        """属性测试：Header 名称应被保留"""
        service = HeaderService()
        header = service.create_header(
            db_session,
            name=name,
            headers={},
        )
        
        assert header.name == name
```

### 前端测试

```bash
cd frontend

# 运行所有测试
bun run test:run

# 运行测试（监视模式）
bun run test

# 运行带 UI
bun run test:ui

# 运行带覆盖率
bun run test:coverage
```

#### 组件测试示例

```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import HeaderCard from '@/components/business/HeaderCard.vue'

describe('HeaderCard', () => {
  it('renders header name', () => {
    render(HeaderCard, {
      props: {
        header: {
          id: 1,
          name: 'Test Header',
          headers: { 'Content-Type': 'application/json' },
        },
      },
    })

    expect(screen.getByText('Test Header')).toBeInTheDocument()
  })

  it('emits edit event on button click', async () => {
    const user = userEvent.setup()
    const { emitted } = render(HeaderCard, {
      props: {
        header: { id: 1, name: 'Test', headers: {} },
      },
    })

    await user.click(screen.getByRole('button', { name: /edit/i }))

    expect(emitted()).toHaveProperty('edit')
  })
})
```

### 测试覆盖率要求

| 类型 | 最低覆盖率 |
|------|-----------|
| 后端单元测试 | 80% |
| 后端集成测试 | 60% |
| 前端组件测试 | 70% |

## 代码审查

### 审查清单

- [ ] 代码符合项目规范
- [ ] 有适当的测试覆盖
- [ ] 没有安全漏洞
- [ ] 性能合理
- [ ] 文档已更新
- [ ] 没有硬编码的敏感信息

### 审查重点

1. **正确性**: 代码是否正确实现了需求
2. **可读性**: 代码是否易于理解
3. **可维护性**: 代码是否易于修改和扩展
4. **性能**: 是否有明显的性能问题
5. **安全性**: 是否有安全漏洞

## 发布流程

### 版本号规范

使用语义化版本 (SemVer)：`MAJOR.MINOR.PATCH`

- MAJOR: 不兼容的 API 更改
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的 Bug 修复

### 发布步骤

1. 从 `develop` 创建 `release/x.y.z` 分支
2. 更新版本号和 CHANGELOG
3. 进行最终测试
4. 合并到 `main` 和 `develop`
5. 创建 Git Tag
6. 构建和部署

```bash
# 创建发布分支
git checkout develop
git pull
git checkout -b release/1.2.0

# 更新版本号
# 编辑 pyproject.toml 和 package.json

# 提交更改
git add .
git commit -m "chore: bump version to 1.2.0"

# 合并到 main
git checkout main
git merge release/1.2.0

# 创建 Tag
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

# 合并回 develop
git checkout develop
git merge release/1.2.0
git push origin develop

# 删除发布分支
git branch -d release/1.2.0
```

## 相关文档

- [架构设计](architecture.md)
- [部署指南](deployment.md)
- [API 文档](api/)
