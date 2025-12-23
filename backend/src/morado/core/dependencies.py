"""Dependency injection utilities for Litestar.

This module provides dependency injection functions for common operations
like getting the current user, database sessions, and authorization checks.
"""

from typing import Annotated

from litestar import Request
from litestar.di import Provide
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.orm import Session

from morado.core.database import get_db
from morado.core.security import TokenData, verify_access_token


async def get_current_user(request: Request) -> TokenData:
    """Get the current authenticated user from the request.

    This dependency extracts the JWT token from the Authorization header,
    verifies it, and returns the token data containing user information.

    Args:
        request: Litestar Request object

    Returns:
        TokenData containing user information

    Raises:
        NotAuthorizedException: If token is missing or invalid

    Example:
        >>> from litestar import get
        >>> from litestar.di import Provide
        >>>
        >>> @get("/profile", dependencies={"user": Provide(get_current_user)})
        >>> async def get_profile(user: TokenData) -> dict:
        ...     return {"user_id": user.user_id, "username": user.username}
    """
    # Get Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise NotAuthorizedException("Missing authorization header")

    # Extract token from "Bearer <token>" format
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise NotAuthorizedException("Invalid authorization header format")

    token = parts[1]

    # Verify token
    token_data = verify_access_token(token)

    if token_data is None:
        raise NotAuthorizedException("Invalid or expired token")

    return token_data


async def get_optional_user(request: Request) -> TokenData | None:
    """Get the current user if authenticated, None otherwise.

    This is similar to get_current_user but doesn't raise an exception
    if the user is not authenticated. Useful for endpoints that work
    differently for authenticated vs anonymous users.

    Args:
        request: Litestar Request object

    Returns:
        TokenData if authenticated, None otherwise

    Example:
        >>> from litestar import get
        >>> from litestar.di import Provide
        >>>
        >>> @get("/content", dependencies={"user": Provide(get_optional_user)})
        >>> async def get_content(user: Optional[TokenData]) -> dict:
        ...     if user:
        ...         return {"content": "Premium content", "user": user.username}
        ...     return {"content": "Public content"}
    """
    try:
        return await get_current_user(request)
    except NotAuthorizedException:
        return None


async def require_admin(request: Request) -> TokenData:
    """Require that the current user is an administrator.

    This dependency verifies that the user is authenticated and has
    admin privileges. Raises an exception if not.

    Args:
        request: Litestar Request object

    Returns:
        TokenData containing admin user information

    Raises:
        NotAuthorizedException: If user is not authenticated or not an admin

    Example:
        >>> from litestar import delete
        >>> from litestar.di import Provide
        >>>
        >>> @delete("/users/{user_id:int}", dependencies={"admin": Provide(require_admin)})
        >>> async def delete_user(user_id: int, admin: TokenData) -> dict:
        ...     # Only admins can delete users
        ...     return {"message": f"User {user_id} deleted by {admin.username}"}
    """
    user = await get_current_user(request)

    if not user.is_admin:
        raise NotAuthorizedException("Admin privileges required")

    return user


def get_db_dependency() -> Provide:
    """Get database session dependency provider.

    Returns:
        Provide instance for database session dependency

    Example:
        >>> from litestar import Litestar
        >>>
        >>> app = Litestar(
        ...     route_handlers=[...],
        ...     dependencies={"db": get_db_dependency()}
        ... )
    """
    return Provide(get_db)


def get_user_dependency() -> Provide:
    """Get current user dependency provider.

    Returns:
        Provide instance for current user dependency

    Example:
        >>> from litestar import Litestar
        >>>
        >>> app = Litestar(
        ...     route_handlers=[...],
        ...     dependencies={"current_user": get_user_dependency()}
        ... )
    """
    return Provide(get_current_user)


def get_optional_user_dependency() -> Provide:
    """Get optional user dependency provider.

    Returns:
        Provide instance for optional user dependency

    Example:
        >>> from litestar import Litestar
        >>>
        >>> app = Litestar(
        ...     route_handlers=[...],
        ...     dependencies={"user": get_optional_user_dependency()}
        ... )
    """
    return Provide(get_optional_user)


def get_admin_dependency() -> Provide:
    """Get admin user dependency provider.

    Returns:
        Provide instance for admin user dependency

    Example:
        >>> from litestar import Litestar, Router
        >>>
        >>> admin_router = Router(
        ...     path="/admin",
        ...     route_handlers=[...],
        ...     dependencies={"admin": get_admin_dependency()}
        ... )
    """
    return Provide(require_admin)


# Type aliases for cleaner type hints
CurrentUser = Annotated[TokenData, Provide(get_current_user)]
OptionalUser = Annotated[TokenData | None, Provide(get_optional_user)]
AdminUser = Annotated[TokenData, Provide(require_admin)]
DatabaseSession = Annotated[Session, Provide(get_db)]
