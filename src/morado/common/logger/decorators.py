"""Decorators for automatic context management and logging.

This module provides decorators that automatically apply request context
from function arguments and log function execution.
"""

import functools
import inspect
from typing import Callable, Any, Optional
from morado.common.logger.context import request_scope, async_request_scope


def with_request_context(
    request_id_arg: str = 'request_id',
    user_id_arg: str = 'user_id',
    trace_id_arg: str = 'trace_id',
    auto_generate: bool = True
) -> Callable:
    """Decorator to automatically apply request context from function arguments.
    
    Extracts context values from function arguments and creates a request scope
    for the duration of the function execution. Supports both sync and async functions.
    
    Args:
        request_id_arg: Name of the argument containing request_id
        user_id_arg: Name of the argument containing user_id
        trace_id_arg: Name of the argument containing trace_id
        auto_generate: Whether to auto-generate request_id if not provided
        
    Returns:
        Decorated function that runs within a request scope
        
    Example:
        @with_request_context()
        def process_request(request_id: str, user_id: int, data: dict):
            logger.info("Processing", data=data)
            # request_id and user_id are automatically in context
    
    Requirements: 7.1, 7.3
    """
    def decorator(func: Callable) -> Callable:
        # Check if function is async
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Extract context values from arguments
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Get context values from bound arguments
                request_id = bound_args.arguments.get(request_id_arg)
                user_id = bound_args.arguments.get(user_id_arg)
                trace_id = bound_args.arguments.get(trace_id_arg)
                
                # If auto_generate is False and request_id is None, don't create scope
                if not auto_generate and request_id is None:
                    return await func(*args, **kwargs)
                
                # Create async request scope with extracted context
                async with async_request_scope(
                    request_id=request_id,
                    user_id=user_id,
                    trace_id=trace_id
                ):
                    return await func(*args, **kwargs)
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Extract context values from arguments
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Get context values from bound arguments
                request_id = bound_args.arguments.get(request_id_arg)
                user_id = bound_args.arguments.get(user_id_arg)
                trace_id = bound_args.arguments.get(trace_id_arg)
                
                # If auto_generate is False and request_id is None, don't create scope
                if not auto_generate and request_id is None:
                    return func(*args, **kwargs)
                
                # Create request scope with extracted context
                with request_scope(
                    request_id=request_id,
                    user_id=user_id,
                    trace_id=trace_id
                ):
                    return func(*args, **kwargs)
            
            return sync_wrapper
    
    return decorator


def async_with_request_context(
    request_id_arg: str = 'request_id',
    user_id_arg: str = 'user_id',
    trace_id_arg: str = 'trace_id',
    auto_generate: bool = True
) -> Callable:
    """Async-specific decorator to apply request context from function arguments.
    
    This is an async-specific version of with_request_context that uses
    async_request_scope internally. Use this for async functions when you want
    to be explicit about async behavior.
    
    Args:
        request_id_arg: Name of the argument containing request_id
        user_id_arg: Name of the argument containing user_id
        trace_id_arg: Name of the argument containing trace_id
        auto_generate: Whether to auto-generate request_id if not provided
        
    Returns:
        Decorated async function that runs within an async request scope
        
    Example:
        @async_with_request_context()
        async def process_async_request(request_id: str, user_id: int, data: dict):
            logger.info("Processing async", data=data)
            # request_id and user_id are automatically in context
    
    Requirements: 10.1, 10.4
    """
    def decorator(func: Callable) -> Callable:
        if not inspect.iscoroutinefunction(func):
            raise TypeError(
                f"async_with_request_context can only be applied to async functions. "
                f"Function '{func.__name__}' is not async."
            )
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract context values from arguments
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Get context values from bound arguments
            request_id = bound_args.arguments.get(request_id_arg)
            user_id = bound_args.arguments.get(user_id_arg)
            trace_id = bound_args.arguments.get(trace_id_arg)
            
            # If auto_generate is False and request_id is None, don't create scope
            if not auto_generate and request_id is None:
                return await func(*args, **kwargs)
            
            # Create async request scope with extracted context
            async with async_request_scope(
                request_id=request_id,
                user_id=user_id,
                trace_id=trace_id
            ):
                return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def log_execution(
    level: str = "INFO",
    include_args: bool = False,
    include_result: bool = False
) -> Callable:
    """Decorator to log function execution entry, exit, and exceptions.
    
    Logs when a function is entered and exited, optionally including
    arguments and return values. Also logs exceptions if they occur.
    
    Note: This decorator requires a logger to be available. It will attempt
    to get a logger using structlog.get_logger() if available, otherwise
    it will use print statements as a fallback.
    
    Args:
        level: Log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        include_args: Whether to log function arguments
        include_result: Whether to log function return value
        
    Returns:
        Decorated function with execution logging
        
    Example:
        @log_execution(level="DEBUG", include_args=True, include_result=True)
        def calculate(x: int, y: int) -> int:
            return x + y
    
    Requirements: General logging utility
    """
    def decorator(func: Callable) -> Callable:
        # Check if function is async
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Try to get a logger
                try:
                    import structlog
                    logger = structlog.get_logger(func.__module__)
                    log_func = getattr(logger, level.lower(), logger.info)
                except (ImportError, AttributeError):
                    # Fallback to print if structlog not available
                    def log_func(event, **kw):
                        print(f"[{level}] {event} {kw}")
                
                # Build entry log data
                entry_data = {"function": func.__name__}
                if include_args:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    entry_data["args"] = dict(bound_args.arguments)
                
                # Log entry
                log_func("function_entry", **entry_data)
                
                try:
                    # Execute function
                    result = await func(*args, **kwargs)
                    
                    # Build exit log data
                    exit_data = {"function": func.__name__}
                    if include_result:
                        exit_data["result"] = result
                    
                    # Log exit
                    log_func("function_exit", **exit_data)
                    
                    return result
                    
                except Exception as e:
                    # Log exception
                    log_func(
                        "function_exception",
                        function=func.__name__,
                        exception_type=type(e).__name__,
                        exception_message=str(e)
                    )
                    raise
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Try to get a logger
                try:
                    import structlog
                    logger = structlog.get_logger(func.__module__)
                    log_func = getattr(logger, level.lower(), logger.info)
                except (ImportError, AttributeError):
                    # Fallback to print if structlog not available
                    def log_func(event, **kw):
                        print(f"[{level}] {event} {kw}")
                
                # Build entry log data
                entry_data = {"function": func.__name__}
                if include_args:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    entry_data["args"] = dict(bound_args.arguments)
                
                # Log entry
                log_func("function_entry", **entry_data)
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Build exit log data
                    exit_data = {"function": func.__name__}
                    if include_result:
                        exit_data["result"] = result
                    
                    # Log exit
                    log_func("function_exit", **exit_data)
                    
                    return result
                    
                except Exception as e:
                    # Log exception
                    log_func(
                        "function_exception",
                        function=func.__name__,
                        exception_type=type(e).__name__,
                        exception_message=str(e)
                    )
                    raise
            
            return sync_wrapper
    
    return decorator
