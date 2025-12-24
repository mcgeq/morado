/**
 * ECharts Configuration
 *
 * Global ECharts setup and component registration for the dashboard.
 */

import { LineChart, PieChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components';
import { use } from 'echarts/core';

// Import ECharts components
import { CanvasRenderer } from 'echarts/renderers';
import type { App } from 'vue';
import ECharts from 'vue-echarts';

// Register ECharts components
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
]);

/**
 * Install ECharts plugin
 */
export function setupECharts(app: App): void {
  // Register v-chart component globally
  app.component('v-chart', ECharts);
}

export default ECharts;
