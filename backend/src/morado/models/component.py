"""Layer 3: Test Component

This module defines the third layer of the test platform architecture:
- TestComponent: Composite components made of multiple scripts
- ComponentScript: Association between components and scripts

Components can reference other components, creating a hierarchical structure.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.script import TestScript
    from morado.models.test_case import TestCaseComponent
    from morado.models.user import User


class TestComponent(Base, TimestampMixin, UUIDMixin):
    """测试联合组件（第三层）

    TestComponent是多个脚本的组合，可以引用其他联合组件，形成层次结构。
    组件可以独立调试执行，支持复杂的测试场景编排。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: 组件名称
        description: 组件描述

        # 组件引用（支持引用其他组件）
        parent_component_id: 父组件ID（用于组件嵌套）

        # 执行配置
        execution_order: 执行顺序配置
        parallel_execution: 是否并行执行
        continue_on_failure: 失败时是否继续

        # 数据共享
        shared_variables: 组件内共享的变量

        # 配置
        is_debuggable: 是否可调试
        version: 版本号
        tags: 标签

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建一个用户管理组件，包含多个脚本
        >>> component = TestComponent(
        ...     name="用户管理完整流程",
        ...     description="包含创建、查询、更新、删除用户的完整流程",
        ...     execution_order="sequential",
        ...     shared_variables={"base_url": "https://api.example.com"}
        ... )
        >>>
        >>> # 创建一个嵌套组件，引用其他组件
        >>> nested_component = TestComponent(
        ...     name="完整业务流程",
        ...     parent_component_id=component.id,
        ...     description="包含用户管理和订单管理的完整业务流程"
        ... )
    """

    __tablename__ = "test_components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="组件名称")
    description: Mapped[str | None] = mapped_column(Text, comment="组件描述")

    # 组件嵌套（支持引用其他组件）
    parent_component_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("test_components.id", ondelete="CASCADE"),
        comment="父组件ID"
    )

    # 执行配置
    execution_order: Mapped[str] = mapped_column(
        String(20),
        default="sequential",
        comment="执行顺序（sequential/parallel）"
    )
    parallel_execution: Mapped[bool] = mapped_column(default=False, comment="是否并行执行")
    continue_on_failure: Mapped[bool] = mapped_column(default=False, comment="失败时是否继续")

    # 数据共享
    shared_variables: Mapped[dict | None] = mapped_column(JSON, comment="组件内共享的变量")

    # 配置
    is_debuggable: Mapped[bool] = mapped_column(default=True, comment="是否可调试")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", comment="版本号")
    tags: Mapped[list | None] = mapped_column(JSON, comment="标签")

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="components")
    parent_component: Mapped[Optional["TestComponent"]] = relationship(
        "TestComponent",
        remote_side=[id],
        back_populates="child_components"
    )
    child_components: Mapped[list["TestComponent"]] = relationship(
        "TestComponent",
        back_populates="parent_component",
        cascade="all, delete-orphan"
    )
    component_scripts: Mapped[list["ComponentScript"]] = relationship(
        "ComponentScript",
        back_populates="component",
        cascade="all, delete-orphan",
        order_by="ComponentScript.execution_order"
    )
    test_case_components: Mapped[list["TestCaseComponent"]] = relationship(
        "TestCaseComponent",
        back_populates="component",
        cascade="all, delete-orphan"
    )


class ComponentScript(Base, TimestampMixin):
    """组件-脚本关联表

    定义组件包含哪些脚本，以及脚本的执行顺序和配置。

    Attributes:
        id: 主键ID
        component_id: 组件ID
        script_id: 脚本ID
        execution_order: 执行顺序（数字越小越先执行）
        is_enabled: 是否启用
        script_parameters: 脚本参数覆盖（JSON格式）
        description: 说明
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 将脚本添加到组件中
        >>> comp_script1 = ComponentScript(
        ...     component_id=1,
        ...     script_id=1,
        ...     execution_order=1,
        ...     script_parameters={"user_id": 123}
        ... )
        >>> comp_script2 = ComponentScript(
        ...     component_id=1,
        ...     script_id=2,
        ...     execution_order=2
        ... )
    """

    __tablename__ = "component_scripts"

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
    execution_order: Mapped[int] = mapped_column(Integer, default=0, comment="执行顺序")
    is_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用")
    script_parameters: Mapped[dict | None] = mapped_column(JSON, comment="脚本参数覆盖")
    description: Mapped[str | None] = mapped_column(Text, comment="说明")

    # Relationships
    component: Mapped["TestComponent"] = relationship("TestComponent", back_populates="component_scripts")
    script: Mapped["TestScript"] = relationship("TestScript", back_populates="component_scripts")
