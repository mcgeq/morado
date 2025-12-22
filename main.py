"""
Example usage of the Morado logger system.
"""
from morado.common.logger import get_logger, request_scope, configure_logger
from morado.common.logger.config import LoggerConfig, UUIDConfig


def main():
    """Main function demonstrating the new logger API."""
    # Configure the logger system (optional - uses defaults if not called)
    config = LoggerConfig(
        level="INFO",
        format="console",
        request_id_config=UUIDConfig(
            format="alphanumeric",
            length=24,
            prefix="REQ",
        )
    )
    configure_logger(config)
    
    # Get a logger instance
    logger = get_logger(__name__)
    
    # Basic logging
    logger.info("Application started", version="1.0.0")
    
    # Using request scope for context tracking
    with request_scope(user_id=42) as ctx:
        logger.info("Processing request", action="fetch_data")
        logger.debug("Request context", context=ctx)
    
    logger.info("Application finished")


if __name__ == "__main__":
    main()
