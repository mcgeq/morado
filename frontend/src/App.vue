<template>
  <router-view v-slot="{ Component, route }">
    <transition name="fade" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>

<script setup lang="ts">
  /**
   * App.vue - Root Component
   *
   * This is the root component of the Morado frontend application.
   * It provides the main router-view for rendering page components
   * with smooth transitions between routes.
   *
   * Features:
   * - Router view with transition animations
   * - Global error handling
   * - Application-wide state initialization
   */

  import { onErrorCaptured, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { createLogger } from './utils/logger';

  const router = useRouter();
  const logger = createLogger('App');

  /**
   * Initialize application on mount
   */
  onMounted(() => {
    // Log application start in development mode
    if (import.meta.env.DEV) {
      logger.info('应用组件已挂载', {
        环境: import.meta.env.MODE,
        'API 基础 URL': import.meta.env.VITE_API_BASE_URL || '/api',
      });
    }

    // Check for redirect query parameter (from authentication guard)
    const redirect = router.currentRoute.value.query.redirect as string;
    if (redirect) {
      logger.debug('检测到重定向参数，正在跳转', { redirect });
      // Remove redirect query and navigate to intended destination
      router.replace(redirect);
    }
  });

  /**
   * Global error handler for component errors
   * Captures errors from child components and handles them gracefully
   */
  onErrorCaptured((err, instance, info) => {
    logger.error('组件错误捕获', {
      error: err,
      info,
      component: instance?.$options.name || 'Unknown',
    });

    // In production, you might want to send errors to a monitoring service
    if (import.meta.env.PROD) {
      // TODO: Send error to monitoring service (e.g., Sentry)
    }

    // Return false to prevent error from propagating further
    // Return true to let the error propagate to parent components
    return false;
  });
</script>

<style>
  /**
   * Global styles and transitions
   */

  /* Fade transition for route changes */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.2s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }

  /* Ensure full height for the app */
  #app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Smooth scrolling */
  html {
    scroll-behavior: smooth;
  }

  /* Custom scrollbar styles */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: #f1f1f1;
  }

  ::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #555;
  }

  /* Focus styles for accessibility */
  *:focus-visible {
    outline: 2px solid #0ea5e9;
    outline-offset: 2px;
  }

  /* Loading spinner animation */
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
