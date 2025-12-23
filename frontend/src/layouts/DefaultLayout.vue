<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header Navigation -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo and Brand -->
          <div class="flex items-center">
            <router-link
              to="/"
              class="text-2xl font-bold text-blue-600 hover:text-blue-700 transition-colors"
            >
              Morado
            </router-link>
          </div>

          <!-- Main Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <!-- Layer 1: API Components -->
            <div class="relative group">
              <button class="text-gray-700 hover:text-blue-600 font-medium transition-colors">
                API组件
              </button>
              <div
                class="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10"
              >
                <div class="py-1">
                  <router-link
                    to="/headers"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Header管理
                  </router-link>
                  <router-link
                    to="/bodies"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Body管理
                  </router-link>
                  <router-link
                    to="/api-definitions"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    API定义
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Layer 2: Scripts -->
            <router-link
              to="/scripts"
              class="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              脚本
            </router-link>

            <!-- Layer 3: Components -->
            <router-link
              to="/components"
              class="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              组件
            </router-link>

            <!-- Layer 4: Test Cases -->
            <div class="relative group">
              <button class="text-gray-700 hover:text-blue-600 font-medium transition-colors">
                测试
              </button>
              <div
                class="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10"
              >
                <div class="py-1">
                  <router-link
                    to="/test-cases"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    测试用例
                  </router-link>
                  <router-link
                    to="/test-suites"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    测试套件
                  </router-link>
                  <router-link
                    to="/reports"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    测试报告
                  </router-link>
                </div>
              </div>
            </div>
          </div>

          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <div v-if="isAuthenticated" class="flex items-center space-x-3">
              <span class="text-gray-700 text-sm">{{ username }}</span>
              <button
                @click="handleLogout"
                class="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                退出
              </button>
            </div>
            <button
              v-else
              @click="handleLogin"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              登录
            </button>
          </div>

          <!-- Mobile Menu Button -->
          <div class="md:hidden">
            <button
              @click="toggleMobileMenu"
              class="text-gray-700 hover:text-blue-600 focus:outline-none"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  v-if="!isMobileMenuOpen"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path
                  v-else
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Mobile Menu -->
        <div v-if="isMobileMenuOpen" class="md:hidden py-4 border-t border-gray-200">
          <div class="space-y-2">
            <div class="px-4 py-2 text-sm font-semibold text-gray-900">API组件</div>
            <router-link
              to="/headers"
              class="block px-6 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              Header管理
            </router-link>
            <router-link
              to="/bodies"
              class="block px-6 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              Body管理
            </router-link>
            <router-link
              to="/api-definitions"
              class="block px-6 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              API定义
            </router-link>

            <router-link
              to="/scripts"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              脚本
            </router-link>

            <router-link
              to="/components"
              class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              组件
            </router-link>

            <div class="px-4 py-2 text-sm font-semibold text-gray-900">测试</div>
            <router-link
              to="/test-cases"
              class="block px-6 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              测试用例
            </router-link>
            <router-link
              to="/test-suites"
              class="block px-6 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              测试套件
            </router-link>
            <router-link
              to="/reports"
              class="block px-6 py-2 text-sm text-gray-700 hover:bg-gray-100"
              @click="closeMobileMenu"
            >
              测试报告
            </router-link>
          </div>
        </div>
      </nav>
    </header>

    <!-- Main Content Area -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center text-sm text-gray-600">
          <p>&copy; 2025 Morado 测试平台. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { createLogger } from '@/utils/logger';

  const logger = createLogger('DefaultLayout');
  const router = useRouter();
  const isMobileMenuOpen = ref(false);

  // Check authentication status
  const isAuthenticated = computed(() => {
    return !!localStorage.getItem('auth_token');
  });

  // Get username from localStorage
  const username = computed(() => {
    const userInfo = localStorage.getItem('user_info');
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo);
        return user.username || '用户';
      } catch {
        return '用户';
      }
    }
    return '用户';
  });

  const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  };

  const closeMobileMenu = () => {
    isMobileMenuOpen.value = false;
  };

  const handleLogin = () => {
    router.push({ name: 'Login' });
  };

  const handleLogout = () => {
    logger.info('用户登出', { username: username.value });

    // Clear authentication data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');

    // Redirect to login page
    router.push({ name: 'Login' });
  };
</script>

<style scoped>
  /* Additional styles for dropdown menus */
  .group:hover .group-hover\:opacity-100 {
    opacity: 1;
  }

  .group:hover .group-hover\:visible {
    visibility: visible;
  }
</style>
