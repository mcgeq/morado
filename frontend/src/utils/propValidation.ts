/**
 * Prop Validation Utilities
 * 
 * Provides runtime validation helpers for Vue component props
 * with development-mode warnings and fallback handling.
 */

/**
 * Validate that a value is a non-negative number
 */
export function validateNonNegativeNumber(value: unknown, propName: string): boolean {
  if (typeof value !== 'number') {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be a number, received ${typeof value}`);
    }
    return false;
  }

  if (Number.isNaN(value)) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} is NaN`);
    }
    return false;
  }

  if (value < 0) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be non-negative, received ${value}`);
    }
    return false;
  }

  return true;
}

/**
 * Validate that a value is a percentage (0-100)
 */
export function validatePercentage(value: unknown, propName: string): boolean {
  if (!validateNonNegativeNumber(value, propName)) {
    return false;
  }

  const numValue = value as number;
  if (numValue > 100) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be between 0 and 100, received ${numValue}`);
    }
    return false;
  }

  return true;
}

/**
 * Validate that a value is a non-empty string
 */
export function validateNonEmptyString(value: unknown, propName: string): boolean {
  if (typeof value !== 'string') {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be a string, received ${typeof value}`);
    }
    return false;
  }

  if (value.trim().length === 0) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} cannot be empty`);
    }
    return false;
  }

  return true;
}

/**
 * Validate that a value is a valid date string
 */
export function validateDateString(value: unknown, propName: string): boolean {
  if (typeof value !== 'string') {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be a string, received ${typeof value}`);
    }
    return false;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} is not a valid date string: ${value}`);
    }
    return false;
  }

  return true;
}

/**
 * Validate that a value is a valid hex color
 */
export function validateHexColor(value: unknown, propName: string): boolean {
  if (typeof value !== 'string') {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be a string, received ${typeof value}`);
    }
    return false;
  }

  const hexColorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  if (!hexColorRegex.test(value)) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} is not a valid hex color: ${value}`);
    }
    return false;
  }

  return true;
}

/**
 * Validate that an array is non-empty
 */
export function validateNonEmptyArray(value: unknown, propName: string): boolean {
  if (!Array.isArray(value)) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be an array, received ${typeof value}`);
    }
    return false;
  }

  if (value.length === 0) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} cannot be empty`);
    }
    return false;
  }

  return true;
}

/**
 * Validate chart dataset structure
 */
export function validateChartDataset(dataset: unknown, propName: string): boolean {
  if (!dataset || typeof dataset !== 'object') {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be an object`);
    }
    return false;
  }

  const ds = dataset as any;

  if (!validateNonEmptyString(ds.label, `${propName}.label`)) {
    return false;
  }

  if (!validateNonNegativeNumber(ds.value, `${propName}.value`)) {
    return false;
  }

  if (!validateNonEmptyString(ds.color, `${propName}.color`)) {
    return false;
  }

  return true;
}

/**
 * Validate area chart series structure
 */
export function validateAreaChartSeries(series: unknown, propName: string): boolean {
  if (!series || typeof series !== 'object') {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName} must be an object`);
    }
    return false;
  }

  const s = series as any;

  if (!validateNonEmptyString(s.name, `${propName}.name`)) {
    return false;
  }

  if (!Array.isArray(s.data)) {
    if (import.meta.env.DEV) {
      console.warn(`[PropValidation] ${propName}.data must be an array`);
    }
    return false;
  }

  if (!s.data.every((v: unknown, i: number) => validateNonNegativeNumber(v, `${propName}.data[${i}]`))) {
    return false;
  }

  if (!validateNonEmptyString(s.color, `${propName}.color`)) {
    return false;
  }

  return true;
}

/**
 * Create a prop validator function for Vue props
 */
export function createPropValidator<T>(
  validatorFn: (value: T, propName: string) => boolean,
  propName: string,
) {
  return (value: T): boolean => {
    return validatorFn(value, propName);
  };
}
