# 开发环境设置指南

本文档描述如何设置开发环境以确保代码质量和一致性。

## 目录

- [必需工具](#必需工具)
- [EditorConfig 设置](#editorconfig-设置)
- [Pre-commit Hooks 设置](#pre-commit-hooks-设置)
- [Python 开发环境](#python-开发环境)
- [前端开发环境](#前端开发环境)
- [验证设置](#验证设置)

## 必需工具

### 1. Python 3.13+

```bash
# 检查 Python 版本
python --version

# 应该显示 Python 3.13.x
```

### 2. UV (Python 包管理器)

```bash
# 安装 uv
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

### 3. Bun (前端包管理器)

```bash
# 安装 Bun
# Windows
powershell -c "irm bun.sh/install.ps1 | iex"

# macOS/Linux
curl -fsSL https://bun.sh/install | bash

# 验证安装
bun --version
```

## EditorConfig 设置

### 什么是 EditorConfig？

EditorConfig 帮助在不同编辑器和 IDE 之间保持一致的代码风格。项目根目录的 `.editorconfig` 文件定义了代码风格规则。

### 编辑器插件安装

#### VS Code
```bash
# 安装 EditorConfig 扩展
code --install-extension EditorConfig.EditorConfig
```

推荐的其他扩展：
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Vue - Official (Vue.volar)
- ESLint (dbaeumer.vscode-eslint)

#### PyCharm / IntelliJ IDEA
- 内置支持，无需额外安装

#### Sublime Text
```bash
# 使用 Package Control 安装
# Ctrl+Shift+P -> Install Package -> EditorConfig
```

#### Vim / Neovim
```vim
" 使用 vim-plug
Plug 'editorconfig/editorconfig-vim'
```

### 验证 EditorConfig

创建测试文件验证配置是否生效：

```bash
# Python 文件应该使用 4 空格缩进
echo "def test():" > test.py

# TypeScript 文件应该使用 2 空格缩进
echo "function test() {" > test.ts

# 在编辑器中打开这些文件，按 Tab 键应该自动使用正确的缩进
```

## Pre-commit Hooks 设置

Pre-commit hooks 在每次 git commit 前自动运行代码质量检查。

### 安装 pre-commit

```bash
# 使用 uv 安装
uv pip install pre-commit

# 或使用 pip
pip install pre-commit
```

### 初始化 pre-commit

```bash
# 在项目根目录运行
pre-commit install

# 这会在 .git/hooks/ 中创建 pre-commit hook
```

### 手动运行检查

```bash
# 检查所有文件
pre-commit run --all-files

# 只检查暂存的文件
pre-commit run

# 检查特定文件
pre-commit run --files backend/src/morado/models/user.py
```

### 跳过 pre-commit（不推荐）

```bash
# 如果确实需要跳过检查
git commit --no-verify -m "commit message"
```

### 更新 pre-commit hooks

```bash
# 更新到最新版本
pre-commit autoupdate
```

## Python 开发环境

### 1. 创建虚拟环境

```bash
# 使用 uv 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. 安装依赖

```bash
# 安装所有依赖（包括开发依赖）
uv pip install -e ".[dev,test]"

# 或者只安装开发依赖
uv pip install ruff ty pytest pytest-cov
```

### 3. 验证工具安装

```bash
# 检查 ruff
ruff --version

# 检查 ty
ty --version

# 检查 pytest
pytest --version
```

### 4. 运行代码质量检查

```bash
# Ruff 检查
ruff check backend/src/morado backend/scripts tests

# Ruff 自动修复
ruff check --fix backend/src/morado backend/scripts tests

# Ty 类型检查
ty check backend/src

# 运行测试
pytest tests/
```

## 前端开发环境

### 1. 安装依赖

```bash
cd frontend

# 使用 Bun 安装依赖
bun install
```

### 2. 配置 ESLint 和 TypeScript

```bash
# 运行 ESLint 检查
bun run lint

# 自动修复
bun run lint:fix

# TypeScript 类型检查
bun run type-check
```

### 3. 开发服务器

```bash
# 启动开发服务器
bun run dev

# 构建生产版本
bun run build
```

## 验证设置

### 完整验证流程

```bash
# 1. 验证 EditorConfig
# 打开任意 .py 文件，按 Tab 应该是 4 空格
# 打开任意 .ts 文件，按 Tab 应该是 2 空格

# 2. 验证 pre-commit
pre-commit run --all-files

# 3. 验证 Python 工具
ruff check backend/src/morado
ty check backend/src

# 4. 验证测试
pytest tests/ -v

# 5. 提交测试
git add .
git commit -m "test: verify development setup"
# 应该自动运行 pre-commit hooks
```

### 常见问题

#### 问题 1: pre-commit 运行很慢

**解决方案**: 
- 可以禁用 ty 类型检查（在 `.pre-commit-config.yaml` 中注释掉）
- 只在 CI/CD 中运行完整的类型检查

#### 问题 2: EditorConfig 不生效

**解决方案**:
- 确保安装了编辑器插件
- 重启编辑器
- 检查 `.editorconfig` 文件是否在项目根目录

#### 问题 3: ruff 和编辑器格式化冲突

**解决方案**:
- 在编辑器中禁用其他 Python 格式化工具（如 autopep8, black）
- 只使用 ruff 作为格式化工具

#### 问题 4: Windows 换行符问题

**解决方案**:
- EditorConfig 已配置使用 LF
- 运行 `git config --global core.autocrlf false`
- 重新克隆仓库或运行 `git add --renormalize .`

## 推荐的开发工作流

### 日常开发

1. **开始工作前**
   ```bash
   git pull
   uv pip install -e ".[dev,test]"  # 更新依赖
   ```

2. **编写代码**
   - 编辑器会自动应用 EditorConfig 规则
   - 保存时自动格式化（如果配置了）

3. **提交前检查**
   ```bash
   # 运行快速检查
   ruff check --fix backend/src/morado
   
   # 运行测试
   pytest tests/ -v
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # pre-commit hooks 自动运行
   ```

5. **推送代码**
   ```bash
   git push
   ```

### 代码审查前

```bash
# 完整的质量检查
ruff check backend/src/morado backend/scripts tests
ty check backend/src
pytest tests/ --cov=backend/src/morado --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

## 团队协作

### 新成员入职

1. 克隆仓库
2. 按照本文档设置开发环境
3. 运行 `pre-commit run --all-files` 验证设置
4. 创建测试提交验证 hooks 工作正常

### 代码规范

- 遵循 `.editorconfig` 定义的风格
- 所有代码必须通过 ruff 检查
- 所有代码必须通过 ty 类型检查
- 所有测试必须通过
- 测试覆盖率应 ≥ 80%

### 持续集成

CI/CD 管道会运行相同的检查：
- Ruff linting
- Ty type checking
- Pytest 测试
- 覆盖率报告

确保本地通过所有检查后再推送代码。

## 总结

✅ **必需步骤**:
1. 安装 EditorConfig 插件
2. 安装 pre-commit 并运行 `pre-commit install`
3. 安装 Python 开发依赖
4. 验证所有工具正常工作

✅ **推荐步骤**:
1. 配置编辑器自动格式化
2. 配置编辑器显示类型提示
3. 配置编辑器集成测试运行器

✅ **最佳实践**:
1. 提交前运行 `ruff check --fix`
2. 定期运行完整测试套件
3. 保持依赖更新
4. 遵循团队代码规范

有问题？查看 [CODE_QUALITY.md](./CODE_QUALITY.md) 获取更多信息。
