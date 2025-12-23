<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-md w-full space-y-8">
      <!-- Logo and Title -->
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Morado</h1>
        <p class="text-lg text-gray-600">自动化测试管理平台</p>
      </div>

      <!-- Login/Register Card -->
      <div class="bg-white rounded-lg shadow-xl p-8">
        <!-- Tabs -->
        <div class="flex border-b border-gray-200 mb-6">
          <button
            :class="[
              'flex-1 py-2 text-center font-medium transition-colors',
              activeTab === 'login'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700',
            ]"
            @click="activeTab = 'login'"
          >
            登录
          </button>
          <button
            :class="[
              'flex-1 py-2 text-center font-medium transition-colors',
              activeTab === 'register'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700',
            ]"
            @click="activeTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- Login Form -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="login-username" class="block text-sm font-medium text-gray-700 mb-2">
              用户名
            </label>
            <input
              id="login-username"
              v-model="loginForm.username"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label for="login-password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <input
              id="login-password"
              v-model="loginForm.password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入密码"
            />
          </div>

          <div class="flex items-center justify-between">
            <label class="flex items-center">
              <input
                v-model="loginForm.remember"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-600">记住我</span>
            </label>
            <a href="#" class="text-sm text-blue-600 hover:text-blue-700">忘记密码？</a>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="!isLoading">登录</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                  fill="none"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              登录中...
            </span>
          </button>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm"
          >
            {{ errorMessage }}
          </div>

          <!-- Demo Hint -->
          <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
            <p class="font-medium mb-1">💡 演示账号</p>
            <p>用户名: demo / 密码: demo123</p>
          </div>
        </form>

        <!-- Register Form -->
        <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label for="register-username" class="block text-sm font-medium text-gray-700 mb-2">
              用户名
            </label>
            <input
              id="register-username"
              v-model="registerForm.username"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label for="register-email" class="block text-sm font-medium text-gray-700 mb-2">
              邮箱
            </label>
            <input
              id="register-email"
              v-model="registerForm.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入邮箱"
            />
          </div>

          <div>
            <label for="register-password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <input
              id="register-password"
              v-model="registerForm.password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请输入密码（至少6位）"
            />
          </div>

          <div>
            <label
              for="register-confirm-password"
              class="block text-sm font-medium text-gray-700 mb-2"
            >
              确认密码
            </label>
            <input
              id="register-confirm-password"
              v-model="registerForm.confirmPassword"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="请再次输入密码"
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="!isLoading">注册</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                  fill="none"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              注册中...
            </span>
          </button>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm"
          >
            {{ errorMessage }}
          </div>
        </form>
      </div>

      <!-- Footer -->
      <p class="text-center text-sm text-gray-600">
        &copy; 2025 Morado 测试平台. All rights reserved.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { createLogger } from '@/utils/logger';

  const logger = createLogger('Login');
  const router = useRouter();
  const route = useRoute();

  const activeTab = ref<'login' | 'register'>('login');
  const isLoading = ref(false);
  const errorMessage = ref('');

  const loginForm = ref({
    username: '',
    password: '',
    remember: false,
  });

  const registerForm = ref({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  /**
   * 处理登录
   */
  async function handleLogin() {
    errorMessage.value = '';
    isLoading.value = true;

    try {
      logger.info('用户尝试登录', { username: loginForm.value.username });

      // 模拟 API 调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      // TODO: 替换为真实的 API 调用
      // const response = await apiLogin(loginForm.value);

      // 简单验证（演示用）
      if (loginForm.value.username === 'demo' && loginForm.value.password === 'demo123') {
        // 设置 token
        const token = `token_${Date.now()}`;
        localStorage.setItem('auth_token', token);

        // 保存用户信息
        localStorage.setItem(
          'user_info',
          JSON.stringify({
            username: loginForm.value.username,
            role: 'developer',
          }),
        );

        logger.success('登录成功', { username: loginForm.value.username });

        // 获取重定向目标
        const redirect = (route.query.redirect as string) || '/';
        router.push(redirect);
      } else {
        errorMessage.value = '用户名或密码错误';
        logger.warn('登录失败', { username: loginForm.value.username });
      }
    } catch (error) {
      errorMessage.value = '登录失败，请稍后重试';
      logger.error('登录异常', error);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * 处理注册
   */
  async function handleRegister() {
    errorMessage.value = '';

    // 验证密码
    if (registerForm.value.password.length < 6) {
      errorMessage.value = '密码至少需要6位';
      return;
    }

    if (registerForm.value.password !== registerForm.value.confirmPassword) {
      errorMessage.value = '两次输入的密码不一致';
      return;
    }

    isLoading.value = true;

    try {
      logger.info('用户尝试注册', { username: registerForm.value.username });

      // 模拟 API 调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));

      // TODO: 替换为真实的 API 调用
      // const response = await apiRegister(registerForm.value);

      logger.success('注册成功', { username: registerForm.value.username });

      // 注册成功后自动登录
      const token = `token_${Date.now()}`;
      localStorage.setItem('auth_token', token);
      localStorage.setItem(
        'user_info',
        JSON.stringify({
          username: registerForm.value.username,
          email: registerForm.value.email,
          role: 'tester',
        }),
      );

      // 跳转到首页
      router.push('/');
    } catch (error) {
      errorMessage.value = '注册失败，请稍后重试';
      logger.error('注册异常', error);
    } finally {
      isLoading.value = false;
    }
  }
</script>
