# TimeUtil 变更日志

## [2024-12-22] - 新增便捷方法

### 新增功能

#### 四个新的便捷方法

1. **`add_to_now(utc=True, **kwargs)`**
   - 在当前时间上加上时间间隔
   - 默认使用 UTC，可选本地时间
   - 简化了常见的"从现在开始计算未来时间"的用例

2. **`subtract_from_now(utc=True, **kwargs)`**
   - 从当前时间减去时间间隔
   - 默认使用 UTC，可选本地时间
   - 简化了常见的"从现在开始计算过去时间"的用例

3. **`add_to_time(dt=None, utc=True, **kwargs)`**
   - 最灵活的加法方法
   - 可以在指定时间或当前时间上操作
   - 当 dt=None 时，行为类似 add_to_now()

4. **`subtract_from_time(dt=None, utc=True, **kwargs)`**
   - 最灵活的减法方法
   - 可以在指定时间或当前时间上操作
   - 当 dt=None 时，行为类似 subtract_from_now()

### 测试

- ✅ 新增 12 个单元测试
- ✅ 所有 92 个测试通过
- ✅ 100% 测试覆盖率（新功能）

### 文档

新增以下文档：

1. **`docs/time_convenience_examples.md`**
   - 详细的使用示例
   - 实际应用场景
   - 完整的代码示例

2. **`docs/TIMEUTIL_ENHANCEMENTS.md`**
   - 功能总结
   - 方法对比
   - 选择指南

3. **`docs/QUICK_START_TIMEUTIL.md`**
   - 快速入门指南
   - 常见场景示例

4. **`examples/time_convenience_demo.py`**
   - 可运行的演示脚本
   - 展示所有新功能

### 向后兼容性

✅ 完全向后兼容
- 所有现有方法保持不变
- 现有代码无需修改
- 新方法是对现有功能的补充

### 代码质量

- ✅ 完整的类型提示
- ✅ 详细的 docstring
- ✅ 错误处理和验证
- ✅ 遵循现有代码风格

### 使用示例

#### 之前（仍然有效）

```python
current = TimeUtil.now_utc()
future = TimeUtil.add_duration(current, hours=2)
```

#### 现在（更简洁）

```python
future = TimeUtil.add_to_now(hours=2)
```

### 支持的时间单位

- weeks（周）
- days（天）
- hours（小时）
- minutes（分钟）
- seconds（秒）
- milliseconds（毫秒）
- microseconds（微秒）

### 实际应用场景

1. **令牌过期时间**：`TimeUtil.add_to_now(hours=24)`
2. **历史数据查询**：`TimeUtil.subtract_from_now(days=7)`
3. **任务调度**：`TimeUtil.add_to_now(hours=2)`
4. **会议提醒**：`TimeUtil.subtract_from_time(meeting_time, minutes=15)`
5. **时间范围计算**：组合使用加减方法

### 技术细节

- 所有方法返回时区感知的 datetime 对象
- 默认使用 UTC 时间
- 自动处理夏令时转换
- 完整的错误处理和类型检查

### 下一步

这些便捷方法使 TimeUtil 类更加易用，同时保持了灵活性和类型安全。未来可以考虑：

- 添加更多时间计算便捷方法
- 支持相对时间描述（如"下周一"）
- 添加时间范围对象
