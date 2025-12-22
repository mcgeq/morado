"""Layer 2: Test Script Models

This module defines the second layer of the test platform architecture:
- TestScript: Executable scripts that reference API definitions
- ScriptParameter: Parameter definitions for scripts

The second layer builds on Layer 1 (API definitions) by creating executable
test scripts that can be debugged independently and used in components and test cases.
"""

from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from morado.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from morado.models.api_component import ApiDefinition
    from morado.models.component import ComponentScript
    from morado.models.test_case import TestCaseScript
    from morado.models.user import User


class ScriptType(str, PyEnum):
    """脚本类型"""
    SETUP = "setup"  # 前置脚本（准备测试环境）
    MAIN = "main"  # 主脚本（核心测试逻辑）
    TEARDOWN = "teardown"  # 后置脚本（清理测试环境）
    UTILITY = "utility"  # 工具脚本（可被其他脚本调用）


class AssertionType(str, PyEnum):
    """断言类型"""
    EQUALS = "equals"  # 相等断言
    NOT_EQUALS = "not_equals"  # 不相等断言
    CONTAINS = "contains"  # 包含断言
    NOT_CONTAINS = "not_contains"  # 不包含断言
    GREATER_THAN = "greater_than"  # 大于断言
    LESS_THAN = "less_than"  # 小于断言
    REGEX_MATCH = "regex_match"  # 正则匹配断言
    JSON_PATH = "json_path"  # JSON路径断言
    STATUS_CODE = "status_code"  # HTTP状态码断言
    RESPONSE_TIME = "response_time"  # 响应时间断言
    CUSTOM = "custom"  # 自定义断言（使用脚本）


