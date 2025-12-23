<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-4xl font-bold text-center mb-8">Tailwind CSS 4 测试页面</h1>

      <!-- 颜色测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">颜色测试</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-primary-500 text-white p-4 rounded-lg text-center">Primary 500</div>
          <div class="bg-primary-600 text-white p-4 rounded-lg text-center">Primary 600</div>
          <div class="bg-blue-500 text-white p-4 rounded-lg text-center">Blue 500</div>
          <div class="bg-green-500 text-white p-4 rounded-lg text-center">Green 500</div>
        </div>
      </section>

      <!-- 间距测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">自定义间距测试</h2>
        <div class="bg-white p-4 rounded-lg">
          <div class="bg-blue-100 p-4 mt-18">mt-18 (自定义间距 4.5rem)</div>
          <div class="bg-green-100 p-4 mt-22">mt-22 (自定义间距 5.5rem)</div>
        </div>
      </section>

      <!-- 圆角测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">圆角测试</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-blue-500 text-white p-4 rounded text-center">rounded</div>
          <div class="bg-blue-500 text-white p-4 rounded-lg text-center">rounded-lg</div>
          <div class="bg-blue-500 text-white p-4 rounded-4xl text-center">rounded-4xl (自定义)</div>
          <div class="bg-blue-500 text-white p-4 rounded-full text-center">rounded-full</div>
        </div>
      </section>

      <!-- 阴影测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">阴影测试</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-white p-4 shadow text-center">shadow</div>
          <div class="bg-white p-4 shadow-md text-center">shadow-md</div>
          <div class="bg-white p-4 shadow-lg text-center">shadow-lg</div>
          <div class="bg-white p-4 shadow-glow text-center">shadow-glow (自定义)</div>
        </div>
      </section>

      <!-- 响应式测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">响应式测试</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-blue-500 text-white p-4 rounded-lg text-center">移动端 1 列</div>
          <div class="bg-blue-500 text-white p-4 rounded-lg text-center">平板 2 列</div>
          <div class="bg-blue-500 text-white p-4 rounded-lg text-center">桌面 3 列</div>
        </div>
      </section>

      <!-- Flexbox 测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">Flexbox 测试</h2>
        <div class="bg-white p-4 rounded-lg">
          <div class="flex items-center justify-between mb-4">
            <span class="text-gray-700">左侧</span>
            <span class="text-gray-700">右侧</span>
          </div>
          <div class="flex items-center justify-center space-x-4">
            <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
              按钮 1
            </button>
            <button class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
              按钮 2
            </button>
            <button class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">按钮 3</button>
          </div>
        </div>
      </section>

      <!-- 状态变体测试 -->
      <section class="mb-12">
        <h2 class="text-2xl font-semibold mb-4">状态变体测试</h2>
        <div class="bg-white p-4 rounded-lg space-y-4">
          <button
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700 active:scale-95 transition-all"
          >
            Hover 和 Active 效果
          </button>
          <input
            type="text"
            placeholder="Focus 效果"
            class="w-full px-4 py-2 border border-gray-300 rounded focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none"
          />
          <button
            disabled
            class="px-4 py-2 bg-gray-500 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            禁用按钮
          </button>
        </div>
      </section>

      <!-- 成功提示 -->
      <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
        <p class="font-bold">✅ Tailwind CSS 4 配置成功！</p>
        <p class="text-sm">所有样式都正常工作，包括自定义主题配置。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  // Tailwind CSS 4 测试页面
</script>
