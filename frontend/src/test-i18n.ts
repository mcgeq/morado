/**
 * Test i18n setup
 * Run this file to verify i18n is working correctly
 */

import { createI18n } from 'vue-i18n';
import enUS from './i18n/locales/en-US';
import zhCN from './i18n/locales/zh-CN';

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
});

const { t } = i18n.global;

console.log('=== Testing i18n ===');
console.log('Chinese (zh-CN):');
console.log('  common.loading:', t('common.loading'));
console.log('  dashboard.title:', t('dashboard.title'));
console.log('  user.totalExecutions:', t('user.totalExecutions'));
console.log('  steps.title:', t('steps.title'));
console.log('  api.title:', t('api.title'));
console.log('  trend.title:', t('trend.title'));

i18n.global.locale.value = 'en-US';
console.log('\nEnglish (en-US):');
console.log('  common.loading:', t('common.loading'));
console.log('  dashboard.title:', t('dashboard.title'));
console.log('  user.totalExecutions:', t('user.totalExecutions'));
console.log('  steps.title:', t('steps.title'));
console.log('  api.title:', t('api.title'));
console.log('  trend.title:', t('trend.title'));

console.log('\n=== i18n test complete ===');
