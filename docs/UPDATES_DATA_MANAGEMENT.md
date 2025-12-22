# 数据管理机制文档更新说明

## 更新日期
2025-12-22

## 更新内容

### 1. 设计文档更新 (`.kiro/specs/project-restructure/design.md`)

在"正确性属性"和"错误处理"章节之间添加了新的章节：

**新增章节：数据管理与执行机制**

包含以下内容：
- 概述
- 参数优先级说明
- 变量替换语法
- 执行上下文介绍
- 数据流示例
- 详细文档引用

**位置：** 第322行之后

**目的：** 在设计文档中提供数据管理机制的概要说明，让读者了解系统如何管理测试数据和参数传递。

### 2. 任务列表更新 (`.kiro/specs/project-restructure/tasks.md`)

#### 更新任务 2.15

**原标题：** 实现四层架构的执行引擎

**新标题：** 实现四层架构的执行引擎和数据管理

**新增内容：**
- 明确列出需要实现的执行上下文类
  - VariableResolver
  - ExecutionContext
  - ScriptExecutionContext
  - ComponentExecutionContext
  - TestCaseExecutionContext
- 详细说明参数管理机制
  - 参数优先级
  - 变量替换语法
  - 内置变量
- 详细说明数据流管理
  - 参数传递
  - 变量共享
  - 脚本输出传递
- 添加参考文档链接

**位置：** 任务2.15

#### 新增任务 10.4.1

**标题：** 验证数据管理和参数传递机制

**内容：**
- 验证参数优先级
- 验证变量替换
- 验证内置变量
- 验证参数覆盖逻辑
- 验证变量传递
- 验证环境隔离
- 运行演示脚本
- 添加参考文档链接

**位置：** 任务10.4之后

**目的：** 确保数据管理机制在实现后能够被充分验证。

### 3. 新增文档

#### 详细文档

1. **`docs/data-management-and-execution.md`**
   - 完整的数据管理和执行机制说明
   - 四层架构中的数据流
   - 参数优先级详解
   - 变量替换规则
   - 执行上下文实现
   - 环境配置管理
   - 完整执行流程示例

2. **`docs/parameter-override-logic.md`**
   - 参数覆盖逻辑详解
   - 覆盖规则说明
   - 参数合并过程
   - 覆盖追踪表
   - 实际应用场景
   - 常见误区
   - 最佳实践

3. **`docs/data-management-summary.md`**
   - 快速参考指南
   - 核心概念
   - 变量替换语法表
   - 各层数据管理说明
   - 数据流示例
   - 实现类介绍
   - 最佳实践

#### 实现代码

1. **`backend/src/morado/services/execution_context.py`**
   - VariableResolver: 变量解析和替换
   - ExecutionContext: 基础执行上下文
   - ScriptExecutionContext: 脚本层执行上下文
   - ComponentExecutionContext: 组件层执行上下文
   - TestCaseExecutionContext: 测试用例层执行上下文

#### 演示脚本

1. **`backend/scripts/demo_execution_context.py`**
   - 变量解析器演示
   - 执行上下文演示
   - 参数优先级演示
   - 层间数据流演示
   - 完整工作流演示

2. **`backend/scripts/demo_parameter_override.py`**
   - 参数覆盖逻辑演示
   - 参数合并过程演示
   - 覆盖追踪表展示
   - 实际应用示例

3. **`backend/scripts/verify_api_component_models.py`**
   - API组件模型验证
   - 枚举验证
   - 模型实例化验证

4. **`backend/scripts/test_relationships.py`**
   - 模型关系验证

5. **`backend/scripts/test_api_component_integration.py`**
   - 完整工作流集成测试

#### 其他文档

1. **`backend/docs/api_component_models.md`**
   - API组件模型使用指南
   - Header、Body、ApiDefinition详细说明
   - 使用模式和最佳实践

## 文档结构

```
morado/
├── .kiro/specs/project-restructure/
│   ├── design.md                    # ✅ 已更新：添加数据管理章节
│   └── tasks.md                     # ✅ 已更新：更新任务2.15，新增任务10.4.1
│
├── docs/
│   ├── data-management-and-execution.md      # ✅ 新增：详细文档
│   ├── parameter-override-logic.md           # ✅ 新增：参数覆盖详解
│   ├── data-management-summary.md            # ✅ 新增：快速参考
│   └── UPDATES_DATA_MANAGEMENT.md            # ✅ 新增：本文档
│
├── backend/
│   ├── src/morado/services/
│   │   └── execution_context.py              # ✅ 新增：执行上下文实现
│   │
│   ├── docs/
│   │   └── api_component_models.md           # ✅ 新增：API组件文档
│   │
│   └── scripts/
│       ├── demo_execution_context.py         # ✅ 新增：执行上下文演示
│       ├── demo_parameter_override.py        # ✅ 新增：参数覆盖演示
│       ├── verify_api_component_models.py    # ✅ 新增：模型验证
│       ├── test_relationships.py             # ✅ 新增：关系验证
│       └── test_api_component_integration.py # ✅ 新增：集成测试
```

## 核心概念

### 参数优先级（从高到低）

```
运行时参数 (Runtime Parameters)        ← 最高优先级
    ↓ 如果没有，则使用
测试用例数据 (Test Case Data)
    ↓ 如果没有，则使用
组件共享变量 (Component Shared Variables)
    ↓ 如果没有，则使用
脚本变量 (Script Variables)
    ↓ 如果没有，则使用
脚本参数默认值 (Script Parameter Defaults)
    ↓ 如果没有，则使用
环境配置 (Environment Config)          ← 最低优先级
```

### 变量替换语法

| 语法 | 说明 | 示例 |
|------|------|------|
| `${variable}` | 简单变量引用 | `${user_name}` → "张三" |
| `${variable:default}` | 带默认值的变量 | `${role:tester}` → "tester" |
| `${env.path.to.value}` | 环境配置引用 | `${env.api.base_url}` |

### 内置系统变量

- `${timestamp}` - 当前时间戳
- `${date}` - 当前日期
- `${datetime}` - 当前日期时间
- `${uuid}` - 随机UUID
- `${random_int}` - 随机整数
- `${random_string}` - 随机字符串

## 使用指南

### 查看详细文档

```bash
# 查看完整的数据管理机制
cat docs/data-management-and-execution.md

# 查看参数覆盖逻辑
cat docs/parameter-override-logic.md

# 查看快速参考
cat docs/data-management-summary.md
```

### 运行演示脚本

```bash
cd backend

# 演示执行上下文和变量替换
uv run python scripts/demo_execution_context.py

# 演示参数覆盖逻辑
uv run python scripts/demo_parameter_override.py

# 验证API组件模型
uv run python scripts/verify_api_component_models.py

# 测试模型关系
uv run python scripts/test_relationships.py

# 集成测试
uv run python scripts/test_api_component_integration.py
```

## 下一步

1. **实现任务2.15**: 实现执行引擎和数据管理机制
2. **实现任务10.4.1**: 验证数据管理和参数传递机制
3. **参考文档**: 使用新增的文档作为实现指南

## 相关文档

- [设计文档](.kiro/specs/project-restructure/design.md)
- [任务列表](.kiro/specs/project-restructure/tasks.md)
- [数据管理与执行机制](docs/data-management-and-execution.md)
- [参数覆盖逻辑详解](docs/parameter-override-logic.md)
- [数据管理机制总结](docs/data-management-summary.md)
- [API组件模型文档](backend/docs/api_component_models.md)
