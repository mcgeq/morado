"""Layer 1: API Definition Components

This module defines the first layer of the test platform architecture:
- Header: Reusable HTTP header components
- Body: Reusable request/response body templates
- ApiDefinition: Complete API interface definitions

The first layer provides the foundation for all test scripts by defining
reusable API components that can be referenced throughout the system.
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.script import TestScript
    from morado.models.user import User


class HeaderScope(str, PyEnum):
    """Header作用域"""

    GLOBAL = "global"  # 全局Header（所有接口可用）
    PROJECT = "project"  # 项目级Header（特定项目可用）
    PRIVATE = "private"  # 私有Header（仅创建者可用）


class BodyType(str, PyEnum):
    """Body类型"""

    REQUEST = "request"  # 请求Body
    RESPONSE = "response"  # 响应Body
    BOTH = "both"  # 请求和响应通用


class HttpMethod(str, PyEnum):
    """HTTP请求方法"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class Header(Base, TimestampMixin, UUIDMixin):
    """HTTP请求头组件（第一层）

    Header是可复用的HTTP请求头组件，可以被多个API定义引用。
    支持全局Header、项目级Header和私有Header。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: Header名称
        description: Header描述

        # Header内容
        headers: Header键值对（JSON格式）

        # 作用域和权限
        scope: 作用域（global/project/private）
        project_id: 项目ID（当scope为project时使用）

        # 配置
        is_active: 是否激活
        version: 版本号
        tags: 标签

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建一个认证Header
        >>> auth_header = Header(
        ...     name="认证Header",
        ...     description="包含Bearer Token的认证Header",
        ...     headers={
        ...         "Authorization": "Bearer ${token}",
        ...         "X-API-Key": "${api_key}"
        ...     },
        ...     scope=HeaderScope.GLOBAL
        ... )
        >>>
        >>> # 创建一个JSON Content-Type Header
        >>> json_header = Header(
        ...     name="JSON Content-Type",
        ...     headers={
        ...         "Content-Type": "application/json",
        ...         "Accept": "application/json"
        ...     },
        ...     scope=HeaderScope.GLOBAL
        ... )
    """

    __tablename__ = "headers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="Header名称")
    description: Mapped[str | None] = mapped_column(Text, comment="Header描述")

    # Header内容
    headers: Mapped[dict] = mapped_column(JSON, nullable=False, comment="Header键值对")

    # 作用域和权限
    scope: Mapped[HeaderScope] = mapped_column(
        Enum(HeaderScope), default=HeaderScope.PRIVATE, comment="作用域"
    )
    project_id: Mapped[int | None] = mapped_column(Integer, comment="项目ID")

    # 配置
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否激活")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", comment="版本号")
    tags: Mapped[list | None] = mapped_column(JSON, comment="标签")

    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="headers")
    api_definitions: Mapped[list["ApiDefinition"]] = relationship(
        "ApiDefinition", back_populates="header", cascade="all, delete-orphan"
    )


class Body(Base, TimestampMixin, UUIDMixin):
    """请求/响应Body组件（第一层）

    Body是可复用的请求/响应体模板，可以被多个API定义引用。
    支持JSON Schema定义和示例数据。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: Body名称
        description: Body描述

        # Body内容
        body_type: Body类型（request/response/both）
        content_type: 内容类型（application/json等）
        body_schema: Body的JSON Schema定义
        example_data: 示例数据

        # 作用域和权限
        scope: 作用域（global/project/private）
        project_id: 项目ID（当scope为project时使用）

        # 配置
        is_active: 是否激活
        version: 版本号
        tags: 标签

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建一个用户信息Body
        >>> user_body = Body(
        ...     name="用户信息Body",
        ...     description="用户基本信息的请求/响应体",
        ...     body_type=BodyType.BOTH,
        ...     content_type="application/json",
        ...     body_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "name": {"type": "string"},
        ...             "age": {"type": "integer"},
        ...             "email": {"type": "string", "format": "email"}
        ...         },
        ...         "required": ["name", "email"]
        ...     },
        ...     example_data={
        ...         "name": "张三",
        ...         "age": 25,
        ...         "email": "zhangsan@example.com"
        ...     },
        ...     scope=BodyScope.GLOBAL
        ... )
    """

    __tablename__ = "bodies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="Body名称")
    description: Mapped[str | None] = mapped_column(Text, comment="Body描述")

    # Body内容
    body_type: Mapped[BodyType] = mapped_column(
        Enum(BodyType), default=BodyType.REQUEST, comment="Body类型"
    )
    content_type: Mapped[str] = mapped_column(
        String(100), default="application/json", comment="内容类型"
    )
    body_schema: Mapped[dict | None] = mapped_column(
        JSON, comment="Body的JSON Schema定义"
    )
    example_data: Mapped[dict | None] = mapped_column(JSON, comment="示例数据")

    # 作用域和权限
    scope: Mapped[HeaderScope] = mapped_column(
        Enum(HeaderScope), default=HeaderScope.PRIVATE, comment="作用域"
    )
    project_id: Mapped[int | None] = mapped_column(Integer, comment="项目ID")

    # 配置
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否激活")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", comment="版本号")
    tags: Mapped[list | None] = mapped_column(JSON, comment="标签")

    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="bodies")
    api_definitions_request: Mapped[list["ApiDefinition"]] = relationship(
        "ApiDefinition",
        foreign_keys="[ApiDefinition.request_body_id]",
        back_populates="request_body",
        cascade="all, delete-orphan",
    )
    api_definitions_response: Mapped[list["ApiDefinition"]] = relationship(
        "ApiDefinition",
        foreign_keys="[ApiDefinition.response_body_id]",
        back_populates="response_body",
        cascade="all, delete-orphan",
    )


