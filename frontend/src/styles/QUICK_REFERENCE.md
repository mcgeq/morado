# Design System Quick Reference

Quick reference guide for using the Morado design system.

## Import

```typescript
// Import everything
import * from '@/styles';

// Import specific items
import { spacing, colors, widgetStyles } from '@/styles/design-system';
import { useWidgetStyles } from '@/composables/useWidgetStyles';
```

## CSS Classes

### Widget Classes
```html
<!-- Basic widget -->
<div class="widget">...</div>

<!-- Widget with hover effect -->
<div class="widget widget-hoverable">...</div>

<!-- Mobile-optimized widget -->
<div class="widget widget-mobile">...</div>
```

### Card Classes
```html
<!-- Basic card -->
<div class="card">...</div>

<!-- Card with hover effect -->
<div class="card card-hoverable">...</div>
```

### Header Classes
```html
<div class="widget-header">
  <h3 class="widget-title">Title</h3>
  <p class="widget-subtitle">Subtitle</p>
</div>
```

### Layout Classes
```html
<!-- Empty state -->
<div class="empty-state">
  <svg class="empty-state-icon">...</svg>
  <p class="empty-state-text">No data</p>
</div>

<!-- Chart container -->
<div class="chart-container">
  <div class="chart-wrapper">...</div>
</div>

<!-- Legend -->
<div class="legend-container">
  <div class="legend-item">
    <span class="legend-color" style="background: #3B82F6"></span>
    <span class="legend-label">Label</span>
    <span class="legend-value">123</span>
  </div>
</div>
```

## Composable Usage

```vue
<script setup>
import { useWidgetStyles } from '@/composables/useWidgetStyles';

const { widgetClasses, widgetStyle, headerStyle } = useWidgetStyles({
  hoverable: true,
  mobile: false,
  minHeight: '300px',
});
</script>

<template>
  <div :class="widgetClasses" :style="widgetStyle">
    <h3 :style="headerStyle">Title</h3>
  </div>
</template>
```

## Design Tokens

### Spacing
```typescript
spacing.xs    // 0.25rem (4px)
spacing.sm    // 0.5rem (8px)
spacing.md    // 1rem (16px)
spacing.lg    // 1.5rem (24px)
spacing.xl    // 2rem (32px)
spacing['2xl'] // 3rem (48px)
spacing['3xl'] // 4rem (64px)

// Widget-specific
widgetSpacing.padding        // 1.5rem (24px)
widgetSpacing.paddingMobile  // 1rem (16px)
widgetSpacing.gap            // 1.5rem (24px)
widgetSpacing.headerMargin   // 1rem (16px)
```

### Border Radius
```typescript
borderRadius.sm   // 0.25rem (4px)
borderRadius.md   // 0.5rem (8px)
borderRadius.lg   // 0.75rem (12px)
borderRadius.xl   // 1rem (16px)
borderRadius.full // 9999px (circle)

// Component-specific
componentRadius.card    // 0.75rem (12px)
componentRadius.button  // 0.5rem (8px)
componentRadius.badge   // 0.5rem (8px)
componentRadius.avatar  // 9999px (circle)
```

### Shadows
```typescript
shadows.sm   // Subtle shadow
shadows.md   // Default shadow
shadows.lg   // Elevated shadow
shadows.xl   // High elevation
shadows['2xl'] // Maximum elevation

// Component-specific
componentShadows.card        // Default card shadow
componentShadows.cardHover   // Card hover shadow
componentShadows.widget      // Widget shadow
componentShadows.widgetHover // Widget hover shadow
componentShadows.dropdown    // Dropdown shadow
componentShadows.modal       // Modal shadow
```

