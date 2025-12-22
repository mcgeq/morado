# TimeUtil 增强功能总结

## 概述

为 `TimeUtil` 类添加了四个新的便捷方法，使时间操作更加简洁和直观。这些方法简化了在当前时间或指定时间上进行加减操作的常见用例。

## 新增方法

### 1. `add_to_now(utc=True, **kwargs) -> datetime`

在当前时间上加上指定的时间间隔。

**参数：**
- `utc` (bool): 是否使用 UTC 时间，默认为 True
- `**kwargs`: 时间间隔参数（days, hours, minutes, seconds, weeks 等）

**示例：**
```python
# 获取 2 小时后的时间（UTC）
future = TimeUtil.add_to_now(hours=2)

# 获取 3 天后的时间（本地时间）
future_local = TimeUtil.add_to_now(utc=False, days=3)
```

### 2. `subtract_from_now(utc=True, **kwargs) -> datetime`

从当前时间减去指定的时间间隔。

**参数：**
- `utc` (bool): 是否使用 UTC 时间，默认为 True
- `**kwargs`: 时间间隔参数（days, hours, minutes, seconds, weeks 等）

**示例：**
```python
# 获取 2 小时前的时间（UTC）
past = TimeUtil.subtract_from_now(hours=2)

# 获取 1 周前的时间（本地时间）
past_local = TimeUtil.subtract_from_now(utc=False, weeks=1)
```

### 3. `add_to_time(dt=None, utc=True, **kwargs) -> datetime`

在指定时间或当前时间上加上时间间隔（最灵活的方法）。

**参数：**
- `dt` (datetime | None): 基准时间，如果为 None 则使用当前时间
- `utc` (bool): 当 dt 为 None 时，是否使用 UTC 时间，默认为 True
- `**kwargs`: 时间间隔参数（days, hours, minutes, seconds, weeks 等）

**示例：**
```python
# 在当前时间上加 1 小时
future = TimeUtil.add_to_time(hours=1)

# 在指定时间上加 3 小时 30 分钟
specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
result = TimeUtil.add_to_time(specific, hours=3, minutes=30)
```

### 4. `subtract_from_time(dt=None, utc=True, **kwargs) -> datetime`

从指定时间或当前时间减去时间间隔（最灵活的方法）。

**参数：**
- `dt` (datetime | None): 基准时间，如果为 None 则使用当前时间
- `utc` (bool): 当 dt 为 None 时，是否使用 UTC 时间，默认为 True
- `**kwargs`: 时间间隔参数（days, hours, minutes, seconds, weeks 等）

**示例：**
```python
# 从当前时间减去 2 小时
past = TimeUtil.subtract_from_time(hours=2)

# 从指定时间减去 3 小时 30 分钟
specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
result = TimeUtil.subtract_from_time(specific, hours=3, minutes=30)
```

## 支持的时间单位

所有方法都支持以下时间单位（通过 `**kwargs` 传递）：

- `weeks` - 周
- `days` - 天
- `hours` - 小时
- `minutes` - 分钟
- `seconds` - 秒
- `milliseconds` - 毫秒
- `microseconds` - 微秒

## 与现有方法的对比

### 旧方式（仍然有效）

```python
# 需要两步：先获取当前时间，再加时间
current = TimeUtil.now_utc()
future = TimeUtil.add_duration(current, hours=2)
```

### 新方式（更简洁）

```python
# 一步完成
future = TimeUtil.add_to_now(hours=2)
```

## 实际应用场景

### 1. 生成过期时间

```python
# 令牌 24 小时后过期
token_expires_at = TimeUtil.add_to_now(hours=24)

# 会话 7 天后过期
session_expires_at = TimeUtil.add_to_now(days=7)
```

### 2. 查询历史数据

```python
# 查询最近 7 天的数据
start_time = TimeUtil.subtract_from_now(days=7)
end_time = TimeUtil.now_utc()
```

### 3. 计划任务

```python
# 2 小时后执行
scheduled_time = TimeUtil.add_to_now(hours=2)

# 明天同一时间执行
tomorrow = TimeUtil.add_to_now(days=1)
```

### 4. 会议提醒

```python
# 会议前 15 分钟提醒
meeting_time = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
reminder_time = TimeUtil.subtract_from_time(meeting_time, minutes=15)
```

### 5. 时间范围计算

```python
# 事件前后 1 小时的时间范围
event_time = datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
range_start = TimeUtil.subtract_from_time(event_time, hours=1)
range_end = TimeUtil.add_to_time(event_time, hours=1)
```

## 方法选择指南

### 使用 `add_to_now()` / `subtract_from_now()` 当：
- 你只需要在当前时间上进行操作
- 代码简洁性是首要考虑

### 使用 `add_to_time()` / `subtract_from_time()` 当：
- 你需要在指定时间上进行操作
- 你需要根据条件选择使用当前时间或指定时间
- 你需要最大的灵活性

## 测试覆盖

所有新方法都有完整的单元测试覆盖：

- ✅ 基本功能测试
- ✅ UTC 和本地时间测试
- ✅ 指定时间和当前时间测试
- ✅ 多种时间单位组合测试
- ✅ 错误处理测试

**测试统计：**
- 新增测试：12 个
- 总测试数：92 个
- 测试通过率：100%

## 注意事项

1. **时区感知**：所有方法返回的都是时区感知的 `datetime` 对象
2. **默认 UTC**：默认使用 UTC 时间，可通过 `utc=False` 使用本地时间
3. **时区要求**：如果传入指定时间，该时间必须是时区感知的
4. **夏令时**：时间计算会自动处理夏令时转换

## 文档和示例

- 详细使用示例：`docs/time_convenience_examples.md`
- 演示脚本：`examples/time_convenience_demo.py`
- API 文档：每个方法都有完整的 docstring

## 向后兼容性

✅ 完全向后兼容，所有现有代码无需修改即可继续工作。

## 总结

这些新方法使 `TimeUtil` 类更加易用，减少了样板代码，同时保持了灵活性和类型安全。它们是对现有 `add_duration()` 和 `subtract_duration()` 方法的补充，而不是替代。
