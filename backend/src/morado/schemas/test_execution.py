"""Test Execution Pydantic schemas.

This module provides schemas for test execution API request/response validation.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from morado.schemas.common import PaginatedResponse, TimestampMixin, UUIDMixin


class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TestExecutionBase(BaseModel):
    """测试执行基础schema

    包含测试执行的基本字段，用于创建和更新操作。
    """

    test_case_id: int | None = Field(default=None, description="测试用例ID")
    test_suite_id: int | None = Field(default=None, description="测试套件ID")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, description="执行状态")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")
    duration: float | None = Field(default=None, ge=0, description="执行时长（秒）")
    environment: str = Field(default="test", max_length=20, description="执行环境")
    executor: str | None = Field(default=None, max_length=100, description="执行者")
    execution_parameters: dict | None = Field(default=None, description="执行参数")
    total_count: int = Field(default=0, ge=0, description="总数")
    passed_count: int = Field(default=0, ge=0, description="通过数")
    failed_count: int = Field(default=0, ge=0, description="失败数")
    error_count: int = Field(default=0, ge=0, description="错误数")
    skipped_count: int = Field(default=0, ge=0, description="跳过数")
    error_message: str | None = Field(default=None, description="错误信息")
    stack_trace: str | None = Field(default=None, description="堆栈跟踪")
    logs: str | None = Field(default=None, description="执行日志")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "test_case_id": 1,
                "status": "running",
                "environment": "test",
                "executor": "jenkins",
                "total_count": 10,
                "passed_count": 8,
                "failed_count": 2,
                "error_count": 0,
                "skipped_count": 0
            }
        }
    )


class TestExecutionCreate(TestExecutionBase):
    """创建测试执行schema

    用于创建新的测试执行记录。
    """

    created_by: int | None = Field(default=None, description="创建者ID")


class TestExecutionUpdate(BaseModel):
    """更新测试执行schema

    所有字段都是可选的，只更新提供的字段。
    """

    status: ExecutionStatus | None = Field(default=None, description="执行状态")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")
    duration: float | None = Field(default=None, ge=0, description="执行时长（秒）")
    environment: str | None = Field(default=None, max_length=20, description="执行环境")
    executor: str | None = Field(default=None, max_length=100, description="执行者")
    execution_parameters: dict | None = Field(default=None, description="执行参数")
    total_count: int | None = Field(default=None, ge=0, description="总数")
    passed_count: int | None = Field(default=None, ge=0, description="通过数")
    failed_count: int | None = Field(default=None, ge=0, description="失败数")
    error_count: int | None = Field(default=None, ge=0, description="错误数")
    skipped_count: int | None = Field(default=None, ge=0, description="跳过数")
    error_message: str | None = Field(default=None, description="错误信息")
    stack_trace: str | None = Field(default=None, description="堆栈跟踪")
    logs: str | None = Field(default=None, description="执行日志")

    model_config = ConfigDict(from_attributes=True)


class TestExecutionResponse(TestExecutionBase, TimestampMixin, UUIDMixin):
    """测试执行响应schema

    包含完整的测试执行信息，包括ID和时间戳。
    """

    id: int = Field(description="执行ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "test_case_id": 1,
                "status": "passed",
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T00:05:00Z",
                "duration": 300.5,
                "environment": "test",
                "executor": "jenkins",
                "total_count": 10,
                "passed_count": 10,
                "failed_count": 0,
                "error_count": 0,
                "skipped_count": 0,
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:05:00Z"
            }
        }
    )


class TestExecutionListResponse(PaginatedResponse[TestExecutionResponse]):
    """测试执行列表响应schema"""


# Execution Result Schemas

class ExecutionResultBase(BaseModel):
    """执行结果基础schema"""

    execution_id: int = Field(description="执行记录ID")
    script_id: int | None = Field(default=None, description="脚本ID")
    component_id: int | None = Field(default=None, description="组件ID")
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING, description="执行状态")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")
    duration: float | None = Field(default=None, ge=0, description="执行时长（秒）")
    request_data: dict | None = Field(default=None, description="请求数据")
    response_data: dict | None = Field(default=None, description="响应数据")
    assertions: list | None = Field(default=None, description="断言结果")
    error_message: str | None = Field(default=None, description="错误信息")
    stack_trace: str | None = Field(default=None, description="堆栈跟踪")
    logs: str | None = Field(default=None, description="日志")
    screenshots: list[str] | None = Field(default=None, description="截图")

    model_config = ConfigDict(from_attributes=True)


class ExecutionResultCreate(ExecutionResultBase):
    """创建执行结果schema"""


class ExecutionResultResponse(ExecutionResultBase, TimestampMixin):
    """执行结果响应schema"""

    id: int = Field(description="结果ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "execution_id": 1,
                "script_id": 1,
                "status": "passed",
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-01T00:00:30Z",
                "duration": 30.5,
                "request_data": {"url": "https://api.example.com", "method": "GET"},
                "response_data": {"status": 200, "body": {"success": True}},
                "assertions": [{"type": "status_code", "expected": 200, "actual": 200, "passed": True}],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:30Z"
            }
        }
    )
