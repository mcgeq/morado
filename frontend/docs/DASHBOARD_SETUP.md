# Dashboard Setup Documentation

## Overview

This document describes the setup and configuration for the home dashboard feature, including all dependencies, configurations, and testing infrastructure.

## Dependencies Installed

### Production Dependencies

- **echarts** (^6.0.0) - Powerful charting library for data visualizations
- **vue-echarts** (^8.0.1) - Vue 3 wrapper for ECharts

### Development Dependencies

- **fast-check** (^4.5.2) - Property-based testing library
- **@types/echarts** (^5.0.0) - TypeScript type definitions for ECharts
- **@testing-library/vue** (^8.1.0) - Vue testing utilities
- **@testing-library/user-event** (^14.6.1) - User interaction simulation
- **jsdom** (^27.3.0) - DOM implementation for testing
- **@vitest/ui** (^4.0.16) - Vitest UI for test visualization

## Project Structure

```
frontend/
├── src/
│   ├── plugins/
│   │   └── echarts.ts              # ECharts global configuration
│   ├── stores/
│   │   ├── dashboard.ts            # Dashboard Pinia store
│   │   ├── README.md               # Store documentation
│   │   └── __tests__/
│   │       ├── dashboard.test.ts           # Unit tests
│   │       └── dashboard.property.test.ts  # Property-based tests
│   ├── types/
│   │   └── dashboard.d.ts          # TypeScript type definitions
│   └── test/
│       └── setup.ts                # Vitest test setup
├── vite.config.ts                  # Vite configuration with test setup
├── tsconfig.app.json               # TypeScript configuration
└── package.json                    # Dependencies
```

## Configuration Files

### 1. ECharts Plugin (`src/plugins/echarts.ts`)

Configures ECharts with required components:
- Canvas Renderer
- Pie Chart (for donut charts)
- Line Chart (for area charts)
- Title, Tooltip, Legend, Grid components

Registers `v-chart` component globally for use in all Vue components.

### 2. Dashboard Store (`src/stores/dashboard.ts`)

Features:
- Pinia store for dashboard state management
- API data fetching with concurrent requests
- 5-minute localStorage caching
- TypeScript interfaces for all data types
- Error handling and loading states

### 3. TypeScript Configuration

Updated `tsconfig.app.json` to include ECharts types:
```json
{
  "types": ["vite/client", "echarts"]
}
```

### 4. Vitest Configuration

Added test configuration to `vite.config.ts`:
```typescript
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: ['./src/test/setup.ts'],
  coverage: {
    provider: 'v8',
    reporter: ['text', 'json', 'html'],
  },
}
```

## Usage

### Using ECharts in Components

```vue
<template>
  <v-chart :option="chartOption" style="height: 400px" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { EChartsOption } from 'echarts';

const chartOption = ref<EChartsOption>({
  title: { text: 'My Chart' },
  xAxis: { type: 'category', data: ['A', 'B', 'C'] },
  yAxis: { type: 'value' },
  series: [{ data: [10, 20, 30], type: 'line' }],
});
</script>
```

### Using Dashboard Store

```vue
<script setup lang="ts">
import { onMounted } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';

const dashboardStore = useDashboardStore();

onMounted(async () => {
  await dashboardStore.refreshDashboard();
});
</script>

<template>
  <div v-if="dashboardStore.loading">Loading...</div>
  <div v-else-if="dashboardStore.isError">{{ dashboardStore.error }}</div>
  <div v-else>
    <h1>Welcome, {{ dashboardStore.userData?.username }}</h1>
    <!-- Dashboard content -->
  </div>
</template>
```

## Testing

### Running Tests

```bash
# Run all tests
bun run vitest --run

# Run specific test file
bun run vitest --run src/stores/__tests__/dashboard.test.ts

# Run with UI
bun run vitest --ui

# Run with coverage
bun run vitest --coverage
```

### Writing Property-Based Tests

Example using fast-check:

```typescript
import * as fc from 'fast-check';

it('should validate property', () => {
  fc.assert(
    fc.property(
      fc.nat(), // Generate natural numbers
      fc.string(), // Generate strings
      (num, str) => {
        // Test property
        return true; // Property should hold
      }
    ),
    { numRuns: 100 } // Run 100 iterations
  );
});
```

## Cache Management

The dashboard implements a 5-minute cache using localStorage:

```typescript
import { isCacheValid, getCacheData, setCacheData, clearCache } from '@/stores/dashboard';

// Check cache validity
if (isCacheValid()) {
  const data = getCacheData();
  // Use cached data
}

// Clear cache manually
clearCache();
```

## API Integration

The dashboard expects these backend endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/user-metrics` | GET | User profile and test metrics |
| `/api/dashboard/step-statistics` | GET | Test step distribution |
| `/api/dashboard/api-usage` | GET | API usage statistics |
| `/api/dashboard/trends` | GET | Trend data (accepts `?days=N` param) |

## Type Safety

All components and stores use TypeScript for type safety:

- Store types: `src/stores/dashboard.ts`
- Component prop types: `src/types/dashboard.d.ts`
- ECharts types: Provided by `@types/echarts`

## Next Steps

1. Implement dashboard components (UserProfileCard, QuickActionsPanel, etc.)
2. Create chart components (DonutChart, AreaChart)
3. Build the main Home.vue dashboard container
4. Implement responsive design
5. Add accessibility features
6. Write comprehensive tests

## Troubleshooting

### ECharts not rendering

Ensure the chart container has a defined height:
```vue
<v-chart :option="option" style="height: 400px" />
```

### TypeScript errors with ECharts

Make sure `@types/echarts` is installed and included in `tsconfig.app.json`.

### Tests failing

Clear localStorage before tests:
```typescript
beforeEach(() => {
  localStorage.clear();
});
```

## Resources

- [ECharts Documentation](https://echarts.apache.org/en/index.html)
- [vue-echarts Documentation](https://github.com/ecomfe/vue-echarts)
- [fast-check Documentation](https://fast-check.dev/)
- [Vitest Documentation](https://vitest.dev/)
- [Pinia Documentation](https://pinia.vuejs.org/)
