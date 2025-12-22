#!/usr/bin/python3
"""
Enhanced UUID generation utility module
Supports multiple formats, charsets, prefixes/suffixes, and length constraints
"""

import random
import secrets
import string
import time
import uuid as stdlib_uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator, model_validator


class UUIDConfig(BaseModel):
    """Configuration for UUID generation"""

    format: Literal["alphanumeric", "numeric", "uuid4", "ulid", "custom"] = (
        "alphanumeric"
    )
    prefix: str = ""
    suffix: str = ""
    length: int | None = 38
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    use_timestamp: bool = True
    secure: bool = True

    @field_validator("charset")
    @classmethod
    def validate_charset(cls, v: str) -> str:
        """Validate charset is not empty"""
        if not v:
            raise ValueError("Charset cannot be empty")
        return v

    @field_validator("length")
    @classmethod
    def validate_length(cls, v: int | None) -> int | None:
        """Validate length if specified"""
        if v is not None and v <= 0:
            raise ValueError("Length must be positive")
        return v

    @model_validator(mode="after")
    def validate_numeric_format(self) -> "UUIDConfig":
        """For numeric format, validate prefix and suffix are numeric"""
        if self.format == "numeric":
            if self.prefix and not self.prefix.isdigit():
                raise ValueError("Prefix must be numeric for numeric format")
            if self.suffix and not self.suffix.isdigit():
                raise ValueError("Suffix must be numeric for numeric format")
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UUIDConfig":
        """Create configuration from dictionary"""
        return cls(**data)