class ParameterType(str, PyEnum):
    """参数类型"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"
    FILE = "file"


class TestScript(Base, TimestampMixin, UUIDMixin):
    """测试脚本（第二层）

    TestScript是引用ApiDefinition的可执行脚本，支持独立调试执行。
    脚本可以定义参数、断言和验证器，并支持前置/主/后置脚本类型。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        name: 脚本名称
        description: 脚本描述

        # API引用
        api_definition_id: 引用的API定义ID

        # 脚本类型和配置
        script_type: 脚本类型（setup/main/teardown/utility）
        execution_order: 执行顺序（在同类型脚本中的顺序）

        # 脚本变量
        variables: 脚本级变量（JSON格式）

        # 断言配置
        assertions: 断言列表（JSON格式）
        validators: 验证器配置（JSON格式）

        # 前置和后置脚本
        pre_script: 前置脚本代码（Python/JavaScript）
        post_script: 后置脚本代码（Python/JavaScript）

        # 输出配置
        extract_variables: 从响应中提取的变量配置
        output_variables: 输出变量列表（传递给下一个脚本）

        # 调试配置
        debug_mode: 是否启用调试模式
        debug_breakpoints: 调试断点配置

        # 重试和超时配置
        retry_count: 重试次数
        retry_interval: 重试间隔（秒）
        timeout_override: 超时时间覆盖（秒）

        # 配置
        is_active: 是否激活
        version: 版本号
        tags: 标签

        created_by: 创建者ID
        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建一个主测试脚本
        >>> script = TestScript(
        ...     name="测试用户登录",
        ...     description="验证用户登录功能",
        ...     api_definition_id=1,
        ...     script_type=ScriptType.MAIN,
        ...     variables={
        ...         "username": "testuser",
        ...         "password": "testpass123"
        ...     },
        ...     assertions=[
        ...         {
        ...             "type": "status_code",
        ...             "expected": 200,
        ...             "message": "登录应该返回200状态码"
        ...         },
        ...         {
        ...             "type": "json_path",
        ...             "path": "$.data.token",
        ...             "assertion": "exists",
        ...             "message": "响应应该包含token"
        ...         }
        ...     ],
        ...     extract_variables={
        ...         "auth_token": "$.data.token",
        ...         "user_id": "$.data.user.id"
        ...     },
        ...     output_variables=["auth_token", "user_id"]
        ... )
        >>>
        >>> # 创建一个前置脚本
        >>> setup_script = TestScript(
        ...     name="准备测试数据",
        ...     description="创建测试用户",
        ...     api_definition_id=2,
        ...     script_type=ScriptType.SETUP,
        ...     execution_order=1
        ... )
    """

    __tablename__ = "test_scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="脚本名称")
    description: Mapped[str | None] = mapped_column(Text, comment="脚本描述")

    # API引用
    api_definition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("api_definitions.id", ondelete="CASCADE"),
        nullable=False,
        comment="引用的API定义ID"
    )

    # 脚本类型和配置
    script_type: Mapped[ScriptType] = mapped_column(
        Enum(ScriptType),
        default=ScriptType.MAIN,
        comment="脚本类型"
    )
    execution_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="执行顺序"
    )

    # 脚本变量
    variables: Mapped[dict | None] = mapped_column(
        JSON,
        comment="脚本级变量"
    )

    # 断言配置
    assertions: Mapped[list | None] = mapped_column(
        JSON,
        comment="断言列表"
    )
    validators: Mapped[dict | None] = mapped_column(
        JSON,
        comment="验证器配置"
    )

    # 前置和后置脚本
    pre_script: Mapped[str | None] = mapped_column(
        Text,
        comment="前置脚本代码"
    )
    post_script: Mapped[str | None] = mapped_column(
        Text,
        comment="后置脚本代码"
    )

    # 输出配置
    extract_variables: Mapped[dict | None] = mapped_column(
        JSON,
        comment="从响应中提取的变量配置"
    )
    output_variables: Mapped[list | None] = mapped_column(
        JSON,
        comment="输出变量列表"
    )

    # 调试配置
    debug_mode: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否启用调试模式"
    )
    debug_breakpoints: Mapped[list | None] = mapped_column(
        JSON,
        comment="调试断点配置"
    )

    # 重试和超时配置
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="重试次数"
    )
    retry_interval: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        comment="重试间隔（秒）"
    )
    timeout_override: Mapped[int | None] = mapped_column(
        Integer,
        comment="超时时间覆盖（秒）"
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
    tags: Mapped[list | None] = mapped_column(
        JSON,
        comment="标签"
    )

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        comment="创建者ID"
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="scripts"
    )
    api_definition: Mapped["ApiDefinition"] = relationship(
        "ApiDefinition",
        back_populates="scripts"
    )
    parameters: Mapped[list["ScriptParameter"]] = relationship(
        "ScriptParameter",
        back_populates="script",
        cascade="all, delete-orphan",
        order_by="ScriptParameter.order"
    )
    component_scripts: Mapped[list["ComponentScript"]] = relationship(
        "ComponentScript",
        back_populates="script",
        cascade="all, delete-orphan"
    )
    test_case_scripts: Mapped[list["TestCaseScript"]] = relationship(
        "TestCaseScript",
        back_populates="script",
        cascade="all, delete-orphan"
    )


class ScriptParameter(Base, TimestampMixin, UUIDMixin):
    """脚本参数定义

    ScriptParameter定义脚本的输入参数，支持类型验证、默认值和描述。
    参数可以在脚本执行时被覆盖（遵循参数优先级规则）。

    Attributes:
        id: 主键ID
        uuid: 唯一标识符
        script_id: 所属脚本ID

        # 参数定义
        name: 参数名称
        description: 参数描述
        parameter_type: 参数类型

        # 默认值和验证
        default_value: 默认值
        is_required: 是否必需
        validation_rules: 验证规则（JSON格式）

        # 显示配置
        order: 显示顺序
        group: 参数分组

        # 配置
        is_sensitive: 是否敏感信息（如密码）

        created_at: 创建时间
        updated_at: 更新时间

    Example:
        >>> # 创建字符串参数
        >>> param1 = ScriptParameter(
        ...     script_id=1,
        ...     name="username",
        ...     description="用户名",
        ...     parameter_type=ParameterType.STRING,
        ...     default_value="testuser",
        ...     is_required=True,
        ...     validation_rules={
        ...         "min_length": 3,
        ...         "max_length": 50,
        ...         "pattern": "^[a-zA-Z0-9_]+$"
        ...     },
        ...     order=1
        ... )
        >>>
        >>> # 创建整数参数
        >>> param2 = ScriptParameter(
        ...     script_id=1,
        ...     name="timeout",
        ...     description="超时时间（秒）",
        ...     parameter_type=ParameterType.INTEGER,
        ...     default_value=30,
        ...     is_required=False,
        ...     validation_rules={
        ...         "min": 1,
        ...         "max": 300
        ...     },
        ...     order=2
        ... )
        >>>
        >>> # 创建敏感参数
        >>> param3 = ScriptParameter(
        ...     script_id=1,
        ...     name="password",
        ...     description="密码",
        ...     parameter_type=ParameterType.STRING,
        ...     is_required=True,
        ...     is_sensitive=True,
        ...     order=3
        ... )
    """

    __tablename__ = "script_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    script_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_scripts.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属脚本ID"
    )

    # 参数定义
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="参数名称"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        comment="参数描述"
    )
    parameter_type: Mapped[ParameterType] = mapped_column(
        Enum(ParameterType),
        default=ParameterType.STRING,
        comment="参数类型"
    )

    # 默认值和验证
    default_value: Mapped[str | None] = mapped_column(
        Text,
        comment="默认值（JSON字符串）"
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否必需"
    )
    validation_rules: Mapped[dict | None] = mapped_column(
        JSON,
        comment="验证规则"
    )

    # 显示配置
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="显示顺序"
    )
    group: Mapped[str | None] = mapped_column(
        String(100),
        comment="参数分组"
    )

    # 配置
    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否敏感信息"
    )

    # Relationships
    script: Mapped["TestScript"] = relationship(
        "TestScript",
        back_populates="parameters"
    )
