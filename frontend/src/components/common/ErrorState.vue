<template>
  <div class="error-state bg-white rounded-lg shadow-md p-6" role="alert" aria-live="assertive">
    <div class="flex flex-col items-center justify-center py-8">
      <!-- Error Icon -->
      <div class="error-icon mb-4">
        <svg
          class="w-16 h-16 text-red-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      <!-- Error Title -->
      <h3 class="text-lg font-semibold text-gray-800 mb-2" id="error-title">{{ title || t('error.loadFailed') }}</h3>

      <!-- Error Message -->
      <p class="text-sm text-gray-600 text-center mb-6 max-w-md" id="error-message">
        {{ message || t('error.cannotLoadData') }}
      </p>

      <!-- Retry Button -->
      <button
        v-if="showRetry"
        @click="handleRetry"
        :disabled="retrying"
        class="retry-button px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        data-testid="retry-button"
        :aria-label="retrying ? t('error.retryPrompt') : t('common.retry')"
      >
        <span v-if="!retrying" class="flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {{ t('common.retry') }}
        </span>
        <span v-else class="flex items-center">
          <svg class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          {{ t('common.retrying') }}
        </span>
      </button>

      <!-- Additional Actions -->
      <div v-if="showContactSupport" class="mt-4">
        <a
          href="#"
          @click.prevent="handleContactSupport"
          class="text-sm text-blue-600 hover:text-blue-700 underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
          aria-label="联系技术支持获取帮助"
        >
          {{ t('error.contactSupport') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useI18n } from 'vue-i18n';

  export interface ErrorStateProps {
    title?: string;
    message?: string;
    showRetry?: boolean;
    showContactSupport?: boolean;
  }

  const props = withDefaults(defineProps<ErrorStateProps>(), {
    title: '',
    message: '',
    showRetry: true,
    showContactSupport: false,
  });
  
  const { t } = useI18n();

  const emit = defineEmits<{
    retry: [];
    contactSupport: [];
  }>();

  const retrying = ref(false);

  const handleRetry = async () => {
    retrying.value = true;
    emit('retry');

    // Reset retrying state after a short delay
    // The parent component should handle the actual retry logic
    setTimeout(() => {
      retrying.value = false;
    }, 2000);
  };

  const handleContactSupport = () => {
    emit('contactSupport');
  };
</script>

<style scoped>
  .error-state {
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .retry-button {
    min-width: 120px;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
