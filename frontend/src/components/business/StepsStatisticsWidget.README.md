# StepsStatisticsWidget Component

## Overview

The `StepsStatisticsWidget` component displays test step execution statistics in a visually appealing donut chart with a detailed legend. It provides an at-a-glance view of test step distribution across three categories: completed steps, SQL execution failures, and API requests.

## Features

✅ **Donut Chart Visualization**: Uses ECharts to render an interactive donut chart
✅ **Percentage Calculations**: Automatically calculates and displays percentages for each category
✅ **Color-Coded Categories**: Uses distinct colors for easy identification
✅ **Legend with Counts**: Displays detailed counts and percentages for each category
✅ **Empty State Handling**: Shows a user-friendly message when no data is available
✅ **Responsive Design**: Adapts to different screen sizes
✅ **Customizable Title**: Accepts an optional title prop

## Requirements Validation

### Requirement 3.1 ✅
**WHEN the dashboard loads THEN the system SHALL display a "Steps" statistics widget showing test step distribution**

- Component renders a statistics widget with title "Steps统计"
- Displays test step distribution data

### Requirement 3.2 ✅
**WHEN displaying step statistics THEN the system SHALL categorize steps into "已完成" (Completed), "SQL执行失败" (SQL Execution Failed), and "API请求" (API Request)**

- Component accepts `statistics` prop with three fields: `completed`, `sqlFailed`, `apiRequest`
- Displays all three categories in the legend

### Requirement 3.3 ✅
**WHEN rendering the steps widget THEN the system SHALL use a donut chart visualization with distinct colors for each category**

- Integrates `DonutChart` component
- Uses distinct colors:
  - Completed: Blue (#3B82F6)
  - SQL Execution Failed: Orange (#F59E0B)
  - API Request: Purple (#8B5CF6)

### Requirement 3.4 ✅
**WHEN displaying percentages THEN the system SHALL round to whole numbers without decimal places**

- Percentage calculation uses `Math.round()` to ensure whole numbers
- Displays percentages in format "XX%"

### Requirement 3.5 ✅
**WHEN the total step count is zero THEN the system SHALL display "暂无数据" (No Data Available)**

- Implements empty state with `data-testid="empty-state"`
- Shows "暂无数据" message with icon when total is 0

## Props

```typescript
interface StepsStatisticsWidgetProps {
  statistics: StepStatistics;
  title?: string;
}

interface StepStatistics {
  completed: number;
  sqlFailed: number;
  apiRequest: number;
}
```

### Props Details

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `statistics` | `StepStatistics` | Yes | - | Object containing counts for each step category |
| `title` | `string` | No | `'Steps统计'` | Custom title for the widget |

## Usage

### Basic Usage

```vue
<template>
  <StepsStatisticsWidget :statistics="stepStats" />
</template>

<script setup lang="ts">
import { StepsStatisticsWidget } from '@/components/business';

const stepStats = {
  completed: 150,
  sqlFailed: 30,
  apiRequest: 70,
};
</script>
```

### With Custom Title

```vue
<template>
  <StepsStatisticsWidget
    :statistics="stepStats"
    title="测试步骤统计"
  />
</template>
```

### With Dashboard Store

```vue
<template>
  <StepsStatisticsWidget
    v-if="dashboardStore.statistics"
    :statistics="dashboardStore.statistics.steps"
  />
</template>

<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';
import { StepsStatisticsWidget } from '@/components/business';

const dashboardStore = useDashboardStore();
</script>
```

## Examples

See `StepsStatisticsWidget.example.vue` for interactive examples including:

1. **Normal Data**: Typical distribution of steps
2. **Mostly Completed**: High success rate scenario
3. **High Failure Rate**: Scenario with many failures
4. **Empty State**: Zero data handling
5. **Equal Distribution**: Balanced distribution
6. **Large Numbers**: Handling of large datasets
7. **Interactive Example**: Live adjustment of values

## Testing

The component includes comprehensive unit tests covering:

- ✅ Rendering without errors
- ✅ Title display (default and custom)
- ✅ Percentage calculations (exact and rounded)
- ✅ Empty state handling
- ✅ Chart visibility based on data
- ✅ Legend items display
- ✅ Count display for each category
- ✅ Total count display
- ✅ Large number handling
- ✅ Uneven distribution calculations
- ✅ Styling classes
- ✅ Legend color display

Run tests with:
```bash
npm test -- StepsStatisticsWidget.test.ts --run
```

## Component Structure

```
StepsStatisticsWidget.vue
├── Widget Header
│   └── Title (default or custom)
├── Empty State (conditional)
│   ├── Icon
│   └── "暂无数据" message
└── Chart Container (conditional)
    ├── DonutChart Component
    │   └── Three datasets with colors
    └── Legend Container
        ├── Legend Items (3)
        │   ├── Color indicator
        │   ├── Label
        │   ├── Count
        │   └── Percentage
        └── Total Section
            └── Total count
```

## Styling

The component uses Tailwind CSS for styling with:

- White background with rounded corners
- Shadow for depth
- Responsive padding
- Flexbox layout for chart and legend
- Consistent spacing throughout

### Key Classes

- `.steps-statistics-widget`: Main container
- `.empty-state`: Empty state display
- `.chart-container`: Chart and legend wrapper
- `.legend-container`: Legend items container
- `.legend-item`: Individual legend entry

## Color Scheme

The component uses the following color scheme as specified in the design document:

| Category | Color | Hex Code |
|----------|-------|----------|
| Completed | Blue | #3B82F6 |
| SQL Failed | Orange | #F59E0B |
| API Request | Purple | #8B5CF6 |

## Accessibility

- Semantic HTML structure
- Clear visual hierarchy
- Color indicators with text labels
- Empty state with descriptive message
- Proper contrast ratios

## Performance

- Computed properties for efficient reactivity
- Minimal re-renders
- Lightweight calculations
- Lazy chart rendering (only when data exists)

## Browser Support

Supports all modern browsers that support:
- Vue 3
- ECharts
- CSS Grid and Flexbox

## Related Components

- `DonutChart.vue`: Base chart component
- `UserProfileCard.vue`: Similar widget pattern
- `QuickActionsPanel.vue`: Dashboard widget example

## Integration with Dashboard

This component is designed to be used in the Home dashboard:

```vue
<template>
  <div class="dashboard">
    <StepsStatisticsWidget
      v-if="statistics?.steps"
      :statistics="statistics.steps"
    />
  </div>
</template>
```

## Future Enhancements

Potential improvements for future iterations:

- Click-through to detailed step view
- Time range filtering
- Export data functionality
- Animation on data updates
- Drill-down capabilities
- Comparison with previous periods

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ Basic donut chart visualization
- ✅ Three-category statistics display
- ✅ Percentage calculations
- ✅ Empty state handling
- ✅ Legend with counts
- ✅ Custom title support
- ✅ Comprehensive test coverage
