/**
 * Widget Styles Composable
 *
 * Provides consistent styling utilities for dashboard widgets.
 * This composable ensures all widgets follow the design system standards.
 *
 * Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
 */

import { type CSSProperties, computed } from 'vue';
import {
  colors,
  componentRadius,
  componentShadows,
  fontSize,
  fontWeight,
  transitions,
  widgetHeaderStyles,
  widgetSpacing,
  widgetStyles,
} from '@/styles/design-system';

/**
 * Options for widget styling
 */
export interface WidgetStyleOptions {
  /**
   * Whether to apply hover effects
   * @default true
   */
  hoverable?: boolean;

  /**
   * Whether to use mobile padding
   * @default false
   */
  mobile?: boolean;

  /**
   * Custom background color
   * @default '#FFFFFF'
   */
  backgroundColor?: string;

  /**
   * Minimum height for the widget
   */
  minHeight?: string;
}

/**
 * Composable for consistent widget styling
 *
 * @example
 * ```vue
 * <script setup>
 * import { useWidgetStyles } from '@/composables/useWidgetStyles';
 *
 * const { widgetClasses, widgetStyle } = useWidgetStyles();
 * </script>
 *
 * <template>
 *   <div :class="widgetClasses" :style="widgetStyle">
 *     <!-- Widget content -->
 *   </div>
 * </template>
 * ```
 */
export function useWidgetStyles(options: WidgetStyleOptions = {}) {
  const {
    hoverable = true,
    mobile = false,
    backgroundColor = widgetStyles.backgroundColor,
    minHeight,
  } = options;

  /**
   * Base widget classes
   */
  const widgetClasses = computed(() => {
    const classes = ['widget'];

    if (hoverable) {
      classes.push('widget-hoverable');
    }

    if (mobile) {
      classes.push('widget-mobile');
    }

    return classes;
  });

  /**
   * Widget inline styles
   */
  const widgetStyle = computed<CSSProperties>(() => {
    const padding = mobile ? widgetStyles.paddingMobile : widgetStyles.padding;

    return {
      backgroundColor,
      borderRadius: widgetStyles.borderRadius,
      boxShadow: widgetStyles.boxShadow,
      padding,
      transition: widgetStyles.transition,
      ...(minHeight && { minHeight }),
    };
  });

  /**
   * Widget header styles
   */
  const headerStyle = computed<CSSProperties>(() => ({
    marginBottom: widgetHeaderStyles.marginBottom,
    fontSize: widgetHeaderStyles.fontSize,
    fontWeight: widgetHeaderStyles.fontWeight,
    color: widgetHeaderStyles.color,
  }));

  return {
    widgetClasses,
    widgetStyle,
    headerStyle,
  };
}

/**
 * Composable for consistent card styling
 * Similar to widget but with slightly different defaults
 */
export function useCardStyles(options: WidgetStyleOptions = {}) {
  return useWidgetStyles({
    hoverable: true,
    ...options,
  });
}

/**
 * Get consistent spacing value
 *
 * @param size - Spacing size key
 * @returns CSS spacing value
 */
export function getSpacing(size: keyof typeof widgetSpacing): string {
  return widgetSpacing[size];
}

/**
 * Get consistent border radius value
 *
 * @param size - Border radius size key
 * @returns CSS border radius value
 */
export function getBorderRadius(size: keyof typeof componentRadius): string {
  return componentRadius[size];
}

/**
 * Get consistent shadow value
 *
 * @param size - Shadow size key
 * @returns CSS box-shadow value
 */
export function getShadow(size: keyof typeof componentShadows): string {
  return componentShadows[size];
}

/**
 * Get consistent transition value
 *
 * @param type - Transition type key
 * @returns CSS transition value
 */
export function getTransition(type: keyof typeof transitions): string {
  return transitions[type];
}

/**
 * Get consistent color value
 *
 * @param color - Color key
 * @returns CSS color value
 */
export function getColor(color: string): string {
  // Handle nested color objects (e.g., 'gray.500')
  if (color.includes('.')) {
    const [colorName, shadeStr] = color.split('.');
    const colorObj = colors[colorName as keyof typeof colors];
    if (typeof colorObj === 'object' && shadeStr) {
      const shade = Number.parseInt(shadeStr, 10) as keyof typeof colorObj;
      if (shade in colorObj) {
        return colorObj[shade];
      }
    }
  }

  // Handle direct color keys
  if (color in colors) {
    const colorValue = colors[color as keyof typeof colors];
    return typeof colorValue === 'string' ? colorValue : colorValue[500];
  }

  return color; // Return as-is if not found
}

/**
 * Get consistent font size value
 *
 * @param size - Font size key
 * @returns CSS font-size value
 */
export function getFontSize(size: keyof typeof fontSize): string {
  return fontSize[size];
}

/**
 * Get consistent font weight value
 *
 * @param weight - Font weight key
 * @returns CSS font-weight value
 */
export function getFontWeight(weight: keyof typeof fontWeight): string {
  return fontWeight[weight];
}

/**
 * Utility class names for consistent styling
 * These can be used directly in templates
 */
export const utilityClasses = {
  // Widget classes
  widget: 'bg-white rounded-lg shadow-md transition-shadow duration-300',
  widgetHoverable: 'hover:shadow-lg hover:-translate-y-0.5',
  widgetHeader: 'text-lg font-semibold text-gray-800 mb-4',

  // Card classes
  card: 'bg-white rounded-lg shadow-md p-6',
  cardHoverable: 'hover:shadow-lg transition-shadow duration-300',

  // Spacing classes
  widgetPadding: 'p-6',
  widgetPaddingMobile: 'p-4',
  widgetGap: 'gap-6',
  widgetGapMobile: 'gap-4',

  // Common patterns
  flexCenter: 'flex items-center justify-center',
  flexBetween: 'flex items-center justify-between',
  gridResponsive: 'grid grid-cols-1 md:grid-cols-2 gap-6',
} as const;
