# Frontend Unit Tests

This directory contains unit tests for the frontend Vue.js application.

## Test Structure

```
tests/frontend/
├── unit/           # Additional unit tests (optional)
│   ├── components/ # Component tests
│   ├── stores/     # Pinia store tests
│   └── utils/      # Utility function tests
└── e2e/            # End-to-end tests (Playwright)
```

Note: Most frontend tests are co-located with their source files in `frontend/src/`.
This directory is available for tests that don't fit the co-location pattern.

## Running Tests

```bash
# Run all tests
cd frontend
bun run test

# Run tests once (no watch mode)
bun run test:run

# Run tests with UI
bun run test:ui

# Run tests with coverage
bun run test:coverage
```

## Test Configuration

Tests are configured in `frontend/vite.config.ts` using Vitest.

- Test environment: jsdom
- Setup file: `frontend/src/test/setup.ts`
- Test patterns: `*.test.ts`, `*.spec.ts`

## Writing Tests

Use Vitest and Vue Testing Library for component tests:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/vue';
import MyComponent from '@/components/MyComponent.vue';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(MyComponent);
    expect(screen.getByText('Hello')).toBeTruthy();
  });
});
```

## Property-Based Testing

Use fast-check for property-based tests:

```typescript
import { describe, it, expect } from 'vitest';
import fc from 'fast-check';

describe('Property Tests', () => {
  it('should satisfy property', () => {
    fc.assert(
      fc.property(fc.string(), (str) => {
        // Property assertion
        return str.length >= 0;
      })
    );
  });
});
```
