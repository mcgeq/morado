"""Base models and mixins for all database models.

This module provides base classes and common mixins that are used
across all models in the application.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    All database models should inherit from this class.
    """


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp fields.

    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class UUIDMixin:
    """Mixin that adds a UUID string identifier field.

    Attributes:
        uuid: Unique identifier string (generated using morado.common.utils.uuid)
    """

    uuid: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True, comment="唯一标识符"
    )
