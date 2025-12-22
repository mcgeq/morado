#!/usr/bin/python3
"""
Basic tests for configuration manager
"""
import os
import tempfile
from pathlib import Path

import pytest

from morado.common.logger.config import (
    LoggerConfig,
    ProcessorConfig,
    ConfigurationManager,
)
from morado.common.utils.uuid import UUIDConfig


def test_logger_config_defaults():
    """Test LoggerConfig with default values"""
    config = LoggerConfig()
    assert config.level == "INFO"
    assert config.format == "console"
    assert config.output == "stdout"
    assert config.module_levels == {}
    assert config.processors == []
    assert config.context_vars == ["request_id", "user_id", "trace_id"]
    assert config.request_id_config is None


def test_logger_config_to_dict():
    """Test LoggerConfig to_dict conversion"""
    config = LoggerConfig(
        level="DEBUG",
        format="json",
        output="stderr",
        module_levels={"morado.api": "WARNING"},
    )
    config_dict = config.to_dict()
    
    assert config_dict["level"] == "DEBUG"
    assert config_dict["format"] == "json"
    assert config_dict["output"] == "stderr"
    assert config_dict["module_levels"] == {"morado.api": "WARNING"}


def test_logger_config_from_dict():
    """Test LoggerConfig from_dict creation"""
    data = {
        "level": "ERROR",
        "format": "structured",
        "output": "stdout",
        "module_levels": {"morado.db": "DEBUG"},
        "context_vars": ["request_id"],
    }
    config = LoggerConfig.from_dict(data)
    
    assert config.level == "ERROR"
    assert config.format == "structured"
    assert config.output == "stdout"
    assert config.module_levels == {"morado.db": "DEBUG"}
    assert config.context_vars == ["request_id"]


def test_logger_config_merge():
    """Test LoggerConfig merge functionality"""
    config1 = LoggerConfig(
        level="INFO",
        module_levels={"morado.api": "DEBUG"},
    )
    config2 = LoggerConfig(
        level="WARNING",
        module_levels={"morado.db": "ERROR"},
    )
    
    merged = config1.merge(config2)
    
    assert merged.level == "WARNING"
    assert merged.module_levels == {"morado.api": "DEBUG", "morado.db": "ERROR"}


def test_processor_config():
    """Test ProcessorConfig dataclass"""
    proc = ProcessorConfig(
        name="custom_processor",
        module="myapp.processors",
        params={"key": "value"},
        enabled=True,
    )
    
    assert proc.name == "custom_processor"
    assert proc.module == "myapp.processors"
    assert proc.params == {"key": "value"}
    assert proc.enabled is True
    
    # Test to_dict
    proc_dict = proc.to_dict()
    assert proc_dict["name"] == "custom_processor"
    
    # Test from_dict
    proc2 = ProcessorConfig.from_dict(proc_dict)
    assert proc2.name == proc.name


def test_configuration_manager_default_config():
    """Test ConfigurationManager get_default_config"""
    config = ConfigurationManager.get_default_config()
    assert isinstance(config, LoggerConfig)
    assert config.level == "INFO"


def test_configuration_manager_load_from_toml():
    """Test loading configuration from TOML file"""
    toml_content = """
[logging]
level = "DEBUG"
format = "json"
output = "stdout"

[logging.module_levels]
"morado.api" = "INFO"
"morado.db" = "WARNING"

[logging.request_id]
format = "alphanumeric"
length = 32
prefix = "REQ"
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(toml_content)
        temp_path = f.name
    
    try:
        config = ConfigurationManager.load_from_file(temp_path)
        
        assert config.level == "DEBUG"
        assert config.format == "json"
        assert config.output == "stdout"
        assert config.module_levels == {"morado.api": "INFO", "morado.db": "WARNING"}
        assert config.request_id_config is not None
        assert config.request_id_config.format == "alphanumeric"
        assert config.request_id_config.length == 32
        assert config.request_id_config.prefix == "REQ"
    finally:
        os.unlink(temp_path)


def test_configuration_manager_load_from_env():
    """Test loading configuration from environment variables"""
    # Set environment variables
    os.environ["MORADO_LOG_LEVEL"] = "ERROR"
    os.environ["MORADO_LOG_FORMAT"] = "json"
    os.environ["MORADO_REQUEST_ID_FORMAT"] = "uuid4"
    os.environ["MORADO_REQUEST_ID_LENGTH"] = "36"
    
    try:
        config = ConfigurationManager.load_from_env()
        
        assert config.level == "ERROR"
        assert config.format == "json"
        assert config.request_id_config is not None
        assert config.request_id_config.format == "uuid4"
        assert config.request_id_config.length == 36
    finally:
        # Clean up environment variables
        del os.environ["MORADO_LOG_LEVEL"]
        del os.environ["MORADO_LOG_FORMAT"]
        del os.environ["MORADO_REQUEST_ID_FORMAT"]
        del os.environ["MORADO_REQUEST_ID_LENGTH"]


def test_configuration_manager_merge_configs():
    """Test merging multiple configurations"""
    config1 = LoggerConfig(level="INFO")
    config2 = LoggerConfig(format="json")
    config3 = LoggerConfig(output="stderr")
    
    merged = ConfigurationManager.merge_configs(config1, config2, config3)
    
    assert merged.level == "INFO"
    assert merged.format == "json"
    assert merged.output == "stderr"


def test_configuration_manager_validate_config():
    """Test configuration validation"""
    # Invalid log level
    config = LoggerConfig(level="INVALID")
    validated = ConfigurationManager.validate_config(config)
    assert validated.level == "INFO"  # Should fall back to default
    
    # Invalid format - Pydantic will prevent this at creation time
    # So we test with a valid format and then validate
    config = LoggerConfig(level="debug", format="json")
    validated = ConfigurationManager.validate_config(config)
    assert validated.level == "DEBUG"  # Should be uppercased
    assert validated.format == "json"
    
    # Test that Pydantic validates format at creation
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        LoggerConfig(format="invalid_format")


def test_configuration_manager_file_not_found():
    """Test handling of missing configuration file"""
    with pytest.raises(FileNotFoundError):
        ConfigurationManager.load_from_file("/nonexistent/path/config.toml")


def test_configuration_manager_find_config_file():
    """Test finding configuration file in standard locations"""
    # Test with environment variable
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("[logging]\nlevel = \"INFO\"")
        temp_path = f.name
    
    try:
        os.environ["MORADO_LOG_CONFIG"] = temp_path
        found_path = ConfigurationManager.find_config_file()
        assert found_path == Path(temp_path)
    finally:
        del os.environ["MORADO_LOG_CONFIG"]
        os.unlink(temp_path)


def test_logger_config_with_uuid_config():
    """Test LoggerConfig with UUIDConfig"""
    uuid_config = UUIDConfig(
        format="alphanumeric",
        length=24,
        prefix="TEST",
    )
    
    logger_config = LoggerConfig(
        level="DEBUG",
        request_id_config=uuid_config,
    )
    
    assert logger_config.request_id_config is not None
    assert logger_config.request_id_config.format == "alphanumeric"
    assert logger_config.request_id_config.prefix == "TEST"
    
    # Test serialization
    config_dict = logger_config.to_dict()
    assert "request_id_config" in config_dict
    
    # Test deserialization
    restored = LoggerConfig.from_dict(config_dict)
    assert restored.request_id_config is not None
    assert restored.request_id_config.format == "alphanumeric"
