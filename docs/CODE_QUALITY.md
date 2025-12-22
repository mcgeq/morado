# 代码质量检查指南

本文档描述了项目中使用的代码质量检查工具和最佳实践。

## 工具概览

### 编辑器配置

1. **EditorConfig** - 跨编辑器的代码风格统一工具

### 后端 (Python)

1. **Ruff** - 快速的 Python linter 和 formatter
2. **Ty** - 快速的 Python 类型检查器

### 前端 (TypeScript/Vue)

1. **ESLint** - JavaScript/TypeScript linter
2. **TypeScript Compiler** - 类型检查

## EditorConfig 配置

EditorConfig 帮助在不同编辑器和 IDE 之间保持一致的代码风格。

### 配置说明

项目根目录的 `.editorconfig` 文件定义了以下规则：

#### 通用规则
- **字符编码**: UTF-8
- **换行符**: LF (Unix 风格)
- **文件结尾**: 自动添加空行
- **尾随空格**: 自动删除

#### Python 文件 (*.py)
- **缩进**: 4 个空格
- **最大行长**: 120 字符

#### JavaScript/TypeScript/Vue 文件
- **缩进**: 2 个空格
- **最大行长**: 100 字符

#### 配置文件 (YAML, JSON, TOML)
- **缩进**: 2 个空格

### 编辑器支持

大多数现代编辑器都原生支持或通过插件支持 EditorConfig：

- **VS Code**: 安装 "EditorConfig for VS Code" 插件
- **IntelliJ IDEA / PyCharm**: 内置支持
- **Sublime Text**: 安装 "EditorConfig" 插件
- **Vim**: 安装 "editorconfig-vim" 插件
- **Atom**: 安装 "editorconfig" 插件

### 验证配置

```bash
# 检查 EditorConfig 是否生效
# 创建一个测试文件，观察编辑器是否自动应用配置

# Python 文件应该使用 4 空格缩进
echo "def test():" > test.py

# TypeScript 文件应该使用 2 空格缩进
echo "function test() {" > test.ts
```

## 后端代码质量检查

### 1. Ruff 检查

Ruff 是一个极快的 Python linter，用于检查代码风格和常见错误。

#### 基本用法

```bash
# 检查所有代码
ruff check backend/src/morado backend/scripts tests

# 自动修复可修复的问题
ruff check --fix backend/src/morado backend/scripts tests

# 检查特定目录
ruff check backend/src/morado/models

# 显示统计信息
ruff check backend/src/morado --statistics
```

#### 配置

Ruff 配置在 `pyproject.toml` 中：

```toml
[tool.ruff]
target-version = "py313"
output-format = "full"

[tool.ruff.lint]
select = [
    "F",     # Pyflakes
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "I",     # isort
    "UP",    # pyupgrade
    # ... 更多规则
]

ignore = [
    "E501",    # Line too long (由 formatter 处理)
    "RUF001",  # Ambiguous unicode character (允许中文)
    # ... 更多忽略规则
]
```

### 2. Ty 类型检查

Ty 是一个快速的 Python 类型检查器，用于验证类型注解的正确性。

#### 基本用法

```bash
# 检查所有代码
ty check backend/src

# 检查特定目录
ty check backend/src/morado/models

# 显示详细错误信息
ty check backend/src --verbose
```

#### 配置

Ty 配置在 `pyproject.toml` 中：

```toml
[tool.ty]

[tool.ty.src]
root = "backend/src"

[tool.ty.environment]
python-version = "3.13"
extra-paths = ["./backend/src"]
```

### 3. 开发工作流

#### 编写新代码时

1. **编写代码**
   ```python
   # backend/src/morado/models/example.py
   from typing import TYPE_CHECKING
   
   if TYPE_CHECKING:
       from morado.models.user import User
   
   class Example:
       def __init__(self, user: "User") -> None:
           self.user = user
   ```

2. **运行 Ruff 检查并自动修复**
   ```bash
   ruff check --fix backend/src/morado/models/example.py
   ```

3. **运行 Ty 类型检查**
   ```bash
   ty check backend/src/morado/models
   ```

4. **修复错误**
   - 根据 Ruff 和 Ty 的输出修复问题
   - 重复步骤 2-3 直到没有错误

#### 提交代码前

```bash
# 完整检查
ruff check backend/src/morado backend/scripts tests
ty check backend/src

# 如果有错误，自动修复
ruff check --fix backend/src/morado backend/scripts tests

# 再次检查
ruff check backend/src/morado backend/scripts tests
ty check backend/src
```

### 4. 常见问题和解决方案

