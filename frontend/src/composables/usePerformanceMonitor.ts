/**
 * Performance Monitor Composable
 *
 * Provides utilities for monitoring component performance and load times.
 *
 * Requirements: 7.1
 */

import { onMounted, onUnmounted, ref } from 'vue';

export interface PerformanceMetrics {
  mountTime: number;
  renderTime: number;
  updateCount: number;
}

/**
 * Composable for monitoring component performance
 *
 * @param componentName - Name of the component being monitored
 * @returns Performance metrics and utilities
 *
 * @example
 * ```vue
 * <script setup>
 * import { usePerformanceMonitor } from '@/composables/usePerformanceMonitor';
 *
 * const { metrics, logMetrics } = usePerformanceMonitor('MyComponent');
 * </script>
 * ```
 */
export function usePerformanceMonitor(componentName: string) {
  const mountStartTime = ref(0);
  const mountTime = ref(0);
  const renderTime = ref(0);
  const updateCount = ref(0);

  // Record mount start time
  mountStartTime.value = performance.now();

  onMounted(() => {
    // Calculate mount time
    mountTime.value = performance.now() - mountStartTime.value;

    if (import.meta.env.DEV) {
      console.log(`[Performance] ${componentName} mounted in ${mountTime.value.toFixed(2)}ms`);
    }

    // Use Performance Observer to track render time
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.entryType === 'measure' && entry.name.includes(componentName)) {
              renderTime.value = entry.duration;
              updateCount.value++;
            }
          }
        });

        observer.observe({ entryTypes: ['measure'] });

        // Cleanup observer on unmount
        onUnmounted(() => {
          observer.disconnect();
        });
      } catch (error) {
        // PerformanceObserver not supported or error occurred
        if (import.meta.env.DEV) {
          console.warn(`[Performance] Could not observe ${componentName}:`, error);
        }
      }
    }
  });

  /**
   * Log current performance metrics
   */
  function logMetrics(): void {
    if (import.meta.env.DEV) {
      console.log(`[Performance] ${componentName} metrics:`, {
        mountTime: `${mountTime.value.toFixed(2)}ms`,
        renderTime: `${renderTime.value.toFixed(2)}ms`,
        updateCount: updateCount.value,
      });
    }
  }

  /**
   * Mark a performance measurement
   */
  function mark(name: string): void {
    if ('performance' in window && 'mark' in performance) {
      performance.mark(`${componentName}-${name}`);
    }
  }

  /**
   * Measure time between two marks
   */
  function measure(name: string, startMark: string, endMark: string): void {
    if ('performance' in window && 'measure' in performance) {
      try {
        performance.measure(
          `${componentName}-${name}`,
          `${componentName}-${startMark}`,
          `${componentName}-${endMark}`,
        );
      } catch (error) {
        // Marks might not exist
        if (import.meta.env.DEV) {
          console.warn(`[Performance] Could not measure ${name}:`, error);
        }
      }
    }
  }

  return {
    mountTime,
    renderTime,
    updateCount,
    logMetrics,
    mark,
    measure,
  };
}

/**
 * Measure the time taken by an async operation
 *
 * @param name - Name of the operation
 * @param operation - Async operation to measure
 * @returns Result of the operation
 */
export async function measureAsync<T>(
  name: string,
  operation: () => Promise<T>,
): Promise<T> {
  const start = performance.now();

  try {
    const result = await operation();
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
 * Get performance navigation timing metrics
 */
export function getNavigationMetrics() {
  if (!('performance' in window) || !('getEntriesByType' in performance)) {
    return null;
  }

  const [navigation] = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];

  if (!navigation) {
    return null;
  }

  return {
    // DNS lookup time
    dnsTime: navigation.domainLookupEnd - navigation.domainLookupStart,
    // TCP connection time
    tcpTime: navigation.connectEnd - navigation.connectStart,
    // Request time
    requestTime: navigation.responseStart - navigation.requestStart,
    // Response time
    responseTime: navigation.responseEnd - navigation.responseStart,
    // DOM processing time
    domProcessingTime: navigation.domComplete - navigation.domInteractive,
    // Total load time
    loadTime: navigation.loadEventEnd - navigation.fetchStart,
    // DOM content loaded time
    domContentLoadedTime: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
  };
}

/**
 * Log navigation metrics to console (development only)
 */
export function logNavigationMetrics(): void {
  if (!import.meta.env.DEV) {
    return;
  }

  const metrics = getNavigationMetrics();

  if (metrics) {
    console.log('[Performance] Navigation metrics:', {
      'DNS Lookup': `${metrics.dnsTime.toFixed(2)}ms`,
      'TCP Connection': `${metrics.tcpTime.toFixed(2)}ms`,
      'Request': `${metrics.requestTime.toFixed(2)}ms`,
      'Response': `${metrics.responseTime.toFixed(2)}ms`,
      'DOM Processing': `${metrics.domProcessingTime.toFixed(2)}ms`,
      'DOM Content Loaded': `${metrics.domContentLoadedTime.toFixed(2)}ms`,
      'Total Load': `${metrics.loadTime.toFixed(2)}ms`,
    });
  }
}
