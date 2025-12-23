"""API Component Pydantic schemas.

This module provides schemas for Layer 1 (API Definition Components):
- Header: Reusable HTTP header components
- Body: Reusable request/response body templates
- ApiDefinition: Complete API interface definitions
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from morado.schemas.common import PaginatedResponse, TimestampMixin, UUIDMixin


class HeaderScope(str, Enum):
    """Header作用域"""

    GLOBAL = "global"
    PROJECT = "project"
    PRIVATE = "private"


class BodyType(str, Enum):
    """Body类型"""

    REQUEST = "request"
    RESPONSE = "response"
    BOTH = "both"


class HttpMethod(str, Enum):
    """HTTP请求方法"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# Header Schemas


class HeaderBase(BaseModel):
    """Header基础schema"""

    name: str = Field(min_length=1, max_length=200, description="Header名称")
    description: str | None = Field(default=None, description="Header描述")
    headers: dict = Field(description="Header键值对")
    scope: HeaderScope = Field(default=HeaderScope.PRIVATE, description="作用域")
    project_id: int | None = Field(default=None, description="项目ID")
    is_active: bool = Field(default=True, description="是否激活")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "认证Header",
                "description": "包含Bearer Token的认证Header",
                "headers": {
                    "Authorization": "Bearer ${token}",
                    "X-API-Key": "${api_key}",
                },
                "scope": "global",
                "is_active": True,
                "version": "1.0.0",
                "tags": ["认证", "通用"],
            }
        },
    )


class HeaderCreate(HeaderBase):
    """创建Header schema"""

    created_by: int | None = Field(default=None, description="创建者ID")


class HeaderUpdate(BaseModel):
    """更新Header schema"""

    name: str | None = Field(
        default=None, min_length=1, max_length=200, description="Header名称"
    )
    description: str | None = Field(default=None, description="Header描述")
    headers: dict | None = Field(default=None, description="Header键值对")
    scope: HeaderScope | None = Field(default=None, description="作用域")
    project_id: int | None = Field(default=None, description="项目ID")
    is_active: bool | None = Field(default=None, description="是否激活")
    version: str | None = Field(default=None, max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(from_attributes=True)


class HeaderResponse(HeaderBase, TimestampMixin, UUIDMixin):
    """Header响应schema"""

    id: int = Field(description="Header ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "认证Header",
                "description": "包含Bearer Token的认证Header",
                "headers": {
                    "Authorization": "Bearer ${token}",
                    "X-API-Key": "${api_key}",
                },
                "scope": "global",
                "is_active": True,
                "version": "1.0.0",
                "tags": ["认证", "通用"],
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )


class HeaderListResponse(PaginatedResponse[HeaderResponse]):
    """Header列表响应schema"""


# Body Schemas


class BodyBase(BaseModel):
    """Body基础schema"""

    name: str = Field(min_length=1, max_length=200, description="Body名称")
    description: str | None = Field(default=None, description="Body描述")
    body_type: BodyType = Field(default=BodyType.REQUEST, description="Body类型")
    content_type: str = Field(
        default="application/json", max_length=100, description="内容类型"
    )
    body_schema: dict | None = Field(default=None, description="Body的JSON Schema定义")
    example_data: dict | None = Field(default=None, description="示例数据")
    scope: HeaderScope = Field(default=HeaderScope.PRIVATE, description="作用域")
    project_id: int | None = Field(default=None, description="项目ID")
    is_active: bool = Field(default=True, description="是否激活")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "用户信息Body",
                "description": "用户基本信息的请求/响应体",
                "body_type": "both",
                "content_type": "application/json",
                "body_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "email": {"type": "string", "format": "email"},
                    },
                    "required": ["name", "email"],
                },
                "example_data": {
                    "name": "张三",
                    "age": 25,
                    "email": "zhangsan@example.com",
                },
                "scope": "global",
                "is_active": True,
                "version": "1.0.0",
                "tags": ["用户", "通用"],
            }
        },
    )


class BodyCreate(BodyBase):
    """创建Body schema"""

    created_by: int | None = Field(default=None, description="创建者ID")


