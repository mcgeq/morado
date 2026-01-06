"""Basic tests for context manager functionality."""

import asyncio

import pytest
from morado.common.logger.context import (
    async_request_scope,
    clear_context,
    get_context_data,
    get_log_context,
    get_request_id,
    request_scope,
    set_context_data,
    set_request_id,
)


def test_context_get_set():
    """Test basic get/set operations for context variables."""
    # Initially should be None
    assert get_request_id() is None
    assert get_context_data("user_id") is None
    assert get_context_data("trace_id") is None

    # Set values
    set_request_id("REQ123")
    set_context_data("user_id", 42)
    set_context_data("trace_id", "TRACE456")

    # Verify values
    assert get_request_id() == "REQ123"
    assert get_context_data("user_id") == 42
    assert get_context_data("trace_id") == "TRACE456"

    # Clear context
    clear_context()

    # Should be None again
    assert get_request_id() is None
    assert get_context_data("user_id") is None
    assert get_context_data("trace_id") is None


def test_context_get_all():
    """Test get_context_data returns all non-None values."""
    clear_context()

    # Empty context
    assert get_context_data() == {}

    # Set some values
    set_request_id("REQ123")
    set_context_data("user_id", 42)

    context = get_context_data()
    assert context == {"user_id": 42}

    # Add trace_id
    set_context_data("trace_id", "TRACE456")

    context = get_context_data()
    assert context == {"user_id": 42, "trace_id": "TRACE456"}

    clear_context()


def test_get_log_context():
    """Test get_log_context returns all context for logging."""
    clear_context()

    # Empty context
    assert get_log_context() == {}

    # Set values
    set_request_id("REQ123")
    set_context_data("user_id", 42)
    set_context_data("trace_id", "TRACE456")

    result = get_log_context()
    assert result == {
        "request_id": "REQ123",
        "user_id": 42,
        "trace_id": "TRACE456",
    }

    clear_context()


def test_request_scope_basic():
    """Test basic request_scope functionality."""
    clear_context()

    with request_scope(request_id="REQ123", user_id=42):
        # Context should be set
        assert get_request_id() == "REQ123"
        assert get_context_data("user_id") == 42

    # Context should be cleared after exit
    assert get_request_id() is None
    assert get_context_data("user_id") is None


def test_request_scope_auto_generate():
    """Test request_scope auto-generates request_id."""
    clear_context()

    with request_scope():
        # Should have auto-generated request_id
        request_id = get_request_id()
        assert request_id is not None
        assert len(request_id) > 0

    # Context should be cleared after exit
    assert get_request_id() is None


def test_request_scope_with_extra_context():
    """Test request_scope with extra context values."""
    clear_context()

    with request_scope(request_id="REQ123", user_id=42, custom_key="custom_value"):
        # Context should be set
        assert get_request_id() == "REQ123"
        assert get_context_data("user_id") == 42
        assert get_context_data("custom_key") == "custom_value"

    # Context should be cleared after exit
    assert get_request_id() is None
    assert get_context_data("user_id") is None
    assert get_context_data("custom_key") is None


@pytest.mark.asyncio
async def test_async_request_scope_basic():
    """Test basic async_request_scope functionality."""
    clear_context()

    async with async_request_scope(request_id="REQ123", user_id=42):
        # Context should be set
        assert get_request_id() == "REQ123"
        assert get_context_data("user_id") == 42

    # Context should be cleared after exit
    assert get_request_id() is None
    assert get_context_data("user_id") is None


@pytest.mark.asyncio
async def test_async_request_scope_isolation():
    """Test async_request_scope maintains isolation between tasks."""
    clear_context()

    results = []

    async def task(task_id: int):
        async with async_request_scope(request_id=f"REQ{task_id}", user_id=task_id):
            # Simulate some async work
            await asyncio.sleep(0.01)
            # Each task should see its own context
            request_id = get_request_id()
            user_id = get_context_data("user_id")
            results.append((task_id, request_id, user_id))

    # Run multiple tasks concurrently
    await asyncio.gather(
        task(1),
        task(2),
        task(3)
    )

    # Each task should have seen its own context
    assert len(results) == 3
    for task_id, request_id, user_id in results:
        assert request_id == f"REQ{task_id}"
        assert user_id == task_id
