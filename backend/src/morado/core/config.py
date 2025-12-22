"""Application configuration management.

This module provides configuration management for the Morado application,
supporting multiple environments (development, testing, production) and
configuration from environment variables and TOML files.
"""

import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    """Application settings with environment-based configuration.

    Settings are loaded from:
    1. Environment variables (highest priority)
    2. TOML configuration files
    3. Default values (lowest priority)

    Attributes:
        app_name: Application name
        version: Application version
        debug: Debug mode flag
        environment: Current environment (development, testing, production)

        # Server settings
        host: Server host address
        port: Server port
        workers: Number of worker processes
        reload: Auto-reload on code changes (development only)

        # Database settings
        database_url: Database connection URL
        database_pool_size: Database connection pool size
        database_echo: Echo SQL queries (for debugging)

        # Redis settings
        redis_url: Redis connection URL
        redis_max_connections: Maximum Redis connections

        # Security settings
        secret_key: Secret key for JWT tokens
        algorithm: JWT algorithm
        access_token_expire_minutes: Access token expiration time

        # CORS settings
        cors_origins: Allowed CORS origins
        cors_allow_credentials: Allow credentials in CORS

        # Logging settings
        log_level: Logging level
        log_format: Log output format
    """

    # Application settings
    app_name: str = "Morado"
    version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "testing", "production"] = "development"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False

    # Database settings
    database_url: str = "postgresql://morado:morado@localhost:5432/morado"
    database_pool_size: int = 10
    database_echo: bool = False

    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS settings
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    cors_allow_credentials: bool = True

    # Logging settings
    log_level: str = "INFO"
    log_format: Literal["console", "json", "structured"] = "console"

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_envs = {"development", "testing", "production"}
        if v not in valid_envs:
            msg = f"Environment must be one of {valid_envs}"
            raise ValueError(msg)
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            msg = f"Log level must be one of {valid_levels}"
            raise ValueError(msg)
        return v_upper

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate secret key in production."""
        # Get environment from values if available
        environment = info.data.get("environment", "development")
        if environment == "production" and v == "your-secret-key-change-this-in-production":
            raise ValueError(
                "Secret key must be changed in production environment. "
                "Set the SECRET_KEY environment variable."
            )
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    def load_from_toml(self, config_path: Path | None = None) -> None:
        """Load additional configuration from TOML file.

        Args:
            config_path: Path to TOML configuration file.
                        If None, searches for config/{environment}.toml
        """
        if config_path is None:
            # Search for environment-specific config file
            config_dir = Path("backend/config")
            config_path = config_dir / f"{self.environment}.toml"

        if not config_path.exists():
            return

        try:
            with open(config_path, "rb") as f:
                config_data = tomllib.load(f)

            # Update settings from TOML file
            # Only update if the value is present in the TOML file
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except Exception as e:
            # Log warning but don't fail
            print(f"Warning: Failed to load config from {config_path}: {e}")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    This function returns a cached instance of Settings to avoid
    reloading configuration on every call. The cache is cleared
    when the process restarts.

    Returns:
        Settings instance with loaded configuration

    Example:
        >>> settings = get_settings()
        >>> print(settings.app_name)
        Morado
        >>> print(settings.database_url)
        postgresql://morado:morado@localhost:5432/morado
    """
    # Get environment from environment variable
    environment = os.getenv("ENVIRONMENT", "development")

    # Create settings instance
    settings = Settings(environment=environment)

    # Load from TOML file if available
    settings.load_from_toml()

    return settings


def reload_settings() -> Settings:
    """Reload settings by clearing the cache.

    This function clears the cached settings and returns a fresh
    instance. Useful for testing or when configuration changes.

    Returns:
        Fresh Settings instance

    Example:
        >>> settings = reload_settings()
        >>> # Settings are reloaded from environment and files
    """
    get_settings.cache_clear()
    return get_settings()
