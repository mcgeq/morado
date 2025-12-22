"""Test Script Pydantic schemas.

This module provides schemas for Layer 2 (Test Scripts):
- TestScript: Executable scripts that reference API definitions
- ScriptParameter: Parameter definitions for scripts
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from morado.schemas.common import PaginatedResponse, TimestampMixin, UUIDMixin


class ScriptType(str, Enum):
    """脚本类型"""
    SETUP = "setup"
    MAIN = "main"
    TEARDOWN = "teardown"
    UTILITY = "utility"


class AssertionType(str, Enum):
    """断言类型"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX_MATCH = "regex_match"
    JSON_PATH = "json_path"
    STATUS_CODE = "status_code"
    RESPONSE_TIME = "response_time"
    CUSTOM = "custom"


class ParameterType(str, Enum):
    """参数类型"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"
    FILE = "file"


# TestScript Schemas

class TestScriptBase(BaseModel):
    """测试脚本基础schema"""

    name: str = Field(min_length=1, max_length=200, description="脚本名称")
    description: str | None = Field(default=None, description="脚本描述")
    api_definition_id: int = Field(description="引用的API定义ID")
    script_type: ScriptType = Field(default=ScriptType.MAIN, description="脚本类型")
    execution_order: int = Field(default=0, description="执行顺序")
    variables: dict | None = Field(default=None, description="脚本级变量")
    assertions: list | None = Field(default=None, description="断言列表")
    validators: dict | None = Field(default=None, description="验证器配置")
    pre_script: str | None = Field(default=None, description="前置脚本代码")
    post_script: str | None = Field(default=None, description="后置脚本代码")
    extract_variables: dict | None = Field(default=None, description="从响应中提取的变量配置")
    output_variables: list[str] | None = Field(default=None, description="输出变量列表")
    debug_mode: bool = Field(default=False, description="是否启用调试模式")
    debug_breakpoints: list | None = Field(default=None, description="调试断点配置")
    retry_count: int = Field(default=0, ge=0, description="重试次数")
    retry_interval: float = Field(default=1.0, ge=0, description="重试间隔（秒）")
    timeout_override: int | None = Field(default=None, ge=1, description="超时时间覆盖（秒）")
    is_active: bool = Field(default=True, description="是否激活")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "测试用户登录",
                "description": "验证用户登录功能",
                "api_definition_id": 1,
                "script_type": "main",
                "execution_order": 1,
                "variables": {
                    "username": "testuser",
                    "password": "testpass123"
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200,
                        "message": "登录应该返回200状态码"
                    },
                    {
                        "type": "json_path",
                        "path": "$.data.token",
                        "assertion": "exists",
                        "message": "响应应该包含token"
                    }
                ],
                "extract_variables": {
                    "auth_token": "$.data.token",
                    "user_id": "$.data.user.id"
                },
                "output_variables": ["auth_token", "user_id"],
                "retry_count": 0,
                "retry_interval": 1.0,
                "is_active": True,
                "version": "1.0.0",
                "tags": ["登录", "认证"]
            }
        }
    )


class TestScriptCreate(TestScriptBase):
    """创建测试脚本schema"""

    created_by: int | None = Field(default=None, description="创建者ID")


class TestScriptUpdate(BaseModel):
    """更新测试脚本schema"""

    name: str | None = Field(default=None, min_length=1, max_length=200, description="脚本名称")
    description: str | None = Field(default=None, description="脚本描述")
    api_definition_id: int | None = Field(default=None, description="引用的API定义ID")
    script_type: ScriptType | None = Field(default=None, description="脚本类型")
    execution_order: int | None = Field(default=None, description="执行顺序")
    variables: dict | None = Field(default=None, description="脚本级变量")
    assertions: list | None = Field(default=None, description="断言列表")
    validators: dict | None = Field(default=None, description="验证器配置")
    pre_script: str | None = Field(default=None, description="前置脚本代码")
    post_script: str | None = Field(default=None, description="后置脚本代码")
    extract_variables: dict | None = Field(default=None, description="从响应中提取的变量配置")
    output_variables: list[str] | None = Field(default=None, description="输出变量列表")
    debug_mode: bool | None = Field(default=None, description="是否启用调试模式")
    debug_breakpoints: list | None = Field(default=None, description="调试断点配置")
    retry_count: int | None = Field(default=None, ge=0, description="重试次数")
    retry_interval: float | None = Field(default=None, ge=0, description="重试间隔（秒）")
    timeout_override: int | None = Field(default=None, ge=1, description="超时时间覆盖（秒）")
    is_active: bool | None = Field(default=None, description="是否激活")
    version: str | None = Field(default=None, max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(from_attributes=True)


class TestScriptResponse(TestScriptBase, TimestampMixin, UUIDMixin):
    """测试脚本响应schema"""

    id: int = Field(description="脚本ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "测试用户登录",
                "description": "验证用户登录功能",
                "api_definition_id": 1,
                "script_type": "main",
                "execution_order": 1,
                "variables": {
                    "username": "testuser",
                    "password": "testpass123"
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200,
                        "message": "登录应该返回200状态码"
                    }
                ],
                "extract_variables": {
                    "auth_token": "$.data.token",
                    "user_id": "$.data.user.id"
                },
                "output_variables": ["auth_token", "user_id"],
                "retry_count": 0,
                "retry_interval": 1.0,
                "is_active": True,
                "version": "1.0.0",
                "tags": ["登录", "认证"],
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class TestScriptListResponse(PaginatedResponse[TestScriptResponse]):
    """测试脚本列表响应schema"""


# ScriptParameter Schemas

class ScriptParameterBase(BaseModel):
    """脚本参数基础schema"""

    script_id: int = Field(description="所属脚本ID")
    name: str = Field(min_length=1, max_length=100, description="参数名称")
    description: str | None = Field(default=None, description="参数描述")
    parameter_type: ParameterType = Field(default=ParameterType.STRING, description="参数类型")
    default_value: str | None = Field(default=None, description="默认值（JSON字符串）")
    is_required: bool = Field(default=False, description="是否必需")
    validation_rules: dict | None = Field(default=None, description="验证规则")
    order: int = Field(default=0, description="显示顺序")
    group: str | None = Field(default=None, max_length=100, description="参数分组")
    is_sensitive: bool = Field(default=False, description="是否敏感信息")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "script_id": 1,
                "name": "username",
                "description": "用户名",
                "parameter_type": "string",
                "default_value": "testuser",
                "is_required": True,
                "validation_rules": {
                    "min_length": 3,
                    "max_length": 50,
                    "pattern": "^[a-zA-Z0-9_]+$"
                },
                "order": 1,
                "is_sensitive": False
            }
        }
    )


class ScriptParameterCreate(ScriptParameterBase):
    """创建脚本参数schema"""


class ScriptParameterUpdate(BaseModel):
    """更新脚本参数schema"""

    name: str | None = Field(default=None, min_length=1, max_length=100, description="参数名称")
    description: str | None = Field(default=None, description="参数描述")
    parameter_type: ParameterType | None = Field(default=None, description="参数类型")
    default_value: str | None = Field(default=None, description="默认值（JSON字符串）")
    is_required: bool | None = Field(default=None, description="是否必需")
    validation_rules: dict | None = Field(default=None, description="验证规则")
    order: int | None = Field(default=None, description="显示顺序")
    group: str | None = Field(default=None, max_length=100, description="参数分组")
    is_sensitive: bool | None = Field(default=None, description="是否敏感信息")

    model_config = ConfigDict(from_attributes=True)


class ScriptParameterResponse(ScriptParameterBase, TimestampMixin, UUIDMixin):
    """脚本参数响应schema"""

    id: int = Field(description="参数ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "script_id": 1,
                "name": "username",
                "description": "用户名",
                "parameter_type": "string",
                "default_value": "testuser",
                "is_required": True,
                "validation_rules": {
                    "min_length": 3,
                    "max_length": 50,
                    "pattern": "^[a-zA-Z0-9_]+$"
                },
                "order": 1,
                "is_sensitive": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class ScriptParameterListResponse(PaginatedResponse[ScriptParameterResponse]):
    """脚本参数列表响应schema"""
