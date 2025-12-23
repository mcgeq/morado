# Frontend API Client

This directory contains the API client modules for the Morado test platform frontend. The API client is organized according to the four-layer architecture of the backend system.

## Architecture Overview

The API client follows the four-layer architecture:

1. **Layer 1: API Definition Components** - Header, Body, and API Definition management
2. **Layer 2: Test Scripts** - Script management and execution
3. **Layer 3: Test Components** - Component management with script composition
4. **Layer 4: Test Cases & Suites** - Test case and test suite management

## Modules

### Core Configuration (`index.ts`)

The base Axios configuration with interceptors for:
- Request/response handling
- Authentication (Bearer token)
- Error handling (401, 403, 404, 422, 500)
- Request/response logging

**Usage:**
```typescript
import apiClient from '@/api'

// Direct usage (not recommended, use specific API modules instead)
const response = await apiClient.get('/some-endpoint')
```

### Layer 1: API Definition Components

#### Header API (`header.ts`)
Manages reusable HTTP header components.

**Example:**
```typescript
import { getHeaders, createHeader, type Header } from '@/api/header'

// Get all headers
const headers = await getHeaders({ scope: 'global' })

// Create a new header
const newHeader = await createHeader({
  name: 'Auth Header',
  headers: { 'Authorization': 'Bearer ${token}' },
  scope: 'global'
})
```

#### Body API (`body.ts`)
Manages reusable request/response body templates.

**Example:**
```typescript
import { getBodies, createBody, type Body } from '@/api/body'

// Get all bodies
const bodies = await getBodies({ body_type: 'request' })

// Create a new body
const newBody = await createBody({
  name: 'User Body',
  body_type: 'both',
  content_type: 'application/json',
  example_data: { name: 'John', email: 'john@example.com' }
})
```

#### API Definition API (`api-definition.ts`)
Manages complete API interface definitions.

**Example:**
```typescript
import { getApiDefinitions, createApiDefinition } from '@/api/api-definition'

// Get all API definitions
const apis = await getApiDefinitions({ method: 'GET' })

// Create a new API definition
const newApi = await createApiDefinition({
  name: 'Get User',
  method: 'GET',
  path: '/api/users/{id}',
  header_id: 1,
  response_body_id: 2
})
```

### Layer 2: Test Scripts

#### Script API (`script.ts`)
Manages test scripts that reference API definitions.

**Example:**
```typescript
import { getScripts, createScript, executeScript } from '@/api/script'

// Get all scripts
const scripts = await getScripts({ script_type: 'main' })

// Create a new script
const newScript = await createScript({
  name: 'Login Test',
  api_definition_id: 1,
  variables: { username: 'test', password: 'pass' },
  assertions: [
    { type: 'status_code', expected: 200 }
  ]
})

// Execute a script for debugging
const result = await executeScript(1, { username: 'admin' })
```

### Layer 3: Test Components

#### Component API (`component.ts`)
Manages composite components that combine multiple scripts.

**Example:**
```typescript
import { getComponents, createComponent, executeComponent } from '@/api/component'

// Get all components
const components = await getComponents({ component_type: 'simple' })

// Create a new component
const newComponent = await createComponent({
  name: 'User Login Flow',
  execution_mode: 'sequential',
  shared_variables: { base_url: 'https://api.example.com' }
})

// Execute a component
const result = await executeComponent(1, { timeout: 60 })
```

### Layer 4: Test Cases & Suites

#### Test Case API (`test-case.ts`)
Manages test cases that reference scripts and components.

**Example:**
```typescript
import { getTestCases, createTestCase, executeTestCase } from '@/api/test-case'

// Get all test cases
const testCases = await getTestCases({ priority: 'high', status: 'active' })

// Create a new test case
const newTestCase = await createTestCase({
  name: 'User Login Test',
  priority: 'high',
  status: 'active',
  test_data: { username: 'test', password: 'pass' }
})

// Execute a test case
const result = await executeTestCase(1)
```

#### Test Suite API (`test-suite.ts`)
Manages test suites that group multiple test cases.

**Example:**
```typescript
import { getTestSuites, createTestSuite, executeTestSuite } from '@/api/test-suite'

// Get all test suites
const testSuites = await getTestSuites({ environment: 'test' })

// Create a new test suite
const newTestSuite = await createTestSuite({
  name: 'Regression Test Suite',
  execution_order: 'sequential',
  environment: 'test'
})

// Execute a test suite
const result = await executeTestSuite(1)
```

### Reports & Analytics

#### Report API (`report.ts`)
Provides test reports and analytics.

**Example:**
```typescript
import { 
  getExecutionSummaryReport, 
  getTestCaseReport,
  getTrendReport 
} from '@/api/report'

// Get execution summary
const summary = await getExecutionSummaryReport({
  start_date: '2024-01-01',
  end_date: '2024-01-31',
  environment: 'test'
})

// Get test case report
const caseReport = await getTestCaseReport(1, 10)

// Get trend report
const trend = await getTrendReport({ days: 30, environment: 'test' })
```

## Error Handling

All API functions automatically handle errors through the Axios interceptor:

- **401 Unauthorized**: Redirects to login page
- **403 Forbidden**: Logs access denied error
- **404 Not Found**: Logs resource not found error
- **422 Validation Error**: Logs validation error
- **500 Server Error**: Logs server error

Errors are logged to the console and can be caught in your components:

```typescript
try {
  const result = await executeTestCase(1)
} catch (error) {
  // Error is already logged by interceptor
  // Handle UI feedback here
  console.error('Test execution failed:', error)
}
```

## Authentication

The API client automatically includes the authentication token from localStorage:

```typescript
// Set token after login
localStorage.setItem('auth_token', 'your-jwt-token')

// Token is automatically included in all requests
const testCases = await getTestCases()

// Clear token on logout
localStorage.removeItem('auth_token')
```

## Environment Configuration

API base URL is configured through environment variables:

- **Development**: `VITE_API_BASE_URL=http://localhost:8000/api/v1`
- **Production**: `VITE_API_BASE_URL=/api/v1`

See `.env.development` and `.env.production` files.

## TypeScript Support

All API modules are fully typed with TypeScript interfaces. Import types as needed:

```typescript
import type { 
  Header, 
  HeaderCreate, 
  HeaderUpdate 
} from '@/api/header'

import type { 
  TestCase, 
  TestCaseCreate,
  TestCaseExecutionResult 
} from '@/api/test-case'
```

## Best Practices

1. **Use specific API modules** instead of the base `apiClient`
2. **Handle errors gracefully** in your components
3. **Use TypeScript types** for type safety
4. **Leverage pagination** for large datasets
5. **Use search and filter** parameters to reduce data transfer
6. **Cache responses** when appropriate (consider using Vue Query or similar)
7. **Implement loading states** in your UI components
8. **Test API calls** with mock data during development
