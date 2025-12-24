/**
 * Design System Constants
 *
 * This file defines the core design tokens for the Morado dashboard.
 * All spacing, colors, shadows, and other visual properties should reference
 * these constants to ensure visual consistency across the application.
 *
 * Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
 */

// ============================================================================
// Spacing System
// ============================================================================

/**
 * Spacing scale based on 4px base unit
 * Use these values for padding, margin, and gap properties
 */
export const spacing = {
  xs: '0.25rem', // 4px
  sm: '0.5rem', // 8px
  md: '1rem', // 16px
  lg: '1.5rem', // 24px
  xl: '2rem', // 32px
  '2xl': '3rem', // 48px
  '3xl': '4rem', // 64px
} as const;

/**
 * Widget-specific spacing
 */
export const widgetSpacing = {
  padding: spacing.lg, // 24px - Standard widget padding
  paddingMobile: spacing.md, // 16px - Mobile widget padding
  gap: spacing.lg, // 24px - Gap between widgets
  gapMobile: spacing.md, // 16px - Mobile gap between widgets
  headerMargin: spacing.md, // 16px - Space below widget headers
} as const;

// ============================================================================
// Border Radius
// ============================================================================

/**
 * Border radius scale for consistent rounded corners
 */
export const borderRadius = {
  none: '0',
  sm: '0.25rem', // 4px
  md: '0.5rem', // 8px
  lg: '0.75rem', // 12px
  xl: '1rem', // 16px
  full: '9999px', // Fully rounded (circles)
} as const;

/**
 * Component-specific border radius
 */
export const componentRadius = {
  card: borderRadius.lg, // 12px - Cards and widgets
  button: borderRadius.md, // 8px - Buttons
  badge: borderRadius.md, // 8px - Badges and tags
  avatar: borderRadius.full, // Fully rounded - Avatars
  input: borderRadius.md, // 8px - Input fields
} as const;

// ============================================================================
// Shadows
// ============================================================================

/**
 * Shadow scale for depth and elevation
 */
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
} as const;

/**
 * Component-specific shadows
 */
export const componentShadows = {
  card: shadows.md, // Default card shadow
  cardHover: shadows.lg, // Card shadow on hover
  widget: shadows.md, // Widget shadow
  widgetHover: shadows.lg, // Widget shadow on hover
  dropdown: shadows.lg, // Dropdown menus
  modal: shadows.xl, // Modal dialogs
} as const;

// ============================================================================
// Typography
// ============================================================================

/**
 * Font size scale
 */
export const fontSize = {
  xs: '0.75rem', // 12px
  sm: '0.875rem', // 14px
  base: '1rem', // 16px
  lg: '1.125rem', // 18px
  xl: '1.25rem', // 20px
  '2xl': '1.5rem', // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
} as const;

/**
 * Font weight scale
 */
export const fontWeight = {
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
} as const;

/**
 * Line height scale
 */
export const lineHeight = {
  tight: '1.25',
  normal: '1.5',
  relaxed: '1.75',
} as const;

/**
 * Typography presets for common text styles
 */
export const typography = {
  h1: {
    fontSize: fontSize['3xl'],
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.tight,
  },
  h2: {
    fontSize: fontSize['2xl'],
    fontWeight: fontWeight.bold,
    lineHeight: lineHeight.tight,
  },
  h3: {
    fontSize: fontSize.xl,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.tight,
  },
  h4: {
    fontSize: fontSize.lg,
    fontWeight: fontWeight.semibold,
    lineHeight: lineHeight.normal,
  },
  body: {
    fontSize: fontSize.base,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
  },
  bodySmall: {
    fontSize: fontSize.sm,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
  },
  caption: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.normal,
    lineHeight: lineHeight.normal,
  },
} as const;

// ============================================================================
// Colors
// ============================================================================

/**
 * Color palette - extends Tailwind's default colors
 * These colors are used for data visualization and UI elements
 */
export const colors = {
  // Primary colors for data visualization
  blue: '#3B82F6',
  green: '#10B981',
  orange: '#F59E0B',
  red: '#EF4444',
  purple: '#8B5CF6',

  // Semantic colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Neutral colors
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
} as const;

/**
 * Chart color scheme for consistent data visualization
 */
export const chartColors = {
  primary: colors.blue,
  secondary: colors.green,
  tertiary: colors.orange,
  quaternary: colors.red,
  quinary: colors.purple,
} as const;

// ============================================================================
// Transitions
// ============================================================================

/**
 * Transition duration scale
 */
export const transitionDuration = {
  fast: '150ms',
  normal: '300ms',
  slow: '500ms',
} as const;

/**
 * Transition timing functions
 */
export const transitionTiming = {
  ease: 'ease',
  easeIn: 'ease-in',
  easeOut: 'ease-out',
  easeInOut: 'ease-in-out',
  linear: 'linear',
} as const;

/**
 * Common transition presets
 */
export const transitions = {
  default: `all ${transitionDuration.normal} ${transitionTiming.ease}`,
  fast: `all ${transitionDuration.fast} ${transitionTiming.ease}`,
  slow: `all ${transitionDuration.slow} ${transitionTiming.ease}`,
  shadow: `box-shadow ${transitionDuration.normal} ${transitionTiming.ease}`,
  transform: `transform ${transitionDuration.normal} ${transitionTiming.ease}`,
} as const;

// ============================================================================
// Breakpoints
// ============================================================================

/**
 * Responsive breakpoints (matches Tailwind defaults)
 */
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ============================================================================
// Z-Index Scale
// ============================================================================

/**
 * Z-index scale for layering
 */
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
} as const;

// ============================================================================
// Widget Styles
// ============================================================================

/**
 * Standard widget style configuration
 * Use this for all dashboard widgets to ensure consistency
 */
export const widgetStyles = {
  backgroundColor: '#FFFFFF',
  borderRadius: componentRadius.card,
  boxShadow: componentShadows.widget,
  padding: widgetSpacing.padding,
  paddingMobile: widgetSpacing.paddingMobile,
  transition: transitions.shadow,

  // Hover state
  hover: {
    boxShadow: componentShadows.widgetHover,
    transform: 'translateY(-2px)',
  },
} as const;

/**
 * Widget header styles
 */
export const widgetHeaderStyles = {
  marginBottom: widgetSpacing.headerMargin,
  fontSize: fontSize.lg,
  fontWeight: fontWeight.semibold,
  color: colors.gray[800],
} as const;

// ============================================================================
// Type Exports
// ============================================================================

export type Spacing = keyof typeof spacing;
export type BorderRadius = keyof typeof borderRadius;
export type Shadow = keyof typeof shadows;
export type FontSize = keyof typeof fontSize;
export type FontWeight = keyof typeof fontWeight;
export type Color = keyof typeof colors;
export type TransitionDuration = keyof typeof transitionDuration;
export type Breakpoint = keyof typeof breakpoints;
