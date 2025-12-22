#!/usr/bin/env python3
"""
Verification script to test that common modules can be imported correctly.
This script tests all the public APIs from morado.common.logger and morado.common.utils.
"""

import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

def test_logger_imports():
    """Test that logger module can be imported correctly."""
    print("Testing logger imports...")

    try:
        # Test basic imports
        from morado.common.logger import (
            ContextManager,
            LoggerConfig,
            get_logger,
        )
        print("✓ All logger imports successful")

        # Test that we can create a logger
        logger = get_logger(__name__)
        print(f"✓ Created logger: {logger}")

        # Test that we can create a config
        config = LoggerConfig(level="DEBUG", format="json")
        print(f"✓ Created LoggerConfig: {config}")

        # Test context manager
        ctx_mgr = ContextManager()
        print(f"✓ Created ContextManager: {ctx_mgr}")

        return True
    except Exception as e:
        print(f"✗ Logger import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils_imports():
    """Test that utils module can be imported correctly."""
    print("\nTesting utils imports...")

    try:
        # Test UUID imports
        from morado.common.utils import (
            alphanumeric,
            numeric,
            ulid,
            uuid4,
        )
        print("✓ UUID imports successful")

        # Test generating UUIDs
        id1 = uuid4()
        print(f"✓ Generated UUID4: {id1}")

        id2 = ulid()
        print(f"✓ Generated ULID: {id2}")

        id3 = alphanumeric(length=24, prefix="TEST")
        print(f"✓ Generated alphanumeric: {id3}")

        id4 = numeric(length=20)
        print(f"✓ Generated numeric: {id4}")

        return True
    except Exception as e:
        print(f"✗ Utils UUID import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_filesystem_imports():
    """Test that filesystem utilities can be imported correctly."""
    print("\nTesting filesystem imports...")

    try:
        from morado.common.utils import FileSystemUtil
        print("✓ FileSystemUtil import successful")

        # Test basic filesystem operations
        exists = FileSystemUtil.exists(".")
        print(f"✓ FileSystemUtil.exists() works: {exists}")

        abs_path = FileSystemUtil.get_absolute_path(".")
        print(f"✓ FileSystemUtil.get_absolute_path() works: {abs_path}")

        return True
    except Exception as e:
        print(f"✗ FileSystemUtil import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_imports():
    """Test that time utilities can be imported correctly."""
    print("\nTesting time imports...")

    try:
        from morado.common.utils import TimeUtil
        print("✓ TimeUtil import successful")

        # Test basic time operations
        utc_now = TimeUtil.now_utc()
        print(f"✓ TimeUtil.now_utc() works: {utc_now}")

        local_now = TimeUtil.now_local()
        print(f"✓ TimeUtil.now_local() works: {local_now}")

        iso_string = TimeUtil.to_iso8601(utc_now)
        print(f"✓ TimeUtil.to_iso8601() works: {iso_string}")

        parsed = TimeUtil.parse_iso8601(iso_string)
        print(f"✓ TimeUtil.parse_iso8601() works: {parsed}")

        return True
    except Exception as e:
        print(f"✗ TimeUtil import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exceptions_imports():
    """Test that exception classes can be imported correctly."""
    print("\nTesting exception imports...")

    try:
        from morado.common.utils import (
            FileExistsError,
            FileNotFoundError,
            FileSystemError,
            TimeParseError,
        )
        print("✓ All exception imports successful")

        # Test that we can instantiate exceptions
        exc1 = FileSystemError("test error")
        print(f"✓ Created FileSystemError: {exc1}")

        exc2 = FileNotFoundError("/test/path")
        print(f"✓ Created FileNotFoundError: {exc2}")

        exc3 = FileExistsError("/test/path")
        print(f"✓ Created FileExistsError: {exc3}")

        exc4 = TimeParseError("invalid-time")
        print(f"✓ Created TimeParseError: {exc4}")

        return True
    except Exception as e:
        print(f"✗ Exception import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all import tests."""
    print("=" * 60)
    print("Common Module Import Verification")
    print("=" * 60)

    results = []

    # Run all tests
    results.append(("Logger", test_logger_imports()))
    results.append(("Utils UUID", test_utils_imports()))
    results.append(("FileSystem", test_filesystem_imports()))
    results.append(("Time", test_time_imports()))
    results.append(("Exceptions", test_exceptions_imports()))

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✓ All import tests passed!")
        return 0
    else:
        print("\n✗ Some import tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
