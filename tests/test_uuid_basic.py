"""Basic tests for UUID generator refactor"""
import pytest
from morado.common.utils.uuid import (
    UUIDConfig,
    UUIDGenerator,
    generate_alphanumeric,
    generate_numeric,
    generate_ulid,
    generate_uuid4,
)


def test_uuid_config_creation():
    """Test UUIDConfig can be created with defaults"""
    config = UUIDConfig()
    assert config.format == "alphanumeric"
    assert config.length == 38  # Updated default length
    assert config.secure is True


def test_uuid_config_validation_invalid_format():
    """Test UUIDConfig validates format"""
    # Pydantic raises ValidationError instead of ValueError
    from pydantic import ValidationError
    with pytest.raises(ValidationError, match="Input should be"):
        UUIDConfig(format="invalid")


def test_uuid_config_validation_empty_charset():
    """Test UUIDConfig validates charset is not empty"""
    with pytest.raises(ValueError, match="Charset cannot be empty"):
        UUIDConfig(charset="")


def test_uuid_config_validation_negative_length():
    """Test UUIDConfig validates length is positive"""
    with pytest.raises(ValueError, match="Length must be positive"):
        UUIDConfig(length=-1)


def test_uuid_config_to_dict():
    """Test UUIDConfig can be converted to dict"""
    config = UUIDConfig(format="uuid4", length=36)
    data = config.to_dict()
    assert data["format"] == "uuid4"
    assert data["length"] == 36


def test_uuid_config_from_dict():
    """Test UUIDConfig can be created from dict"""
    data = {"format": "ulid", "length": 26, "secure": True}
    config = UUIDConfig.from_dict(data)
    assert config.format == "ulid"
    assert config.length == 26
    assert config.secure is True


def test_uuid4_generation():
    """Test UUID4 generation"""
    uuid = UUIDGenerator.uuid4()
    assert isinstance(uuid, str)
    assert len(uuid) == 36  # Standard UUID4 format with hyphens
    assert uuid.count("-") == 4


def test_ulid_generation():
    """Test ULID generation"""
    ulid = UUIDGenerator.ulid()
    assert isinstance(ulid, str)
    assert len(ulid) == 26  # ULID is 26 characters


def test_ulid_sortability():
    """Test ULIDs are sortable by time"""
    import time
    ulid1 = UUIDGenerator.ulid()
    time.sleep(0.01)  # Sleep 10ms
    ulid2 = UUIDGenerator.ulid()
    assert ulid1 < ulid2  # Later ULID should be lexicographically greater


def test_alphanumeric_generation():
    """Test alphanumeric ID generation"""
    uuid = UUIDGenerator.alphanumeric(length=24)
    assert isinstance(uuid, str)
    assert len(uuid) == 24


def test_numeric_generation():
    """Test numeric ID generation"""
    uuid = UUIDGenerator.numeric(length=20)
    assert isinstance(uuid, str)
    assert len(uuid) == 20
    assert uuid.isdigit()


def test_generate_with_config():
    """Test generate method with config"""
    config = UUIDConfig(format="uuid4")
    uuid = UUIDGenerator.generate(config)
    assert isinstance(uuid, str)
    assert len(uuid) == 36


def test_alphanumeric_with_prefix_suffix():
    """Test alphanumeric with prefix and suffix"""
    uuid = UUIDGenerator.alphanumeric(length=30, prefix="REQ", suffix="END")
    assert uuid.startswith("REQ")
    assert uuid.endswith("END")
    assert len(uuid) == 30


def test_numeric_with_invalid_prefix():
    """Test numeric rejects non-numeric prefix"""
    with pytest.raises(ValueError, match="Prefix must be numeric"):
        UUIDGenerator.numeric(prefix="ABC")


def test_convenience_functions():
    """Test convenience functions work"""
    uuid4 = generate_uuid4()
    assert len(uuid4) == 36

    ulid = generate_ulid()
    assert len(ulid) == 26

    alphanumeric = generate_alphanumeric(length=20)
    assert len(alphanumeric) == 20

    numeric = generate_numeric(length=15)
    assert len(numeric) == 15
    assert numeric.isdigit()


def test_stateless_generator():
    """Test that UUIDGenerator is stateless (no instance state)"""
    # All methods should be static, no need to instantiate
    uuid1 = UUIDGenerator.uuid4()
    uuid2 = UUIDGenerator.uuid4()
    assert uuid1 != uuid2  # Should generate different UUIDs
