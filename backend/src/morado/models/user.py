"""User Model

This module defines the user model and related authentication/authorization.
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.api_component import ApiDefinition, Body, Header
    from morado.models.component import TestComponent
    from morado.models.script import TestScript
    from morado.models.test_case import TestCase
    from morado.models.test_execution import TestExecution
    from morado.models.test_suite import TestSuite


class UserRole(str, PyEnum):
    """用户角色"""
    ADMIN = "admin"  # 管理员
    DEVELOPER = "developer"  # 开发者
    TESTER = "tester"  # 测试人员
    VIEWER = "viewer"  # 查看者


class User(Base, TimestampMixin, UUIDMixin):
    """用户模型

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        username: 用户名
        email: 邮箱
        password_hash: 密码哈希
        full_name: 全名
        role: 角色
        is_active: 是否激活
        is_superuser: 是否超级用户
        avatar_url: 头像URL
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> user = User(
        ...     username="john_doe",
        ...     email="john@example.com",
        ...     full_name="John Doe",
        ...     role=UserRole.TESTER
        ... )
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="用户名"
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="邮箱"
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    full_name: Mapped[str | None] = mapped_column(String(100), comment="全名")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.TESTER,
        comment="角色"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超级用户")
    avatar_url: Mapped[str | None] = mapped_column(String(500), comment="头像URL")

    # Relationships
    headers: Mapped[list["Header"]] = relationship("Header", back_populates="creator")
    bodies: Mapped[list["Body"]] = relationship("Body", back_populates="creator")
    api_definitions: Mapped[list["ApiDefinition"]] = relationship("ApiDefinition", back_populates="creator")
    scripts: Mapped[list["TestScript"]] = relationship("TestScript", back_populates="creator")
    components: Mapped[list["TestComponent"]] = relationship("TestComponent", back_populates="creator")
    test_cases: Mapped[list["TestCase"]] = relationship("TestCase", back_populates="creator")
    test_suites: Mapped[list["TestSuite"]] = relationship("TestSuite", back_populates="creator")
    executions: Mapped[list["TestExecution"]] = relationship("TestExecution", back_populates="creator")
