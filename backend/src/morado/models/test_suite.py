"""Test Suite Model

Test suites are collections of test cases that can be executed together.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.test_case import TestCase
    from morado.models.user import User


class TestSuite(Base, TimestampMixin, UUIDMixin):
    """测试套件

    TestSuite是测试用例的集合，用于批量执行测试。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: 套件名称
        description: 套件描述

        # 执行配置
        execution_order: 执行顺序配置
        parallel_execution: 是否并行执行
        continue_on_failure: 失败时是否继续

        # 调度配置
        schedule_config: 调度配置（cron表达式等）
        is_scheduled: 是否启用调度

        # 环境和数据
        environment: 执行环境
        global_variables: 全局变量

        # 配置
        tags: 标签
        version: 版本号

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> suite = TestSuite(
        ...     name="用户模块回归测试套件",
        ...     description="包含所有用户相关功能的测试用例",
        ...     parallel_execution=True,
        ...     environment="test"
        ... )
    """

    __tablename__ = "test_suites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="套件名称")
    description: Mapped[str | None] = mapped_column(Text, comment="套件描述")

    # 执行配置
    execution_order: Mapped[str] = mapped_column(
        String(20),
        default="sequential",
        comment="执行顺序（sequential/parallel）"
    )
    parallel_execution: Mapped[bool] = mapped_column(default=False, comment="是否并行执行")
    continue_on_failure: Mapped[bool] = mapped_column(default=True, comment="失败时是否继续")

    # 调度配置
    schedule_config: Mapped[dict | None] = mapped_column(JSON, comment="调度配置")
    is_scheduled: Mapped[bool] = mapped_column(default=False, comment="是否启用调度")

    # 环境和数据
    environment: Mapped[str] = mapped_column(String(20), default="test", comment="执行环境")
    global_variables: Mapped[dict | None] = mapped_column(JSON, comment="全局变量")

    # 配置
    tags: Mapped[list | None] = mapped_column(JSON, comment="标签")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", comment="版本号")

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="test_suites")
    test_suite_cases: Mapped[list["TestSuiteCase"]] = relationship(
        "TestSuiteCase",
        back_populates="test_suite",
        cascade="all, delete-orphan",
        order_by="TestSuiteCase.execution_order"
    )


class TestSuiteCase(Base, TimestampMixin):
    """测试套件-用例关联表

    定义测试套件包含哪些测试用例，以及用例的执行顺序。

    Attributes:
        id: 主键ID
        test_suite_id: 测试套件ID
        test_case_id: 测试用例ID
        execution_order: 执行顺序
        is_enabled: 是否启用
        case_parameters: 用例参数覆盖
        description: 说明
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = "test_suite_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_suite_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_suites.id", ondelete="CASCADE"),
        nullable=False,
        comment="测试套件ID"
    )
    test_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        comment="测试用例ID"
    )
    execution_order: Mapped[int] = mapped_column(Integer, default=0, comment="执行顺序")
    is_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    case_parameters: Mapped[dict | None] = mapped_column(JSON, comment="用例参数覆盖")
    description: Mapped[str | None] = mapped_column(Text, comment="说明")

    # Relationships
    test_suite: Mapped["TestSuite"] = relationship("TestSuite", back_populates="test_suite_cases")
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="test_suite_cases")
