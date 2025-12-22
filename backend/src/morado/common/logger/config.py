#!/usr/bin/python3
"""
Configuration management for the logger system
Handles loading, validation, and merging of logger configurations
"""
import os
import tomllib
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from morado.common.utils.uuid import UUIDConfig


class ProcessorConfig(BaseModel):
    """Configuration for a log processor"""
    name: str
    module: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ProcessorConfig':
        """Create configuration from dictionary"""
        return cls(**data)


class LoggerConfig(BaseModel):
    """Complete logger configuration schema"""
    level: str = "INFO"
    format: Literal["console", "json", "structured"] = "console"
    output: str = "stdout"  # stdout, stderr, or file path
    module_levels: dict[str, str] = Field(default_factory=dict)
    processors: list[ProcessorConfig] = Field(default_factory=list)
    context_vars: list[str] = Field(default_factory=lambda: ["request_id", "user_id", "trace_id"])
    request_id_config: UUIDConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        result = self.model_dump()
        # Convert nested Pydantic models to dicts
        if result.get("request_id_config") is not None:
            result["request_id_config"] = self.request_id_config.to_dict()
        result["processors"] = [p.to_dict() for p in self.processors]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'LoggerConfig':
        """Create configuration from dictionary"""
        # Handle processors
        processors_data = data.get("processors", [])
        processors = []
        if isinstance(processors_data, list):
            for proc in processors_data:
                if isinstance(proc, dict):
                    processors.append(ProcessorConfig.from_dict(proc))
                elif isinstance(proc, ProcessorConfig):
                    processors.append(proc)

        # Handle request_id_config
        request_id_config = None
        if "request_id_config" in data and data["request_id_config"] is not None:
            rid_data = data["request_id_config"]
            if isinstance(rid_data, dict):
                request_id_config = UUIDConfig.from_dict(rid_data)
            elif isinstance(rid_data, UUIDConfig):
                request_id_config = rid_data

        return cls(
            level=data.get("level", "INFO"),
            format=data.get("format", "console"),
            output=data.get("output", "stdout"),
            module_levels=data.get("module_levels", {}).copy() if isinstance(data.get("module_levels"), dict) else {},
            processors=processors,
            context_vars=data.get("context_vars", ["request_id", "user_id", "trace_id"]).copy() if isinstance(data.get("context_vars"), list) else ["request_id", "user_id", "trace_id"],
            request_id_config=request_id_config
        )

    def merge(self, other: 'LoggerConfig') -> 'LoggerConfig':
        """
        Merge with another config (other takes precedence)
        Returns a new LoggerConfig with merged values
        """
        # Start with a copy of self's values
        merged_data = self.to_dict()
        other_data = other.to_dict()

        # Merge simple fields (other takes precedence if different from default)
        default_config = LoggerConfig()

        # For level, format, output: use other if it's not the default
        if other.level != default_config.level:
            merged_data["level"] = other.level

        if other.format != default_config.format:
            merged_data["format"] = other.format

        if other.output != default_config.output:
            merged_data["output"] = other.output

        # Merge module_levels (other takes precedence for overlapping keys)
        merged_data["module_levels"].update(other.module_levels)

        # Merge processors (append other's processors to self's)
        merged_data["processors"].extend(other_data["processors"])

        # Merge context_vars (use other if not default)
        if other.context_vars != default_config.context_vars:
            merged_data["context_vars"] = other.context_vars

        # Use other's request_id_config if present
        if other.request_id_config is not None:
            merged_data["request_id_config"] = other_data["request_id_config"]

        return LoggerConfig.from_dict(merged_data)


