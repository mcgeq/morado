/**
 * ECharts Configuration
 *
 * Global ECharts setup and component registration for the dashboard.
 */

import type { App } from 'vue';
import ECharts from 'vue-echarts';
import { use } from 'echarts/core';

// Import ECharts components
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components';

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
