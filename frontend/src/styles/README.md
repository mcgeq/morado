# Design System

This directory contains the design system constants and utilities for the Morado dashboard.

## Overview

The design system ensures visual consistency across all dashboard components by providing:

- **Spacing values**: Consistent padding, margin, and gap values
- **Border radius**: Standardized corner rounding
- **Shadows**: Elevation and depth effects
- **Typography**: Font sizes, weights, and line heights
- **Colors**: Color palette for UI and data visualization
- **Transitions**: Animation timing and easing functions

## Files

### `design-system.ts`

Core design tokens and constants. Import these values to ensure consistency:

```typescript
import { spacing, colors, widgetStyles } from '@/styles/design-system';
```

### `widgets.css`

CSS utility classes for widgets and cards. These classes are automatically available globally:

```vue
<template>
  <div class="widget widget-hoverable">
    <div class="widget-header">
      <h3 class="widget-title">My Widget</h3>
    </div>
    <!-- Widget content -->
  </div>
</template>
```

### `useWidgetStyles.ts`

Vue composable for programmatic styling:

```vue
<script setup>
import { useWidgetStyles } from '@/composables/useWidgetStyles';

const { widgetClasses, widgetStyle, headerStyle } = useWidgetStyles({
  hoverable: true,
  minHeight: '300px',
});
</script>

<template>
  <div :class="widgetClasses" :style="widgetStyle">
    <h3 :style="headerStyle">Widget Title</h3>
  </div>
</template>
```

## Usage Guidelines

### Creating a New Widget

1. **Use the widget class**:
   ```html
   <div class="widget widget-hoverable">
     <!-- content -->
   </div>
   ```

2. **Use the widget header**:
   ```html
   <div class="widget-header">
     <h3 class="widget-title">Title</h3>
   </div>
   ```

3. **Apply consistent spacing**:
   - Use `widgetSpacing.padding` for widget padding
   - Use `widgetSpacing.gap` for spacing between elements
   - Use `widgetSpacing.headerMargin` for header bottom margin

### Using Design Tokens

#### Spacing

```typescript
import { spacing, widgetSpacing } from '@/styles';

// Use in computed styles
const style = {
  padding: widgetSpacing.padding,
  marginBottom: spacing.lg,
};
```

#### Colors

```typescript
import { colors, chartColors } from '@/styles';

// Use for data visualization
const chartColor = chartColors.primary; // #3B82F6

// Use for UI elements
const textColor = colors.gray[700];
```

#### Shadows

```typescript
import { componentShadows } from '@/styles';

const style = {
  boxShadow: componentShadows.card,
};
```

#### Border Radius

```typescript
import { componentRadius } from '@/styles';

const style = {
  borderRadius: componentRadius.card,
};
```

### Responsive Design

The design system includes responsive utilities:

```css
/* Mobile-first approach */
.widget {
  padding: 1rem; /* Mobile */
}

@media (min-width: 768px) {
  .widget {
    padding: 1.5rem; /* Tablet and desktop */
  }
}
```

### Utility Classes

Available utility classes from `widgets.css`:

- **Widget classes**: `widget`, `widget-hoverable`, `widget-mobile`
- **Card classes**: `card`, `card-hoverable`
- **Header classes**: `widget-header`, `widget-title`, `widget-subtitle`
- **Spacing classes**: `widget-padding`, `widget-gap`, `widget-margin-bottom`
- **Layout classes**: `empty-state`, `legend-container`, `chart-container`
- **Animation classes**: `fade-in`, `scale-in`

## Design Principles

### 1. Consistency

All widgets should use the same:
- Padding: `1.5rem` (24px) on desktop, `1rem` (16px) on mobile
- Border radius: `0.75rem` (12px)
- Shadow: `md` shadow by default, `lg` on hover
- Gap between widgets: `1.5rem` (24px)

### 2. Accessibility

- All interactive elements have focus styles
- Color contrast meets WCAG AA standards
- Keyboard navigation is supported

### 3. Responsiveness

- Mobile-first approach
- Breakpoints: 640px (sm), 768px (md), 1024px (lg)
- Fluid typography and spacing

### 4. Performance

- CSS custom properties for dynamic theming
- Minimal CSS specificity
- Reusable utility classes

## Examples

### Basic Widget

```vue
<template>
  <div class="widget widget-hoverable">
    <div class="widget-header">
      <h3 class="widget-title">Statistics</h3>
      <p class="widget-subtitle">Last 7 days</p>
    </div>
    <div class="chart-container">
      <!-- Chart component -->
    </div>
  </div>
</template>
```

### Card with Metrics

```vue
<template>
  <div class="card card-hoverable">
    <div class="grid grid-cols-3 gap-4">
      <div class="metric-badge bg-blue-50 rounded-lg p-3">
        <div class="metric-badge-value text-blue-600">123</div>
        <div class="metric-badge-label">Total</div>
      </div>
      <!-- More metrics -->
    </div>
  </div>
</template>
```

### Empty State

```vue
<template>
  <div class="widget">
    <div class="empty-state">
      <svg class="empty-state-icon"><!-- icon --></svg>
      <p class="empty-state-text">No data available</p>
    </div>
  </div>
</template>
```

## Maintenance

When updating the design system:

1. Update constants in `design-system.ts`
2. Update utility classes in `widgets.css` if needed
3. Update this README with new patterns
4. Test all dashboard components for consistency
5. Update component documentation

## Requirements

This design system satisfies requirements:
- **10.1**: Consistent spacing, padding, and border radius
- **10.2**: Defined typography scale
- **10.3**: Established color palette
- **10.4**: Consistent shadow styles
- **10.5**: Single icon library with consistent sizing
