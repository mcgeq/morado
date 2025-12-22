"""演示 TimeUtil 便捷方法的使用示例

这个脚本展示了如何使用 TimeUtil 类的新增便捷方法来进行时间计算。
"""

from datetime import datetime, timezone
from morado.common.utils import TimeUtil


def demo_add_to_now():
    """演示 add_to_now 方法"""
    print("=" * 60)
    print("演示 add_to_now() - 在当前时间上加时间")
    print("=" * 60)
    
    current = TimeUtil.now_utc()
    print(f"当前 UTC 时间: {current}")
    
    # 2 小时后
    future_2h = TimeUtil.add_to_now(hours=2)
    print(f"2 小时后: {future_2h}")
    
    # 3 天 5 小时后
    future_3d5h = TimeUtil.add_to_now(days=3, hours=5)
    print(f"3 天 5 小时后: {future_3d5h}")
    
    # 1 周后
    next_week = TimeUtil.add_to_now(weeks=1)
    print(f"1 周后: {next_week}")
    
    # 使用本地时间
    local_future = TimeUtil.add_to_now(utc=False, hours=1)
    print(f"本地时间 1 小时后: {local_future}")
    print()


def demo_subtract_from_now():
    """演示 subtract_from_now 方法"""
    print("=" * 60)
    print("演示 subtract_from_now() - 从当前时间减去时间")
    print("=" * 60)
    
    current = TimeUtil.now_utc()
    print(f"当前 UTC 时间: {current}")
    
    # 2 小时前
    past_2h = TimeUtil.subtract_from_now(hours=2)
    print(f"2 小时前: {past_2h}")
    
    # 3 天前
    past_3d = TimeUtil.subtract_from_now(days=3)
    print(f"3 天前: {past_3d}")
    
    # 1 周前
    last_week = TimeUtil.subtract_from_now(weeks=1)
    print(f"1 周前: {last_week}")
    
    # 30 分钟前（本地时间）
    local_past = TimeUtil.subtract_from_now(utc=False, minutes=30)
    print(f"本地时间 30 分钟前: {local_past}")
    print()


def demo_add_to_time():
    """演示 add_to_time 方法"""
    print("=" * 60)
    print("演示 add_to_time() - 在指定时间或当前时间上加时间")
    print("=" * 60)
    
    # 在当前时间上加
    future_current = TimeUtil.add_to_time(hours=1)
    print(f"当前时间 + 1 小时: {future_current}")
    
    # 在指定时间上加
    specific = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
    print(f"\n指定时间: {specific}")
    
    future_specific = TimeUtil.add_to_time(specific, hours=3, minutes=30)
    print(f"指定时间 + 3 小时 30 分钟: {future_specific}")
    
    # 使用 None 明确表示当前时间
    future_none = TimeUtil.add_to_time(None, days=1)
    print(f"\nNone (当前时间) + 1 天: {future_none}")
    
    # 使用本地时间
    future_local = TimeUtil.add_to_time(None, utc=False, hours=2)
    print(f"本地时间 + 2 小时: {future_local}")
    print()


def demo_subtract_from_time():
    """演示 subtract_from_time 方法"""
    print("=" * 60)
    print("演示 subtract_from_time() - 从指定时间或当前时间减去时间")
    print("=" * 60)
    
    # 从当前时间减
    past_current = TimeUtil.subtract_from_time(hours=2)
    print(f"当前时间 - 2 小时: {past_current}")
    
    # 从指定时间减
    specific = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
    print(f"\n指定时间: {specific}")
    
    past_specific = TimeUtil.subtract_from_time(specific, hours=3, minutes=30)
    print(f"指定时间 - 3 小时 30 分钟: {past_specific}")
    
    # 使用本地时间
    past_local = TimeUtil.subtract_from_time(None, utc=False, weeks=1)
    print(f"\n本地时间 - 1 周: {past_local}")
    print()


def demo_practical_use_cases():
    """演示实际应用场景"""
    print("=" * 60)
    print("实际应用场景")
    print("=" * 60)
    
    # 场景 1: 生成令牌过期时间
    print("\n场景 1: 生成令牌过期时间")
    token_expires = TimeUtil.add_to_now(hours=24)
    print(f"令牌将在 24 小时后过期: {token_expires}")
    
    # 场景 2: 查询历史数据时间范围
    print("\n场景 2: 查询最近 7 天的数据")
    start_time = TimeUtil.subtract_from_now(days=7)
    end_time = TimeUtil.now_utc()
    print(f"开始时间: {start_time}")
    print(f"结束时间: {end_time}")
    
    # 场景 3: 计划任务
    print("\n场景 3: 计划 2 小时后执行的任务")
    scheduled_time = TimeUtil.add_to_now(hours=2)
    print(f"任务执行时间: {scheduled_time}")
    
    # 场景 4: 会议提醒
    print("\n场景 4: 会议提醒（会议前 15 分钟）")
    meeting_time = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
    reminder_time = TimeUtil.subtract_from_time(meeting_time, minutes=15)
    print(f"会议时间: {meeting_time}")
    print(f"提醒时间: {reminder_time}")
    
    # 场景 5: 计算截止日期
    print("\n场景 5: 项目截止日期（7 天 12 小时后）")
    deadline = TimeUtil.add_to_now(days=7, hours=12)
    print(f"截止日期: {deadline}")
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("TimeUtil 便捷方法演示")
    print("=" * 60 + "\n")
    
    demo_add_to_now()
    demo_subtract_from_now()
    demo_add_to_time()
    demo_subtract_from_time()
    demo_practical_use_cases()
    
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
