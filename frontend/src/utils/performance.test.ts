/**
 * Performance Utilities Tests
 *
 * Tests for performance optimization utilities including debounce,
 * throttle, memoization, and lazy loading.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  debounce,
  throttle,
  memoize,
  createLazyLoader,
  measurePerformance,
} from './performance';

describe('Performance Utilities', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('debounce', () => {
    it('should delay function execution', () => {
      const fn = vi.fn();
      const debounced = debounce(fn, 100);

      debounced();
      expect(fn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(50);
      expect(fn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(50);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should reset timer on subsequent calls', () => {
      const fn = vi.fn();
      const debounced = debounce(fn, 100);

      debounced();
      vi.advanceTimersByTime(50);
      debounced();
      vi.advanceTimersByTime(50);
      expect(fn).not.toHaveBeenCalled();

      vi.advanceTimersByTime(50);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should pass arguments correctly', () => {
      const fn = vi.fn();
      const debounced = debounce(fn, 100);

      debounced('arg1', 'arg2');
      vi.advanceTimersByTime(100);

      expect(fn).toHaveBeenCalledWith('arg1', 'arg2');
    });
  });

  describe('throttle', () => {
    it('should limit function calls', () => {
      const fn = vi.fn();
      const throttled = throttle(fn, 100);

      throttled();
      expect(fn).toHaveBeenCalledTimes(1);

      throttled();
      expect(fn).toHaveBeenCalledTimes(1);

      vi.advanceTimersByTime(100);
      throttled();
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('should pass arguments correctly', () => {
      const fn = vi.fn();
      const throttled = throttle(fn, 100);

      throttled('arg1', 'arg2');
      expect(fn).toHaveBeenCalledWith('arg1', 'arg2');
    });
  });

  describe('memoize', () => {
    it('should cache function results', () => {
      const fn = vi.fn((a: number, b: number) => a + b);
      const memoized = memoize(fn);

      const result1 = memoized(1, 2);
      const result2 = memoized(1, 2);

      expect(result1).toBe(3);
      expect(result2).toBe(3);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should call function again for different arguments', () => {
      const fn = vi.fn((a: number, b: number) => a + b);
      const memoized = memoize(fn);

      memoized(1, 2);
      memoized(2, 3);

      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('should use custom key function', () => {
      const fn = vi.fn((obj: { id: number; name: string }) => obj.name);
      const memoized = memoize(fn, (obj) => obj.id.toString());

      const obj1 = { id: 1, name: 'Alice' };
      const obj2 = { id: 1, name: 'Bob' }; // Same id, different name

      const result1 = memoized(obj1);
      const result2 = memoized(obj2);

      expect(result1).toBe('Alice');
      expect(result2).toBe('Alice'); // Cached result
      expect(fn).toHaveBeenCalledTimes(1);
    });
  });

  describe('createLazyLoader', () => {
    it('should load module only once', async () => {
      vi.useRealTimers(); // Use real timers for async operations
      const importFn = vi.fn(async () => ({ value: 42 }));
      const loader = createLazyLoader(importFn);

      const result1 = await loader();
      const result2 = await loader();

      expect(result1).toEqual({ value: 42 });
      expect(result2).toEqual({ value: 42 });
      expect(importFn).toHaveBeenCalledTimes(1);
      vi.useFakeTimers(); // Restore fake timers
    });

    it('should handle concurrent loads', async () => {
      vi.useRealTimers(); // Use real timers for async operations
      const importFn = vi.fn(async () => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return { value: 42 };
      });
      const loader = createLazyLoader(importFn);

      const [result1, result2] = await Promise.all([loader(), loader()]);

      expect(result1).toEqual({ value: 42 });
      expect(result2).toEqual({ value: 42 });
      expect(importFn).toHaveBeenCalledTimes(1);
      vi.useFakeTimers(); // Restore fake timers
    });
  });

  describe('measurePerformance', () => {
    it('should measure sync function performance', async () => {
      vi.useRealTimers(); // Use real timers for performance measurement
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      const fn = () => 42;
      const result = await measurePerformance('test', fn);

      expect(result).toBe(42);
      
      if (import.meta.env.DEV) {
        expect(consoleSpy).toHaveBeenCalled();
      }
      
      consoleSpy.mockRestore();
      vi.useFakeTimers(); // Restore fake timers
    });

    it('should measure async function performance', async () => {
      vi.useRealTimers(); // Use real timers for performance measurement
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      const fn = async () => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return 42;
      };
      
      const result = await measurePerformance('test', fn);

      expect(result).toBe(42);
      
      if (import.meta.env.DEV) {
        expect(consoleSpy).toHaveBeenCalled();
      }
      
      consoleSpy.mockRestore();
      vi.useFakeTimers(); // Restore fake timers
    });

    it('should handle errors and still measure time', async () => {
      vi.useRealTimers(); // Use real timers for performance measurement
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      const fn = async () => {
        throw new Error('Test error');
      };

      await expect(measurePerformance('test', fn)).rejects.toThrow('Test error');
      expect(consoleErrorSpy).toHaveBeenCalled();
      
      consoleErrorSpy.mockRestore();
      vi.useFakeTimers(); // Restore fake timers
    });
  });
});