class UUIDGenerator:
    """
    Stateless UUID generator with multiple format support
    All methods are static and have no dependencies on logger module
    """

    # Predefined character sets
    NUMERIC = string.digits
    ALPHANUMERIC_LOWER = string.ascii_lowercase + string.digits
    ALPHANUMERIC_UPPER = string.ascii_uppercase + string.digits
    ALPHANUMERIC_MIXED = string.ascii_letters + string.digits
    HEX = string.digits + "ABCDEF"

    @staticmethod
    def generate(config: UUIDConfig | None = None) -> str:
        """
        Generate UUID based on configuration
        :param config: UUID configuration, uses defaults if None
        :return: Generated UUID string
        """
        if config is None:
            config = UUIDConfig()

        # Route to appropriate generator based on format
        if config.format == "uuid4":
            return UUIDGenerator.uuid4()
        elif config.format == "ulid":
            return UUIDGenerator.ulid()
        elif config.format == "numeric":
            return UUIDGenerator.numeric(
                length=config.length or 20,
                prefix=config.prefix,
                suffix=config.suffix,
                use_timestamp=config.use_timestamp,
            )
        elif config.format == "alphanumeric":
            return UUIDGenerator.alphanumeric(
                length=config.length or 38,
                prefix=config.prefix,
                suffix=config.suffix,
                charset=config.charset,
                use_timestamp=config.use_timestamp,
                secure=config.secure,
            )
        else:  # custom
            return UUIDGenerator._generate_custom(
                prefix=config.prefix,
                suffix=config.suffix,
                length=config.length,
                charset=config.charset,
                use_timestamp=config.use_timestamp,
                secure=config.secure,
            )

    @staticmethod
    def uuid4() -> str:
        """
        Generate standard RFC 4122 UUID4
        :return: UUID4 string in standard format (e.g., '550e8400-e29b-41d4-a716-446655440000')
        """
        return str(stdlib_uuid.uuid4())

    @staticmethod
    def ulid() -> str:
        """
        Generate ULID-like sortable ID (timestamp-based)
        Format: 10 characters timestamp (base32) + 16 characters random (base32)
        Ensures monotonic ordering within milliseconds
        :return: ULID-like string (26 characters)
        """
        # ULID uses Crockford's base32 (excludes I, L, O, U to avoid confusion)
        base32_charset = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        # Get timestamp in milliseconds
        timestamp_ms = int(time.time() * 1000)

        # Encode timestamp as 10 characters (48 bits)
        timestamp_part = ""
        for _ in range(10):
            timestamp_part = base32_charset[timestamp_ms % 32] + timestamp_part
            timestamp_ms //= 32

        # Generate 16 random characters (80 bits) for uniqueness
        random_part = "".join(secrets.choice(base32_charset) for _ in range(16))

        return timestamp_part + random_part

    @staticmethod
    def alphanumeric(
        length: int = 38,
        prefix: str = "",
        suffix: str = "",
        charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        use_timestamp: bool = False,
        secure: bool = True,
    ) -> str:
        """
        Generate alphanumeric ID
        :param length: Total length of the ID (default: 38)
        :param prefix: Prefix string
        :param suffix: Suffix string
        :param charset: Character set to use
        :param use_timestamp: Whether to include timestamp
        :param secure: Whether to use cryptographically secure random
        :return: Alphanumeric ID string
        """
        return UUIDGenerator._generate_custom(
            prefix=prefix,
            suffix=suffix,
            length=length,
            charset=charset,
            use_timestamp=use_timestamp,
            secure=secure,
        )

    @staticmethod
    def numeric(
        length: int = 20,
        prefix: str = "",
        suffix: str = "",
        use_timestamp: bool = False,
    ) -> str:
        """
        Generate numeric ID
        :param length: Total length of the ID
        :param prefix: Numeric prefix string
        :param suffix: Numeric suffix string
        :param use_timestamp: Whether to include timestamp
        :return: Numeric ID string
        """
        # Validate prefix and suffix are numeric
        if prefix and not prefix.isdigit():
            raise ValueError("Prefix must be numeric for numeric UUID")
        if suffix and not suffix.isdigit():
            raise ValueError("Suffix must be numeric for numeric UUID")

        return UUIDGenerator._generate_custom(
            prefix=prefix,
            suffix=suffix,
            length=length,
            charset=UUIDGenerator.NUMERIC,
            use_timestamp=use_timestamp,
            secure=True,
        )

    @staticmethod
    def _generate_timestamp_prefix() -> str:
        """
        Generate yyyyMMddHHmmssSSS format timestamp prefix (no separators)
        :return: Timestamp string (17 characters)
        """
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S%f")[:-3]  # Precise to milliseconds

    @staticmethod
    def _generate_random_string(length: int, charset: str, secure: bool = False) -> str:
        """
        Generate random string of specified length
        :param length: String length
        :param charset: Available character set
        :param secure: Whether to use cryptographically secure random source
        :return: Random string
        """
        if secure:
            return "".join(secrets.choice(charset) for _ in range(length))
        else:
            return "".join(random.choices(charset, k=length))

    @staticmethod
    def _generate_custom(
        prefix: str = "",
        suffix: str = "",
        length: int | None = None,
        charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        use_timestamp: bool = False,
        secure: bool = False,
    ) -> str:
        """
        Generate custom format UUID (no separators)
        :param prefix: Prefix string
        :param suffix: Suffix string
        :param length: Total length limit (including prefix/suffix)
        :param charset: Random part character set
        :param use_timestamp: Whether to add timestamp prefix
        :param secure: Whether to use cryptographically secure random source
        :return: Custom format UUID without separators
        """
        # Handle timestamp prefix
        timestamp_part = ""
        if use_timestamp:
            timestamp_part = UUIDGenerator._generate_timestamp_prefix()
            # Check if timestamp exceeds specified length
            if length is not None and len(timestamp_part) > length:
                raise ValueError("Timestamp prefix exceeds specified total length")

        # Calculate part lengths
        prefix_len = len(prefix) + len(timestamp_part)
        suffix_len = len(suffix)
        fixed_len = prefix_len + suffix_len

        # Determine random part length
        if length is not None:
            if fixed_len >= length:
                raise ValueError("Prefix/suffix length exceeds or equals total length")
            rand_len = length - fixed_len
        else:
            rand_len = 8  # Default random part length

        # Generate random part
        random_part = UUIDGenerator._generate_random_string(rand_len, charset, secure)

        # Combine parts (no separators)
        result = prefix + timestamp_part + random_part + suffix
        return result


# Convenience function interfaces
def generate_uuid(config: UUIDConfig | None = None) -> str:
    """Generate UUID based on configuration"""
    return UUIDGenerator.generate(config)


