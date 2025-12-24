<template>
  <!-- Error State for Invalid Props (Development Only) -->
  <div
    v-if="!hasValidData && isDevelopment"
    class="card border-2 border-red-300 bg-red-50"
    role="alert"
    aria-live="assertive"
  >
    <div class="flex items-center text-red-700">
      <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <div>
        <p class="font-semibold">Invalid Props - UserProfileCard</p>
        <p class="text-sm mt-1">
          {{ !isValidUser ? 'Invalid user data. ' : '' }}
          {{ !isValidMetrics ? 'Invalid metrics data. ' : '' }}
          Check console for details.
        </p>
      </div>
    </div>
  </div>

  <!-- Normal Card -->
  <article
    v-else
    class="card card-hoverable cursor-pointer"
    @click="handleClick"
    role="button"
    tabindex="0"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    :aria-label="t('user.profileCard')"
  >
    <!-- User Info Section -->
    <div class="flex items-center mb-6">
      <!-- Avatar -->
      <div class="flex-shrink-0 mr-4">
        <img
          v-if="user.avatar && !imageError"
          :src="user.avatar"
          :alt="t('user.avatar', { username: user.username })"
          class="w-16 h-16 rounded-full object-cover"
          @error="handleImageError"
        />
        <div
          v-else
          class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-2xl font-bold"
          role="img"
          :aria-label="t('user.defaultAvatar', { username: user.username, initial: getUserInitial })"
        >
          {{ getUserInitial }}
        </div>
      </div>

      <!-- User Details -->
      <div class="flex-1 min-w-0">
        <h3 class="text-xl font-semibold text-gray-900 truncate">{{ user.username }}</h3>
        <p class="text-sm text-gray-500 mt-1">
          <span class="sr-only">{{ t('user.registrationTimeLabel') }}</span>
          {{ t('user.registrationTime') }}: {{ formattedRegistrationDate }}
        </p>
      </div>
    </div>

    <!-- Metrics Section -->
    <div class="grid grid-cols-3 gap-2 sm:gap-4" role="list" :aria-label="t('user.executionStats')">
      <!-- Total Executions -->
      <div
        class="metric-badge bg-blue-50 rounded-lg p-2 sm:p-3 text-center"
        data-testid="total-executions"
        role="listitem"
      >
        <div class="flex items-center justify-center mb-1">
          <svg
            class="w-4 h-4 sm:w-5 sm:h-5 text-blue-600 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <div class="text-xl sm:text-2xl font-bold text-blue-600" :aria-label="t('user.totalExecutions')">
          {{ formatNumberWithSeparator(metrics.totalExecutions) }}
        </div>
        <div class="text-xs text-gray-600 mt-1">{{ t('user.totalExecutions') }}</div>
      </div>

      <!-- Passed Tests -->
      <div
        class="metric-badge bg-green-50 rounded-lg p-2 sm:p-3 text-center"
        data-testid="passed-tests"
        role="listitem"
      >
        <div class="flex items-center justify-center mb-1">
          <svg
            class="w-4 h-4 sm:w-5 sm:h-5 text-green-600 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="text-xl sm:text-2xl font-bold text-green-600" :aria-label="t('user.passedTests')">
          {{ formatNumberWithSeparator(metrics.passedTests) }}
        </div>
        <div class="text-xs text-gray-600 mt-1">{{ t('user.passedTests') }}</div>
      </div>

      <!-- Failed Tests -->
      <div
        class="metric-badge bg-red-50 rounded-lg p-2 sm:p-3 text-center"
        data-testid="failed-tests"
        role="listitem"
      >
        <div class="flex items-center justify-center mb-1">
          <svg
            class="w-4 h-4 sm:w-5 sm:h-5 text-red-600 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="text-xl sm:text-2xl font-bold text-red-600" :aria-label="t('user.failedTests')">
          {{ formatNumberWithSeparator(metrics.failedTests) }}
        </div>
        <div class="text-xs text-gray-600 mt-1">{{ t('user.failedTests') }}</div>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useLocale } from '@/composables/useLocale';
  import type { UserProfileCardProps } from '@/types/dashboard';
  import {
    validateNonEmptyString,
    validateNonNegativeNumber,
    validateDateString,
  } from '@/utils/propValidation';

  const props = defineProps<UserProfileCardProps>();
  
  const { t, formatDate, formatNumberWithSeparator } = useLocale();
  const router = useRouter();
  const imageError = ref(false);

  // Runtime prop validation
  if (import.meta.env.DEV) {
    if (!props.user) {
      console.error('[UserProfileCard] user prop is required');
    } else {
      validateNonEmptyString(props.user.id, 'user.id');
      validateNonEmptyString(props.user.username, 'user.username');
      validateDateString(props.user.registrationDate, 'user.registrationDate');
    }

    if (!props.metrics) {
      console.error('[UserProfileCard] metrics prop is required');
    } else {
      validateNonNegativeNumber(props.metrics.totalExecutions, 'metrics.totalExecutions');
      validateNonNegativeNumber(props.metrics.passedTests, 'metrics.passedTests');
      validateNonNegativeNumber(props.metrics.failedTests, 'metrics.failedTests');
    }
  }

  const isValidUser = computed(() => {
    return (
      props.user &&
      typeof props.user.id === 'string' &&
      props.user.id.length > 0 &&
      typeof props.user.username === 'string' &&
      props.user.username.length > 0 &&
      typeof props.user.registrationDate === 'string' &&
      !Number.isNaN(new Date(props.user.registrationDate).getTime())
    );
  });

  const isValidMetrics = computed(() => {
    return (
      props.metrics &&
      typeof props.metrics.totalExecutions === 'number' &&
      typeof props.metrics.passedTests === 'number' &&
      typeof props.metrics.failedTests === 'number' &&
      !Number.isNaN(props.metrics.totalExecutions) &&
      !Number.isNaN(props.metrics.passedTests) &&
      !Number.isNaN(props.metrics.failedTests) &&
      props.metrics.totalExecutions >= 0 &&
      props.metrics.passedTests >= 0 &&
      props.metrics.failedTests >= 0
    );
  });

  const hasValidData = computed(() => isValidUser.value && isValidMetrics.value);
  const isDevelopment = import.meta.env.DEV;

  const getUserInitial = computed(() => {
    return props.user.username.charAt(0).toUpperCase();
  });

  const formattedRegistrationDate = computed(() => {
    try {
      return formatDate(props.user.registrationDate, 'long');
    } catch {
      return props.user.registrationDate;
    }
  });

  function handleImageError(): void {
    imageError.value = true;
  }

  function handleClick(): void {
    router.push('/profile');
  }
</script>

<style scoped>
  .card {
    transition: all 0.3s ease;
  }

  .card:hover {
    transform: translateY(-2px);
  }

  .card:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  .metric-badge {
    transition: transform 0.2s ease;
  }

  .card:hover .metric-badge {
    transform: scale(1.05);
  }
</style>
