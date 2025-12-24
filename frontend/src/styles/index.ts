/**
 * Design System Exports
 *
 * Central export point for all design system utilities.
 * Import from this file to access design tokens and utilities.
 *
 * @example
 * ```typescript
 * import { spacing, colors, widgetStyles } from '@/styles';
 * ```
 */

// Export composables
export * from '../composables/useWidgetStyles';
// Export all design system constants
export * from './design-system';

// Re-export commonly used values for convenience
export {
  borderRadius,
  breakpoints,
  chartColors,
  colors,
  componentRadius,
  componentShadows,
  fontSize,
  fontWeight,
  lineHeight,
  shadows,
  spacing,
  transitionDuration,
  transitions,
  transitionTiming,
  typography,
  widgetHeaderStyles,
  widgetSpacing,
  widgetStyles,
  zIndex,
} from './design-system';
