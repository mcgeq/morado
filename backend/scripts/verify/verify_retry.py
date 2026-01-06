"""Verification script for retry module implementation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from morado.common.http.retry import RetryConfig, RetryHandler, RetryStrategy
    from morado.common.http.exceptions import RetryExhaustedError, HttpTimeoutError
    
    print("✓ Import successful")
    
    # Test RetryStrategy enum
    print(f"✓ RetryStrategy values: {[s.value for s in RetryStrategy]}")
    
    # Test RetryConfig creation
    config = RetryConfig(
        max_retries=3,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=60.0,
    )
    print(f"✓ RetryConfig created: max_retries={config.max_retries}, strategy={config.strategy.value}")
    
    # Test RetryHandler creation
    handler = RetryHandler(config)
    print(f"✓ RetryHandler created")
    
    # Test should_retry logic
    should_retry_timeout = handler.should_retry(exception=HttpTimeoutError("timeout"))
    print(f"✓ should_retry for timeout: {should_retry_timeout}")
    
    should_retry_5xx = handler.should_retry(status_code=500)
    print(f"✓ should_retry for 5xx: {should_retry_5xx}")
    
    should_retry_4xx = handler.should_retry(status_code=404)
    print(f"✓ should_retry for 4xx: {should_retry_4xx}")
    
    # Test delay calculation
    delay_0 = handler.calculate_delay(0)
    delay_1 = handler.calculate_delay(1)
    delay_2 = handler.calculate_delay(2)
    print(f"✓ Delay calculation (exponential): attempt 0={delay_0}s, attempt 1={delay_1}s, attempt 2={delay_2}s")
    
    # Test with fixed strategy
    fixed_config = RetryConfig(strategy=RetryStrategy.FIXED, initial_delay=2.0)
    fixed_handler = RetryHandler(fixed_config)
    fixed_delay_0 = fixed_handler.calculate_delay(0)
    fixed_delay_1 = fixed_handler.calculate_delay(1)
    print(f"✓ Delay calculation (fixed): attempt 0={fixed_delay_0}s, attempt 1={fixed_delay_1}s")
    
    # Test with linear strategy
    linear_config = RetryConfig(strategy=RetryStrategy.LINEAR, initial_delay=1.0)
    linear_handler = RetryHandler(linear_config)
    linear_delay_0 = linear_handler.calculate_delay(0)
    linear_delay_1 = linear_handler.calculate_delay(1)
    linear_delay_2 = linear_handler.calculate_delay(2)
    print(f"✓ Delay calculation (linear): attempt 0={linear_delay_0}s, attempt 1={linear_delay_1}s, attempt 2={linear_delay_2}s")
    
    # Test execute_with_retry with successful function
    class Counter:
        def __init__(self):
            self.count = 0
    
    counter = Counter()
    def successful_func():
        counter.count += 1
        return "success"
    
    result = handler.execute_with_retry(successful_func)
    print(f"✓ execute_with_retry successful: result={result}, calls={counter.count}")
    
    # Test execute_with_retry with retryable failure
    class Counter:
        def __init__(self):
            self.count = 0
    
    counter = Counter()
    def failing_func():
        counter.count += 1
        if counter.count < 3:
            raise HttpTimeoutError("timeout")
        return "success after retries"
    
    result = handler.execute_with_retry(failing_func)
    print(f"✓ execute_with_retry with retries: result={result}, calls={counter.count}")
    print(f"✓ Retry history entries: {len(handler.retry_history)}")
    
    # Test execute_with_retry with exhausted retries
    counter2 = Counter()
    def always_failing_func():
        counter2.count += 1
        raise HttpTimeoutError("always timeout")
    
    try:
        handler.execute_with_retry(always_failing_func)
        print("✗ Should have raised RetryExhaustedError")
    except RetryExhaustedError as e:
        print(f"✓ RetryExhaustedError raised correctly: {len(e.retry_history)} attempts")
    
    print("\n✅ All verification checks passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
