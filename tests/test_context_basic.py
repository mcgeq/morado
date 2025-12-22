"""Basic tests for context manager functionality."""

import pytest
import asyncio
from morado.common.logger.context import (
    ContextManager,
    RequestContext,
    request_scope,
    async_request_scope,
)


def test_context_manager_get_set():
    """Test basic get/set operations for context variables."""
    # Initially should be None
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None
    assert ContextManager.get_trace_id() is None
    
    # Set values
    ContextManager.set_request_id("REQ123")
    ContextManager.set_user_id(42)
    ContextManager.set_trace_id("TRACE456")
    
    # Verify values
    assert ContextManager.get_request_id() == "REQ123"
    assert ContextManager.get_user_id() == 42
    assert ContextManager.get_trace_id() == "TRACE456"
    
    # Clear context
    ContextManager.clear_context()
    
    # Should be None again
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None
    assert ContextManager.get_trace_id() is None


def test_context_manager_get_all():
    """Test get_all_context returns all non-None values."""
    ContextManager.clear_context()
    
    # Empty context
    assert ContextManager.get_all_context() == {}
    
    # Set some values
    ContextManager.set_request_id("REQ123")
    ContextManager.set_user_id(42)
    
    context = ContextManager.get_all_context()
    assert context == {"request_id": "REQ123", "user_id": 42}
    
    # Add trace_id
    ContextManager.set_trace_id("TRACE456")
    
    context = ContextManager.get_all_context()
    assert context == {"request_id": "REQ123", "user_id": 42, "trace_id": "TRACE456"}
    
    ContextManager.clear_context()


def test_request_context_to_dict():
    """Test RequestContext to_dict method."""
    ctx = RequestContext(
        request_id="REQ123",
        user_id=42,
        trace_id="TRACE456",
        additional={"custom": "value"}
    )
    
    result = ctx.to_dict()
    assert result == {
        "request_id": "REQ123",
        "user_id": 42,
        "trace_id": "TRACE456",
        "custom": "value"
    }


def test_request_context_to_dict_with_none():
    """Test RequestContext to_dict excludes None values."""
    ctx = RequestContext(
        request_id="REQ123",
        user_id=None,
        trace_id=None
    )
    
    result = ctx.to_dict()
    assert result == {"request_id": "REQ123"}


def test_request_scope_basic():
    """Test basic request_scope functionality."""
    ContextManager.clear_context()
    
    with request_scope(request_id="REQ123", user_id=42) as ctx:
        # Context should be set
        assert ContextManager.get_request_id() == "REQ123"
        assert ContextManager.get_user_id() == 42
        assert ctx["request_id"] == "REQ123"
        assert ctx["user_id"] == 42
    
    # Context should be cleared after exit
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None


def test_request_scope_auto_generate():
    """Test request_scope auto-generates request_id."""
    ContextManager.clear_context()
    
    with request_scope() as ctx:
        # Should have auto-generated request_id
        request_id = ContextManager.get_request_id()
        assert request_id is not None
        assert len(request_id) > 0
        assert ctx["request_id"] == request_id
    
    # Context should be cleared after exit
    assert ContextManager.get_request_id() is None


def test_request_scope_restoration():
    """Test request_scope restores previous context."""
    ContextManager.clear_context()
    
    # Set initial context
    ContextManager.set_request_id("OUTER")
    ContextManager.set_user_id(1)
    
    with request_scope(request_id="INNER", user_id=2):
        # Inner context should be active
        assert ContextManager.get_request_id() == "INNER"
        assert ContextManager.get_user_id() == 2
    
    # Outer context should be restored
    assert ContextManager.get_request_id() == "OUTER"
    assert ContextManager.get_user_id() == 1
    
    ContextManager.clear_context()


@pytest.mark.asyncio
async def test_async_request_scope_basic():
    """Test basic async_request_scope functionality."""
    ContextManager.clear_context()
    
    async with async_request_scope(request_id="REQ123", user_id=42) as ctx:
        # Context should be set
        assert ContextManager.get_request_id() == "REQ123"
        assert ContextManager.get_user_id() == 42
        assert ctx["request_id"] == "REQ123"
        assert ctx["user_id"] == 42
    
    # Context should be cleared after exit
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None


@pytest.mark.asyncio
async def test_async_request_scope_isolation():
    """Test async_request_scope maintains isolation between tasks."""
    ContextManager.clear_context()
    
    results = []
    
    async def task(task_id: int):
        async with async_request_scope(request_id=f"REQ{task_id}", user_id=task_id):
            # Simulate some async work
            await asyncio.sleep(0.01)
            # Each task should see its own context
            request_id = ContextManager.get_request_id()
            user_id = ContextManager.get_user_id()
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