### Colors
```typescript
// Primary colors
colors.blue    // #3B82F6
colors.green   // #10B981
colors.orange  // #F59E0B
colors.red     // #EF4444
colors.purple  // #8B5CF6

// Semantic colors
colors.success // #10B981
colors.warning // #F59E0B
colors.error   // #EF4444
colors.info    // #3B82F6

// Gray scale
colors.gray[50]  // Lightest
colors.gray[500] // Medium
colors.gray[900] // Darkest

// Chart colors
chartColors.primary    // Blue
chartColors.secondary  // Green
chartColors.tertiary   // Orange
chartColors.quaternary // Red
chartColors.quinary    // Purple
```

### Typography
```typescript
// Font sizes
fontSize.xs    // 0.75rem (12px)
fontSize.sm    // 0.875rem (14px)
fontSize.base  // 1rem (16px)
fontSize.lg    // 1.125rem (18px)
fontSize.xl    // 1.25rem (20px)
fontSize['2xl'] // 1.5rem (24px)
fontSize['3xl'] // 1.875rem (30px)
fontSize['4xl'] // 2.25rem (36px)

// Font weights
fontWeight.normal   // 400
fontWeight.medium   // 500
fontWeight.semibold // 600
fontWeight.bold     // 700

// Typography presets
typography.h1        // { fontSize: '1.875rem', fontWeight: '700', lineHeight: '1.25' }
typography.h2        // { fontSize: '1.5rem', fontWeight: '700', lineHeight: '1.25' }
typography.h3        // { fontSize: '1.25rem', fontWeight: '600', lineHeight: '1.25' }
typography.body      // { fontSize: '1rem', fontWeight: '400', lineHeight: '1.5' }
typography.caption   // { fontSize: '0.75rem', fontWeight: '400', lineHeight: '1.5' }
```

### Transitions
```typescript
// Durations
transitionDuration.fast   // 150ms
transitionDuration.normal // 300ms
transitionDuration.slow   // 500ms

// Presets
transitions.default   // all 300ms ease
transitions.fast      // all 150ms ease
transitions.shadow    // box-shadow 300ms ease
transitions.transform // transform 300ms ease
```

## Utility Functions

```typescript
import {
  getSpacing,
  getBorderRadius,
  getShadow,
  getColor,
  getFontSize,
  getFontWeight,
} from '@/composables/useWidgetStyles';

// Get values
const padding = getSpacing('padding');        // '1.5rem'
const radius = getBorderRadius('card');       // '0.75rem'
const shadow = getShadow('card');             // '0 4px 6px...'
const color = getColor('blue');               // '#3B82F6'
const nestedColor = getColor('gray.500');     // '#6B7280'
const size = getFontSize('lg');               // '1.125rem'
const weight = getFontWeight('semibold');     // '600'
```

## Common Patterns

### Standard Widget
```vue
<template>
  <div class="widget widget-hoverable">
    <div class="widget-header">
      <h3 class="widget-title">{{ title }}</h3>
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

## Responsive Breakpoints

```typescript
breakpoints.sm   // 640px
breakpoints.md   // 768px
breakpoints.lg   // 1024px
breakpoints.xl   // 1280px
breakpoints['2xl'] // 1536px
```

### Responsive CSS
```css
/* Mobile first */
.widget {
  padding: 1rem;
}

/* Tablet and up */
@media (min-width: 768px) {
  .widget {
    padding: 1.5rem;
  }
}
```

## Z-Index Scale

```typescript
zIndex.base          // 0
zIndex.dropdown      // 1000
zIndex.sticky        // 1020
zIndex.fixed         // 1030
zIndex.modalBackdrop // 1040
zIndex.modal         // 1050
zIndex.popover       // 1060
zIndex.tooltip       // 1070
```

## Best Practices

1. **Always use design tokens** instead of hardcoded values
2. **Use CSS classes** for simple cases
3. **Use composables** for dynamic styling
4. **Follow mobile-first** approach for responsive design
5. **Maintain consistency** across all components
6. **Test accessibility** with keyboard navigation
7. **Document custom patterns** in this guide

## Need Help?

- See `src/styles/README.md` for detailed documentation
- Check `src/components/common/DesignSystemExample.vue` for live examples
- Run tests: `bun run test:run --dir src/styles`
