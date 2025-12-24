# ApiUsageWidget Component

## Overview

The `ApiUsageWidget` component displays API and test case usage statistics in a two-column layout. It shows completion percentages and detailed metrics for both API completion and test case completion, with color-coded indicators to visualize performance.

## Features

- **Two-Column Layout**: Displays API completion and test case completion side by side
- **Large Percentage Display**: Shows completion rates prominently in large, colored text
- **Detailed Metrics**: Lists specific counts for total, completed, and tagged items
- **Color-Coded Indicators**: Visual indicators (green/yellow/red) based on performance ratios
- **Responsive Design**: Adapts to different screen sizes
- **Consistent Styling**: Follows the dashboard design system

## Props

### `data` (required)

Type: `ApiUsageData`

The API usage data to display, containing both API completion and test case completion information.

```typescript
interface ApiUsageData {
  apiCompletion: {
    percentage: number;        // API completion percentage (0-100)
    totalApis: number;         // Total number of APIs
    completedApis: number;     // Number of completed APIs
    taggedApis: number;        // Number of tagged APIs
  };
  testCaseCompletion: {
    percentage: number;        // Test case completion percentage (0-100)
    totalTestCases: number;    // Total number of test cases
    passedTestCases: number;   // Number of passed test cases
    taggedTestCases: number;   // Number of tagged test cases
  };
}
```

### `title` (optional)

Type: `string`  
Default: `'API使用情况'`

The title displayed at the top of the widget.

## Usage

### Basic Usage

```vue
<template>
  <ApiUsageWidget :data="apiUsageData" />
</template>

<script setup lang="ts">
import { ApiUsageWidget } from '@/components/business';
import type { ApiUsageData } from '@/types/dashboard';

const apiUsageData: ApiUsageData = {
  apiCompletion: {
    percentage: 75,
    totalApis: 100,
    completedApis: 75,
    taggedApis: 60,
  },
  testCaseCompletion: {
    percentage: 80,
    totalTestCases: 200,
    passedTestCases: 160,
    taggedTestCases: 150,
  },
};
</script>
```

### With Custom Title

```vue
<template>
  <ApiUsageWidget :data="apiUsageData" title="API统计概览" />
</template>
```

### With Dashboard Store

```vue
<template>
  <ApiUsageWidget 
    v-if="dashboardStore.statistics?.apiUsage"
    :data="dashboardStore.statistics.apiUsage" 
  />
</template>

<script setup lang="ts">
import { ApiUsageWidget } from '@/components/business';
import { useDashboardStore } from '@/stores/dashboard';

const dashboardStore = useDashboardStore();
</script>
```

## Color Indicators

The component uses color-coded indicators to show performance at a glance:

- **Green** (🟢): Good performance (≥70% ratio)
- **Yellow** (🟡): Moderate performance (40-69% ratio)
- **Red** (🔴): Poor performance (<40% ratio)
- **Gray** (⚪): No data (total is 0)

The indicator color is calculated based on the ratio of the metric value to the total value.

## Layout

The widget uses a two-column grid layout:

```
┌─────────────────────────────────────────────────┐
│ API使用情况                                      │
├─────────────────────┬───────────────────────────┤
│ API完成度           │ 用例完成度                 │
│ 75%                 │ 80%                       │
│                     │                           │
│ 用例管理API总数: 100│ 用例总数: 200             │
│ API总数: 75         │ 测试通过打标数量: 🟢 160  │
│ API通过打标数量: 🟢 60│ 测试通过打标数量: 🟢 150  │
└─────────────────────┴───────────────────────────┘
```

## Styling

The component follows the dashboard design system:

- **Background**: White (`bg-white`)
- **Border Radius**: Large (`rounded-lg`)
- **Shadow**: Medium (`shadow-md`)
- **Padding**: 6 units (`p-6`)
- **API Percentage Color**: Blue (`text-blue-600`)
- **Test Case Percentage Color**: Green (`text-green-600`)

## Accessibility

- Uses semantic HTML structure
- Includes `data-testid` attributes for testing
- Maintains good color contrast ratios
- Responsive text sizing

## Requirements Validation

This component satisfies the following requirements:

- **4.1**: Displays "API使用情况" statistics widget
- **4.2**: Shows two sections: API completion and test case completion
- **4.3**: Displays percentage values in "XX%" format
- **4.4**: Lists API details with corresponding numeric values
- **4.5**: Lists test case details with corresponding numeric values

## Testing

The component includes test IDs for easy testing:

- `api-completion-percentage`: API completion percentage value
- `testcase-completion-percentage`: Test case completion percentage value
- `total-apis`: Total APIs count
- `completed-apis`: Completed APIs count
- `tagged-apis`: Tagged APIs count
- `total-testcases`: Total test cases count
- `passed-testcases`: Passed test cases count
- `tagged-testcases`: Tagged test cases count

## Examples

See `ApiUsageWidget.example.vue` for comprehensive usage examples including:

1. Normal usage with moderate completion rates
2. High completion rates (green indicators)
3. Low completion rates (red indicators)
4. Zero data handling
5. Mixed performance (yellow indicators)

## Related Components

- `StepsStatisticsWidget`: Displays test step statistics
- `TrendAnalysisWidget`: Shows trend analysis over time
- `UserProfileCard`: Displays user profile information

## Notes

- The component expects valid numeric values for all metrics
- Percentage values should be between 0 and 100
- The divider line is positioned absolutely between the two columns
- Color indicators automatically adjust based on performance ratios
