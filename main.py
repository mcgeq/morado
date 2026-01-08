"""
Example usage of the Morado logger system.
"""

from morado.common.logger import configure_logger, get_logger, request_scope
from morado.common.logger.config import LoggerConfig, UUIDConfig


def main():
    """Main function demonstrating the new logger API."""
    # Configure the logger system (optional - uses defaults if not called)
    request_id_cfg = UUIDConfig(
        format="alphanumeric",
        length=38,
        prefix="REQ",
    )

    config = LoggerConfig(
        level="INFO", format="console", request_id_config=request_id_cfg
    )
    configure_logger(config)

    # Get a logger instance
    logger = get_logger(__name__)

    # Basic logging
    logger.info("Application started", version="1.0.0")

    # Using request scope for context tracking
    # Pass request_id_config to use the configured UUID format
    with request_scope(user_id=42, request_id_config=request_id_cfg) as ctx:
        logger.info("Processing request", action="fetch_data")
        logger.debug("Request context", context=ctx)

    # Or use default 38-character UUID without prefix
    with request_scope(user_id=99) as ctx:
        logger.info("Another request", action="process_data")
        logger.debug("Request context", context=ctx)

    logger.info("Application finished")


if __name__ == "__main__":
    main()
