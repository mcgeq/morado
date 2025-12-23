# Layout Components

This directory contains layout components that provide consistent page structure across the application.

## Available Layouts

### DefaultLayout

The `DefaultLayout.vue` provides a complete page structure with:
- **Header Navigation**: Top navigation bar with logo and menu items
- **Main Content Area**: Centered content area with consistent padding
- **Footer**: Bottom footer with copyright information
- **Responsive Design**: Mobile-friendly with hamburger menu
- **Four-Layer Architecture Navigation**: Organized menu structure for API components, scripts, components, and test cases

**Features:**
- Dropdown menus for grouped navigation items
- Authentication status display
- Mobile responsive navigation
- Consistent spacing and styling

**Use Cases:**
- Most application pages
- Pages that need standard navigation
- Pages that should maintain consistent layout

### EmptyLayout

The `EmptyLayout.vue` provides a minimal layout with:
- No header or navigation
- No footer
- Just the router-view content

**Use Cases:**
- Login/Authentication pages
- 404 Not Found pages
- Full-screen views (presentations, reports)
- Landing pages with custom designs
- Any page that needs complete layout control

## Usage in Router

To use layouts in your routes, wrap them as parent routes:

```typescript
import { createRouter, createWebHistory } from 'vue-router';
import DefaultLayout from '@/layouts/DefaultLayout.vue';
import EmptyLayout from '@/layouts/EmptyLayout.vue';

const routes = [
  // Routes with DefaultLayout
  {
    path: '/',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue')
      },
      {
        path: 'test-cases',
        name: 'TestCaseList',
        component: () => import('@/views/TestCase/List.vue')
      }
      // ... more routes
    ]
  },
  
  // Routes with EmptyLayout
  {
    path: '/auth',
    component: EmptyLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/Auth/Login.vue')
      }
    ]
  },
  
  // Direct route without layout (uses EmptyLayout implicitly)
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
];
```

## Current Implementation

Currently, the router uses direct route definitions without layout wrappers. The layouts are available for use when you want to:

1. **Add consistent navigation** to all pages - wrap routes with `DefaultLayout`
2. **Create pages without navigation** - wrap routes with `EmptyLayout` or use direct routes

## Customization

### DefaultLayout Customization

You can customize the DefaultLayout by:
- Modifying navigation items in the template
- Adjusting colors and styling
- Adding/removing menu sections
- Customizing the authentication logic

### EmptyLayout Customization

The EmptyLayout is intentionally minimal. If you need a different minimal layout:
- Create a new layout component (e.g., `MinimalLayout.vue`)
- Add any minimal UI elements you need
- Use it in your routes

## Authentication Integration

The DefaultLayout includes placeholder authentication logic:

```typescript
const isAuthenticated = computed(() => {
  return !!localStorage.getItem('auth_token');
});
```

**To integrate real authentication:**
1. Replace the localStorage check with your authentication store
2. Update the `handleLogin` and `handleLogout` functions
3. Connect to your authentication API

Example with Pinia store:

```typescript
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const isAuthenticated = computed(() => userStore.isAuthenticated);

const handleLogout = async () => {
  await userStore.logout();
  router.push({ name: 'Home' });
};
```

## Best Practices

1. **Use DefaultLayout for most pages** - Provides consistent user experience
2. **Use EmptyLayout sparingly** - Only for pages that truly need no navigation
3. **Keep layouts simple** - Complex logic should be in components or stores
4. **Make layouts responsive** - Ensure mobile users have good experience
5. **Test navigation** - Verify all menu items work correctly

## Future Enhancements

Potential improvements for the layouts:

- [ ] Add breadcrumb navigation
- [ ] Add user profile dropdown
- [ ] Add notification system
- [ ] Add theme switcher (light/dark mode)
- [ ] Add search functionality
- [ ] Add keyboard shortcuts
- [ ] Add loading indicators
- [ ] Add sidebar for additional navigation
