"""Common Pydantic schemas.

This module provides common schemas used across the API, including
pagination, responses, and error handling.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    """分页参数

    Attributes:
        page: 页码（从1开始）
        page_size: 每页数量
        sort_by: 排序字段
        sort_order: 排序方向（asc/desc）

    Example:
        >>> params = PaginationParams(page=1, page_size=20)
    """

    page: int = Field(default=1, ge=1, description="页码（从1开始）")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    sort_by: str | None = Field(default=None, description="排序字段")
    sort_order: str = Field(
        default="desc", pattern="^(asc|desc)$", description="排序方向"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "page_size": 20,
                "sort_by": "created_at",
                "sort_order": "desc",
            }
        }
    )


class PaginatedResponse[T](BaseModel):
    """分页响应

    Attributes:
        items: 数据列表
        total: 总数
        page: 当前页码
        page_size: 每页数量
        total_pages: 总页数

    Example:
        >>> response = PaginatedResponse(
        ...     items=[item1, item2],
        ...     total=100,
        ...     page=1,
        ...     page_size=20
        ... )
    """

    items: list[T] = Field(description="数据列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """消息响应

    用于返回简单的成功消息。

    Attributes:
        message: 消息内容
        data: 可选的附加数据

    Example:
        >>> response = MessageResponse(message="操作成功")
    """

    message: str = Field(description="消息内容")
    data: dict[str, Any] | None = Field(default=None, description="附加数据")

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "操作成功", "data": {"id": 1}}}
    )


class ErrorResponse(BaseModel):
    """错误响应

    统一的错误响应格式。

    Attributes:
        error_code: 错误代码
        message: 错误消息
        details: 错误详情
        timestamp: 时间戳
        request_id: 请求ID

    Example:
        >>> error = ErrorResponse(
        ...     error_code="VALIDATION_ERROR",
        ...     message="数据验证失败",
        ...     details={"field": "name", "error": "不能为空"}
        ... )
    """

    error_code: str = Field(description="错误代码")
    message: str = Field(description="错误消息")
    details: dict[str, Any] | None = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    request_id: str | None = Field(default=None, description="请求ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "数据验证失败",
                "details": {"field": "name", "error": "不能为空"},
                "timestamp": "2024-01-01T00:00:00Z",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    )


class TimestampMixin(BaseModel):
    """时间戳混入

    为schema添加created_at和updated_at字段。
    """

    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class UUIDMixin(BaseModel):
    """UUID混入

    为schema添加uuid字段。
    """

    uuid: str = Field(description="唯一标识符")

    model_config = ConfigDict(from_attributes=True)
