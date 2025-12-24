/**
 * Prop Validation Utilities Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  validateNonNegativeNumber,
  validatePercentage,
  validateNonEmptyString,
  validateDateString,
  validateHexColor,
  validateNonEmptyArray,
  validateChartDataset,
  validateAreaChartSeries,
} from './propValidation';

describe('propValidation', () => {
  let consoleWarnSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleWarnSpy.mockRestore();
  });

  describe('validateNonNegativeNumber', () => {
    it('should return true for valid non-negative numbers', () => {
      expect(validateNonNegativeNumber(0, 'test')).toBe(true);
      expect(validateNonNegativeNumber(42, 'test')).toBe(true);
      expect(validateNonNegativeNumber(3.14, 'test')).toBe(true);
    });

    it('should return false for negative numbers', () => {
      expect(validateNonNegativeNumber(-1, 'test')).toBe(false);
      expect(validateNonNegativeNumber(-100, 'test')).toBe(false);
    });

    it('should return false for NaN', () => {
      expect(validateNonNegativeNumber(Number.NaN, 'test')).toBe(false);
    });

    it('should return false for non-numbers', () => {
      expect(validateNonNegativeNumber('42' as any, 'test')).toBe(false);
      expect(validateNonNegativeNumber(null as any, 'test')).toBe(false);
      expect(validateNonNegativeNumber(undefined as any, 'test')).toBe(false);
    });
  });

  describe('validatePercentage', () => {
    it('should return true for valid percentages', () => {
      expect(validatePercentage(0, 'test')).toBe(true);
      expect(validatePercentage(50, 'test')).toBe(true);
      expect(validatePercentage(100, 'test')).toBe(true);
    });

    it('should return false for values > 100', () => {
      expect(validatePercentage(101, 'test')).toBe(false);
      expect(validatePercentage(200, 'test')).toBe(false);
    });

    it('should return false for negative values', () => {
      expect(validatePercentage(-1, 'test')).toBe(false);
    });
  });

  describe('validateNonEmptyString', () => {
    it('should return true for non-empty strings', () => {
      expect(validateNonEmptyString('hello', 'test')).toBe(true);
      expect(validateNonEmptyString('  text  ', 'test')).toBe(true);
    });

    it('should return false for empty strings', () => {
      expect(validateNonEmptyString('', 'test')).toBe(false);
      expect(validateNonEmptyString('   ', 'test')).toBe(false);
    });

    it('should return false for non-strings', () => {
      expect(validateNonEmptyString(42 as any, 'test')).toBe(false);
      expect(validateNonEmptyString(null as any, 'test')).toBe(false);
    });
  });

  describe('validateDateString', () => {
    it('should return true for valid date strings', () => {
      expect(validateDateString('2024-01-01', 'test')).toBe(true);
      expect(validateDateString('2024-01-01T12:00:00Z', 'test')).toBe(true);
    });

    it('should return false for invalid date strings', () => {
      expect(validateDateString('not-a-date', 'test')).toBe(false);
      expect(validateDateString('2024-13-01', 'test')).toBe(false);
    });

    it('should return false for non-strings', () => {
      expect(validateDateString(new Date() as any, 'test')).toBe(false);
    });
  });

  describe('validateHexColor', () => {
    it('should return true for valid hex colors', () => {
      expect(validateHexColor('#000000', 'test')).toBe(true);
      expect(validateHexColor('#FFF', 'test')).toBe(true);
      expect(validateHexColor('#3B82F6', 'test')).toBe(true);
    });

    it('should return false for invalid hex colors', () => {
      expect(validateHexColor('000000', 'test')).toBe(false);
      expect(validateHexColor('#GGG', 'test')).toBe(false);
      expect(validateHexColor('rgb(0,0,0)', 'test')).toBe(false);
    });
  });

  describe('validateNonEmptyArray', () => {
    it('should return true for non-empty arrays', () => {
      expect(validateNonEmptyArray([1, 2, 3], 'test')).toBe(true);
      expect(validateNonEmptyArray(['a'], 'test')).toBe(true);
    });

    it('should return false for empty arrays', () => {
      expect(validateNonEmptyArray([], 'test')).toBe(false);
    });

    it('should return false for non-arrays', () => {
      expect(validateNonEmptyArray('not-array' as any, 'test')).toBe(false);
      expect(validateNonEmptyArray(null as any, 'test')).toBe(false);
    });
  });

  describe('validateChartDataset', () => {
    it('should return true for valid chart datasets', () => {
      const dataset = {
        label: 'Test',
        value: 42,
        color: '#3B82F6',
      };
      expect(validateChartDataset(dataset, 'test')).toBe(true);
    });

    it('should return false for invalid datasets', () => {
      expect(validateChartDataset(null, 'test')).toBe(false);
      expect(validateChartDataset({ label: '', value: 42, color: '#000' }, 'test')).toBe(false);
      expect(validateChartDataset({ label: 'Test', value: -1, color: '#000' }, 'test')).toBe(false);
    });
  });

  describe('validateAreaChartSeries', () => {
    it('should return true for valid series', () => {
      const series = {
        name: 'Test Series',
        data: [1, 2, 3, 4],
        color: '#3B82F6',
      };
      expect(validateAreaChartSeries(series, 'test')).toBe(true);
    });

    it('should return false for invalid series', () => {
      expect(validateAreaChartSeries(null, 'test')).toBe(false);
      expect(validateAreaChartSeries({ name: '', data: [1, 2], color: '#000' }, 'test')).toBe(false);
      expect(validateAreaChartSeries({ name: 'Test', data: [-1, 2], color: '#000' }, 'test')).toBe(false);
    });
  });
});
