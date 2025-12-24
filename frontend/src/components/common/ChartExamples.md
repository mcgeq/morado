# Chart Components Usage Examples

## DonutChart Component

The DonutChart component is a reusable donut chart built with ECharts for displaying statistical data.

### Basic Usage

```vue
<template>
  <DonutChart
    :datasets="chartData"
    size="md"
    :showLegend="true"
  />
</template>

<script setup lang="ts">
import { DonutChart } from '@/components/common';
import type { ChartDataset } from '@/types/dashboard';

const chartData: ChartDataset[] = [
  { label: 'Completed', value: 50, color: '#3B82F6' },
  { label: 'SQL Failed', value: 30, color: '#F59E0B' },
  { label: 'API Request', value: 20, color: '#8B5CF6' },
];
</script>
```

### With Center Text

```vue
<template>
  <DonutChart
    :datasets="chartData"
    centerText="Total: 100"
    size="lg"
    :showLegend="false"
  />
</template>
```

### Props

- `datasets` (required): Array of ChartDataset objects with label, value, and color
- `centerText` (optional): Text to display in the center of the donut
- `showLegend` (optional, default: true): Whether to show the legend
- `size` (optional, default: 'md'): Size variant - 'sm', 'md', or 'lg'

## AreaChart Component

The AreaChart component is a reusable area chart built with ECharts for displaying trend data over time.

### Basic Usage

```vue
<template>
  <AreaChart
    :series="chartSeries"
    :labels="dateLabels"
    xAxisLabel="Date"
    yAxisLabel="Count"
    :showGrid="true"
  />
</template>

<script setup lang="ts">
import { AreaChart } from '@/components/common';
import type { AreaChartSeries } from '@/types/dashboard';

const chartSeries: AreaChartSeries[] = [
  {
    name: 'Scheduled Components',
    data: [10, 20, 30, 40, 50],
    color: '#3B82F6',
  },
  {
    name: 'Test Case Components',
    data: [15, 25, 35, 45, 55],
    color: '#10B981',
  },
];

const dateLabels = [
  '2024-01-01',
  '2024-01-02',
  '2024-01-03',
  '2024-01-04',
  '2024-01-05',
];
</script>
```

### Multiple Series

```vue
<template>
  <AreaChart
    :series="multiSeries"
    :labels="labels"
    :showGrid="false"
  />
</template>

<script setup lang="ts">
const multiSeries: AreaChartSeries[] = [
  { name: 'Scheduled', data: [10, 20, 30], color: '#3B82F6' },
  { name: 'Test Case', data: [15, 25, 35], color: '#10B981' },
  { name: 'Actual', data: [20, 30, 40], color: '#F59E0B' },
  { name: 'Detection', data: [25, 35, 45], color: '#EF4444' },
];

const labels = ['Day 1', 'Day 2', 'Day 3'];
</script>
```

### Props

- `series` (required): Array of AreaChartSeries objects with name, data array, and color
- `labels` (required): Array of strings for x-axis labels
- `yAxisLabel` (optional): Label for the y-axis
- `xAxisLabel` (optional): Label for the x-axis
- `showGrid` (optional, default: true): Whether to show the grid lines

## Features

Both components include:

- **Responsive Design**: Charts automatically resize to fit their container
- **Interactive Tooltips**: Hover over data points to see detailed information
- **Smooth Animations**: Smooth transitions when data changes
- **Customizable Colors**: Each data series can have its own color
- **TypeScript Support**: Full type safety with TypeScript interfaces
- **ECharts Integration**: Built on top of the powerful ECharts library

## Color Palette

Recommended colors from the design system:

- Blue: `#3B82F6` - Primary actions, completed items
- Green: `#10B981` - Success, passed tests
- Orange: `#F59E0B` - Warnings, pending items
- Red: `#EF4444` - Errors, failed items
- Purple: `#8B5CF6` - Special categories

## Testing

Both components are fully tested with:

- Unit tests for rendering and props
- Property-based tests for data validation
- Integration tests with ECharts

See the test files for examples:
- `DonutChart.test.ts`
- `AreaChart.test.ts`