def generate_uuid4() -> str:
    """Generate standard RFC 4122 UUID4"""
    return UUIDGenerator.uuid4()


def generate_ulid() -> str:
    """Generate ULID-like sortable ID"""
    return UUIDGenerator.ulid()


def generate_alphanumeric(
    length: int = 38,
    prefix: str = "",
    suffix: str = "",
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    use_timestamp: bool = False,
    secure: bool = True,
) -> str:
    """Generate alphanumeric ID (default length: 38)"""
    return UUIDGenerator.alphanumeric(
        length=length,
        prefix=prefix,
        suffix=suffix,
        charset=charset,
        use_timestamp=use_timestamp,
        secure=secure,
    )


def generate_numeric(
    length: int = 20, prefix: str = "", suffix: str = "", use_timestamp: bool = False
) -> str:
    """Generate numeric ID"""
    return UUIDGenerator.numeric(
        length=length, prefix=prefix, suffix=suffix, use_timestamp=use_timestamp
    )


# Legacy compatibility functions (deprecated but maintained for backward compatibility)
def generate_custom_uuid(
    prefix: str = "",
    suffix: str = "",
    length: int | None = None,
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    random_part_length: int | None = None,
    use_timestamp: bool = False,
    secure: bool = False,
) -> str:
    """Generate custom format UUID (legacy compatibility)"""
    actual_length = (
        length
        if random_part_length is None
        else (len(prefix) + len(suffix) + random_part_length)
    )
    return UUIDGenerator._generate_custom(
        prefix=prefix,
        suffix=suffix,
        length=actual_length,
        charset=charset,
        use_timestamp=use_timestamp,
        secure=secure,
    )


def generate_numeric_uuid(
    prefix: str = "",
    suffix: str = "",
    length: int | None = None,
    random_part_length: int | None = None,
    use_timestamp: bool = False,
) -> str:
    """Generate numeric UUID (legacy compatibility)"""
    actual_length = (
        length
        if random_part_length is None
        else (len(prefix) + len(suffix) + random_part_length)
    )
    return UUIDGenerator.numeric(
        length=actual_length or 20,
        prefix=prefix,
        suffix=suffix,
        use_timestamp=use_timestamp,
    )


def generate_alphanumeric_uuid(
    prefix: str = "",
    suffix: str = "",
    length: int | None = None,
    mixed_case: bool = True,
    random_part_length: int | None = None,
    use_timestamp: bool = False,
    secure: bool = False,
) -> str:
    """Generate alphanumeric UUID (legacy compatibility, default length: 38)"""
    charset = (
        UUIDGenerator.ALPHANUMERIC_MIXED
        if mixed_case
        else UUIDGenerator.ALPHANUMERIC_UPPER
    )
    actual_length = (
        length
        if random_part_length is None
        else (len(prefix) + len(suffix) + random_part_length)
    )
    return UUIDGenerator.alphanumeric(
        length=actual_length or 38,
        prefix=prefix,
        suffix=suffix,
        charset=charset,
        use_timestamp=use_timestamp,
        secure=secure,
    )


def generate_distributed_uuid(
    node_id: str = "",
    prefix: str = "",
    suffix: str = "",
    length: int | None = None,
    random_part_length: int | None = None,
    secure: bool = True,
) -> str:
    """Generate distributed system UUID (legacy compatibility)"""
    # Process node ID (limit length)
    if node_id:
        node_id = node_id.replace("-", "").upper()[:4].ljust(4, "0")
    else:
        node_id = "NODE"[:4].ljust(4, "0")

    # Build full prefix
    full_prefix = f"{prefix}{node_id}"

    actual_length = (
        length
        if random_part_length is None
        else (len(full_prefix) + len(suffix) + random_part_length)
    )

    return UUIDGenerator._generate_custom(
        prefix=full_prefix,
        suffix=suffix,
        length=actual_length,
        charset=UUIDGenerator.ALPHANUMERIC_UPPER,
        use_timestamp=True,
        secure=secure,
    )


if __name__ == "__main__":
    pass