class ConfigurationManager:
    """Manages configuration loading and merging"""

    # Valid log levels
    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    # Valid output formats
    VALID_FORMATS = {"console", "json", "structured"}

    # Valid output destinations
    VALID_OUTPUTS = {"stdout", "stderr"}  # Plus any file path

    @staticmethod
    def get_default_config() -> LoggerConfig:
        """
        Get default configuration
        :return: Default LoggerConfig instance
        """
        return LoggerConfig()

    @staticmethod
    def load_from_file(path: str) -> LoggerConfig:
        """
        Load configuration from TOML or YAML file
        :param path: Path to configuration file
        :return: LoggerConfig instance
        :raises FileNotFoundError: If file doesn't exist
        :raises ValueError: If file format is unsupported or malformed
        """
        file_path = Path(path)

        if not file_path.exists():
            msg = f"Configuration file not found: {path}"
            raise FileNotFoundError(msg)

        # Determine file type by extension
        suffix = file_path.suffix.lower()

        if suffix in [".toml"]:
            return ConfigurationManager._load_from_toml(file_path)
        elif suffix in [".yaml", ".yml"]:
            return ConfigurationManager._load_from_yaml(file_path)
        else:
            msg = f"Unsupported configuration file format: {suffix}"
            raise ValueError(msg)

    @staticmethod
    def _load_from_toml(file_path: Path) -> LoggerConfig:
        """Load configuration from TOML file"""
        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)

            # Extract logging section
            logging_data = data.get("logging", {})

            # Parse configuration
            config_dict = {
                "level": logging_data.get("level", "INFO"),
                "format": logging_data.get("format", "console"),
                "output": logging_data.get("output", "stdout"),
                "module_levels": logging_data.get("module_levels", {}),
                "context_vars": logging_data.get("context_vars", ["request_id", "user_id", "trace_id"]),
            }

            # Parse processors
            processors_data = logging_data.get("processors", {})
            processors = []
            if isinstance(processors_data, dict):
                for name, proc_config in processors_data.items():
                    if isinstance(proc_config, dict):
                        processors.append(ProcessorConfig(
                            name=name,
                            module=proc_config.get("module"),
                            params=proc_config.get("params", {}),
                            enabled=proc_config.get("enabled", True)
                        ))
            config_dict["processors"] = processors

            # Parse request_id configuration
            request_id_data = logging_data.get("request_id", {})
            if request_id_data:
                config_dict["request_id_config"] = UUIDConfig.from_dict(request_id_data)

            return LoggerConfig.from_dict(config_dict)

        except tomllib.TOMLDecodeError as e:
            msg = f"Malformed TOML file: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Error loading TOML configuration: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def _load_from_yaml(file_path: Path) -> LoggerConfig:
        """Load configuration from YAML file"""
        try:
            import yaml
        except ImportError as e:
            raise ImportError("PyYAML is required for YAML configuration files. Install with: pip install pyyaml") from e

        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)

            # Extract logging section
            logging_data = data.get("logging", {})

            # Parse configuration (similar to TOML)
            config_dict = {
                "level": logging_data.get("level", "INFO"),
                "format": logging_data.get("format", "console"),
                "output": logging_data.get("output", "stdout"),
                "module_levels": logging_data.get("module_levels", {}),
                "context_vars": logging_data.get("context_vars", ["request_id", "user_id", "trace_id"]),
            }

            # Parse processors
            processors_data = logging_data.get("processors", {})
            processors = []
            if isinstance(processors_data, dict):
                for name, proc_config in processors_data.items():
                    if isinstance(proc_config, dict):
                        processors.append(ProcessorConfig(
                            name=name,
                            module=proc_config.get("module"),
                            params=proc_config.get("params", {}),
                            enabled=proc_config.get("enabled", True)
                        ))
            config_dict["processors"] = processors

            # Parse request_id configuration
            request_id_data = logging_data.get("request_id", {})
            if request_id_data:
                config_dict["request_id_config"] = UUIDConfig.from_dict(request_id_data)

            return LoggerConfig.from_dict(config_dict)

        except yaml.YAMLError as e:
            msg = f"Malformed YAML file: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Error loading YAML configuration: {e}"
            raise ValueError(msg) from e

    @staticmethod
    def load_from_env() -> LoggerConfig:
        """
        Load configuration from environment variables
        Supported environment variables:
        - MORADO_LOG_LEVEL: Global log level
        - MORADO_LOG_FORMAT: Output format (console, json, structured)
        - MORADO_LOG_OUTPUT: Output destination (stdout, stderr, file path)
        - MORADO_REQUEST_ID_FORMAT: Request ID format
        - MORADO_REQUEST_ID_LENGTH: Request ID length
        - MORADO_REQUEST_ID_PREFIX: Request ID prefix
        - MORADO_REQUEST_ID_SUFFIX: Request ID suffix
        :return: LoggerConfig instance with values from environment
        """
        config_dict = {}

        # Load basic configuration
        if "MORADO_LOG_LEVEL" in os.environ:
            config_dict["level"] = os.environ["MORADO_LOG_LEVEL"]

        if "MORADO_LOG_FORMAT" in os.environ:
            config_dict["format"] = os.environ["MORADO_LOG_FORMAT"]

        if "MORADO_LOG_OUTPUT" in os.environ:
            config_dict["output"] = os.environ["MORADO_LOG_OUTPUT"]

        # Load request_id configuration
        request_id_config = {}
        if "MORADO_REQUEST_ID_FORMAT" in os.environ:
            request_id_config["format"] = os.environ["MORADO_REQUEST_ID_FORMAT"]

        if "MORADO_REQUEST_ID_LENGTH" in os.environ:
            try:
                request_id_config["length"] = int(os.environ["MORADO_REQUEST_ID_LENGTH"])
            except ValueError:
                pass  # Ignore invalid values

        if "MORADO_REQUEST_ID_PREFIX" in os.environ:
            request_id_config["prefix"] = os.environ["MORADO_REQUEST_ID_PREFIX"]

        if "MORADO_REQUEST_ID_SUFFIX" in os.environ:
            request_id_config["suffix"] = os.environ["MORADO_REQUEST_ID_SUFFIX"]

        if request_id_config:
            config_dict["request_id_config"] = UUIDConfig.from_dict(request_id_config)

        # If no environment variables found, return default config
        if not config_dict:
            return LoggerConfig()

        # Merge with defaults
        default_config = LoggerConfig()
        env_config = LoggerConfig.from_dict(config_dict)
        return default_config.merge(env_config)

    @staticmethod
    def merge_configs(*configs: LoggerConfig) -> LoggerConfig:
        """
        Merge multiple configurations with precedence
        Later configs take precedence over earlier ones
        :param configs: Variable number of LoggerConfig instances
        :return: Merged LoggerConfig instance
        """
        if not configs:
            return LoggerConfig()

        result = configs[0]
        for config in configs[1:]:
            result = result.merge(config)

        return result

    @staticmethod
    def find_config_file() -> Path | None:
        """
        Search for configuration file in standard locations
        Search order:
        1. Path specified in MORADO_LOG_CONFIG environment variable
        2. ./logging.toml (current directory)
        3. ./config/logging.toml
        4. ~/.morado/logging.toml (user home)
        :return: Path to configuration file if found, None otherwise
        """
        # Check environment variable
        if "MORADO_LOG_CONFIG" in os.environ:
            env_path = Path(os.environ["MORADO_LOG_CONFIG"])
            if env_path.exists():
                return env_path

        # Check current directory
        current_dir_config = Path("logging.toml")
        if current_dir_config.exists():
            return current_dir_config

        # Check config subdirectory
        config_dir_config = Path("config/logging.toml")
        if config_dir_config.exists():
            return config_dir_config

        # Check user home directory
        home_config = Path.home() / ".morado" / "logging.toml"
        if home_config.exists():
            return home_config

        return None

    @staticmethod
    def validate_config(config: LoggerConfig) -> LoggerConfig:
        """
        Validate configuration and return a corrected version
        Logs warnings for invalid values and uses defaults
        :param config: LoggerConfig to validate
        :return: Validated LoggerConfig with corrections applied
        """
        validated = LoggerConfig.from_dict(config.to_dict())

        # Validate log level
        if validated.level.upper() not in ConfigurationManager.VALID_LOG_LEVELS:
            print(f"Warning: Invalid log level '{validated.level}'. Using default 'INFO'.")
            validated.level = "INFO"
        else:
            validated.level = validated.level.upper()

        # Validate format
        if validated.format not in ConfigurationManager.VALID_FORMATS:
            print(f"Warning: Invalid log format '{validated.format}'. Using default 'console'.")
            validated.format = "console"

        # Validate output
        if validated.output not in ConfigurationManager.VALID_OUTPUTS:
            # Check if it's a file path
            if not validated.output.startswith("/") and not validated.output.startswith("./"):
                print(f"Warning: Invalid log output '{validated.output}'. Using default 'stdout'.")
                validated.output = "stdout"

        # Validate module levels
        for module, level in list(validated.module_levels.items()):
            if level.upper() not in ConfigurationManager.VALID_LOG_LEVELS:
                print(f"Warning: Invalid log level '{level}' for module '{module}'. Removing module-specific level.")
                del validated.module_levels[module]
            else:
                validated.module_levels[module] = level.upper()

        return validated

    @staticmethod
    def load_config(
        config_file: str | None = None,
        auto_search: bool = True,
        load_env: bool = True,
        validate: bool = True
    ) -> LoggerConfig:
        """
        Load configuration with full precedence chain
        Precedence: code > environment variables > config file > defaults
        :param config_file: Explicit path to config file (optional)
        :param auto_search: Whether to search for config file in standard locations
        :param load_env: Whether to load environment variables
        :param validate: Whether to validate the final configuration
        :return: Loaded and merged LoggerConfig
        """
        configs = []

        # Start with defaults
        configs.append(ConfigurationManager.get_default_config())

        # Load from file if available
        file_config = None
        if config_file:
            try:
                file_config = ConfigurationManager.load_from_file(config_file)
                configs.append(file_config)
            except FileNotFoundError:
                print(f"Info: Configuration file not found: {config_file}. Using defaults.")
            except ValueError as e:
                print(f"Warning: Error loading configuration file: {e}. Using defaults.")
        elif auto_search:
            config_path = ConfigurationManager.find_config_file()
            if config_path:
                try:
                    file_config = ConfigurationManager.load_from_file(str(config_path))
                    configs.append(file_config)
                except ValueError as e:
                    print(f"Warning: Error loading configuration file {config_path}: {e}. Using defaults.")

        # Load from environment variables
        if load_env:
            env_config = ConfigurationManager.load_from_env()
            # Only add if it has non-default values
            if env_config.to_dict() != LoggerConfig().to_dict():
                configs.append(env_config)

        # Merge all configurations
        merged_config = ConfigurationManager.merge_configs(*configs)

        # Validate if requested
        if validate:
            merged_config = ConfigurationManager.validate_config(merged_config)

        return merged_config
