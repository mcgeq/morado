"""Morado Core - Application Configuration and Infrastructure

This module provides core application configuration, database setup,
security settings, and dependency injection for the Morado backend.

Configuration:
    from morado.core import get_settings, Settings

    settings = get_settings()
    print(f"App name: {settings.app_name}")
    print(f"Debug mode: {settings.debug}")

Database:
    from morado.core import get_db_session, init_database

    # Initialize database
    init_database()

    # Get database session
    async with get_db_session() as session:
        # Use session for database operations
        pass

Dependencies:
    from morado.core import get_current_user
    from litestar import get

    @get("/profile")
    async def get_profile(user: User = Depends(get_current_user)) -> dict:
        return {"user_id": user.id, "username": user.username}
"""

from morado.core.config import Settings, get_settings
from morado.core.database import (
    DatabaseManager,
    close_database,
    get_db_session,
    init_database,
)
from morado.core.dependencies import (
    get_current_user,
    get_db,
    require_admin,
)
from morado.core.security import (
    SecurityConfig,
    create_access_token,
    get_password_hash,
    verify_access_token,
    verify_password,
)

__all__ = [
    "DatabaseManager",
    # Security
    "SecurityConfig",
    # Configuration
    "Settings",
    "close_database",
    "create_access_token",
    # Dependencies
    "get_current_user",
    "get_db",
    # Database
    "get_db_session",
    "get_password_hash",
    "get_settings",
    "init_database",
    "require_admin",
    "verify_access_token",
    "verify_password",
]
