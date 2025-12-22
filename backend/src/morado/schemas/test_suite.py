"""Test Suite Pydantic schemas.

This module provides schemas for test suite API request/response validation.
"""


from pydantic import BaseModel, ConfigDict, Field

from morado.schemas.common import PaginatedResponse, TimestampMixin, UUIDMixin


class TestSuiteBase(BaseModel):
    """测试套件基础schema

    包含测试套件的基本字段，用于创建和更新操作。
    """

    name: str = Field(min_length=1, max_length=200, description="套件名称")
    description: str | None = Field(default=None, description="套件描述")
    execution_order: str = Field(default="sequential", pattern="^(sequential|parallel)$", description="执行顺序")
    parallel_execution: bool = Field(default=False, description="是否并行执行")
    continue_on_failure: bool = Field(default=True, description="失败时是否继续")
    schedule_config: dict | None = Field(default=None, description="调度配置")
    is_scheduled: bool = Field(default=False, description="是否启用调度")
    environment: str = Field(default="test", max_length=20, description="执行环境")
    global_variables: dict | None = Field(default=None, description="全局变量")
    tags: list[str] | None = Field(default=None, description="标签")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "用户模块回归测试套件",
                "description": "包含所有用户相关功能的测试用例",
                "execution_order": "sequential",
                "parallel_execution": False,
                "continue_on_failure": True,
                "environment": "test",
                "tags": ["回归测试", "用户模块"],
                "version": "1.0.0"
            }
        }
    )


class TestSuiteCreate(TestSuiteBase):
    """创建测试套件schema

    用于创建新的测试套件。
    """

    created_by: int | None = Field(default=None, description="创建者ID")


class TestSuiteUpdate(BaseModel):
    """更新测试套件schema

    所有字段都是可选的，只更新提供的字段。
    """

    name: str | None = Field(default=None, min_length=1, max_length=200, description="套件名称")
    description: str | None = Field(default=None, description="套件描述")
    execution_order: str | None = Field(default=None, pattern="^(sequential|parallel)$", description="执行顺序")
    parallel_execution: bool | None = Field(default=None, description="是否并行执行")
    continue_on_failure: bool | None = Field(default=None, description="失败时是否继续")
    schedule_config: dict | None = Field(default=None, description="调度配置")
    is_scheduled: bool | None = Field(default=None, description="是否启用调度")
    environment: str | None = Field(default=None, max_length=20, description="执行环境")
    global_variables: dict | None = Field(default=None, description="全局变量")
    tags: list[str] | None = Field(default=None, description="标签")
    version: str | None = Field(default=None, max_length=20, description="版本号")

    model_config = ConfigDict(from_attributes=True)


class TestSuiteResponse(TestSuiteBase, TimestampMixin, UUIDMixin):
    """测试套件响应schema

    包含完整的测试套件信息，包括ID和时间戳。
    """

    id: int = Field(description="套件ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "用户模块回归测试套件",
                "description": "包含所有用户相关功能的测试用例",
                "execution_order": "sequential",
                "parallel_execution": False,
                "continue_on_failure": True,
                "environment": "test",
                "tags": ["回归测试", "用户模块"],
                "version": "1.0.0",
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )


class TestSuiteListResponse(PaginatedResponse[TestSuiteResponse]):
    """测试套件列表响应schema"""


# Test Suite Case Schemas

class TestSuiteCaseBase(BaseModel):
    """测试套件-用例关联基础schema"""

    test_suite_id: int = Field(description="测试套件ID")
    test_case_id: int = Field(description="测试用例ID")
    execution_order: int = Field(default=0, description="执行顺序")
    is_enabled: bool = Field(default=True, description="是否启用")
    case_parameters: dict | None = Field(default=None, description="用例参数覆盖")
    description: str | None = Field(default=None, description="说明")

    model_config = ConfigDict(from_attributes=True)


class TestSuiteCaseCreate(TestSuiteCaseBase):
    """创建测试套件-用例关联schema"""


class TestSuiteCaseResponse(TestSuiteCaseBase, TimestampMixin):
    """测试套件-用例关联响应schema"""

    id: int = Field(description="关联ID")

    model_config = ConfigDict(from_attributes=True)
