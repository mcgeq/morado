# Dashboard API Implementation

## Overview

This document describes the implementation of the dashboard API endpoints for the Morado testing platform home page.

## Implemented Endpoints

### 1. GET /dashboard/user-metrics

**Purpose**: Retrieve user information and testing metrics for the dashboard.

**Query Parameters**:
- `user_id` (optional, default: 1): User ID to fetch metrics for

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

**Requirements Validated**: 1.1

---

### 2. GET /dashboard/step-statistics

**Purpose**: Retrieve test execution step statistics.

**Response**:
```json
{
  "completed": 500,
  "sql_failed": 25,
  "api_request": 1000,
  "total": 1525
}
```

**Requirements Validated**: 3.1

---

### 3. GET /dashboard/api-usage

**Purpose**: Retrieve API definition and test case usage statistics.

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

**Requirements Validated**: 4.1

---

### 4. GET /dashboard/trends

**Purpose**: Retrieve trend data for various components over time.

**Query Parameters**:
- `days` (optional, default: 7, max: 365): Number of days to include in trend

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
    },
    {
      "date": "2024-01-16",
      "scheduled_components": 12,
      "test_case_components": 18,
      "actual_components": 10,
      "detection_components": 25
    }
  ]
}
```

**Requirements Validated**: 5.1

---

## Architecture

### Service Layer

**File**: `backend/src/morado/services/dashboard.py`

The `DashboardService` class provides business logic for:
- Aggregating user metrics from the database
- Calculating step statistics from execution data
- Computing API usage and completion rates
- Generating trend data over specified time periods

### API Controller

**File**: `backend/src/morado/api/v1/dashboard.py`

The `DashboardController` class provides REST API endpoints that:
- Accept HTTP requests with query parameters
- Validate input parameters
- Call the service layer for data processing
- Return JSON responses

### Application Registration

**File**: `backend/src/morado/app.py`

The dashboard controller is registered in the Litestar application with:
- Route handler registration
- OpenAPI documentation tag
- Dependency injection for database sessions

---

## Error Handling

All endpoints include error handling for:
- Invalid user IDs (returns default/empty data)
- Database connection errors (handled by Litestar middleware)
- Invalid query parameters (validated by Litestar)

---

## Authentication

**Note**: The current implementation does not include authentication middleware. This should be added in a future iteration to ensure only authenticated users can access dashboard data.

To add authentication:
1. Create an authentication guard/middleware
2. Add it to the DashboardController
3. Extract user_id from the authenticated session instead of query parameter

---

## Testing

### Manual Testing

You can test the endpoints using curl or any HTTP client:

```bash
# Get user metrics
curl http://localhost:8000/dashboard/user-metrics?user_id=1

# Get step statistics
curl http://localhost:8000/dashboard/step-statistics

# Get API usage
curl http://localhost:8000/dashboard/api-usage

# Get trends (last 30 days)
curl http://localhost:8000/dashboard/trends?days=30
```

### Integration Tests

Integration tests should be added to `tests/backend/integration/test_api/test_dashboard_api.py` to verify:
- Endpoint accessibility
- Response format validation
- Data accuracy
- Error handling

---

## Future Enhancements

1. **Authentication**: Add authentication middleware to protect endpoints
2. **Caching**: Implement Redis caching for frequently accessed data
3. **Pagination**: Add pagination support for large datasets
4. **Filtering**: Add more filtering options (date ranges, environments, etc.)
5. **Real-time Updates**: Consider WebSocket support for real-time dashboard updates
6. **Performance**: Optimize database queries with proper indexing
7. **Aggregation**: Pre-compute statistics for better performance

---

## Database Queries

The service layer uses SQLAlchemy to query:
- `users` table for user information
- `test_executions` table for execution statistics
- `api_definitions` table for API counts
- `test_scripts` table for script counts
- `test_components` table for component counts
- `test_cases` table for test case counts

All queries are optimized to minimize database load and use appropriate aggregation functions.


---

## Implementation Notes

### Authentication Middleware

The task requirements mention implementing authentication middleware for dashboard endpoints. However, after reviewing the codebase, authentication is not yet implemented in the Morado platform. 

**Current State**: 
- No authentication system exists in the codebase
- User ID is passed as a query parameter
- All endpoints are publicly accessible

**Recommended Implementation** (when authentication is ready):

```python
# backend/src/morado/api/v1/dashboard.py

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler


async def dashboard_auth_guard(
    connection: ASGIConnection, route_handler: BaseRouteHandler
) -> None:
    """Authentication guard for dashboard endpoints.
    
    Raises:
        NotAuthorizedException: If user is not authenticated
    """
    # Check if user is authenticated
    user = connection.scope.get("user")
    if not user:
        raise NotAuthorizedException("Authentication required")


class DashboardController(Controller):
    """Controller for Dashboard endpoints."""

    path = "/dashboard"
    tags = ["Dashboard"]
    guards = [dashboard_auth_guard]  # Add authentication guard
    dependencies = {"dashboard_service": Provide(provide_dashboard_service)}
    
    # ... rest of the controller
```

**Steps to implement authentication**:
1. Create authentication middleware in `backend/src/morado/middleware/auth.py`
2. Add JWT token validation
3. Extract user from token and add to request scope
4. Create authentication guard for dashboard endpoints
5. Update endpoints to use authenticated user ID instead of query parameter

### Error Handling

The implementation includes basic error handling:

1. **Parameter Validation**: Litestar automatically validates query parameters (e.g., `days` must be between 1-365)
2. **Database Errors**: Handled by Litestar's exception handlers
3. **Missing Data**: Service methods return default/empty data for missing users
4. **SQL Errors**: Caught by SQLAlchemy and propagated to Litestar

**Additional error handling to consider**:
- Rate limiting for dashboard endpoints
- Request timeout handling
- Database connection pool exhaustion
- Invalid date ranges in trend queries

### Validation

Current validation includes:
- Query parameter type validation (int, string)
- Range validation for `days` parameter (1-365)
- Non-null checks for required parameters

**Additional validation to consider**:
- User ID existence validation
- Date range validation
- Environment name validation
- Pagination parameter validation
