# EditorConfig 和代码规范配置

本文档说明项目中新增的 EditorConfig 和代码质量工具配置。

## 新增文件

### 1. `.editorconfig`

跨编辑器的代码风格统一配置文件。

**主要配置**:
- **Python 文件**: 4 空格缩进，最大行长 120
- **JavaScript/TypeScript/Vue**: 2 空格缩进，最大行长 100
- **配置文件 (YAML/JSON/TOML)**: 2 空格缩进
- **统一换行符**: LF (Unix 风格)
- **字符编码**: UTF-8
- **自动删除尾随空格**
- **文件末尾自动添加空行**

### 2. `.pre-commit-config.yaml`

Git pre-commit hooks 配置，在提交前自动运行代码质量检查。

**包含的检查**:
- ✅ 通用文件检查（尾随空格、文件结尾、YAML/JSON 语法）
- ✅ Python: Ruff linter 和 formatter
- ✅ Markdown: markdownlint
- ✅ 安全检查: detect-secrets
- ⏸️ Python 类型检查: ty (可选，默认禁用以提高速度)
- ⏸️ 前端: ESLint (待前端项目初始化后启用)

### 3. `.gitignore` (更新)

添加了更多忽略项：
- 代码质量工具缓存 (`.ruff_cache/`, `.mypy_cache/`)
- 环境文件 (`.env`, `.env.local`)
- 数据库文件 (`.db`, `.sqlite`)
- 日志文件 (`*.log`, `logs/`)
- 前端相关 (待启用)

### 4. 文档

- **`docs/CODE_QUALITY.md`**: 代码质量检查完整指南（已更新，添加 EditorConfig 说明）
- **`docs/SETUP_DEVELOPMENT.md`**: 开发环境设置详细指南（新增）
- **`docs/EDITORCONFIG_SETUP.md`**: 本文档

## 快速开始

### 1. 安装 EditorConfig 插件

根据你的编辑器安装相应插件：

```bash
# VS Code
code --install-extension EditorConfig.EditorConfig

# 其他编辑器请参考 docs/SETUP_DEVELOPMENT.md
```

### 2. 安装 pre-commit (可选但推荐)

```bash
# 使用 uv
uv pip install pre-commit

# 初始化 hooks
pre-commit install

# 测试运行
pre-commit run --all-files
```

### 3. 验证配置

```bash
# 检查 Python 代码
ruff check backend/src/morado backend/scripts tests

# 检查类型
ty check backend/src

# 运行测试
pytest tests/
```

## 使用说明

### EditorConfig

安装插件后，编辑器会自动应用配置：
- 打开 `.py` 文件，按 Tab → 4 空格
- 打开 `.ts` 文件，按 Tab → 2 空格
- 保存文件时自动删除尾随空格
- 保存文件时自动添加文件末尾空行

### Pre-commit Hooks

安装后，每次 `git commit` 时自动运行：

```bash
# 正常提交 - 自动运行检查
git add .
git commit -m "feat: add new feature"

# 如果检查失败，修复后重新提交
# 某些问题会自动修复，需要重新 add
git add .
git commit -m "feat: add new feature"

# 紧急情况下跳过检查（不推荐）
git commit --no-verify -m "urgent fix"
```

### 手动运行检查

```bash
# 运行所有 pre-commit 检查
pre-commit run --all-files

# 只运行特定检查
pre-commit run ruff --all-files
pre-commit run markdownlint --all-files

# 检查特定文件
pre-commit run --files backend/src/morado/models/user.py
```

## 配置说明

### EditorConfig 规则

```ini
# Python 文件
[*.py]
indent_style = space
indent_size = 4
max_line_length = 120

# TypeScript/Vue 文件
[*.{js,jsx,ts,tsx,vue}]
indent_style = space
indent_size = 2
max_line_length = 100

# 配置文件
[*.{yml,yaml,json,toml}]
indent_style = space
indent_size = 2
```

### Pre-commit 配置

主要 hooks：

1. **trailing-whitespace**: 删除尾随空格
2. **end-of-file-fixer**: 确保文件末尾有空行
3. **check-yaml/json/toml**: 验证配置文件语法
4. **ruff**: Python linter 和 formatter
5. **markdownlint**: Markdown 格式检查
6. **detect-secrets**: 检测敏感信息泄露

### 自定义配置

#### 禁用特定 hook

编辑 `.pre-commit-config.yaml`，注释掉不需要的 hook：

```yaml
# - repo: https://github.com/igorshubovych/markdownlint-cli
#   rev: v0.43.0
#   hooks:
#     - id: markdownlint
```

#### 启用 ty 类型检查

取消注释 `.pre-commit-config.yaml` 中的 ty 配置：

```yaml
- repo: local
  hooks:
    - id: ty-check
      name: Ty type checker (Python)
      entry: ty check backend/src
      language: system
      pass_filenames: false
      files: ^backend/.*\.py$
```

#### 添加文件排除

编辑 `.pre-commit-config.yaml` 的 `exclude` 部分：

```yaml
exclude: |
  (?x)^(
    \.git/|
    \.venv/|
    your_custom_pattern/|
  )
```

## 最佳实践

### 开发工作流

1. **首次设置**
   ```bash
   # 安装 EditorConfig 插件
   # 安装 pre-commit
   pre-commit install
   ```

2. **日常开发**
   ```bash
   # 编写代码（编辑器自动应用 EditorConfig）
   # 提交代码（pre-commit 自动检查）
   git add .
   git commit -m "feat: new feature"
   ```

3. **提交前检查**
   ```bash
   # 手动运行完整检查
   ruff check --fix backend/src/morado
   ty check backend/src
   pytest tests/
   
   # 或使用 pre-commit
   pre-commit run --all-files
   ```

### 团队协作

1. **新成员入职**: 按照 `docs/SETUP_DEVELOPMENT.md` 设置环境
2. **代码审查**: 确保所有检查通过
3. **CI/CD**: 在 CI 中运行相同的检查

### 常见问题

#### Q: EditorConfig 不生效？
A: 确保安装了编辑器插件并重启编辑器

#### Q: Pre-commit 太慢？
A: 禁用 ty 类型检查，只在 CI 中运行

#### Q: 如何临时跳过检查？
A: 使用 `git commit --no-verify`（不推荐）

#### Q: 如何更新 pre-commit hooks？
A: 运行 `pre-commit autoupdate`

## 相关文档

- [CODE_QUALITY.md](./CODE_QUALITY.md) - 代码质量检查完整指南
- [SETUP_DEVELOPMENT.md](./SETUP_DEVELOPMENT.md) - 开发环境设置详细指南
- [EditorConfig 官网](https://editorconfig.org/)
- [Pre-commit 官网](https://pre-commit.com/)

## 总结

✅ **已配置**:
- EditorConfig 统一代码风格
- Pre-commit hooks 自动化检查
- 完善的 .gitignore
- 详细的文档

✅ **效果**:
- 团队代码风格一致
- 提交前自动检查质量
- 减少代码审查时间
- 提高代码质量

✅ **下一步**:
- 团队成员安装 EditorConfig 插件
- 团队成员安装 pre-commit
- 在 CI/CD 中集成相同检查
- 根据团队需求调整配置
