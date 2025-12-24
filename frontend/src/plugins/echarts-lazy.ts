/**
 * Lazy-loaded ECharts Configuration
 *
 * Provides lazy loading for ECharts to improve initial page load performance.
 * ECharts components are only loaded when needed (when charts are rendered).
 *
 * Requirements: 7.1
 */

import type { App } from 'vue';
import { createLazyLoader } from '@/utils/performance';

/**
 * Lazy loader for ECharts core
 */
const loadEChartsCore = createLazyLoader(async () => {
  const { use } = await import('echarts/core');
  const { CanvasRenderer } = await import('echarts/renderers');
  return { use, CanvasRenderer };
});

/**
 * Lazy loader for ECharts components
 */
const loadEChartsComponents = createLazyLoader(async () => {
  const [
    { GridComponent, LegendComponent, TitleComponent, TooltipComponent },
    { LineChart, PieChart },
  ] = await Promise.all([
    import('echarts/components'),
    import('echarts/charts'),
  ]);

  return {
    GridComponent,
    LegendComponent,
    TitleComponent,
    TooltipComponent,
    LineChart,
    PieChart,
  };
});

/**
 * Lazy loader for vue-echarts component
 */
const loadVueECharts = createLazyLoader(async () => {
  const module = await import('vue-echarts');
  return module.default;
});

/**
 * Flag to track if ECharts has been initialized
 */
let isInitialized = false;

/**
 * Initialize ECharts with all required components
 * This is called automatically when the first chart is rendered
 */
export async function initializeECharts(): Promise<void> {
  if (isInitialized) {
    return;
  }

  try {
    // Load ECharts core and components in parallel
    const [{ use, CanvasRenderer }, components] = await Promise.all([
      loadEChartsCore(),
      loadEChartsComponents(),
    ]);

    // Register all components
    use([
      CanvasRenderer,
      components.PieChart,
      components.LineChart,
      components.TitleComponent,
      components.TooltipComponent,
      components.LegendComponent,
      components.GridComponent,
    ]);

    isInitialized = true;

    if (import.meta.env.DEV) {
      console.log('[ECharts] Lazy initialization complete');
    }
  } catch (error) {
    console.error('[ECharts] Failed to initialize:', error);
    throw error;
  }
}

/**
 * Get the vue-echarts component (lazy loaded)
 * This ensures ECharts is initialized before returning the component
 */
export async function getVueEChartsComponent() {
  // Initialize ECharts if not already done
  await initializeECharts();

  // Load and return the vue-echarts component
  return loadVueECharts();
}

/**
 * Setup ECharts plugin with lazy loading
 * This registers a stub component that loads the real component on demand
 */
export function setupEChartsLazy(app: App): void {
  // Register a lazy-loading wrapper component
  app.component('v-chart', {
    name: 'VChartLazy',
    async setup() {
      // This will be called when the component is first used
      const VChart = await getVueEChartsComponent();
      return { VChart };
    },
    template: '<component :is="VChart" v-bind="$attrs" />',
  });

  if (import.meta.env.DEV) {
    console.log('[ECharts] Lazy loading plugin registered');
  }
}

/**
 * Preload ECharts during idle time
 * This can be called to preload ECharts without blocking the main thread
 */
export function preloadECharts(): void {
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(
      () => {
        initializeECharts().catch(error => {
          console.error('[ECharts] Preload failed:', error);
        });
      },
      { timeout: 2000 },
    );
  } else {
    // Fallback: load after a short delay
    setTimeout(() => {
      initializeECharts().catch(error => {
        console.error('[ECharts] Preload failed:', error);
      });
    }, 1000);
  }
}
