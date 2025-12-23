# Dashboard Store

## Overview

The dashboard store manages the state and data fetching for the home dashboard feature. It provides centralized state management for user metrics, statistics, and trend data with built-in caching support.

## Features

- **Centralized State Management**: Uses Pinia for reactive state management
- **Data Caching**: 5-minute cache using localStorage to reduce server load
- **Concurrent Data Fetching**: Fetches all dashboard data in parallel for optimal performance
- **Error Handling**: Comprehensive error handling with user-friendly error messages
- **TypeScript Support**: Full type safety with TypeScript interfaces

## Usage

### Basic Usage

```typescript
import { useDashboardStore } from '@/stores/dashboard';

// In a Vue component
const dashboardStore = useDashboardStore();

// Fetch dashboard data (uses cache if available)
await dashboardStore.refreshDashboard();

// Access data
const userData = dashboardStore.userData;
const statistics = dashboardStore.statistics;

// Check loading state
if (dashboardStore.loading) {
  // Show loading indicator
}

// Check for errors
if (dashboardStore.isError) {
  console.error(dashboardStore.error);
}
```

### Force Refresh (Bypass Cache)

```typescript
// Force fresh data fetch, ignoring cache
await dashboardStore.refreshDashboard(false);
```

### Manual Cache Management

```typescript
import { clearCache, isCacheValid, getCacheData } from '@/stores/dashboard';

// Check if cache is valid
if (isCacheValid()) {
  const cached = getCacheData();
  console.log('Using cached data:', cached);
}

// Clear cache manually
clearCache();
```

## API Endpoints

The dashboard store expects the following backend API endpoints:

- `GET /api/dashboard/user-metrics` - User profile and metrics
- `GET /api/dashboard/step-statistics` - Test step statistics
- `GET /api/dashboard/api-usage` - API usage statistics
- `GET /api/dashboard/trends?days=7` - Trend data for specified days

## Type Definitions

All TypeScript interfaces are available in:
- `@/stores/dashboard.ts` - Store types and API response types
- `@/types/dashboard.d.ts` - Component prop types

## Testing

### Unit Tests

```bash
bun run vitest --run src/stores/__tests__/dashboard.test.ts
```

### Property-Based Tests

```bash
bun run vitest --run src/stores/__tests__/dashboard.property.test.ts
```

## Cache Configuration

- **Cache Duration**: 5 minutes (300,000 milliseconds)
- **Cache Key**: `dashboard_cache`
- **Storage**: localStorage
- **Validation**: Timestamp-based freshness check

## Error Handling

The store handles various error scenarios:

1. **Network Errors**: Displays user-friendly error messages
2. **API Errors**: Transforms backend errors into readable messages
3. **Cache Errors**: Gracefully handles localStorage failures
4. **Partial Failures**: Continues operation even if some data fails to load

## State Properties

- `loading` - Boolean indicating if data is being fetched
- `error` - Error message string or null
- `lastUpdated` - Date of last successful data fetch
- `userData` - User profile and metrics data
- `statistics` - Dashboard statistics (steps, API usage, trends)

## Computed Properties

- `hasData` - True if both userData and statistics are loaded
- `isError` - True if there is an error

## Actions

- `refreshDashboard(useCache?)` - Fetch all dashboard data
- `fetchUserMetrics()` - Fetch user metrics only
- `fetchStepStatistics()` - Fetch step statistics only
- `fetchApiUsage()` - Fetch API usage only
- `fetchTrends(days?)` - Fetch trend data
- `loadFromCache()` - Load data from cache if valid
- `clearError()` - Clear error state
- `reset()` - Reset store to initial state
