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
        get_logger,
        configure_logger,
        LoggerSystem,
    )
except ImportError:
    # Fallback for when logger.py is not yet implemented
    import structlog
    
    def get_logger(name=None):
        """Get a logger instance (fallback implementation)"""
        return structlog.get_logger(name)
    
    def configure_logger(config=None, config_file=None, **overrides):
        """Configure logger (fallback implementation)"""
        pass
    
    class LoggerSystem:
        """Logger system placeholder"""
        pass

# Context management
from morado.common.logger.context import (
    request_scope,
    async_request_scope,
    ContextManager,
    RequestContext,
)

# Decorators
from morado.common.logger.decorators import (
    with_request_context,
    async_with_request_context,
    log_execution,
)

# Configuration
from morado.common.logger.config import (
    LoggerConfig,
    ProcessorConfig,
    ConfigurationManager,
)

# UUID configuration (re-exported for convenience)
from morado.common.utils.uuid import UUIDConfig

# Public API
__all__ = [
    # Core logger functions
    'get_logger',
    'configure_logger',
    'LoggerSystem',
    
    # Context management
    'request_scope',
    'async_request_scope',
    'ContextManager',
    'RequestContext',
    
    # Decorators
    'with_request_context',
    'async_with_request_context',
    'log_execution',
    
    # Configuration
    'LoggerConfig',
    'ProcessorConfig',
    'ConfigurationManager',
    'UUIDConfig',
]
