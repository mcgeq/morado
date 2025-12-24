/**
 * useLocale Composable
 * 
 * Provides locale management functionality including:
 * - Current locale state
 * - Locale switching
 * - Locale-aware date formatting
 * - Locale-aware number formatting
 */

import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { LOCALES, setStoredLocale, type Locale } from '@/i18n';

export function useLocale() {
  const { locale, t, d, n } = useI18n();

  /**
   * Current locale
   */
  const currentLocale = computed<Locale>(() => locale.value as Locale);

  /**
   * Available locales
   */
  const availableLocales = computed(() => Object.values(LOCALES));

  /**
   * Current locale label
   */
  const currentLocaleLabel = computed(() => LOCALES[currentLocale.value]?.label || '');

  /**
   * Switch to a different locale
   */
  function switchLocale(newLocale: Locale): void {
    if (newLocale === locale.value) return;
    
    locale.value = newLocale;
    setStoredLocale(newLocale);
    
    // Update document language attribute
    if (typeof document !== 'undefined') {
      document.documentElement.lang = newLocale;
    }
  }

  /**
   * Format date with current locale
   */
  function formatDate(date: Date | string | number, format: 'short' | 'long' = 'long'): string {
    try {
      const dateObj = date instanceof Date ? date : new Date(date);
      return d(dateObj, format);
    } catch (error) {
      console.error('Failed to format date:', error);
      return String(date);
    }
  }

  /**
   * Format number with current locale
   */
  function formatNumber(value: number, format: 'decimal' | 'percent' | 'currency' = 'decimal'): string {
    try {
      return n(value, format);
    } catch (error) {
      console.error('Failed to format number:', error);
      return String(value);
    }
  }

  /**
   * Format number with thousand separators (legacy support)
   */
  function formatNumberWithSeparator(value: number): string {
    return formatNumber(value, 'decimal');
  }

  return {
    // State
    currentLocale,
    currentLocaleLabel,
    availableLocales,
    
    // Methods
    switchLocale,
    formatDate,
    formatNumber,
    formatNumberWithSeparator,
    
    // i18n methods
    t,
    d,
    n,
  };
}