#### 问题 1: 循环导入

**错误**: `F821 Undefined name 'User'`

**解决方案**: 使用 `TYPE_CHECKING`

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from morado.models.user import User

class Example:
    user: "User"  # 使用字符串注解
```

#### 问题 2: 行太长

**错误**: `E501 Line too long (120 > 88)`

**解决方案**: 
- 已在配置中忽略 (E501)
- 或者手动换行

```python
# 换行
result = some_function(
    parameter1,
    parameter2,
    parameter3
)
```

#### 问题 3: 中文字符警告

**错误**: `RUF001 Ambiguous unicode character`

**解决方案**: 已在配置中忽略 (RUF001, RUF002, RUF003)

#### 问题 4: 缺少 `__init__.py`

**错误**: `INP001 File is part of an implicit namespace package`

**解决方案**: 创建 `__init__.py` 文件

```bash
# 创建空的 __init__.py
touch backend/src/morado/new_module/__init__.py
```

## 前端代码质量检查

### 1. ESLint 检查

```bash
# 检查所有代码
cd frontend
bun run lint

# 自动修复
bun run lint:fix
```

### 2. TypeScript 类型检查

```bash
# 类型检查
cd frontend
bun run type-check

# 或直接使用 tsc
tsc --noEmit
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  backend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install ruff ty
      
      - name: Run Ruff
        run: ruff check backend/src backend/scripts tests
      
      - name: Run Ty
        run: ty check backend/src
  
  frontend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
      
      - name: Install dependencies
        run: |
          cd frontend
          bun install
      
      - name: Run ESLint
        run: |
          cd frontend
          bun run lint
      
      - name: Run TypeScript check
        run: |
          cd frontend
          bun run type-check
```

## 代码质量标准

### 必须满足的标准

1. ✅ **Ruff 检查**: 0 错误
2. ✅ **Ty 类型检查**: 0 严重错误（允许警告）
3. ✅ **所有测试通过**: 100%
4. ✅ **测试覆盖率**: ≥ 80%

### 推荐的标准

1. 📝 **文档字符串**: 所有公共函数和类都有文档
2. 📝 **类型注解**: 所有函数参数和返回值都有类型注解
3. 📝 **注释**: 复杂逻辑有清晰的注释
4. 📝 **命名规范**: 遵循 PEP 8 命名规范

## 快速参考

### 常用命令

```bash
# 后端完整检查
ruff check backend/src/morado backend/scripts tests
ty check backend/src

# 后端自动修复
ruff check --fix backend/src/morado backend/scripts tests

# 前端完整检查
cd frontend && bun run lint && bun run type-check

# 前端自动修复
cd frontend && bun run lint:fix
```

### 检查特定模块

```bash
# 检查 models
ruff check backend/src/morado/models
ty check backend/src/morado/models

# 检查 services
ruff check backend/src/morado/services
ty check backend/src/morado/services

# 检查 API
ruff check backend/src/morado/api
ty check backend/src/morado/api
```

## 最佳实践

### 开发环境设置

1. **安装 EditorConfig 插件**
   - 确保你的编辑器支持 EditorConfig
   - 这样可以自动应用项目的代码风格规则

2. **配置 Git Hooks**
   ```bash
   # 可以使用 pre-commit 工具自动运行检查
   pip install pre-commit
   
   # 创建 .pre-commit-config.yaml
   # 在每次提交前自动运行 ruff 和 ty
   ```

3. **IDE 集成**
   - **VS Code**: 安装 Python、Ruff、Pylance 扩展
   - **PyCharm**: 配置外部工具运行 ruff 和 ty
   - **Vim/Neovim**: 配置 ALE 或 coc.nvim

### 代码审查清单

提交代码前确保：

- ✅ EditorConfig 规则已应用（缩进、换行符等）
- ✅ Ruff 检查通过（0 错误）
- ✅ Ty 类型检查通过（0 严重错误）
- ✅ 所有测试通过
- ✅ 代码有适当的注释和文档字符串
- ✅ 没有调试代码（print、console.log 等）
- ✅ 敏感信息已移除（密码、API 密钥等）

## 总结

- 🎨 **统一风格**: 使用 EditorConfig 确保团队代码风格一致
- 🔍 **定期检查**: 每次提交前运行代码质量检查
- 🔧 **自动修复**: 使用 `--fix` 选项自动修复简单问题
- 📊 **持续改进**: 定期审查和更新代码质量标准
- 🎯 **零容忍**: 不允许提交有错误的代码

遵循这些指南可以确保代码库保持高质量和一致性！
