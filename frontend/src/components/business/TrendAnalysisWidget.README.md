# TrendAnalysisWidget Component

## Overview

The `TrendAnalysisWidget` component displays trend analysis data over time using an area chart visualization. It shows four different component types (scheduled, test case, actual, and detection) with distinct colors and supports interactive legends and tooltips.

## Features

- **Area Chart Visualization**: Multi-series area chart showing trends over time
- **Four Component Types**: Displays scheduled, test case, actual, and detection components
- **Color-Coded Series**: Each component type has a distinct color for easy identification
- **Interactive Legend**: Toggle series visibility and view detailed information
- **Tooltip on Hover**: Shows detailed values when hovering over data points
- **Date Formatting**: Displays dates in YYYY-MM-DD format
- **Zero Value Handling**: Properly handles zero values without creating gaps in the chart
- **Empty State**: Shows a friendly message when no data is available
- **Responsive Design**: Adapts to different screen sizes
- **Date Range Display**: Optional display of the data's date range

## Props

### `data` (required)

- **Type**: `TrendDataPoint[]`
- **Description**: Array of trend data points containing date and component counts
- **Structure**:
  ```typescript
  interface TrendDataPoint {
    date: string; // YYYY-MM-DD format
    scheduledComponents: number;
    testCaseComponents: number;
    actualComponents: number;
    detectionComponents: number;
  }
  ```

### `title` (optional)

- **Type**: `string`
- **Default**: `'定时参数测试统计'`
- **Description**: The title displayed at the top of the widget

### `dateRange` (optional)

- **Type**: `{ start: string; end: string }`
- **Description**: Optional date range to display below the title
- **Format**: Both `start` and `end` should be in YYYY-MM-DD format

## Usage

### Basic Usage

```vue
<template>
  <TrendAnalysisWidget :data="trendData" />
</template>

<script setup lang="ts">
import TrendAnalysisWidget from '@/components/business/TrendAnalysisWidget.vue';
import type { TrendDataPoint } from '@/types/dashboard';

const trendData: TrendDataPoint[] = [
  {
    date: '2024-01-01',
    scheduledComponents: 10,
    testCaseComponents: 20,
    actualComponents: 15,
    detectionComponents: 5,
  },
  {
    date: '2024-01-02',
    scheduledComponents: 12,
    testCaseComponents: 22,
    actualComponents: 18,
    detectionComponents: 7,
  },
  // ... more data points
];
</script>
```

### With Custom Title

```vue
<TrendAnalysisWidget
  :data="trendData"
  title="组件趋势分析"
/>
```

### With Date Range

```vue
<TrendAnalysisWidget
  :data="trendData"
  :date-range="{ start: '2024-01-01', end: '2024-01-31' }"
/>
```

### With Dashboard Store

```vue
<template>
  <TrendAnalysisWidget
    v-if="dashboardStore.statistics"
    :data="dashboardStore.statistics.trends"
  />
</template>

<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';
import TrendAnalysisWidget from '@/components/business/TrendAnalysisWidget.vue';

const dashboardStore = useDashboardStore();
</script>
```

## Color Scheme

The component uses the following color scheme as defined in the design document:

- **Scheduled Components** (定时元件): Blue (#3B82F6)
- **Test Case Components** (用例元件): Green (#10B981)
- **Actual Components** (实际元件): Orange (#F59E0B)
- **Detection Components** (检测元件): Red (#EF4444)

## Empty State

When the `data` prop is an empty array, the component displays an empty state with:
- A chart icon
- The message "暂无趋势数据" (No trend data available)

## Zero Value Handling

The component properly handles zero values in the data:
- Zero values are displayed as points on the chart (not gaps)
- The chart line continues through zero values
- Tooltips show "0" for zero values

## Chart Features

### Interactive Legend

- Click on legend items to show/hide series
- Legend displays all four component types
- Located at the top of the chart

### Tooltip

- Displays on hover over data points
- Shows the date and values for all series at that point
- Formatted with series name and value

### Axes

- **X-Axis**: Displays dates in YYYY-MM-DD format
- **Y-Axis**: Displays count values with label "数量" (Quantity)
- **Grid**: Dashed grid lines for easier value reading

## Responsive Behavior

The component is fully responsive:
- Minimum height: 400px for the widget container
- Chart height: 350px
- Adapts to container width
- Maintains readability on smaller screens

## Requirements Validation

This component validates the following requirements:

- **5.1**: Displays "定时参数测试统计" chart on dashboard load
- **5.2**: Uses area chart with time on x-axis and count on y-axis
- **5.3**: Shows multiple series (scheduled, test case, actual, detection components)
- **5.4**: Uses distinct colors for each series with legend
- **5.5**: Formats dates in YYYY-MM-DD format
- **5.6**: Displays tooltip with detailed values on hover
- **5.7**: Displays zero values rather than gaps in the chart

## Testing

The component includes comprehensive unit tests covering:
- Rendering with default and custom titles
- Date range display
- Empty state handling
- Chart rendering with data
- Data transformation to chart format
- Color scheme validation
- Zero value handling
- Date format validation
- Axis label configuration

Run tests with:
```bash
npm test -- TrendAnalysisWidget.test.ts
```

## Dependencies

- **Vue 3**: Core framework
- **ECharts**: Chart rendering (via AreaChart component)
- **TypeScript**: Type safety

## Related Components

- `AreaChart`: The underlying chart component used for visualization
- `StepsStatisticsWidget`: Similar widget using DonutChart
- `ApiUsageWidget`: Another dashboard widget component

## Notes

- The component expects dates in YYYY-MM-DD format
- All numeric values should be non-negative integers
- The component handles empty data gracefully
- Zero values are preserved in the visualization (no gaps)
- The chart is interactive with hover tooltips and legend toggles
