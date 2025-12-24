/**
 * Window Resize Composable
 *
 * Provides debounced window resize handling to optimize performance
 * and prevent excessive re-renders during window resize events.
 *
 * Requirements: 7.1
 */

import { onBeforeUnmount, onMounted, ref } from 'vue';
import { debounce } from '@/utils/performance';

export interface WindowSize {
  width: number;
  height: number;
}

export interface UseWindowResizeOptions {
  /**
   * Debounce delay in milliseconds
   * @default 150
   */
  debounceDelay?: number;

  /**
   * Whether to initialize immediately on mount
   * @default true
   */
  immediate?: boolean;

  /**
   * Custom callback to execute on resize
   */
  onResize?: (size: WindowSize) => void;
}

/**
 * Composable for handling window resize events with debouncing
 *
 * @param options - Configuration options
 * @returns Window size reactive reference
 *
 * @example
 * ```vue
 * <script setup>
 * import { useWindowResize } from '@/composables/useWindowResize';
 *
 * const { width, height } = useWindowResize({
 *   debounceDelay: 200,
 *   onResize: (size) => {
 *     console.log('Window resized:', size);
 *   }
 * });
 * </script>
 * ```
 */
export function useWindowResize(options: UseWindowResizeOptions = {}) {
  const { debounceDelay = 150, immediate = true, onResize } = options;

  // Reactive window size
  const width = ref(window.innerWidth);
  const height = ref(window.innerHeight);

  /**
   * Update window size
   */
  function updateSize(): void {
    width.value = window.innerWidth;
    height.value = window.innerHeight;

    // Call custom callback if provided
    if (onResize) {
      onResize({ width: width.value, height: height.value });
    }
  }

  // Create debounced resize handler
  const debouncedResize = debounce(updateSize, debounceDelay);

  // Setup and cleanup
  onMounted(() => {
    if (immediate) {
      updateSize();
    }

    window.addEventListener('resize', debouncedResize);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('resize', debouncedResize);
  });

  return {
    width,
    height,
    updateSize,
  };
}

/**
 * Composable for responsive breakpoints
 *
 * @param options - Configuration options
 * @returns Reactive breakpoint flags
 *
 * @example
 * ```vue
 * <script setup>
 * import { useBreakpoints } from '@/composables/useWindowResize';
 *
 * const { isMobile, isTablet, isDesktop } = useBreakpoints();
 * </script>
 * ```
 */
export function useBreakpoints(options: UseWindowResizeOptions = {}) {
  const { width } = useWindowResize(options);

  // Breakpoint flags (matching Tailwind defaults)
  const isMobile = ref(width.value < 768);
  const isTablet = ref(width.value >= 768 && width.value < 1024);
  const isDesktop = ref(width.value >= 1024);

  // Update breakpoint flags when width changes
  function updateBreakpoints(): void {
    isMobile.value = width.value < 768;
    isTablet.value = width.value >= 768 && width.value < 1024;
    isDesktop.value = width.value >= 1024;
  }

  // Watch for width changes
  const { debounceDelay = 150 } = options;
  const debouncedUpdate = debounce(updateBreakpoints, debounceDelay);

  onMounted(() => {
    updateBreakpoints();
    window.addEventListener('resize', debouncedUpdate);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('resize', debouncedUpdate);
  });

  return {
    width,
    isMobile,
    isTablet,
    isDesktop,
  };
}
