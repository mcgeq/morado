"""Test Component Pydantic schemas.

This module provides schemas for Layer 3 (Test Components):
- TestComponent: Composite components that combine multiple scripts
- ComponentScript: Association between components and scripts
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from morado.schemas.common import PaginatedResponse, TimestampMixin, UUIDMixin


class ComponentType(str, Enum):
    """组件类型"""
    SIMPLE = "simple"
    COMPOSITE = "composite"
    TEMPLATE = "template"


class ExecutionMode(str, Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


# TestComponent Schemas

class TestComponentBase(BaseModel):
    """测试组件基础schema"""

    name: str = Field(min_length=1, max_length=200, description="组件名称")
    description: str | None = Field(default=None, description="组件描述")
    component_type: ComponentType = Field(default=ComponentType.SIMPLE, description="组件类型")
    execution_mode: ExecutionMode = Field(default=ExecutionMode.SEQUENTIAL, description="执行模式")
    parent_component_id: int | None = Field(default=None, description="父组件ID")
    shared_variables: dict | None = Field(default=None, description="组件级共享变量")
    timeout: int = Field(default=300, ge=1, description="超时时间（秒）")
    retry_count: int = Field(default=0, ge=0, description="重试次数")
    continue_on_failure: bool = Field(default=False, description="失败时是否继续")
    execution_condition: str | None = Field(default=None, description="执行条件（用于conditional模式）")
    is_active: bool = Field(default=True, description="是否激活")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "用户登录流程",
                "description": "包含登录前准备、登录、验证的完整流程",
                "component_type": "simple",
                "execution_mode": "sequential",
                "shared_variables": {
                    "base_url": "https://api.example.com",
                    "timeout": 30
                },
                "timeout": 300,
                "retry_count": 0,
                "continue_on_failure": False,
                "is_active": True,
                "version": "1.0.0",
                "tags": ["登录", "用户"]
            }
        }
    )


class TestComponentCreate(TestComponentBase):
    """创建测试组件schema"""

    created_by: int | None = Field(default=None, description="创建者ID")


class TestComponentUpdate(BaseModel):
    """更新测试组件schema"""

    name: str | None = Field(default=None, min_length=1, max_length=200, description="组件名称")
    description: str | None = Field(default=None, description="组件描述")
    component_type: ComponentType | None = Field(default=None, description="组件类型")
    execution_mode: ExecutionMode | None = Field(default=None, description="执行模式")
    parent_component_id: int | None = Field(default=None, description="父组件ID")
    shared_variables: dict | None = Field(default=None, description="组件级共享变量")
    timeout: int | None = Field(default=None, ge=1, description="超时时间（秒）")
    retry_count: int | None = Field(default=None, ge=0, description="重试次数")
    continue_on_failure: bool | None = Field(default=None, description="失败时是否继续")
    execution_condition: str | None = Field(default=None, description="执行条件（用于conditional模式）")
    is_active: bool | None = Field(default=None, description="是否激活")
    version: str | None = Field(default=None, max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(from_attributes=True)


class TestComponentResponse(TestComponentBase, TimestampMixin, UUIDMixin):
    """测试组件响应schema"""

    id: int = Field(description="组件ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "用户登录流程",
                "description": "包含登录前准备、登录、验证的完整流程",
                "component_type": "simple",
                "execution_mode": "sequential",
                "shared_variables": {
                    "base_url": "https://api.example.com",
                    "timeout": 30
                },
                "timeout": 300,
                "retry_count": 0,
                "continue_on_failure": False,
                "is_active": True,
                "version": "1.0.0",
                "tags": ["登录", "用户"],
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class TestComponentListResponse(PaginatedResponse[TestComponentResponse]):
    """测试组件列表响应schema"""


# ComponentScript Schemas

class ComponentScriptBase(BaseModel):
    """组件-脚本关联基础schema"""

    component_id: int = Field(description="组件ID")
    script_id: int = Field(description="脚本ID")
    execution_order: int = Field(default=0, description="执行顺序")
    is_enabled: bool = Field(default=True, description="是否启用")
    script_parameters: dict | None = Field(default=None, description="脚本参数覆盖")
    execution_condition: str | None = Field(default=None, description="执行条件")
    skip_on_condition: bool = Field(default=False, description="条件不满足时是否跳过")
    description: str | None = Field(default=None, description="说明")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "component_id": 1,
                "script_id": 1,
                "execution_order": 1,
                "is_enabled": True,
                "script_parameters": {
                    "username": "test_user",
                    "timeout": 60
                },
                "description": "登录脚本"
            }
        }
    )


class ComponentScriptCreate(ComponentScriptBase):
    """创建组件-脚本关联schema"""


class ComponentScriptUpdate(BaseModel):
    """更新组件-脚本关联schema"""

    execution_order: int | None = Field(default=None, description="执行顺序")
    is_enabled: bool | None = Field(default=None, description="是否启用")
    script_parameters: dict | None = Field(default=None, description="脚本参数覆盖")
    execution_condition: str | None = Field(default=None, description="执行条件")
    skip_on_condition: bool | None = Field(default=None, description="条件不满足时是否跳过")
    description: str | None = Field(default=None, description="说明")

    model_config = ConfigDict(from_attributes=True)


class ComponentScriptResponse(ComponentScriptBase, TimestampMixin):
    """组件-脚本关联响应schema"""

    id: int = Field(description="关联ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "component_id": 1,
                "script_id": 1,
                "execution_order": 1,
                "is_enabled": True,
                "script_parameters": {
                    "username": "test_user",
                    "timeout": 60
                },
                "description": "登录脚本",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class ComponentScriptListResponse(PaginatedResponse[ComponentScriptResponse]):
    """组件-脚本关联列表响应schema"""
