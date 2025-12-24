/**
 * i18n Configuration
 * 
 * This file sets up vue-i18n for internationalization support.
 * Supports Chinese (Simplified) and English (US) locales.
 */

import { createI18n } from 'vue-i18n';
import enUS from './locales/en-US';
import zhCN from './locales/zh-CN';

// Type-safe locale keys
export type Locale = 'zh-CN' | 'en-US';

// Available locales
export const LOCALES: Record<Locale, { name: string; label: string }> = {
  'zh-CN': { name: 'zh-CN', label: '简体中文' },
  'en-US': { name: 'en-US', label: 'English (US)' },
};

// Default locale
const DEFAULT_LOCALE: Locale = 'zh-CN';

// Get stored locale from localStorage or use default
function getStoredLocale(): Locale {
  try {
    const stored = localStorage.getItem('app-locale');
    if (stored && (stored === 'zh-CN' || stored === 'en-US')) {
      return stored as Locale;
    }
  } catch (error) {
    console.warn('Failed to read locale from localStorage:', error);
  }
  return DEFAULT_LOCALE;
}

// Store locale to localStorage
export function setStoredLocale(locale: Locale): void {
  try {
    localStorage.setItem('app-locale', locale);
  } catch (error) {
    console.warn('Failed to save locale to localStorage:', error);
  }
}

// Create i18n instance
const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: getStoredLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
  datetimeFormats: {
    'zh-CN': {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      },
      long: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      },
    },
    'en-US': {
      short: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      },
      long: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      },
    },
  },
  numberFormats: {
    'zh-CN': {
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      },
      percent: {
        style: 'percent',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      },
      currency: {
        style: 'currency',
        currency: 'CNY',
        currencyDisplay: 'symbol',
      },
    },
    'en-US': {
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      },
      percent: {
        style: 'percent',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      },
      currency: {
        style: 'currency',
        currency: 'USD',
        currencyDisplay: 'symbol',
      },
    },
  },
});

export default i18n;
