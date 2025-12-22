"""CORS middleware configuration for the Morado application.

This module provides CORS (Cross-Origin Resource Sharing) configuration
for the Litestar application, allowing controlled access from frontend
applications running on different origins.
"""

from litestar.config.cors import CORSConfig

from morado.core.config import Settings


def create_cors_config(settings: Settings) -> CORSConfig:
    """Create CORS configuration from application settings.

    This function creates a CORSConfig instance based on the application
    settings, enabling cross-origin requests from specified origins.

    Args:
        settings: Application settings containing CORS configuration.

    Returns:
        CORSConfig instance configured with allowed origins and credentials.

    Example:
        >>> from morado.core.config import get_settings
        >>> settings = get_settings()
        >>> cors_config = create_cors_config(settings)
        >>> print(cors_config.allow_origins)
        ['http://localhost:3000']

    Note:
        In production, ensure that only trusted origins are included in
        the cors_origins list to prevent security vulnerabilities.
    """
    return CORSConfig(
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )
