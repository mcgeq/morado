# Router Configuration

This directory contains the Vue Router configuration for the Morado frontend application.

## Overview

The router is configured with:
- **History Mode**: Uses HTML5 History API for clean URLs
- **Lazy Loading**: All route components are lazy-loaded for optimal performance
- **Route Guards**: Authentication checks and navigation guards
- **Meta Fields**: Route metadata for titles and authentication requirements

## Route Structure

The routes are organized according to the four-layer architecture:

### Layer 1: API Components
- `/headers` - Header component management
- `/bodies` - Body component management
- `/api-definitions` - API definition management

### Layer 2: Scripts
- `/scripts` - Script management and execution
- `/scripts/:id/debug` - Script debugging interface

### Layer 3: Components
- `/components` - Component management
- `/components/:id/debug` - Component debugging interface

### Layer 4: Test Cases
- `/test-cases` - Test case management
- `/test-suites` - Test suite management
- `/reports` - Test report dashboard

## Route Guards

### Authentication Guard

The `beforeEach` navigation guard checks if a route requires authentication:

```typescript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const isAuthenticated = checkAuthentication();
    if (!isAuthenticated) {
      next({ name: 'Home', query: { redirect: to.fullPath } });
    } else {
      next();
    }
  } else {
    next();
  }
});
```

### Document Title

The router automatically updates the document title based on route metadata:

```typescript
if (to.meta.title) {
  document.title = `${to.meta.title} - Morado`;
}
```

## Lazy Loading

All route components use dynamic imports for code splitting:

```typescript
{
  path: '/scripts',
  component: () => import('@/views/Script/List.vue')
}
```

This ensures that component code is only loaded when the route is accessed.

## Navigation Helpers

The router exports helper functions for common navigation tasks:

```typescript
import { navigationHelpers } from '@/router';

// Navigate to home
navigationHelpers.goHome();

// Navigate back
navigationHelpers.goBack();

// Navigate to a named route
navigationHelpers.goTo('ScriptList');
```

## Usage in Components

### Using router-link

```vue
<template>
  <router-link to="/scripts">Scripts</router-link>
  <router-link :to="{ name: 'ScriptEdit', params: { id: '123' }}">
    Edit Script
  </router-link>
</template>
```

### Programmatic Navigation

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToScripts = () => {
  router.push({ name: 'ScriptList' });
};

const goToScriptEdit = (id: string) => {
  router.push({ name: 'ScriptEdit', params: { id } });
};
</script>
```

## Route Meta Fields

Each route can have the following meta fields:

- `title`: Page title (string)
- `requiresAuth`: Whether authentication is required (boolean)

Example:

```typescript
{
  path: '/scripts',
  name: 'ScriptList',
  component: () => import('@/views/Script/List.vue'),
  meta: {
    title: '脚本管理',
    requiresAuth: true
  }
}
```

## Scroll Behavior

The router is configured to:
- Restore scroll position when using browser back/forward buttons
- Scroll to top when navigating to a new route

## Future Enhancements

- Add role-based access control (RBAC) to route guards
- Implement route-level permissions
- Add loading states during route transitions
- Add route transition animations
