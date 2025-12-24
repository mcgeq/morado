# Loading and Error State Components

This document describes the loading and error state components created for the dashboard.

## Components Overview

### 1. WidgetSkeleton.vue

A reusable skeleton loader component that displays placeholder content while data is loading.

**Props:**
- `type` (optional): The type of skeleton to display
  - `'profile'`: User profile card skeleton
  - `'chart'`: Chart widget skeleton (donut/pie charts)
  - `'stats'`: Statistics widget skeleton
  - `'trend'`: Trend analysis chart skeleton
  - `'actions'`: Quick actions panel skeleton
  - `'default'`: Generic skeleton (default)

**Usage:**
```vue
<template>
  <WidgetSkeleton type="profile" />
  <WidgetSkeleton type="chart" />
  <WidgetSkeleton type="stats" />
</template>

<script setup>
import { WidgetSkeleton } from '@/components/common';
</script>
```

**Features:**
- Animated pulse effect
- Type-specific layouts matching actual widgets
- Consistent styling with dashboard design system
- Responsive design

---

### 2. ErrorState.vue

A component that displays error messages with optional retry functionality.

**Props:**
- `title` (optional): Error title (default: "加载失败")
- `message` (optional): Error message (default: "无法加载数据，请检查网络连接后重试")
- `showRetry` (optional): Show retry button (default: true)
- `showContactSupport` (optional): Show contact support link (default: false)

**Events:**
- `retry`: Emitted when retry button is clicked
- `contactSupport`: Emitted when contact support link is clicked

**Usage:**
```vue
<template>
  <ErrorState
    title="网络错误"
    message="无法连接到服务器"
    :show-retry="true"
    :show-contact-support="true"
    @retry="handleRetry"
    @contact-support="handleContactSupport"
  />
</template>

<script setup>
import { ErrorState } from '@/components/common';

const handleRetry = () => {
  // Retry logic
};

const handleContactSupport = () => {
  // Contact support logic
};
</script>
```

**Features:**
- Error icon with visual feedback
- Customizable title and message
- Optional retry button with loading state
- Optional contact support link
- Accessible and keyboard-friendly

---

### 3. LoadingState.vue

A comprehensive loading state component that can display skeleton loaders for the entire dashboard or specific sections.

**Props:**
- `showHeader` (optional): Show header skeleton (default: false)
- `showProfile` (optional): Show profile card skeleton (default: false)
- `showQuickActions` (optional): Show quick actions skeleton (default: false)
- `showStatistics` (optional): Show statistics grid skeleton (default: false)
- `showStepsStats` (optional): Show steps statistics skeleton (default: false)
- `showApiUsage` (optional): Show API usage skeleton (default: false)
- `showTrends` (optional): Show trends skeleton (default: false)
- `fullDashboard` (optional): Show full dashboard loading (default: true)
- `showLoadingText` (optional): Show loading text (default: false)
- `loadingText` (optional): Custom loading text (default: "加载中...")

**Usage:**

Full dashboard loading:
```vue
<template>
  <LoadingState :full-dashboard="true" />
</template>
```

Specific sections:
```vue
<template>
  <LoadingState
    :full-dashboard="false"
    :show-profile="true"
    :show-quick-actions="true"
    :show-statistics="true"
  />
</template>
```

With loading text:
```vue
<template>
  <LoadingState
    :full-dashboard="true"
    :show-loading-text="true"
    loading-text="正在加载仪表板数据..."
  />
</template>
```

**Features:**
- Flexible configuration for different loading scenarios
- Composed of WidgetSkeleton components
- Responsive grid layout
- Optional loading text with spinner
- Matches dashboard layout structure

---

## Integration with Dashboard

### Typical Usage Pattern

```vue
<template>
  <div class="dashboard">
    <!-- Loading State -->
    <LoadingState v-if="loading" :full-dashboard="true" />
    
    <!-- Error State -->
    <ErrorState
      v-else-if="error"
      :message="error"
      @retry="fetchDashboardData"
    />
    
    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Dashboard widgets -->
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { LoadingState, ErrorState } from '@/components/common';

const loading = ref(true);
const error = ref(null);

const fetchDashboardData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // Fetch data
    await loadData();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};
</script>
```

### Partial Loading

For loading individual widgets:

```vue
<template>
  <div class="widget">
    <WidgetSkeleton v-if="loading" type="chart" />
    <ErrorState v-else-if="error" :message="error" @retry="loadWidget" />
    <ChartWidget v-else :data="data" />
  </div>
</template>
```

---

## Design Considerations

### Visual Consistency
- All components use consistent spacing (padding, margin)
- Border radius matches dashboard widgets (rounded-lg)
- Shadow styles match card components (shadow-md)
- Colors follow Tailwind CSS design system

### Accessibility
- Error states include descriptive text
- Retry buttons are keyboard accessible
- Loading states use semantic HTML
- ARIA labels can be added as needed

### Performance
- Skeleton loaders use CSS animations (no JavaScript)
- Components are lightweight and fast to render
- Pulse animation is GPU-accelerated

### User Experience
- Loading states provide visual feedback
- Error messages are clear and actionable
- Retry functionality is intuitive
- Loading text provides context

---

## Requirements Validation

These components satisfy the following requirements from the design document:

**Requirement 7.1**: Dashboard displays loading indicator while fetching data
- ✅ LoadingState component provides comprehensive loading indicators

**Requirement 7.2**: API calls show skeleton loaders for each widget
- ✅ WidgetSkeleton component provides type-specific skeleton loaders

**Requirement 7.3**: Data fetching failures display error messages with retry options
- ✅ ErrorState component provides error display with retry functionality

---

## Testing

All components include comprehensive unit tests:
- `ErrorState.test.ts`: Tests error display, retry functionality, and events
- `WidgetSkeleton.test.ts`: Tests different skeleton types and rendering
- `LoadingState.test.ts`: Tests loading state configurations and composition

Run tests:
```bash
npm run test
```

---

## Examples

Example files are provided for each component:
- `ErrorState.example.vue`: Various error state scenarios
- `WidgetSkeleton.example.vue`: All skeleton types
- `LoadingState.example.vue`: Different loading configurations

View examples in development mode by importing them into your routes or test pages.
