"""Configuration models for HTTP client wrapper.

This module defines Pydantic models for configuring the HTTP client.
"""

from pydantic import BaseModel, Field, field_validator


class HttpClientConfig(BaseModel):
    """Configuration for HTTP client.

    This model defines all configurable options for the HTTP client wrapper.
    """

    # Base configuration
    base_url: str | None = Field(
        None,
        description="Base URL for all requests. If provided, all request URLs will be relative to this base.",
    )
    connect_timeout: int = Field(
        10,
        gt=0,
        le=300,
        description="Connection timeout in seconds. Must be between 1 and 300.",
    )
    read_timeout: int = Field(
        30,
        gt=0,
        le=600,
        description="Read timeout in seconds. Must be between 1 and 600.",
    )
    pool_connections: int = Field(
        10,
        gt=0,
        le=100,
        description="Number of connection pools to cache. Must be between 1 and 100.",
    )
    pool_maxsize: int = Field(
        10,
        gt=0,
        le=100,
        description="Maximum number of connections to save in the pool. Must be between 1 and 100.",
    )

    # Retry configuration
    enable_retry: bool = Field(
        True,
        description="Whether to enable automatic retry on failures.",
    )
    max_retries: int = Field(
        3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts. Must be between 0 and 10.",
    )
    retry_strategy: str = Field(
        "exponential",
        description="Retry strategy: 'fixed', 'exponential', or 'linear'.",
    )
    initial_delay: float = Field(
        1.0,
        gt=0,
        le=60,
        description="Initial delay between retries in seconds. Must be between 0 and 60.",
    )
    max_delay: float = Field(
        60.0,
        gt=0,
        le=300,
        description="Maximum delay between retries in seconds. Must be between 0 and 300.",
    )

    # Logging configuration
    enable_logging: bool = Field(
        True,
        description="Whether to enable request/response logging.",
    )
    log_request_body: bool = Field(
        True,
        description="Whether to log request body content.",
    )
    log_response_body: bool = Field(
        True,
        description="Whether to log response body content.",
    )
    max_log_body_size: int = Field(
        1024,
        gt=0,
        le=10240,
        description="Maximum size of request/response body to log in bytes. Must be between 1 and 10240.",
    )

    # Tracing configuration
    enable_tracing: bool = Field(
        True,
        description="Whether to enable request tracing with execution context.",
    )
    trace_header_name: str = Field(
        "X-Request-ID",
        description="HTTP header name for request ID tracing.",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str | None) -> str | None:
        """Validate that base_url starts with http:// or https://."""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return v

    @field_validator("retry_strategy")
    @classmethod
    def validate_retry_strategy(cls, v: str) -> str:
        """Validate that retry_strategy is one of the allowed values."""
        allowed = {"fixed", "exponential", "linear"}
        if v not in allowed:
            msg = f"retry_strategy must be one of {allowed}"
            raise ValueError(msg)
        return v

    @field_validator("trace_header_name")
    @classmethod
    def validate_trace_header_name(cls, v: str) -> str:
        """Validate that trace_header_name is not empty."""
        if not v or not v.strip():
            raise ValueError("trace_header_name cannot be empty")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "base_url": "https://api.example.com",
                    "connect_timeout": 10,
                    "read_timeout": 30,
                    "enable_retry": True,
                    "max_retries": 3,
                    "retry_strategy": "exponential",
                }
            ]
        }
    }
