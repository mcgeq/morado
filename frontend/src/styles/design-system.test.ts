/**
 * Design System Tests
 * 
 * Tests for design system constants and utilities
 */

import { describe, it, expect } from 'vitest';
import {
  spacing,
  widgetSpacing,
  borderRadius,
  componentRadius,
  shadows,
  componentShadows,
  fontSize,
  fontWeight,
  colors,
  chartColors,
  widgetStyles,
} from './design-system';

describe('Design System Constants', () => {
  describe('Spacing', () => {
    it('should have consistent spacing values', () => {
      expect(spacing.xs).toBe('0.25rem');
      expect(spacing.sm).toBe('0.5rem');
      expect(spacing.md).toBe('1rem');
      expect(spacing.lg).toBe('1.5rem');
      expect(spacing.xl).toBe('2rem');
    });

    it('should have widget-specific spacing', () => {
      expect(widgetSpacing.padding).toBe(spacing.lg);
      expect(widgetSpacing.paddingMobile).toBe(spacing.md);
      expect(widgetSpacing.gap).toBe(spacing.lg);
    });
  });

  describe('Border Radius', () => {
    it('should have consistent border radius values', () => {
      expect(borderRadius.sm).toBe('0.25rem');
      expect(borderRadius.md).toBe('0.5rem');
      expect(borderRadius.lg).toBe('0.75rem');
      expect(borderRadius.xl).toBe('1rem');
    });

    it('should have component-specific border radius', () => {
      expect(componentRadius.card).toBe(borderRadius.lg);
      expect(componentRadius.button).toBe(borderRadius.md);
      expect(componentRadius.avatar).toBe(borderRadius.full);
    });
  });

  describe('Shadows', () => {
    it('should have shadow values', () => {
      expect(shadows.none).toBe('none');
      expect(shadows.sm).toBeDefined();
      expect(shadows.md).toBeDefined();
      expect(shadows.lg).toBeDefined();
    });

    it('should have component-specific shadows', () => {
      expect(componentShadows.card).toBe(shadows.md);
      expect(componentShadows.cardHover).toBe(shadows.lg);
      expect(componentShadows.widget).toBe(shadows.md);
    });
  });

  describe('Typography', () => {
    it('should have font size values', () => {
      expect(fontSize.xs).toBe('0.75rem');
      expect(fontSize.sm).toBe('0.875rem');
      expect(fontSize.base).toBe('1rem');
      expect(fontSize.lg).toBe('1.125rem');
    });

    it('should have font weight values', () => {
      expect(fontWeight.normal).toBe('400');
      expect(fontWeight.medium).toBe('500');
      expect(fontWeight.semibold).toBe('600');
      expect(fontWeight.bold).toBe('700');
    });
  });

  describe('Colors', () => {
    it('should have primary colors', () => {
      expect(colors.blue).toBe('#3B82F6');
      expect(colors.green).toBe('#10B981');
      expect(colors.orange).toBe('#F59E0B');
      expect(colors.red).toBe('#EF4444');
      expect(colors.purple).toBe('#8B5CF6');
    });

    it('should have semantic colors', () => {
      expect(colors.success).toBe('#10B981');
      expect(colors.warning).toBe('#F59E0B');
      expect(colors.error).toBe('#EF4444');
      expect(colors.info).toBe('#3B82F6');
    });

    it('should have gray scale', () => {
      expect(colors.gray[50]).toBeDefined();
      expect(colors.gray[500]).toBeDefined();
      expect(colors.gray[900]).toBeDefined();
    });

    it('should have chart colors', () => {
      expect(chartColors.primary).toBe(colors.blue);
      expect(chartColors.secondary).toBe(colors.green);
      expect(chartColors.tertiary).toBe(colors.orange);
    });
  });

  describe('Widget Styles', () => {
    it('should have consistent widget styles', () => {
      expect(widgetStyles.backgroundColor).toBe('#FFFFFF');
      expect(widgetStyles.borderRadius).toBe(componentRadius.card);
      expect(widgetStyles.boxShadow).toBe(componentShadows.widget);
      expect(widgetStyles.padding).toBe(widgetSpacing.padding);
    });

    it('should have hover state', () => {
      expect(widgetStyles.hover.boxShadow).toBe(componentShadows.widgetHover);
      expect(widgetStyles.hover.transform).toBe('translateY(-2px)');
    });
  });
});
