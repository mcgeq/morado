"""Layer 3: Test Component Models

This module defines the third layer of the test platform architecture:
- TestComponent: Composite components that combine multiple scripts
- ComponentScript: Association between components and scripts

The third layer enables script composition and reuse by creating components
that can contain multiple scripts and even nest other components.
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .script import TestScript
    from .test_case import TestCaseComponent
    from .user import User


class ComponentType(str, PyEnum):
    """组件类型"""
    SIMPLE = "simple"  # 简单组件（仅包含脚本）
    COMPOSITE = "composite"  # 复合组件（包含脚本和子组件）
    TEMPLATE = "template"  # 模板组件（可被复制使用）


class ExecutionMode(str, PyEnum):
    """执行模式"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    CONDITIONAL = "conditional"  # 条件执行


class TestComponent(Base, TimestampMixin, UUIDMixin):
    """测试组件（第三层）

    TestComponent是多个脚本的组合，支持组件嵌套。
    组件可以独立执行和调试，也可以被测试用例引用。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: 组件名称
        description: 组件描述

        # 组件类型和配置
        component_type: 组件类型（simple/composite/template）
        execution_mode: 执行模式（sequential/parallel/conditional）

        # 组件嵌套
        parent_component_id: 父组件ID（支持组件嵌套）

        # 共享变量
        shared_variables: 组件级共享变量（在脚本间传递）

        # 执行配置
        timeout: 超时时间（秒）
        retry_count: 重试次数
        continue_on_failure: 失败时是否继续

        # 条件执行配置
        execution_condition: 执行条件（用于conditional模式）

        # 配置
        is_active: 是否激活
        version: 版本号
        tags: 标签

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建一个简单组件
        >>> component = TestComponent(
        ...     name="用户登录流程",
        ...     description="包含登录前准备、登录、验证的完整流程",
        ...     component_type=ComponentType.SIMPLE,
        ...     execution_mode=ExecutionMode.SEQUENTIAL,
        ...     shared_variables={
        ...         "base_url": "https://api.example.com",
        ...         "timeout": 30
        ...     }
        ... )
        >>>
        >>> # 创建一个嵌套组件
        >>> parent_component = TestComponent(
        ...     name="完整测试套件",
        ...     description="包含多个子组件的复合测试",
        ...     component_type=ComponentType.COMPOSITE,
        ...     execution_mode=ExecutionMode.SEQUENTIAL
        ... )
        >>>
        >>> child_component = TestComponent(
        ...     name="子组件",
        ...     description="被父组件引用的子组件",
        ...     component_type=ComponentType.SIMPLE,
        ...     parent_component_id=parent_component.id
        ... )
    """

    __tablename__: str = "test_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="组件名称")
    description: Mapped[str | None] = mapped_column(Text, comment="组件描述")

    # 组件类型和配置
    component_type: Mapped[ComponentType] = mapped_column(
        Enum(ComponentType),
        default=ComponentType.SIMPLE,
        comment="组件类型"
    )
    execution_mode: Mapped[ExecutionMode] = mapped_column(
        Enum(ExecutionMode),
        default=ExecutionMode.SEQUENTIAL,
        comment="执行模式"
    )

    # 组件嵌套
    parent_component_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("test_components.id", ondelete="CASCADE"),
        comment="父组件ID"
    )

    # 共享变量
    shared_variables: Mapped[dict[str, object] | None] = mapped_column(
        JSON,
        comment="组件级共享变量"
    )

    # 执行配置
    timeout: Mapped[int] = mapped_column(
        Integer,
        default=300,
        comment="超时时间（秒）"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="重试次数"
    )
    continue_on_failure: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="失败时是否继续"
    )

    # 条件执行配置
    execution_condition: Mapped[str | None] = mapped_column(
        Text,
        comment="执行条件（用于conditional模式）"
    )

    # 配置
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        comment="版本号"
    )
    tags: Mapped[list[str] | None] = mapped_column(
        JSON,
        comment="标签"
    )

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="创建者ID"
    )

    # Relationships
    creator: Mapped["User | None"] = relationship(
        "User",
        back_populates="components"
    )

    # 组件嵌套关系
    parent_component: Mapped["TestComponent | None"] = relationship(
        "TestComponent",
        remote_side=[id],
        back_populates="child_components",
        foreign_keys=[parent_component_id]
    )
    child_components: Mapped[list["TestComponent"]] = relationship(
        "TestComponent",
        back_populates="parent_component",
        cascade="all, delete-orphan",
        foreign_keys=[parent_component_id]
    )

    # 组件-脚本关联
    component_scripts: Mapped[list["ComponentScript"]] = relationship(
        "ComponentScript",
        back_populates="component",
        cascade="all, delete-orphan",
        order_by="ComponentScript.execution_order"
    )

    # 测试用例-组件关联
    test_case_components: Mapped[list["TestCaseComponent"]] = relationship(
        "TestCaseComponent",
        back_populates="component",
        cascade="all, delete-orphan"
    )


class ComponentScript(Base, TimestampMixin):
    """组件-脚本关联表

    定义组件包含哪些脚本，以及脚本的执行顺序和参数覆盖。
    支持参数覆盖机制，组件级参数会覆盖脚本的默认参数。

    Attributes:
        id: 主键ID
        component_id: 组件ID
        script_id: 脚本ID

        # 执行配置
        execution_order: 执行顺序（数字越小越先执行）
        is_enabled: 是否启用

        # 参数覆盖
        script_parameters: 脚本参数覆盖（JSON格式）
        # 参数优先级：运行时 > 测试用例 > 组件 > 脚本 > 环境

        # 条件执行
        execution_condition: 执行条件（表达式）
        skip_on_condition: 条件不满足时是否跳过

        # 说明
        description: 说明

        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 将脚本添加到组件中
        >>> component_script = ComponentScript(
        ...     component_id=1,
        ...     script_id=1,
        ...     execution_order=1,
        ...     script_parameters={
        ...         "username": "test_user",
        ...         "timeout": 60  # 覆盖脚本的默认超时时间
        ...     },
        ...     description="登录脚本"
        ... )
        >>>
        >>> # 添加条件执行的脚本
        >>> conditional_script = ComponentScript(
        ...     component_id=1,
        ...     script_id=2,
        ...     execution_order=2,
        ...     execution_condition="${prev_status} == 'success'",
        ...     skip_on_condition=True,
        ...     description="仅在前一个脚本成功时执行"
        ... )
    """

    __tablename__: str = "component_scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    component_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_components.id", ondelete="CASCADE"),
        nullable=False,
        comment="组件ID"
    )
    script_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_scripts.id", ondelete="CASCADE"),
        nullable=False,
        comment="脚本ID"
    )

    # 执行配置
    execution_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="执行顺序"
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否启用"
    )

    # 参数覆盖
    script_parameters: Mapped[dict[str, object] | None] = mapped_column(
        JSON,
        comment="脚本参数覆盖"
    )

    # 条件执行
    execution_condition: Mapped[str | None] = mapped_column(
        Text,
        comment="执行条件"
    )
    skip_on_condition: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="条件不满足时是否跳过"
    )

    # 说明
    description: Mapped[str | None] = mapped_column(
        Text,
        comment="说明"
    )

    # Relationships
    component: Mapped["TestComponent"] = relationship(
        "TestComponent",
        back_populates="component_scripts"
    )
    script: Mapped["TestScript"] = relationship(
        "TestScript",
        back_populates="component_scripts"
    )