class BodyUpdate(BaseModel):
    """更新Body schema"""

    name: str | None = Field(
        default=None, min_length=1, max_length=200, description="Body名称"
    )
    description: str | None = Field(default=None, description="Body描述")
    body_type: BodyType | None = Field(default=None, description="Body类型")
    content_type: str | None = Field(
        default=None, max_length=100, description="内容类型"
    )
    body_schema: dict | None = Field(default=None, description="Body的JSON Schema定义")
    example_data: dict | None = Field(default=None, description="示例数据")
    scope: HeaderScope | None = Field(default=None, description="作用域")
    project_id: int | None = Field(default=None, description="项目ID")
    is_active: bool | None = Field(default=None, description="是否激活")
    version: str | None = Field(default=None, max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(from_attributes=True)


class BodyResponse(BodyBase, TimestampMixin, UUIDMixin):
    """Body响应schema"""

    id: int = Field(description="Body ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "用户信息Body",
                "description": "用户基本信息的请求/响应体",
                "body_type": "both",
                "content_type": "application/json",
                "body_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "email": {"type": "string", "format": "email"},
                    },
                    "required": ["name", "email"],
                },
                "example_data": {
                    "name": "张三",
                    "age": 25,
                    "email": "zhangsan@example.com",
                },
                "scope": "global",
                "is_active": True,
                "version": "1.0.0",
                "tags": ["用户", "通用"],
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )


class BodyListResponse(PaginatedResponse[BodyResponse]):
    """Body列表响应schema"""


# ApiDefinition Schemas


class ApiDefinitionBase(BaseModel):
    """API定义基础schema"""

    name: str = Field(min_length=1, max_length=200, description="API名称")
    description: str | None = Field(default=None, description="API描述")
    method: HttpMethod = Field(description="HTTP方法")
    path: str = Field(min_length=1, max_length=500, description="API路径")
    base_url: str | None = Field(default=None, max_length=500, description="基础URL")
    header_id: int | None = Field(default=None, description="引用的Header组件ID")
    request_body_id: int | None = Field(
        default=None, description="引用的请求Body组件ID"
    )
    response_body_id: int | None = Field(
        default=None, description="引用的响应Body组件ID"
    )
    inline_request_body: dict | None = Field(default=None, description="内联请求体")
    inline_response_body: dict | None = Field(default=None, description="内联响应体")
    query_parameters: dict | None = Field(default=None, description="查询参数定义")
    path_parameters: dict | None = Field(default=None, description="路径参数定义")
    timeout: int = Field(default=30, ge=1, description="超时时间（秒）")
    is_active: bool = Field(default=True, description="是否激活")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "获取用户信息",
                "description": "根据用户ID获取用户详细信息",
                "method": "GET",
                "path": "/api/users/{id}",
                "base_url": "https://api.example.com",
                "header_id": 1,
                "response_body_id": 2,
                "path_parameters": {"id": {"type": "integer", "description": "用户ID"}},
                "timeout": 30,
                "is_active": True,
                "version": "1.0.0",
                "tags": ["用户", "查询"],
            }
        },
    )


class ApiDefinitionCreate(ApiDefinitionBase):
    """创建API定义schema"""

    created_by: int | None = Field(default=None, description="创建者ID")


class ApiDefinitionUpdate(BaseModel):
    """更新API定义schema"""

    name: str | None = Field(
        default=None, min_length=1, max_length=200, description="API名称"
    )
    description: str | None = Field(default=None, description="API描述")
    method: HttpMethod | None = Field(default=None, description="HTTP方法")
    path: str | None = Field(
        default=None, min_length=1, max_length=500, description="API路径"
    )
    base_url: str | None = Field(default=None, max_length=500, description="基础URL")
    header_id: int | None = Field(default=None, description="引用的Header组件ID")
    request_body_id: int | None = Field(
        default=None, description="引用的请求Body组件ID"
    )
    response_body_id: int | None = Field(
        default=None, description="引用的响应Body组件ID"
    )
    inline_request_body: dict | None = Field(default=None, description="内联请求体")
    inline_response_body: dict | None = Field(default=None, description="内联响应体")
    query_parameters: dict | None = Field(default=None, description="查询参数定义")
    path_parameters: dict | None = Field(default=None, description="路径参数定义")
    timeout: int | None = Field(default=None, ge=1, description="超时时间（秒）")
    is_active: bool | None = Field(default=None, description="是否激活")
    version: str | None = Field(default=None, max_length=20, description="版本号")
    tags: list[str] | None = Field(default=None, description="标签")

    model_config = ConfigDict(from_attributes=True)


class ApiDefinitionResponse(ApiDefinitionBase, TimestampMixin, UUIDMixin):
    """API定义响应schema"""

    id: int = Field(description="API定义ID")
    created_by: int | None = Field(default=None, description="创建者ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                "name": "获取用户信息",
                "description": "根据用户ID获取用户详细信息",
                "method": "GET",
                "path": "/api/users/{id}",
                "base_url": "https://api.example.com",
                "header_id": 1,
                "response_body_id": 2,
                "path_parameters": {"id": {"type": "integer", "description": "用户ID"}},
                "timeout": 30,
                "is_active": True,
                "version": "1.0.0",
                "tags": ["用户", "查询"],
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    )


class ApiDefinitionListResponse(PaginatedResponse[ApiDefinitionResponse]):
    """API定义列表响应schema"""
