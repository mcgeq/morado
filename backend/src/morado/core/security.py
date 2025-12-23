"""Security utilities for authentication and authorization.

This module provides password hashing, JWT token generation and verification,
and other security-related utilities for the Morado application.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from pydantic import BaseModel

from morado.core.config import get_settings

# Try to import password hashing and JWT libraries
try:
    from passlib.context import CryptContext  # type: ignore[import-untyped]

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    pwd_context = None

try:
    from jose import JWTError, jwt  # type: ignore[import-untyped]

    JOSE_AVAILABLE = True
except ImportError:
    JOSE_AVAILABLE = False
    JWTError = Exception
    jwt = None


class SecurityConfig(BaseModel):
    """Security configuration.

    Attributes:
        secret_key: Secret key for JWT tokens
        algorithm: JWT algorithm (default: HS256)
        access_token_expire_minutes: Access token expiration time
    """

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


class TokenData(BaseModel):
    """JWT token payload data.

    Attributes:
        user_id: User ID
        username: Username
        email: User email
        is_admin: Admin flag
        exp: Expiration timestamp
    """

    user_id: int
    username: str
    email: str | None = None
    is_admin: bool = False
    exp: datetime | None = None


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Example:
        >>> hashed = get_password_hash("my_password")
        >>> print(hashed)
        $2b$12$...
    """
    if not PASSLIB_AVAILABLE or pwd_context is None:
        raise ImportError(
            "passlib is required for password hashing. Install with: pip install passlib[bcrypt]"
        )
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = get_password_hash("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    if not PASSLIB_AVAILABLE or pwd_context is None:
        raise ImportError(
            "passlib is required for password verification. Install with: pip install passlib[bcrypt]"
        )
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token (should include user_id, username, etc.)
        expires_delta: Token expiration time. If None, uses default from settings.

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token(
        ...     data={"user_id": 1, "username": "john", "is_admin": False}
        ... )
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    if not JOSE_AVAILABLE or jwt is None:
        raise ImportError(
            "python-jose is required for JWT tokens. Install with: pip install python-jose[cryptography]"
        )

    settings = get_settings()

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta

    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_access_token(token: str) -> TokenData | None:
    """Verify and decode a JWT access token.

    Args:
        token: JWT token string to verify

    Returns:
        TokenData if token is valid, None otherwise

    Example:
        >>> token = create_access_token(
        ...     data={"user_id": 1, "username": "john", "is_admin": False}
        ... )
        >>> token_data = verify_access_token(token)
        >>> print(token_data.user_id)
        1
        >>> print(token_data.username)
        john
    """
    if not JOSE_AVAILABLE or jwt is None:
        raise ImportError(
            "python-jose is required for JWT tokens. Install with: pip install python-jose[cryptography]"
        )

    settings = get_settings()

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        user_id: int = payload.get("user_id")
        username: str = payload.get("username")

        if user_id is None or username is None:
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            email=payload.get("email"),
            is_admin=payload.get("is_admin", False),
            exp=datetime.fromtimestamp(payload.get("exp")),
        )
    except JWTError:
        return None


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT refresh token.

    Refresh tokens have a longer expiration time than access tokens
    and are used to obtain new access tokens without re-authentication.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time. If None, uses 7 days.

    Returns:
        Encoded JWT refresh token string

    Example:
        >>> refresh_token = create_refresh_token(
        ...     data={"user_id": 1, "username": "john"}
        ... )
    """
    if not JOSE_AVAILABLE or jwt is None:
        raise ImportError(
            "python-jose is required for JWT tokens. Install with: pip install python-jose[cryptography]"
        )

    settings = get_settings()

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        # Default refresh token expiration: 7 days
        expire = datetime.now(UTC) + timedelta(days=7)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_refresh_token(token: str) -> TokenData | None:
    """Verify and decode a JWT refresh token.

    Args:
        token: JWT refresh token string to verify

    Returns:
        TokenData if token is valid and is a refresh token, None otherwise

    Example:
        >>> refresh_token = create_refresh_token(
        ...     data={"user_id": 1, "username": "john"}
        ... )
        >>> token_data = verify_refresh_token(refresh_token)
        >>> if token_data:
        ...     # Create new access token
        ...     new_access_token = create_access_token(
        ...         data={"user_id": token_data.user_id, "username": token_data.username}
        ...     )
    """
    if not JOSE_AVAILABLE or jwt is None:
        raise ImportError(
            "python-jose is required for JWT tokens. Install with: pip install python-jose[cryptography]"
        )

    settings = get_settings()

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        # Verify this is a refresh token
        if payload.get("type") != "refresh":
            return None

        user_id: int = payload.get("user_id")
        username: str = payload.get("username")

        if user_id is None or username is None:
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            email=payload.get("email"),
            is_admin=payload.get("is_admin", False),
            exp=datetime.fromtimestamp(payload.get("exp")),
        )
    except JWTError:
        return None
