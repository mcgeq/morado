"""Test Case Pydantic schemas.

This module provides schemas for test case API request/response validation.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from morado.schemas.common import PaginatedResponse, TimestampMixin, UUIDMixin


class TestCasePriority(str, Enum):
    """测试用例优先级"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestCaseStatus(str, Enum):
    """测试用例状态"""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TestCaseBase(BaseModel):
    """测试用例基础schema

    包含测试用例的基本字段，用于创建和更新操作。
    """

    name: str = Field(min_length=1, max_length=200, description="用例名称")
    description: str | None = Field(default=None, description="用例描述")
    priority: TestCasePriority = Field(
        default=TestCasePriority.MEDIUM, description="优先级"
    )
    status: TestCaseStatus = Field(default=TestCaseStatus.DRAFT, description="状态")
    category: str | None = Field(default=None, max_length=100, description="分类")
    tags: list[str] | None = Field(default=None, description="标签")
    preconditions: str | None = Field(default=None, description="前置条件")
    postconditions: str | None = Field(default=None, description="后置条件")
    execution_order: str = Field(
        default="sequential", pattern="^(sequential|parallel)$", description="执行顺序"
    )
    timeout: int = Field(default=300, ge=1, description="超时时间（秒）")
    retry_count: int = Field(default=0, ge=0, description="重试次数")
    continue_on_failure: bool = Field(default=False, description="失败时是否继续")
    test_data: dict | None = Field(default=None, description="测试数据")
    environment: str = Field(default="test", max_length=20, description="执行环境")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    is_automated: bool = Field(default=True, description="是否自动化")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "用户登录测试",
                "description": "测试用户登录功能",
                "priority": "high",
                "status": "active",
                "category": "用户管理",
                "tags": ["登录", "认证"],
                "timeout": 300,
                "environment": "test",
            }
        },
    )


class TestCaseCreate(TestCaseBase):
    """创建测试用例schema

    用于创建新的测试用例。
    """

    created_by: int | None = Field(default=None, description="创建者ID")


class TestCaseUpdate(BaseModel):
    """更新测试用例schema

    所有字段都是可选的，只更新提供的字段。
    """

    name: str | None = Field(
        default=None, min_length=1, max_length=200, description="用例名称"
    )
    description: str | None = Field(default=None, description="用例描述")
    priority: TestCasePriority | None = Field(default=None, description="优先级")
    status: TestCaseStatus | None = Field(default=None, description="状态")
    category: str | None = Field(default=None, max_length=100, description="分类")
    tags: list[str] | None = Field(default=None, description="标签")
    preconditions: str | None = Field(default=None, description="前置条件")
    postconditions: str | None = Field(default=None, description="后置条件")
    execution_order: str | None = Field(
        default=None, pattern="^(sequential|parallel)$", description="执行顺序"
    )
    timeout: int | None = Field(default=None, ge=1, description="超时时间（秒）")
    retry_count: int | None = Field(default=None, ge=0, description="重试次数")
    continue_on_failure: bool | None = Field(default=None, description="失败时是否继续")
    test_data: dict | None = Field(default=None, description="测试数据")
    environment: str | None = Field(default=None, max_length=20, description="执行环境")
    version: str | None = Field(default=None, max_length=20, description="版本号")
    is_automated: bool | None = Field(default=None, description="是否自动化")

    model_config = ConfigDict(from_attributes=True)


class TestCaseResponse(TestCaseBase, TimestampMixin, UUIDMixin):
    """测试用例响应schema

    包含完整的测试用例信息，包括ID和时间戳。
    """

    id: int = Field(description="用例ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "用户登录测试",
                "description": "测试用户登录功能",
                "priority": "high",
                "status": "active",
                "category": "用户管理",
                "tags": ["登录", "认证"],
                "timeout": 300,
                "environment": "test",
                "version": "1.0.0",
                "is_automated": True,
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )


class TestCaseListResponse(PaginatedResponse[TestCaseResponse]):
    """测试用例列表响应schema"""


# Test Case Script Schemas


class TestCaseScriptBase(BaseModel):
    """测试用例-脚本关联基础schema"""

    test_case_id: int = Field(description="测试用例ID")
    script_id: int = Field(description="脚本ID")
    execution_order: int = Field(default=0, description="执行顺序")
    is_enabled: bool = Field(default=True, description="是否启用")
    script_parameters: dict | None = Field(default=None, description="脚本参数覆盖")
    description: str | None = Field(default=None, description="说明")

    model_config = ConfigDict(from_attributes=True)


class TestCaseScriptCreate(TestCaseScriptBase):
    """创建测试用例-脚本关联schema"""


class TestCaseScriptResponse(TestCaseScriptBase, TimestampMixin):
    """测试用例-脚本关联响应schema"""

    id: int = Field(description="关联ID")

    model_config = ConfigDict(from_attributes=True)


# Test Case Component Schemas


class TestCaseComponentBase(BaseModel):
    """测试用例-组件关联基础schema"""

    test_case_id: int = Field(description="测试用例ID")
    component_id: int = Field(description="组件ID")
    execution_order: int = Field(default=0, description="执行顺序")
    is_enabled: bool = Field(default=True, description="是否启用")
    component_parameters: dict | None = Field(default=None, description="组件参数覆盖")
    description: str | None = Field(default=None, description="说明")

    model_config = ConfigDict(from_attributes=True)


class TestCaseComponentCreate(TestCaseComponentBase):
    """创建测试用例-组件关联schema"""


class TestCaseComponentResponse(TestCaseComponentBase, TimestampMixin):
    """测试用例-组件关联响应schema"""

    id: int = Field(description="关联ID")

    model_config = ConfigDict(from_attributes=True)
