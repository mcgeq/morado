<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Morado 测试平台</h1>
        <p class="text-xl text-gray-600">基于四层架构的自动化测试管理平台</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Layer 1: API Components -->
        <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">第一层：API组件</h2>
          <div class="space-y-2">
            <router-link
              to="/headers"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              Header 管理
            </router-link>
            <router-link
              to="/bodies"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              Body 管理
            </router-link>
            <router-link
              to="/api-definitions"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              API 定义
            </router-link>
          </div>
        </div>

        <!-- Layer 2: Scripts -->
        <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">第二层：脚本</h2>
          <div class="space-y-2">
            <router-link
              to="/scripts"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              脚本管理
            </router-link>
            <p class="text-sm text-gray-600 mt-4">引用API定义创建可执行脚本</p>
          </div>
        </div>

        <!-- Layer 3: Components -->
        <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">第三层：组件</h2>
          <div class="space-y-2">
            <router-link
              to="/components"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              组件管理
            </router-link>
            <p class="text-sm text-gray-600 mt-4">组合多个脚本，支持嵌套</p>
          </div>
        </div>

        <!-- Layer 4: Test Cases -->
        <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">第四层：测试用例</h2>
          <div class="space-y-2">
            <router-link
              to="/test-cases"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              测试用例
            </router-link>
            <router-link
              to="/test-suites"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              测试套件
            </router-link>
            <router-link
              to="/reports"
              class="block text-blue-600 hover:text-blue-800 hover:underline"
            >
              测试报告
            </router-link>
          </div>
        </div>
      </div>

      <div class="mt-12 text-center">
        <p class="text-gray-600">
          快速开始：创建 Header 和 Body → 定义 API → 编写脚本 → 组合组件 → 创建测试用例
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  // Home page component
</script>
