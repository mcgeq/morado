# 演示脚本

本目录包含各种功能演示脚本，用于展示系统的各个特性。

## 脚本列表

### demo_execution_context.py
演示执行上下文的使用。

**展示内容：**
- 变量解析和替换
- 参数优先级
- 内置变量使用

### demo_execution_engine_tracing.py
演示执行引擎的追踪功能。

**展示内容：**
- 脚本执行追踪
- 组件执行追踪
- 测试用例执行追踪

### demo_logging_integration.py
演示日志集成功能。

**展示内容：**
- 结构化日志
- 日志上下文
- 日志级别配置

### demo_parameter_override.py
演示参数覆盖机制。

**展示内容：**
- 参数优先级（运行时 > 测试用例 > 组件 > 脚本 > 环境）
- 参数传递
- 变量替换

### demo_request_tracing.py
演示 HTTP 请求追踪。

**展示内容：**
- 请求 ID 生成
- 请求链路追踪
- 请求日志记录

### demo_script_models.py
演示脚本模型的使用。

**展示内容：**
- 脚本创建
- 脚本参数配置
- 脚本执行

### demo_test_case_layer4.py
演示第四层（测试用例层）的功能。

**展示内容：**
- 测试用例创建
- 引用脚本和组件
- 测试用例执行

### demo_tracing_integration.py
演示追踪集成功能。

**展示内容：**
- 分布式追踪
- 追踪上下文传递
- 追踪数据收集

## 使用方法

所有演示脚本都可以直接运行：

```bash
cd backend
uv run python scripts/demo/<script_name>.py
```

## 注意事项

- 演示脚本通常不需要数据库连接
- 某些脚本可能需要先运行数据库初始化脚本
- 演示脚本主要用于学习和理解系统功能
