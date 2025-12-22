"""Basic tests for decorator functionality."""

import asyncio

import pytest
from morado.common.logger.context import ContextManager
from morado.common.logger.decorators import (
    async_with_request_context,
    log_execution,
    with_request_context,
)


def test_with_request_context_sync():
    """Test with_request_context decorator with sync function."""

    @with_request_context()
    def process_request(request_id: str, user_id: int, data: str):
        # Context should be set
        assert ContextManager.get_request_id() == request_id
        assert ContextManager.get_user_id() == user_id
        return f"Processed: {data}"

    result = process_request(request_id="REQ123", user_id=42, data="test")
    assert result == "Processed: test"

    # Context should be cleared after function exits
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None


def test_with_request_context_auto_generate():
    """Test with_request_context auto-generates request_id."""

    @with_request_context()
    def process_request(user_id: int, data: str):
        # request_id should be auto-generated
        request_id = ContextManager.get_request_id()
        assert request_id is not None
        assert len(request_id) > 0
        assert ContextManager.get_user_id() == user_id
        return request_id

    result = process_request(user_id=42, data="test")
    assert result is not None

    # Context should be cleared after function exits
    assert ContextManager.get_request_id() is None


def test_with_request_context_no_auto_generate():
    """Test with_request_context with auto_generate=False."""

    @with_request_context(auto_generate=False)
    def process_request(user_id: int, data: str):
        # request_id should not be set
        request_id = ContextManager.get_request_id()
        return request_id

    result = process_request(user_id=42, data="test")
    assert result is None


@pytest.mark.asyncio
async def test_with_request_context_async():
    """Test with_request_context decorator with async function."""

    @with_request_context()
    async def process_async_request(request_id: str, user_id: int, data: str):
        # Context should be set
        assert ContextManager.get_request_id() == request_id
        assert ContextManager.get_user_id() == user_id
        await asyncio.sleep(0.01)  # Simulate async work
        return f"Processed async: {data}"

    result = await process_async_request(request_id="REQ456", user_id=99, data="async_test")
    assert result == "Processed async: async_test"

    # Context should be cleared after function exits
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None


@pytest.mark.asyncio
async def test_async_with_request_context():
    """Test async_with_request_context decorator."""

    @async_with_request_context()
    async def process_async_request(request_id: str, user_id: int, data: str):
        # Context should be set
        assert ContextManager.get_request_id() == request_id
        assert ContextManager.get_user_id() == user_id
        await asyncio.sleep(0.01)  # Simulate async work
        return f"Processed: {data}"

    result = await process_async_request(request_id="REQ789", user_id=123, data="test")
    assert result == "Processed: test"

    # Context should be cleared after function exits
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None


def test_async_with_request_context_on_sync_function_raises():
    """Test that async_with_request_context raises TypeError on sync function."""

    with pytest.raises(TypeError, match="can only be applied to async functions"):
        @async_with_request_context()
        def sync_function(request_id: str):
            return "sync"


def test_log_execution_sync():
    """Test log_execution decorator with sync function."""

    @log_execution(level="INFO", include_args=True, include_result=True)
    def calculate(x: int, y: int) -> int:
        return x + y

    result = calculate(5, 3)
    assert result == 8


@pytest.mark.asyncio
async def test_log_execution_async():
    """Test log_execution decorator with async function."""

    @log_execution(level="INFO", include_args=True, include_result=True)
    async def calculate_async(x: int, y: int) -> int:
        await asyncio.sleep(0.01)
        return x + y

    result = await calculate_async(10, 20)
    assert result == 30


def test_log_execution_with_exception():
    """Test log_execution decorator handles exceptions."""

    @log_execution(level="ERROR")
    def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        failing_function()


def test_with_request_context_custom_arg_names():
    """Test with_request_context with custom argument names."""

    @with_request_context(request_id_arg='req_id', user_id_arg='uid')
    def process_request(req_id: str, uid: int, data: str):
        assert ContextManager.get_request_id() == req_id
        assert ContextManager.get_user_id() == uid
        return data

    result = process_request(req_id="CUSTOM123", uid=999, data="custom")
    assert result == "custom"

    # Context should be cleared
    assert ContextManager.get_request_id() is None
    assert ContextManager.get_user_id() is None


def test_with_request_context_partial_context():
    """Test with_request_context with only some context values."""

    @with_request_context()
    def process_request(request_id: str, data: str):
        assert ContextManager.get_request_id() == request_id
        assert ContextManager.get_user_id() is None  # Not provided
        return data

    result = process_request(request_id="PARTIAL123", data="partial")
    assert result == "partial"