class ApiDefinition(Base, TimestampMixin, UUIDMixin):
    """API接口定义（第一层）

    ApiDefinition定义完整的API接口，可以引用Header和Body组件，
    也可以使用内联的Body定义。支持两种组合方式：
    1. 引用Header + 引用Body
    2. 引用Header + 内联Body

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: API名称
        description: API描述

        # API基本信息
        method: HTTP方法（GET/POST/PUT等）
        path: API路径
        base_url: 基础URL（可选）

        # Header引用（方式1和方式2都使用）
        header_id: 引用的Header组件ID

        # Body引用（方式1：引用Body组件）
        request_body_id: 引用的请求Body组件ID
        response_body_id: 引用的响应Body组件ID

        # 内联Body（方式2：自定义Body）
        inline_request_body: 内联请求体
        inline_response_body: 内联响应体

        # 查询参数和路径参数
        query_parameters: 查询参数定义
        path_parameters: 路径参数定义

        # 配置
        timeout: 超时时间（秒）
        is_active: 是否激活
        version: 版本号
        tags: 标签

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 方式1：引用Header和Body组件
        >>> api_def1 = ApiDefinition(
        ...     name="获取用户信息",
        ...     method=HttpMethod.GET,
        ...     path="/api/users/{id}",
        ...     header_id=1,  # 引用认证Header
        ...     response_body_id=2,  # 引用用户信息Body
        ...     path_parameters={"id": {"type": "integer", "description": "用户ID"}}
        ... )
        >>>
        >>> # 方式2：引用Header + 自定义Body
        >>> api_def2 = ApiDefinition(
        ...     name="创建用户",
        ...     method=HttpMethod.POST,
        ...     path="/api/users",
        ...     header_id=1,  # 引用认证Header
        ...     inline_request_body={  # 自定义请求体
        ...         "name": "李四",
        ...         "age": 30,
        ...         "email": "lisi@example.com"
        ...     }
        ... )
    """

    __tablename__ = "api_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="API名称")
    description: Mapped[str | None] = mapped_column(Text, comment="API描述")

    # API基本信息
    method: Mapped[HttpMethod] = mapped_column(
        Enum(HttpMethod), nullable=False, comment="HTTP方法"
    )
    path: Mapped[str] = mapped_column(String(500), nullable=False, comment="API路径")
    base_url: Mapped[str | None] = mapped_column(String(500), comment="基础URL")

    # Header引用
    header_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("headers.id", ondelete="SET NULL"),
        comment="引用的Header组件ID",
    )

    # Body引用（方式1）
    request_body_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("bodies.id", ondelete="SET NULL"),
        comment="引用的请求Body组件ID",
    )
    response_body_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("bodies.id", ondelete="SET NULL"),
        comment="引用的响应Body组件ID",
    )

    # 内联Body（方式2）
    inline_request_body: Mapped[dict | None] = mapped_column(JSON, comment="内联请求体")
    inline_response_body: Mapped[dict | None] = mapped_column(
        JSON, comment="内联响应体"
    )

    # 查询参数和路径参数
    query_parameters: Mapped[dict | None] = mapped_column(JSON, comment="查询参数定义")
    path_parameters: Mapped[dict | None] = mapped_column(JSON, comment="路径参数定义")

    # 配置
    timeout: Mapped[int] = mapped_column(Integer, default=30, comment="超时时间（秒）")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否激活")
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", comment="版本号")
    tags: Mapped[list | None] = mapped_column(JSON, comment="标签")

    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User", back_populates="api_definitions"
    )
    header: Mapped[Optional["Header"]] = relationship(
        "Header", back_populates="api_definitions"
    )
    request_body: Mapped[Optional["Body"]] = relationship(
        "Body", foreign_keys=[request_body_id], back_populates="api_definitions_request"
    )
    response_body: Mapped[Optional["Body"]] = relationship(
        "Body",
        foreign_keys=[response_body_id],
        back_populates="api_definitions_response",
    )
    scripts: Mapped[list["TestScript"]] = relationship(
        "TestScript", back_populates="api_definition", cascade="all, delete-orphan"
    )
