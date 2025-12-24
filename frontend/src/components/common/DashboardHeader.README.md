# DashboardHeader Component

## Overview

The `DashboardHeader` component provides a consistent header for dashboard pages, featuring a title, last updated timestamp, and a refresh button. It integrates seamlessly with the dashboard store to trigger data refreshes.

## Features

- **Title Display**: Customizable dashboard title
- **Last Updated Timestamp**: Shows when data was last refreshed
- **Refresh Button**: Integrated refresh functionality with loading state
- **Responsive Design**: Adapts to different screen sizes
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Usage

### Basic Usage

```vue
<template>
  <DashboardHeader
    title="仪表盘"
    :last-updated="lastUpdated"
    :loading="isLoading"
    @refresh="handleRefresh"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { DashboardHeader } from '@/components/common';

const lastUpdated = ref(new Date());
const isLoading = ref(false);

function handleRefresh() {
  isLoading.value = true;
  // Fetch fresh data
  setTimeout(() => {
    isLoading.value = false;
    lastUpdated.value = new Date();
  }, 2000);
}
</script>
```

### With Dashboard Store

```vue
<template>
  <DashboardHeader
    title="数据概览"
    :last-updated="dashboardStore.lastUpdated"
    :loading="dashboardStore.loading"
    @refresh="refreshDashboard"
  />
</template>

<script setup lang="ts">
import { DashboardHeader } from '@/components/common';
import { useDashboardStore } from '@/stores/dashboard';

const dashboardStore = useDashboardStore();

async function refreshDashboard() {
  await dashboardStore.refreshDashboard(false);
}
</script>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | `'仪表盘'` | The dashboard title to display |
| `lastUpdated` | `Date \| null` | `null` | Timestamp of last data update |
| `loading` | `boolean` | `false` | Whether data is currently being refreshed |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `refresh` | `void` | Emitted when the refresh button is clicked |

## Slots

This component does not use slots.

## Styling

The component uses Tailwind CSS classes for styling and includes:
- White background with rounded corners
- Shadow for depth
- Hover effect for enhanced shadow
- Responsive flex layout
- Consistent spacing and typography

### Custom Styling

You can override styles using scoped CSS or by wrapping the component:

```vue
<template>
  <div class="custom-header-wrapper">
    <DashboardHeader
      title="Custom Dashboard"
      :last-updated="lastUpdated"
      @refresh="handleRefresh"
    />
  </div>
</template>

<style scoped>
.custom-header-wrapper :deep(.dashboard-header) {
  background: linear-gradient(to right, #3b82f6, #8b5cf6);
  color: white;
}
</style>
```

## RefreshButton Component

The `DashboardHeader` uses the `RefreshButton` component internally. You can also use `RefreshButton` independently:

```vue
<template>
  <RefreshButton
    :loading="isLoading"
    :show-label="true"
    variant="primary"
    size="md"
    @click="handleRefresh"
  />
</template>
```

### RefreshButton Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `loading` | `boolean` | `false` | Shows loading spinner when true |
| `showLabel` | `boolean` | `true` | Whether to show text label |
| `variant` | `'primary' \| 'secondary' \| 'ghost'` | `'ghost'` | Button style variant |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |

## Accessibility

The component follows accessibility best practices:

- **ARIA Labels**: Refresh button has descriptive `aria-label`
- **Keyboard Navigation**: All interactive elements are keyboard accessible
- **Focus Indicators**: Clear focus states for keyboard users
- **Semantic HTML**: Uses proper heading hierarchy (`<h1>`)

## Examples

See `DashboardHeader.example.vue` for comprehensive usage examples including:
- Basic usage
- Loading states
- Custom titles
- Dashboard store integration
- Refresh event handling

## Testing

The component includes comprehensive unit tests covering:
- Rendering with various props
- Loading state behavior
- Refresh functionality
- Date formatting
- Accessibility features
- Styling classes

Run tests with:
```bash
npm run test -- DashboardHeader.test.ts
```

## Requirements Validation

This component satisfies the following requirements from the home-dashboard spec:

- **Requirement 8.1**: Provides a refresh button in the header
- **Requirement 8.2**: Triggers dashboard refresh when button is clicked
- **Requirement 8.3**: Shows loading indicator during refresh

## Related Components

- `RefreshButton`: The refresh button used in the header
- `LoadingState`: Can be used alongside for full-page loading
- `ErrorState`: Can be used for error handling

## Notes

- The last updated timestamp is formatted using Chinese locale (`zh-CN`)
- The component automatically handles date formatting errors
- The refresh button is disabled during loading to prevent multiple simultaneous refreshes
- The component uses the dashboard store's `lastUpdated` state for timestamp display
