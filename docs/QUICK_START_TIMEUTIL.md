# TimeUtil 快速入门

## 基本用法

### 获取当前时间

```python
from morado.common.utils import TimeUtil

# UTC 时间
utc_now = TimeUtil.now_utc()

# 本地时间
local_now = TimeUtil.now_local()
```

### 时间加减（新功能！）

#### 简单方式 - 在当前时间上操作

```python
# 2 小时后
future = TimeUtil.add_to_now(hours=2)

# 3 天前
past = TimeUtil.subtract_from_now(days=3)

# 1 周后（本地时间）
next_week = TimeUtil.add_to_now(utc=False, weeks=1)
```

#### 灵活方式 - 在任意时间上操作

```python
from datetime import datetime, timezone

# 在当前时间上加
future = TimeUtil.add_to_time(hours=1)

# 在指定时间上加
meeting = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
reminder = TimeUtil.subtract_from_time(meeting, minutes=15)
```

### 格式化和解析

```python
# 格式化为 ISO 8601
iso_string = TimeUtil.to_iso8601(utc_now)

# 解析 ISO 8601
parsed = TimeUtil.parse_iso8601("2024-01-15T14:30:45+00:00")

# 自定义格式
formatted = TimeUtil.format_time(utc_now, "%Y-%m-%d %H:%M:%S")
```

### 时区转换

```python
# 转换到纽约时间
ny_time = TimeUtil.convert_timezone(utc_now, "America/New_York")

# 转换到东京时间
tokyo_time = TimeUtil.convert_timezone(utc_now, "Asia/Tokyo")
```

## 常见场景

### 生成令牌过期时间

```python
# 24 小时后过期
expires_at = TimeUtil.add_to_now(hours=24)
```

### 查询历史数据

```python
# 最近 7 天
start = TimeUtil.subtract_from_now(days=7)
end = TimeUtil.now_utc()
```

### 计划任务

```python
# 2 小时后执行
scheduled = TimeUtil.add_to_now(hours=2)
```

### 会议提醒

```python
# 会议前 15 分钟
meeting_time = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
reminder_time = TimeUtil.subtract_from_time(meeting_time, minutes=15)
```

## 更多信息

- 详细文档：`docs/time_convenience_examples.md`
- 增强功能说明：`docs/TIMEUTIL_ENHANCEMENTS.md`
- 演示脚本：`examples/time_convenience_demo.py`
