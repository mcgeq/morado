"""Core logger implementation using structlog.

This module provides the main logger system implementation with:
- Structlog-based logging with configurable processors
- Integration with context management
- Support for multiple output formats (console, JSON, structured)
- Configuration-driven setup
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.types import FilteringBoundLogger

from morado.common.logger.config import ConfigurationManager, LoggerConfig
from morado.common.logger.context import get_context_data, get_request_id


class LoggerSystem:
    """Main logger system class.

    Manages the global logger configuration and provides access to
    configured logger instances.
    """

    _configured: bool = False
    _config: LoggerConfig | None = None

    @classmethod
    def configure(
        cls,
        config: LoggerConfig | None = None,
        config_file: str | Path | None = None,
        **overrides: Any,
    ) -> None:
        """Configure the logger system.

        Args:
            config: LoggerConfig instance to use
            config_file: Path to configuration file (TOML/YAML)
            **overrides: Additional configuration overrides

        Example:
            >>> LoggerSystem.configure(config=LoggerConfig(level="DEBUG"))
            >>> LoggerSystem.configure(config_file="logging.toml")
            >>> LoggerSystem.configure(level="INFO", format="json")
        """
        # Load configuration
        if config is None:
            if config_file:
                config = ConfigurationManager.load_from_file(
                    str(config_file), **overrides
                )
            else:
                config = ConfigurationManager.load_from_env(**overrides)

        cls._config = config

        # Configure structlog
        cls._configure_structlog(config)

        # Configure standard library logging
        cls._configure_stdlib_logging(config)

        cls._configured = True

    @classmethod
    def _configure_structlog(cls, config: LoggerConfig) -> None:
        """Configure structlog with the given configuration.

        Args:
            config: Logger configuration
        """
        # Build processor chain
        processors: list[Any] = [
            # Add context variables
            structlog.contextvars.merge_contextvars,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add log level
            structlog.processors.add_log_level,
            # Add logger name
            structlog.processors.StackInfoRenderer(),
        ]

        # Add format-specific processors
        if config.format == "json":
            processors.extend(
                [
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer(),
                ]
            )
        elif config.format == "structured":
            processors.extend(
                [
                    structlog.processors.format_exc_info,
                    structlog.processors.KeyValueRenderer(
                        key_order=[
                            "timestamp",
                            "level",
                            "event",
                            "request_id",
                            "user_id",
                        ]
                    ),
                ]
            )
        else:  # console
            processors.extend([structlog.dev.ConsoleRenderer(colors=True)])

        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(
                cls._get_log_level(config.level)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(
                file=cls._get_output_stream(config.output)
            ),
            cache_logger_on_first_use=True,
        )

    @classmethod
    def _configure_stdlib_logging(cls, config: LoggerConfig) -> None:
        """Configure standard library logging.

        Args:
            config: Logger configuration
        """
        # Set root logger level
        logging.basicConfig(
            level=cls._get_log_level(config.level),
            format="%(message)s",
            stream=cls._get_output_stream(config.output),
        )

        # Configure module-specific levels
        for module, level in config.module_levels.items():
            logging.getLogger(module).setLevel(cls._get_log_level(level))

    @classmethod
    def _get_log_level(cls, level: str) -> int:
        """Convert string log level to logging constant.

        Args:
            level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Logging level constant
        """
        return getattr(logging, level.upper(), logging.INFO)

    @classmethod
    def _get_output_stream(cls, output: str) -> Any:
        """Get output stream for logging.

        Args:
            output: Output specification (stdout, stderr, or file path)

        Returns:
            Output stream object
        """
        if output == "stdout":
            return sys.stdout
        if output == "stderr":
            return sys.stderr
        # Assume it's a file path
        return open(output, "a", encoding="utf-8")

    @classmethod
    def get_logger(cls, name: str | None = None) -> FilteringBoundLogger:
        """Get a logger instance.

        Args:
            name: Logger name (typically __name__)

        Returns:
            Configured structlog logger instance

        Example:
            >>> logger = LoggerSystem.get_logger(__name__)
            >>> logger.info("Hello, world!")
        """
        if not cls._configured:
            # Auto-configure with defaults if not configured
            cls.configure()

        logger = structlog.get_logger(name)

        # Bind context variables if available
        context = {}
        request_id = get_request_id()
        if request_id:
            context["request_id"] = request_id

        # Get user_id and trace_id from context data
        context_data = get_context_data()
        if context_data:
            if "user_id" in context_data:
                context["user_id"] = context_data["user_id"]
            if "trace_id" in context_data:
                context["trace_id"] = context_data["trace_id"]

        if context:
            logger = logger.bind(**context)

        return logger

    @classmethod
    def is_configured(cls) -> bool:
        """Check if logger system is configured.

        Returns:
            True if configured, False otherwise
        """
        return cls._configured

    @classmethod
    def get_config(cls) -> LoggerConfig | None:
        """Get current logger configuration.

        Returns:
            Current LoggerConfig or None if not configured
        """
        return cls._config


# Public API functions
def configure_logger(
    config: LoggerConfig | None = None,
    config_file: str | Path | None = None,
    **overrides: Any,
) -> None:
    """Configure the logger system.

    This is a convenience function that delegates to LoggerSystem.configure().

    Args:
        config: LoggerConfig instance to use
        config_file: Path to configuration file (TOML/YAML)
        **overrides: Additional configuration overrides

    Example:
        >>> configure_logger(config=LoggerConfig(level="DEBUG"))
        >>> configure_logger(config_file="logging.toml")
        >>> configure_logger(level="INFO", format="json")
    """
    LoggerSystem.configure(config=config, config_file=config_file, **overrides)


def get_logger(name: str | None = None) -> FilteringBoundLogger:
    """Get a logger instance.

    This is a convenience function that delegates to LoggerSystem.get_logger().

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request", user_id=42)
    """
    return LoggerSystem.get_logger(name)
