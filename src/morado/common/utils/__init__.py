"""Morado Common Utilities - Public API

This module provides utility functions for the Morado application,
including UUID generation in various formats.

UUID Generation:
    from morado.common.utils import UUIDGenerator, uuid4, ulid
    
    # Generate standard UUID4
    id1 = uuid4()
    
    # Generate ULID-like sortable ID
    id2 = ulid()
    
    # Generate custom alphanumeric ID
    id3 = alphanumeric(length=32, prefix="USER")
    
    # Generate numeric ID
    id4 = numeric(length=20)

Configuration:
    from morado.common.utils import UUIDGenerator, UUIDConfig
    
    config = UUIDConfig(
        format="alphanumeric",
        length=24,
        prefix="REQ",
        secure=True
    )
    
    request_id = UUIDGenerator.generate(config)
"""

from morado.common.utils.uuid import (
    UUIDGenerator,
    UUIDConfig,
)


# Convenience functions for common UUID formats
def uuid4() -> str:
    """Generate a standard RFC 4122 UUID4.
    
    Returns:
        UUID4 string in standard format (e.g., "550e8400-e29b-41d4-a716-446655440000")
        
    Example:
        >>> id = uuid4()
        >>> len(id)
        36
    """
    return UUIDGenerator.uuid4()


def ulid() -> str:
    """Generate a ULID-like sortable timestamp-based ID.
    
    ULIDs are lexicographically sortable and encode timestamp information,
    making them ideal for distributed systems and time-series data.
    
    Returns:
        ULID string (26 characters, base32 encoded)
        
    Example:
        >>> id1 = ulid()
        >>> import time
        >>> time.sleep(0.001)
        >>> id2 = ulid()
        >>> id1 < id2  # Sortable by time
        True
    """
    return UUIDGenerator.ulid()


def alphanumeric(
    length: int = 24,
    prefix: str = "",
    suffix: str = "",
    charset: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    use_timestamp: bool = False,
    secure: bool = True
) -> str:
    """Generate an alphanumeric ID.
    
    Args:
        length: Total length of the ID (including prefix and suffix)
        prefix: Optional prefix to prepend
        suffix: Optional suffix to append
        charset: Character set to use (default: uppercase alphanumeric)
        use_timestamp: Whether to include timestamp component
        secure: If True, use cryptographically secure random source
        
    Returns:
        Alphanumeric ID string
        
    Example:
        >>> id = alphanumeric(length=24, prefix="REQ")
        >>> id.startswith("REQ")
        True
        >>> len(id)
        24
    """
    return UUIDGenerator.alphanumeric(
        length=length,
        prefix=prefix,
        suffix=suffix,
        charset=charset,
        use_timestamp=use_timestamp,
        secure=secure
    )


def numeric(
    length: int = 20,
    prefix: str = "",
    suffix: str = "",
    use_timestamp: bool = False
) -> str:
    """Generate a numeric-only ID.
    
    Args:
        length: Total length of the ID (including prefix and suffix)
        prefix: Optional numeric prefix to prepend
        suffix: Optional numeric suffix to append
        use_timestamp: Whether to include timestamp component
        
    Returns:
        Numeric ID string
        
    Example:
        >>> id = numeric(length=20, prefix="123")
        >>> id.startswith("123")
        True
        >>> len(id)
        20
    """
    return UUIDGenerator.numeric(
        length=length,
        prefix=prefix,
        suffix=suffix,
        use_timestamp=use_timestamp
    )


# Public API
__all__ = [
    # Core UUID generator
    'UUIDGenerator',
    'UUIDConfig',
    
    # Convenience functions
    'uuid4',
    'ulid',
    'alphanumeric',
    'numeric',
]
