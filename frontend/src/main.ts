/**
 * main.ts - Application Entry Point
 *
 * This file initializes the Vue 3 application with all necessary plugins,
 * configurations, and global settings for the Morado testing platform.
 *
 * Setup includes:
 * - Vue application instance creation
 * - Router configuration
 * - Pinia state management
 * - Global error handling
 * - Performance monitoring (development mode)
 */

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import pinia from './stores';
import { logger } from './utils/logger';
import { setupECharts } from './plugins/echarts';

// Import global styles
import './styles/main.css';

/**
 * Create Vue application instance
 */
const app = createApp(App);

/**
 * Configure global error handler
 * Catches unhandled errors in the application
 */
app.config.errorHandler = (err, _instance, info) => {
  logger.error('全局错误处理器捕获到错误', { error: err, info });

  // In production, send errors to monitoring service
  if (import.meta.env.PROD) {
    // TODO: Send to error monitoring service (e.g., Sentry)
    // Example: Sentry.captureException(err);
  }
};

/**
 * Configure global warning handler (development only)
 * Helps catch potential issues during development
 */
if (import.meta.env.DEV) {
  app.config.warnHandler = (msg, _instance, trace) => {
    logger.warn('Vue 警告', { message: msg, trace });
  };
}

/**
 * Configure performance monitoring (development only)
 * Enables Vue DevTools performance tracking
 */
if (import.meta.env.DEV) {
  app.config.performance = true;
}

/**
 * Register global properties
 * These are accessible in all components via this.$property
 */
app.config.globalProperties.$appName = 'Morado';
app.config.globalProperties.$appVersion = '0.1.0';

/**
 * Install plugins
 */
// Install Vue Router
app.use(router);

// Install Pinia state management
app.use(pinia);

// Install ECharts
setupECharts(app);

/**
 * Global directives (optional)
 * Example: Custom directives for common functionality
 */
// app.directive('focus', {
//   mounted(el) {
//     el.focus();
//   }
// });

/**
 * Mount the application
 * Wait for router to be ready before mounting to ensure
 * proper handling of initial navigation
 */
router.isReady().then(() => {
  app.mount('#app');

  // Log successful mount in development
  if (import.meta.env.DEV) {
    logger.success('Morado 测试平台已成功挂载', {
      环境: import.meta.env.MODE,
      当前路由: router.currentRoute.value.path,
      版本: '0.1.0',
    });
  }
});

/**
 * Handle unhandled promise rejections
 * Prevents silent failures in async operations
 */
window.addEventListener('unhandledrejection', event => {
  logger.error('未处理的 Promise 拒绝', {
    reason: event.reason,
    promise: event.promise,
  });

  // Prevent default browser behavior
  event.preventDefault();

  // In production, send to monitoring service
  if (import.meta.env.PROD) {
    // TODO: Send to error monitoring service
  }
});

/**
 * Export app instance for testing purposes
 */
export default app;
