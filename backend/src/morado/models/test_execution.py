"""Test Execution Model

This module defines models for tracking test execution and results.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.test_case import TestCase
    from morado.models.user import User


class ExecutionStatus(str, PyEnum):
    """执行状态"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 执行中
    PASSED = "passed"  # 通过
    FAILED = "failed"  # 失败
    ERROR = "error"  # 错误
    SKIPPED = "skipped"  # 跳过
    CANCELLED = "cancelled"  # 取消


class TestExecution(Base, TimestampMixin, UUIDMixin):
    """测试执行记录

    记录测试用例或测试套件的执行情况。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符

        # 关联
        test_case_id: 测试用例ID（如果是单个用例执行）
        test_suite_id: 测试套件ID（如果是套件执行）

        # 执行信息
        status: 执行状态
        start_time: 开始时间
        end_time: 结束时间
        duration: 执行时长（秒）

        # 环境和配置
        environment: 执行环境
        executor: 执行者
        execution_parameters: 执行参数

        # 结果统计
        total_count: 总数
        passed_count: 通过数
        failed_count: 失败数
        error_count: 错误数
        skipped_count: 跳过数

        # 详细信息
        error_message: 错误信息
        stack_trace: 堆栈跟踪
        logs: 执行日志

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> execution = TestExecution(
        ...     test_case_id=1,
        ...     status=ExecutionStatus.RUNNING,
        ...     environment="test",
        ...     executor="jenkins"
        ... )
    """

    __tablename__ = "test_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 关联
    test_case_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), comment="测试用例ID"
    )
    test_suite_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("test_suites.id", ondelete="CASCADE"), comment="测试套件ID"
    )

    # 执行信息
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment="执行状态"
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), comment="开始时间"
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), comment="结束时间"
    )
    duration: Mapped[float | None] = mapped_column(Float, comment="执行时长（秒）")

    # 环境和配置
    environment: Mapped[str] = mapped_column(
        String(20), default="test", comment="执行环境"
    )
    executor: Mapped[str | None] = mapped_column(String(100), comment="执行者")
    execution_parameters: Mapped[dict | None] = mapped_column(JSON, comment="执行参数")

    # 结果统计
    total_count: Mapped[int] = mapped_column(Integer, default=0, comment="总数")
    passed_count: Mapped[int] = mapped_column(Integer, default=0, comment="通过数")
    failed_count: Mapped[int] = mapped_column(Integer, default=0, comment="失败数")
    error_count: Mapped[int] = mapped_column(Integer, default=0, comment="错误数")
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, comment="跳过数")

    # 详细信息
    error_message: Mapped[str | None] = mapped_column(Text, comment="错误信息")
    stack_trace: Mapped[str | None] = mapped_column(Text, comment="堆栈跟踪")
    logs: Mapped[str | None] = mapped_column(Text, comment="执行日志")

    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User", back_populates="executions"
    )
    test_case: Mapped[Optional["TestCase"]] = relationship(
        "TestCase", back_populates="executions"
    )
    execution_results: Mapped[list["ExecutionResult"]] = relationship(
        "ExecutionResult", back_populates="execution", cascade="all, delete-orphan"
    )


class ExecutionResult(Base, TimestampMixin):
    """执行结果详情

    记录每个脚本或组件的执行结果详情。

    Attributes:
        id: 主键ID
        execution_id: 执行记录ID

        # 关联
        script_id: 脚本ID
        component_id: 组件ID

        # 结果信息
        status: 执行状态
        start_time: 开始时间
        end_time: 结束时间
        duration: 执行时长（秒）

        # 请求和响应
        request_data: 请求数据
        response_data: 响应数据

        # 断言结果
        assertions: 断言结果

        # 错误信息
        error_message: 错误信息
        stack_trace: 堆栈跟踪

        # 其他
        logs: 日志
        screenshots: 截图（如果有）

        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = "execution_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_executions.id", ondelete="CASCADE"),
        nullable=False,
        comment="执行记录ID",
    )

    # 关联
    script_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("test_scripts.id", ondelete="SET NULL"), comment="脚本ID"
    )
    component_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("test_components.id", ondelete="SET NULL"), comment="组件ID"
    )

    # 结果信息
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus), default=ExecutionStatus.PENDING, comment="执行状态"
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), comment="开始时间"
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), comment="结束时间"
    )
    duration: Mapped[float | None] = mapped_column(Float, comment="执行时长（秒）")

    # 请求和响应
    request_data: Mapped[dict | None] = mapped_column(JSON, comment="请求数据")
    response_data: Mapped[dict | None] = mapped_column(JSON, comment="响应数据")

    # 断言结果
    assertions: Mapped[list | None] = mapped_column(JSON, comment="断言结果")

    # 错误信息
    error_message: Mapped[str | None] = mapped_column(Text, comment="错误信息")
    stack_trace: Mapped[str | None] = mapped_column(Text, comment="堆栈跟踪")

    # 其他
    logs: Mapped[str | None] = mapped_column(Text, comment="日志")
    screenshots: Mapped[list | None] = mapped_column(JSON, comment="截图")

    # Relationships
    execution: Mapped["TestExecution"] = relationship(
        "TestExecution", back_populates="execution_results"
    )
