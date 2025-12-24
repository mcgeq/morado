<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 class="text-3xl font-bold mb-4">{{ t('dashboard.title') }}</h1>
        
        <div class="mb-6">
          <LanguageSwitcher />
        </div>

        <div class="space-y-4">
          <div class="border-b pb-4">
            <h2 class="text-xl font-semibold mb-2">Common Translations</h2>
            <ul class="space-y-2">
              <li><strong>Loading:</strong> {{ t('common.loading') }}</li>
              <li><strong>No Data:</strong> {{ t('common.noData') }}</li>
              <li><strong>Refresh:</strong> {{ t('common.refresh') }}</li>
              <li><strong>Retry:</strong> {{ t('common.retry') }}</li>
            </ul>
          </div>

          <div class="border-b pb-4">
            <h2 class="text-xl font-semibold mb-2">Dashboard Translations</h2>
            <ul class="space-y-2">
              <li><strong>Title:</strong> {{ t('dashboard.title') }}</li>
              <li><strong>Last Updated:</strong> {{ t('dashboard.lastUpdated') }}</li>
              <li><strong>Data Refreshed:</strong> {{ t('dashboard.dataRefreshed') }}</li>
            </ul>
          </div>

          <div class="border-b pb-4">
            <h2 class="text-xl font-semibold mb-2">User Translations</h2>
            <ul class="space-y-2">
              <li><strong>Total Executions:</strong> {{ t('user.totalExecutions') }}</li>
              <li><strong>Passed Tests:</strong> {{ t('user.passedTests') }}</li>
              <li><strong>Failed Tests:</strong> {{ t('user.failedTests') }}</li>
            </ul>
          </div>

          <div class="border-b pb-4">
            <h2 class="text-xl font-semibold mb-2">Widget Titles</h2>
            <ul class="space-y-2">
              <li><strong>Steps:</strong> {{ t('steps.title') }}</li>
              <li><strong>API:</strong> {{ t('api.title') }}</li>
              <li><strong>Trend:</strong> {{ t('trend.title') }}</li>
            </ul>
          </div>

          <div class="border-b pb-4">
            <h2 class="text-xl font-semibold mb-2">Date Formatting</h2>
            <ul class="space-y-2">
              <li><strong>Short:</strong> {{ formatDate(new Date(), 'short') }}</li>
              <li><strong>Long:</strong> {{ formatDate(new Date(), 'long') }}</li>
            </ul>
          </div>

          <div>
            <h2 class="text-xl font-semibold mb-2">Number Formatting</h2>
            <ul class="space-y-2">
              <li><strong>Decimal:</strong> {{ formatNumber(1234567.89, 'decimal') }}</li>
              <li><strong>With Separator:</strong> {{ formatNumberWithSeparator(1234567) }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          <strong>Current Locale:</strong> {{ currentLocale }} ({{ currentLocaleLabel }})
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { LanguageSwitcher } from '@/components/common';
  import { useLocale } from '@/composables/useLocale';

  const { t, currentLocale, currentLocaleLabel, formatDate, formatNumber, formatNumberWithSeparator } = useLocale();
</script>
