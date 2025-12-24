/**
 * Performance Utilities
 *
 * Provides utilities for optimizing application performance including
 * debouncing, throttling, and lazy loading helpers.
 *
 * Requirements: 7.1
 */

/**
 * Debounce function to limit how often a function can be called
 *
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 *
 * @example
 * ```typescript
 * const debouncedResize = debounce(() => {
 *   console.log('Window resized');
 * }, 300);
 *
 * window.addEventListener('resize', debouncedResize);
 * ```
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return function debounced(...args: Parameters<T>) {
    // Clear existing timeout
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
    }

    // Set new timeout
    timeoutId = setTimeout(() => {
      fn(...args);
      timeoutId = null;
    }, delay);
  };
}

/**
 * Throttle function to limit how often a function can be called
 *
 * @param fn - Function to throttle
 * @param limit - Time limit in milliseconds
 * @returns Throttled function
 *
 * @example
 * ```typescript
 * const throttledScroll = throttle(() => {
 *   console.log('Scrolled');
 * }, 100);
 *
 * window.addEventListener('scroll', throttledScroll);
 * ```
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number,
): (...args: Parameters<T>) => void {
  let inThrottle = false;

  return function throttled(...args: Parameters<T>) {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      const timeoutId: ReturnType<typeof setTimeout> = setTimeout(() => {
        inThrottle = false;
      }, limit);
      // Store timeout ID to prevent unused variable warning
      void timeoutId;
    }
  };
}

/**
 * Create a lazy loader for dynamic imports
 *
 * @param importFn - Function that returns a dynamic import promise
 * @returns Promise that resolves to the imported module
 *
 * @example
 * ```typescript
 * const loadECharts = createLazyLoader(() => import('echarts'));
 * const echarts = await loadECharts();
 * ```
 */
export function createLazyLoader<T>(importFn: () => Promise<T>): () => Promise<T> {
  let cached: T | null = null;
  let loading: Promise<T> | null = null;

  return async () => {
    // Return cached module if available
    if (cached !== null) {
      return cached;
    }

    // Return existing loading promise if in progress
    if (loading !== null) {
      return loading;
    }

    // Start loading
    loading = importFn().then(module => {
      cached = module;
      loading = null;
      return module;
    });

    return loading;
  };
}

/**
 * Request idle callback wrapper with fallback for browsers that don't support it
 *
 * @param callback - Function to call when idle
 * @param options - Options for requestIdleCallback
 * @returns Callback ID that can be used to cancel
 */
export function requestIdleCallback(
  callback: () => void,
  options?: { timeout?: number },
): number {
  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, options);
  }

  // Fallback to setTimeout
  return setTimeout(callback, 1) as unknown as number;
}

/**
 * Cancel idle callback
 *
 * @param id - Callback ID returned by requestIdleCallback
 */
export function cancelIdleCallback(id: number): void {
  if ('cancelIdleCallback' in window) {
    window.cancelIdleCallback(id);
  } else {
    clearTimeout(id);
  }
}

/**
 * Measure performance of a function
 *
 * @param name - Name of the measurement
 * @param fn - Function to measure
 * @returns Result of the function
 */
export async function measurePerformance<T>(
  name: string,
  fn: () => T | Promise<T>,
): Promise<T> {
  const start = performance.now();

  try {
    const result = await fn();
    const duration = performance.now() - start;

    if (import.meta.env.DEV) {
      console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
    }

    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[Performance] ${name} failed after ${duration.toFixed(2)}ms`, error);
    throw error;
  }
}

/**
 * Create a memoized version of a function
 *
 * @param fn - Function to memoize
 * @param keyFn - Optional function to generate cache key from arguments
 * @returns Memoized function
 *
 * @example
 * ```typescript
 * const expensiveCalculation = memoize((a: number, b: number) => {
 *   return a * b;
 * });
 * ```
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyFn?: (...args: Parameters<T>) => string,
): T {
  const cache = new Map<string, ReturnType<T>>();

  return ((...args: Parameters<T>) => {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

/**
 * Clear memoization cache for a memoized function
 * Note: This requires storing the cache externally
 */
export function createMemoizedWithClear<T extends (...args: any[]) => any>(
  fn: T,
  keyFn?: (...args: Parameters<T>) => string,
): { fn: T; clear: () => void } {
  const cache = new Map<string, ReturnType<T>>();

  const memoizedFn = ((...args: Parameters<T>) => {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key);
    }

    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;

  return {
    fn: memoizedFn,
    clear: () => cache.clear(),
  };
}
