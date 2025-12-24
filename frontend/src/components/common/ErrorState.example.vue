<template>
  <div class="error-state-examples p-8 space-y-8 bg-gray-50">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">ErrorState Component Examples</h1>

    <!-- Example 1: Default Error State -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">1. Default Error State</h2>
      <ErrorState @retry="handleRetry" />
    </section>

    <!-- Example 2: Custom Error Message -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">2. Custom Error Message</h2>
      <ErrorState
        title="网络连接失败"
        message="无法连接到服务器，请检查您的网络设置并重试"
        @retry="handleRetry"
      />
    </section>

    <!-- Example 3: Error Without Retry Button -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">3. Error Without Retry Button</h2>
      <ErrorState
        title="权限不足"
        message="您没有权限访问此资源，请联系管理员"
        :show-retry="false"
      />
    </section>

    <!-- Example 4: Error With Contact Support -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">4. Error With Contact Support</h2>
      <ErrorState
        title="服务器错误"
        message="服务器遇到了一个问题，我们正在努力修复"
        :show-contact-support="true"
        @retry="handleRetry"
        @contact-support="handleContactSupport"
      />
    </section>

    <!-- Example 5: Authentication Error -->
    <section class="example-section">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">5. Authentication Error</h2>
      <ErrorState
        title="会话已过期"
        message="您的登录会话已过期，请重新登录"
        :show-retry="false"
        :show-contact-support="false"
      />
    </section>

    <!-- Notification Area -->
    <div
      v-if="notification"
      class="fixed bottom-4 right-4 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg"
    >
      {{ notification }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import ErrorState from './ErrorState.vue';

  const notification = ref('');

  const handleRetry = () => {
    notification.value = '正在重试...';
    setTimeout(() => {
      notification.value = '';
    }, 2000);
  };

  const handleContactSupport = () => {
    notification.value = '正在打开技术支持页面...';
    setTimeout(() => {
      notification.value = '';
    }, 2000);
  };
</script>

<style scoped>
  .example-section {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
</style>
