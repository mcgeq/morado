"""Morado Logger System - Public API

This module provides a clean, configurable logging system with:
- Configuration-driven architecture (YAML/TOML files)
- Request-scoped context management
- Multiple output formats (console, JSON, structured)
- Extensible processors and renderers
- Async support

Basic Usage:
    from morado.common.logger import get_logger, request_scope

    logger = get_logger(__name__)

    with request_scope(user_id=42):
        logger.info("Processing request")

Configuration:
    from morado.common.logger import configure_logger, LoggerConfig

    config = LoggerConfig(level="DEBUG", format="json")
    configure_logger(config)
"""

# Core logger functionality
# Note: These will be implemented in task 4
# For now, we provide placeholder imports that will work once task 4 is complete
try:
    from morado.common.logger.logger import (
        LoggerSystem,
        configure_logger,
        get_logger,
    )
except ImportError:
    # Fallback for when logger.py is not yet implemented
    import structlog

    def get_logger(name=None):
        """Get a logger instance (fallback implementation)"""
        return structlog.get_logger(name)

    def configure_logger(config=None, config_file=None, **overrides):
        """Configure logger (fallback implementation)"""

    class LoggerSystem:
        """Logger system placeholder"""

# Context management
# Configuration
from morado.common.logger.config import (
    ConfigurationManager,
    LoggerConfig,
    ProcessorConfig,
)

# Import only what exists in our new context module
from morado.common.logger.context import (
    clear_context,
    get_context_data,
    get_log_context,
    get_request_id,
    set_context_data,
    set_request_id,
)

# Keep the old context imports for backward compatibility
try:
    from morado.common.logger.context import (
        ContextManager,
        RequestContext,
        async_request_scope,
        request_scope,
    )
except ImportError:
    # These may not exist yet, provide placeholders
    ContextManager = None  # type: ignore
    RequestContext = None  # type: ignore

    def request_scope(*args, **kwargs):  # type: ignore
        """Placeholder for request_scope"""
        from contextlib import contextmanager

        @contextmanager
        def _scope():
            yield {}

        return _scope()

    def async_request_scope(*args, **kwargs):  # type: ignore
        """Placeholder for async_request_scope"""
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _scope():
            yield {}

        return _scope()

# Decorators
try:
    from morado.common.logger.decorators import (
        async_with_request_context,
        log_execution,
        with_request_context,
    )
except ImportError:
    # Decorators may not be fully compatible yet
    def log_execution(*args, **kwargs):  # type: ignore
        """Placeholder for log_execution decorator"""

        def decorator(func):  # type: ignore
            return func

        return decorator

    def with_request_context(*args, **kwargs):  # type: ignore
        """Placeholder for with_request_context decorator"""

        def decorator(func):  # type: ignore
            return func

        return decorator

    def async_with_request_context(*args, **kwargs):  # type: ignore
        """Placeholder for async_with_request_context decorator"""

        def decorator(func):  # type: ignore
            return func

        return decorator

# UUID configuration (re-exported for convenience)
from morado.common.utils.uuid import UUIDConfig

# Public API
__all__ = [
    "ConfigurationManager",
    "LoggerConfig",
    "LoggerSystem",
    "ProcessorConfig",
    "UUIDConfig",
    "configure_logger",
    "get_logger",
    "log_execution",
    # New context functions
    "clear_context",
    "get_context_data",
    "get_log_context",
    "get_request_id",
    "set_context_data",
    "set_request_id",
    # Old context functions (for backward compatibility)
    "ContextManager",
    "RequestContext",
    "async_request_scope",
    "async_with_request_context",
    "request_scope",
    "with_request_context",
]
