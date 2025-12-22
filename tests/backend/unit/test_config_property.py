"""Property-based tests for configuration management.

Feature: project-restructure, Property 1: 环境配置切换一致性

This module tests that environment configuration switching works correctly
across all valid environments using property-based testing with Hypothesis.
"""

import os
import sys
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from morado.core.config import reload_settings

# Property 1: Environment configuration switching consistency
# For any valid environment name (development, testing, production),
# when setting the corresponding environment variable, the system should
# load that environment's configuration file, and the configuration object
# should contain that environment's specific settings.

@given(environment=st.sampled_from(["development", "testing", "production"]))
@settings(max_examples=100)
def test_environment_config_consistency(environment: str):
    """
    **Feature: project-restructure, Property 1: 环境配置切换一致性**
    **Validates: Requirements 5.2**

    Property: For any valid environment name, when the environment is set,
    the system should load the corresponding configuration file and the
    configuration should reflect that environment's settings.

    This property verifies that:
    1. Each environment can be loaded without errors
    2. The loaded configuration has the correct environment value
    3. Environment-specific settings are properly loaded from TOML files
    4. The configuration is consistent with the environment
    """
    # Set the environment variable
    os.environ["ENVIRONMENT"] = environment

    try:
        # Reload settings to pick up the new environment
        settings = reload_settings()

        # Verify the environment is set correctly
        assert settings.environment == environment, \
            f"Expected environment '{environment}', got '{settings.environment}'"

        # Verify environment-specific properties
        if environment == "development":
            # Development should have debug enabled
            assert settings.debug is True, \
                "Development environment should have debug=True"
            # Development should allow reload
            assert settings.reload is True, \
                "Development environment should have reload=True"
            # Development should have DEBUG log level
            assert settings.log_level == "DEBUG", \
                f"Development should have DEBUG log level, got {settings.log_level}"
            # Development should use console format
            assert settings.log_format == "console", \
                f"Development should use console format, got {settings.log_format}"
            # Development database should have _dev suffix
            assert "morado_dev" in settings.database_url, \
                f"Development database URL should contain 'morado_dev', got {settings.database_url}"

        elif environment == "testing":
            # Testing should have debug enabled
            assert settings.debug is True, \
                "Testing environment should have debug=True"
            # Testing should not allow reload
            assert settings.reload is False, \
                "Testing environment should have reload=False"
            # Testing should have WARNING log level
            assert settings.log_level == "WARNING", \
                f"Testing should have WARNING log level, got {settings.log_level}"
            # Testing should use json format
            assert settings.log_format == "json", \
                f"Testing should use json format, got {settings.log_format}"
            # Testing database should have _test suffix
            assert "morado_test" in settings.database_url, \
                f"Testing database URL should contain 'morado_test', got {settings.database_url}"

        elif environment == "production":
            # Production should have debug disabled
            assert settings.debug is False, \
                "Production environment should have debug=False"
            # Production should not allow reload
            assert settings.reload is False, \
                "Production environment should have reload=False"
            # Production should have INFO log level
            assert settings.log_level == "INFO", \
                f"Production should have INFO log level, got {settings.log_level}"
            # Production should use json format
            assert settings.log_format == "json", \
                f"Production should use json format, got {settings.log_format}"
            # Production database should not have _dev or _test suffix
            assert "morado_dev" not in settings.database_url, \
                f"Production database URL should not contain 'morado_dev', got {settings.database_url}"
            assert "morado_test" not in settings.database_url, \
                f"Production database URL should not contain 'morado_test', got {settings.database_url}"

        # Verify helper properties work correctly
        assert settings.is_development == (environment == "development"), \
            f"is_development should be {environment == 'development'}"
        assert settings.is_testing == (environment == "testing"), \
            f"is_testing should be {environment == 'testing'}"
        assert settings.is_production == (environment == "production"), \
            f"is_production should be {environment == 'production'}"

        # Verify that exactly one environment flag is True
        env_flags = [settings.is_development, settings.is_testing, settings.is_production]
        assert sum(env_flags) == 1, \
            "Exactly one environment flag should be True"

    finally:
        # Clean up: restore default environment
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        reload_settings()


def test_environment_config_isolation():
    """
    Test that switching between environments properly isolates configuration.

    This test verifies that changing the environment actually changes the
    configuration and that settings from one environment don't leak into another.
    """
    environments = ["development", "testing", "production"]
    configs = {}

    # Load each environment's configuration
    for env in environments:
        os.environ["ENVIRONMENT"] = env
        settings = reload_settings()
        configs[env] = {
            "debug": settings.debug,
            "reload": settings.reload,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "database_url": settings.database_url,
        }

    # Clean up
    if "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]
    reload_settings()

    # Verify that configurations are different
    assert configs["development"]["debug"] != configs["production"]["debug"], \
        "Development and production should have different debug settings"

    assert configs["development"]["reload"] != configs["production"]["reload"], \
        "Development and production should have different reload settings"

    assert configs["development"]["log_level"] != configs["production"]["log_level"], \
        "Development and production should have different log levels"

    assert configs["development"]["database_url"] != configs["testing"]["database_url"], \
        "Development and testing should have different database URLs"

    assert configs["testing"]["database_url"] != configs["production"]["database_url"], \
        "Testing and production should have different database URLs"


if __name__ == "__main__":
    # Run the property-based test
    test_environment_config_consistency()
    test_environment_config_isolation()
    print("✓ All property-based tests passed!")
