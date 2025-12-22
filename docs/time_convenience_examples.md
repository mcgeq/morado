# TimeUtil 便捷方法使用示例

## 概述

`TimeUtil` 类新增了四个便捷方法，用于在当前时间或指定时间上进行加减操作。

## 新增方法

### 1. `add_to_now()` - 在当前时间上加时间

默认使用 UTC 时间，也可以使用本地时间。

```python
from morado.common.utils.time import TimeUtil

# 获取 2 小时后的时间（UTC）
future = TimeUtil.add_to_now(hours=2)

# 获取 3 天 5 小时后的时间（本地时间）
future_local = TimeUtil.add_to_now(utc=False, days=3, hours=5)

# 获取 1 周后的时间
next_week = TimeUtil.add_to_now(weeks=1)

# 获取 30 分钟后的时间
in_30_min = TimeUtil.add_to_now(minutes=30)

# 组合多个时间单位
complex_future = TimeUtil.add_to_now(days=7, hours=3, minutes=15, seconds=30)
```

### 2. `subtract_from_now()` - 从当前时间减去时间

默认使用 UTC 时间，也可以使用本地时间。

```python
from morado.common.utils.time import TimeUtil

# 获取 2 小时前的时间（UTC）
past = TimeUtil.subtract_from_now(hours=2)

# 获取 3 天前的时间（本地时间）
past_local = TimeUtil.subtract_from_now(utc=False, days=3)

# 获取 1 周前的时间
last_week = TimeUtil.subtract_from_now(weeks=1)

# 获取 30 分钟前的时间
half_hour_ago = TimeUtil.subtract_from_now(minutes=30)
```

### 3. `add_to_time()` - 在指定时间或当前时间上加时间

最灵活的方法，可以指定时间，也可以使用当前时间。

```python
from morado.common.utils.time import TimeUtil
from datetime import datetime, timezone

# 在当前时间上加 1 小时（UTC）
future = TimeUtil.add_to_time(hours=1)

# 在当前本地时间上加 1 天
future_local = TimeUtil.add_to_time(utc=False, days=1)

# 在指定时间上加 3 小时 30 分钟
specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
result = TimeUtil.add_to_time(specific, hours=3, minutes=30)
# 结果: 2024-01-15 13:30:00+00:00

# 也可以显式传入 None 使用当前时间
future = TimeUtil.add_to_time(None, hours=2)
```

### 4. `subtract_from_time()` - 从指定时间或当前时间减去时间

最灵活的方法，可以指定时间，也可以使用当前时间。

```python
from morado.common.utils.time import TimeUtil
from datetime import datetime, timezone

# 从当前时间减去 2 小时（UTC）
past = TimeUtil.subtract_from_time(hours=2)

# 从当前本地时间减去 1 周
past_local = TimeUtil.subtract_from_time(utc=False, weeks=1)

# 从指定时间减去 3 小时 30 分钟
specific = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
result = TimeUtil.subtract_from_time(specific, hours=3, minutes=30)
# 结果: 2024-01-15 06:30:00+00:00
```

## 支持的时间单位

所有方法都支持以下时间单位（通过 `**kwargs` 传递给 `timedelta`）：

- `weeks` - 周
- `days` - 天
- `hours` - 小时
- `minutes` - 分钟
- `seconds` - 秒
- `milliseconds` - 毫秒
- `microseconds` - 微秒

## 实际应用场景

### 场景 1: 生成过期时间

```python
from morado.common.utils.time import TimeUtil

# 生成 24 小时后过期的令牌
token_expires_at = TimeUtil.add_to_now(hours=24)

# 生成 7 天后过期的会话
session_expires_at = TimeUtil.add_to_now(days=7)
```

### 场景 2: 查询历史数据

```python
from morado.common.utils.time import TimeUtil

# 查询最近 7 天的数据
start_time = TimeUtil.subtract_from_now(days=7)
end_time = TimeUtil.now_utc()

# 查询最近 1 小时的日志
log_start = TimeUtil.subtract_from_now(hours=1)
```

### 场景 3: 计划任务时间

```python
from morado.common.utils.time import TimeUtil

# 计划 2 小时后执行的任务
scheduled_time = TimeUtil.add_to_now(hours=2)

# 计划明天同一时间执行
tomorrow = TimeUtil.add_to_now(days=1)
```

### 场景 4: 时间范围计算

```python
from morado.common.utils.time import TimeUtil
from datetime import datetime, timezone

# 给定一个事件时间，计算前后 1 小时的范围
event_time = datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
range_start = TimeUtil.subtract_from_time(event_time, hours=1)
range_end = TimeUtil.add_to_time(event_time, hours=1)
```

## 与现有方法的对比

### 旧方式（仍然有效）

```python
from morado.common.utils.time import TimeUtil

# 需要先获取当前时间，然后加时间
current = TimeUtil.now_utc()
future = TimeUtil.add_duration(current, hours=2)
```

### 新方式（更简洁）

```python
from morado.common.utils.time import TimeUtil

# 一步完成
future = TimeUtil.add_to_now(hours=2)
```

## 注意事项

1. 所有方法返回的都是**时区感知**的 `datetime` 对象
2. 默认使用 **UTC 时间**，可以通过 `utc=False` 使用本地时间
3. 如果传入指定时间，该时间必须是时区感知的
4. 时间计算会自动处理夏令时转换

## 完整示例

```python
from morado.common.utils.time import TimeUtil
from datetime import datetime, timezone

# 示例 1: 简单的未来时间计算
print("2 小时后:", TimeUtil.add_to_now(hours=2))
print("3 天前:", TimeUtil.subtract_from_now(days=3))

# 示例 2: 使用本地时间
print("本地时间 1 周后:", TimeUtil.add_to_now(utc=False, weeks=1))

# 示例 3: 在指定时间上操作
meeting_time = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
reminder_time = TimeUtil.subtract_from_time(meeting_time, minutes=15)
print(f"会议时间: {meeting_time}")
print(f"提醒时间: {reminder_time}")

# 示例 4: 组合多个时间单位
deadline = TimeUtil.add_to_now(days=7, hours=12, minutes=30)
print(f"截止时间: {deadline}")

# 示例 5: 灵活使用 add_to_time
# 使用当前时间
future1 = TimeUtil.add_to_time(hours=1)
# 使用指定时间
specific = TimeUtil.now_utc()
future2 = TimeUtil.add_to_time(specific, hours=1)
```
