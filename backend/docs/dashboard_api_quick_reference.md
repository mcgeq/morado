# Dashboard API Quick Reference

Quick reference guide for frontend developers integrating with the dashboard API.

---

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### 1. User Metrics

```http
GET /dashboard/user-metrics?user_id={id}
```

**Response**:
```json
{
  "user_id": 1,
  "username": "john_doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "registration_date": "2024-01-15T10:30:00",
  "total_executions": 150,
  "passed_tests": 120,
  "failed_tests": 30
}
```

---

### 2. Step Statistics

```http
GET /dashboard/step-statistics
```

**Response**:
```json
{
  "completed": 500,
  "sql_failed": 25,
  "api_request": 1000,
  "total": 1525
}
```

---

### 3. API Usage

```http
GET /dashboard/api-usage
```

**Response**:
```json
{
  "api_completion_rate": 75,
  "total_apis": 100,
  "completed_apis": 75,
  "tagged_apis": 50,
  "test_case_completion_rate": 80,
  "total_test_cases": 200,
  "passed_test_cases": 160,
  "tagged_test_cases": 120
}
```

---

### 4. Trends

```http
GET /dashboard/trends?days={number}
```

**Parameters**:
- `days` (optional): Number of days (1-365, default: 7)

**Response**:
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "scheduled_components": 10,
      "test_case_components": 15,
      "actual_components": 8,
      "detection_components": 20
    }
  ]
}
```

---

## TypeScript Types

```typescript
// User Metrics Response
interface UserMetricsResponse {
  user_id: number;
  username: string;
  avatar_url: string | null;
  registration_date: string | null;
  total_executions: number;
  passed_tests: number;
  failed_tests: number;
}

// Step Statistics Response
interface StepStatisticsResponse {
  completed: number;
  sql_failed: number;
  api_request: number;
  total: number;
}

// API Usage Response
interface ApiUsageResponse {
  api_completion_rate: number;
  total_apis: number;
  completed_apis: number;
  tagged_apis: number;
  test_case_completion_rate: number;
  total_test_cases: number;
  passed_test_cases: number;
  tagged_test_cases: number;
}

// Trend Data Point
interface TrendDataPoint {
  date: string; // YYYY-MM-DD format
  scheduled_components: number;
  test_case_components: number;
  actual_components: number;
  detection_components: number;
}

// Trends Response
interface TrendsResponse {
  data: TrendDataPoint[];
}
```

---

## Example Usage (Axios)

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Fetch user metrics
async function fetchUserMetrics(userId: number): Promise<UserMetricsResponse> {
  const response = await axios.get(`${API_BASE_URL}/dashboard/user-metrics`, {
    params: { user_id: userId }
  });
  return response.data;
}

// Fetch step statistics
async function fetchStepStatistics(): Promise<StepStatisticsResponse> {
  const response = await axios.get(`${API_BASE_URL}/dashboard/step-statistics`);
  return response.data;
}

// Fetch API usage
async function fetchApiUsage(): Promise<ApiUsageResponse> {
  const response = await axios.get(`${API_BASE_URL}/dashboard/api-usage`);
  return response.data;
}

// Fetch trends
async function fetchTrends(days: number = 7): Promise<TrendsResponse> {
  const response = await axios.get(`${API_BASE_URL}/dashboard/trends`, {
    params: { days }
  });
  return response.data;
}

// Fetch all dashboard data
async function fetchDashboardData(userId: number, trendDays: number = 7) {
  const [userMetrics, stepStats, apiUsage, trends] = await Promise.all([
    fetchUserMetrics(userId),
    fetchStepStatistics(),
    fetchApiUsage(),
    fetchTrends(trendDays)
  ]);

  return {
    userMetrics,
    stepStats,
    apiUsage,
    trends
  };
}
```

---

## Error Handling

```typescript
import axios, { AxiosError } from 'axios';

async function fetchDashboardDataSafe(userId: number) {
  try {
    const data = await fetchDashboardData(userId);
    return { success: true, data };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      
      if (axiosError.response) {
        // Server responded with error status
        console.error('Server error:', axiosError.response.status);
        return { 
          success: false, 
          error: `Server error: ${axiosError.response.status}` 
        };
      } else if (axiosError.request) {
        // Request made but no response
        console.error('Network error:', axiosError.message);
        return { 
          success: false, 
          error: 'Network error: Unable to reach server' 
        };
      }
    }
    
    // Unknown error
    console.error('Unknown error:', error);
    return { 
      success: false, 
      error: 'An unexpected error occurred' 
    };
  }
}
```

---

## Caching Strategy

```typescript
interface CachedData<T> {
  data: T;
  timestamp: number;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

function getCachedData<T>(key: string): T | null {
  const cached = localStorage.getItem(key);
  if (!cached) return null;

  const { data, timestamp }: CachedData<T> = JSON.parse(cached);
  const now = Date.now();

  if (now - timestamp > CACHE_DURATION) {
    localStorage.removeItem(key);
    return null;
  }

  return data;
}

function setCachedData<T>(key: string, data: T): void {
  const cached: CachedData<T> = {
    data,
    timestamp: Date.now()
  };
  localStorage.setItem(key, JSON.stringify(cached));
}

async function fetchUserMetricsWithCache(userId: number): Promise<UserMetricsResponse> {
  const cacheKey = `dashboard_user_metrics_${userId}`;
  
  // Try to get from cache
  const cached = getCachedData<UserMetricsResponse>(cacheKey);
  if (cached) {
    return cached;
  }

  // Fetch from API
  const data = await fetchUserMetrics(userId);
  
  // Store in cache
  setCachedData(cacheKey, data);
  
  return data;
}
```

---

## Notes

1. **Authentication**: Currently not implemented. User ID is passed as query parameter.
2. **CORS**: Ensure CORS is configured on the backend for your frontend domain.
3. **Error Handling**: Always implement proper error handling for network requests.
4. **Caching**: Consider implementing client-side caching to reduce server load.
5. **Loading States**: Show loading indicators while fetching data.
6. **Retry Logic**: Implement retry logic for failed requests.

---

## Testing

```typescript
// Mock data for testing
const mockUserMetrics: UserMetricsResponse = {
  user_id: 1,
  username: "test_user",
  avatar_url: null,
  registration_date: "2024-01-01T00:00:00",
  total_executions: 100,
  passed_tests: 80,
  failed_tests: 20
};

const mockStepStats: StepStatisticsResponse = {
  completed: 500,
  sql_failed: 25,
  api_request: 1000,
  total: 1525
};

// Use in tests or development
if (process.env.NODE_ENV === 'development') {
  // Use mock data
} else {
  // Use real API
}
```
