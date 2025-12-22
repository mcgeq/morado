"""Layer 4: Test Case

This module defines the fourth layer of the test platform architecture:
- TestCase: Test cases that reference scripts and components
- TestCaseScript: Association between test cases and scripts
- TestCaseComponent: Association between test cases and components

Test cases are the top-level execution units that users interact with.
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.component import TestComponent
    from morado.models.script import TestScript
    from morado.models.test_execution import TestExecution
    from morado.models.test_suite import TestSuiteCase
    from morado.models.user import User


class TestCasePriority(str, PyEnum):
    """测试用例优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestCaseStatus(str, PyEnum):
    """测试用例状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 激活
    DEPRECATED = "deprecated"  # 已废弃
    ARCHIVED = "archived"  # 已归档


class TestCase(Base, TimestampMixin, UUIDMixin):
    """测试用例（第四层）

    TestCase是测试平台的最顶层，可以引用脚本和联合组件。
    用例是用户直接操作和执行的单元，代表一个完整的测试场景。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: 用例名称
        description: 用例描述

        # 分类和优先级
        priority: 优先级
        status: 状态
        category: 分类
        tags: 标签

        # 前置和后置条件
        preconditions: 前置条件
        postconditions: 后置条件

        # 执行配置
        execution_order: 执行顺序配置
        timeout: 超时时间（秒）
        retry_count: 重试次数
        continue_on_failure: 失败时是否继续

        # 数据和环境
        test_data: 测试数据
        environment: 执行环境（dev/test/prod）

        # 版本和维护
        version: 版本号
        is_automated: 是否自动化

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建一个测试用例，引用脚本和组件
        >>> test_case = TestCase(
        ...     name="用户注册登录完整流程测试",
        ...     description="测试用户从注册到登录的完整流程",
        ...     priority=TestCasePriority.HIGH,
        ...     category="用户管理",
        ...     test_data={"username": "test_user", "password": "Test@123"}
        ... )
    """

    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="用例名称")
    description: Mapped[str | None] = mapped_column(Text, comment="用例描述")

    # 分类和优先级
    priority: Mapped[TestCasePriority] = mapped_column(
        Enum(TestCasePriority),
        default=TestCasePriority.MEDIUM,
        comment="优先级"
    )
    status: Mapped[TestCaseStatus] = mapped_column(
        Enum(TestCaseStatus),
        default=TestCaseStatus.DRAFT,
        comment="状态"
    )
    category: Mapped[str | None] = mapped_column(String(100), comment="分类")
    tags: Mapped[list | None] = mapped_column(JSON, comment="标签")

    # 前置和后置条件
    preconditions: Mapped[str | None] = mapped_column(Text, comment="前置条件")
    postconditions: Mapped[str | None] = mapped_column(Text, comment="后置条件")

    # 执行配置
    execution_order: Mapped[str] = mapped_column(
        String(20),
        default="sequential",
        comment="执行顺序（sequential/parallel）"
    )
    timeout: Mapped[int] = mapped_column(Integer, default=300, comment="超时时间（秒）")
    retry_count: Mapped[int] = mapped_column(Integer, default=0, comment="重试次数")
    continue_on_failure: Mapped[bool] = mapped_column(default=False, comment="失败时是否继续")

    # 数据和环境
    test_data: Mapped[dict | None] = mapped_column(JSON, comment="测试数据")
    environment: Mapped[str] = mapped_column(String(20), default="test", comment="执行环境")

    # 版本和维护
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", comment="版本号")
    is_automated: Mapped[bool] = mapped_column(default=True, comment="是否自动化")

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="test_cases")
    test_case_scripts: Mapped[list["TestCaseScript"]] = relationship(
        "TestCaseScript",
        back_populates="test_case",
        cascade="all, delete-orphan",
        order_by="TestCaseScript.execution_order"
    )
    test_case_components: Mapped[list["TestCaseComponent"]] = relationship(
        "TestCaseComponent",
        back_populates="test_case",
        cascade="all, delete-orphan",
        order_by="TestCaseComponent.execution_order"
    )
    test_suite_cases: Mapped[list["TestSuiteCase"]] = relationship(
        "TestSuiteCase",
        back_populates="test_case",
        cascade="all, delete-orphan"
    )
    executions: Mapped[list["TestExecution"]] = relationship(
        "TestExecution",
        back_populates="test_case",
        cascade="all, delete-orphan"
    )


class TestCaseScript(Base, TimestampMixin):
    """测试用例-脚本关联表

    定义测试用例包含哪些脚本，以及脚本的执行顺序和配置。

    Attributes:
        id: 主键ID
        test_case_id: 测试用例ID
        script_id: 脚本ID
        execution_order: 执行顺序（数字越小越先执行）
        is_enabled: 是否启用
        script_parameters: 脚本参数覆盖（JSON格式）
        description: 说明
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 将脚本添加到测试用例中
        >>> case_script = TestCaseScript(
        ...     test_case_id=1,
        ...     script_id=1,
        ...     execution_order=1,
        ...     script_parameters={"username": "test_user"}
        ... )
    """

    __tablename__ = "test_case_scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        comment="测试用例ID"
    )
    script_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_scripts.id", ondelete="CASCADE"),
        nullable=False,
        comment="脚本ID"
    )
    execution_order: Mapped[int] = mapped_column(Integer, default=0, comment="执行顺序")
    is_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    script_parameters: Mapped[dict | None] = mapped_column(JSON, comment="脚本参数覆盖")
    description: Mapped[str | None] = mapped_column(Text, comment="说明")

    # Relationships
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="test_case_scripts")
    script: Mapped["TestScript"] = relationship("TestScript", back_populates="test_case_scripts")


class TestCaseComponent(Base, TimestampMixin):
    """测试用例-组件关联表

    定义测试用例包含哪些组件，以及组件的执行顺序和配置。

    Attributes:
        id: 主键ID
        test_case_id: 测试用例ID
        component_id: 组件ID
        execution_order: 执行顺序（数字越小越先执行）
        is_enabled: 是否启用
        component_parameters: 组件参数覆盖（JSON格式）
        description: 说明
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 将组件添加到测试用例中
        >>> case_component = TestCaseComponent(
        ...     test_case_id=1,
        ...     component_id=1,
        ...     execution_order=2,
        ...     component_parameters={"base_url": "https://test.example.com"}
        ... )
    """

    __tablename__ = "test_case_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_case_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        comment="测试用例ID"
    )
    component_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_components.id", ondelete="CASCADE"),
        nullable=False,
        comment="组件ID"
    )
    execution_order: Mapped[int] = mapped_column(Integer, default=0, comment="执行顺序")
    is_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    component_parameters: Mapped[dict | None] = mapped_column(JSON, comment="组件参数覆盖")
    description: Mapped[str | None] = mapped_column(Text, comment="说明")

    # Relationships
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="test_case_components")
    component: Mapped["TestComponent"] = relationship("TestComponent", back_populates="test_case_components")
