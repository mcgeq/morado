# Tailwind CSS 4 配置指南

## 概述

本项目使用 Tailwind CSS 4，这是 Tailwind 的最新版本，采用了全新的 CSS 引擎，配置更加简洁。

## 安装的包

```json
{
  "dependencies": {
    "@tailwindcss/vite": "^4.1.18"
  },
  "devDependencies": {
    "tailwindcss": "^4.1.18"
  }
}
```

## Vite 配置

在 `vite.config.ts` 中引入 Tailwind CSS Vite 插件：

```typescript
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [
    tailwindcss(), // Tailwind CSS 4 Vite plugin
    vue(),
  ],
  // ... 其他配置
});
```

## CSS 配置

在 `src/styles/main.css` 中导入 Tailwind CSS：

```css
@import "tailwindcss";
```

## Tailwind CSS 4 的主要变化

### 1. 不再需要配置文件

Tailwind CSS 4 **不需要** `tailwind.config.js` 或 `postcss.config.js` 文件。所有配置都通过 CSS 完成。

### 2. 使用 @theme 自定义主题

在 CSS 文件中使用 `@theme` 指令自定义主题：

```css
@theme {
  /* 自定义颜色 */
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;
  
  /* 自定义间距 */
  --spacing-18: 4.5rem;
  
  /* 自定义字体 */
  --font-sans: ui-sans-serif, system-ui, sans-serif;
  
  /* 自定义圆角 */
  --radius-4xl: 2rem;
  
  /* 自定义阴影 */
  --shadow-glow: 0 0 20px rgba(14, 165, 233, 0.5);
}
```

### 3. 使用 @layer 添加自定义样式

```css
@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
  }
  
  h1 {
    @apply text-4xl font-bold tracking-tight;
  }
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700;
  }
}

@layer utilities {
  .text-shadow {
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  }
}
```

## 当前项目配置

### 主题配置 (src/styles/main.css)

```css
@import "tailwindcss";

@theme {
  /* 主色调 - 蓝色系 */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-200: #bae6fd;
  --color-primary-300: #7dd3fc;
  --color-primary-400: #38bdf8;
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;
  --color-primary-700: #0369a1;
  --color-primary-800: #075985;
  --color-primary-900: #0c4a6e;
  --color-primary-950: #082f49;

  /* 自定义间距 */
  --spacing-18: 4.5rem;
  --spacing-22: 5.5rem;

  /* 自定义字体 */
  --font-sans: ui-sans-serif, system-ui, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas;

  /* 自定义圆角 */
  --radius-4xl: 2rem;

  /* 自定义阴影 */
  --shadow-glow: 0 0 20px rgba(14, 165, 233, 0.5);
}

/* 基础样式 */
@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
  }

  h1 {
    @apply text-4xl font-bold tracking-tight;
  }

  h2 {
    @apply text-3xl font-semibold tracking-tight;
  }

  h3 {
    @apply text-2xl font-semibold tracking-tight;
  }

  h4 {
    @apply text-xl font-semibold;
  }
}
```

## 使用自定义主题

### 使用自定义颜色

```html
<!-- 使用自定义的 primary 颜色 -->
<div class="bg-primary-500 text-white">
  主色调背景
</div>

<button class="bg-primary-600 hover:bg-primary-700">
  按钮
</button>
```

### 使用自定义间距

```html
<!-- 使用自定义间距 -->
<div class="mt-18 mb-22">
  自定义间距
</div>
```

### 使用自定义圆角

```html
<!-- 使用自定义圆角 -->
<div class="rounded-4xl">
  超大圆角
</div>
```

### 使用自定义阴影

```html
<!-- 使用自定义阴影 -->
<div class="shadow-glow">
  发光效果
</div>
```

## 常用 Tailwind CSS 类

### 布局

```html
<!-- Flexbox -->
<div class="flex items-center justify-between">
  <span>左侧</span>
  <span>右侧</span>
</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>

<!-- 容器 -->
<div class="container mx-auto px-4">
  内容
</div>
```

### 间距

```html
<!-- Padding -->
<div class="p-4">内边距</div>
<div class="px-4 py-2">水平和垂直内边距</div>

<!-- Margin -->
<div class="m-4">外边距</div>
<div class="mx-auto">水平居中</div>
```

### 颜色

```html
<!-- 背景色 -->
<div class="bg-blue-500">蓝色背景</div>
<div class="bg-gray-100">灰色背景</div>

<!-- 文字颜色 -->
<span class="text-red-500">红色文字</span>
<span class="text-gray-700">灰色文字</span>
```

### 文字

```html
<!-- 字体大小 -->
<h1 class="text-4xl">超大标题</h1>
<p class="text-base">正常文字</p>
<small class="text-sm">小字</small>

<!-- 字体粗细 -->
<span class="font-bold">粗体</span>
<span class="font-semibold">半粗体</span>
<span class="font-normal">正常</span>

<!-- 文字对齐 -->
<p class="text-center">居中</p>
<p class="text-left">左对齐</p>
<p class="text-right">右对齐</p>
```

### 边框

```html
<!-- 边框 -->
<div class="border border-gray-300">边框</div>
<div class="border-2 border-blue-500">粗边框</div>

<!-- 圆角 -->
<div class="rounded">小圆角</div>
<div class="rounded-lg">大圆角</div>
<div class="rounded-full">完全圆角</div>
```

### 阴影

```html
<!-- 阴影 -->
<div class="shadow">小阴影</div>
<div class="shadow-md">中等阴影</div>
<div class="shadow-lg">大阴影</div>
```

### 响应式设计

```html
<!-- 响应式类 -->
<div class="w-full md:w-1/2 lg:w-1/3">
  移动端全宽，平板半宽，桌面三分之一宽
</div>

<!-- 响应式显示/隐藏 -->
<div class="hidden md:block">
  只在中等及以上屏幕显示
</div>
```

### 状态变体

```html
<!-- Hover -->
<button class="bg-blue-500 hover:bg-blue-700">
  悬停变色
</button>

<!-- Focus -->
<input class="border focus:border-blue-500 focus:ring-2 focus:ring-blue-200">

<!-- Active -->
<button class="active:scale-95">
  点击缩小
</button>

<!-- Disabled -->
<button class="disabled:opacity-50 disabled:cursor-not-allowed">
  禁用状态
</button>
```

## 性能优化

Tailwind CSS 4 使用新的 CSS 引擎，性能大幅提升：

- ✅ 更快的构建速度
- ✅ 更小的 CSS 文件
- ✅ 更好的开发体验
- ✅ 原生 CSS 变量支持

## 调试技巧

### 1. 使用浏览器开发者工具

在浏览器中检查元素，查看应用的 Tailwind 类。

### 2. 使用 Tailwind CSS IntelliSense

安装 VS Code 扩展 "Tailwind CSS IntelliSense" 获得自动补全和预览。

### 3. 查看生成的 CSS

在开发模式下，可以在浏览器的 Network 标签中查看生成的 CSS 文件。

## 常见问题

### Q: 为什么没有 tailwind.config.js？

A: Tailwind CSS 4 不再需要配置文件，所有配置都通过 CSS 的 `@theme` 指令完成。

### Q: 如何添加自定义颜色？

A: 在 `@theme` 块中添加 CSS 变量：

```css
@theme {
  --color-brand-500: #your-color;
}
```

然后使用 `bg-brand-500`、`text-brand-500` 等类。

### Q: 如何使用 PostCSS 插件？

A: Tailwind CSS 4 的 Vite 插件内置了必要的 PostCSS 处理，通常不需要额外配置。

### Q: 样式不生效怎么办？

A: 检查以下几点：
1. 确保在 `main.ts` 中导入了 `./styles/main.css`
2. 确保 Vite 配置中添加了 `tailwindcss()` 插件
3. 重启开发服务器

## 参考资源

- [Tailwind CSS 4 官方文档](https://tailwindcss.com/docs)
- [Tailwind CSS 4 发布说明](https://tailwindcss.com/blog/tailwindcss-v4)
- [@tailwindcss/vite 插件文档](https://github.com/tailwindlabs/tailwindcss-vite)
- [Vite 官方文档](https://vitejs.dev/)

## 总结

Tailwind CSS 4 的配置非常简单：

1. ✅ 安装 `tailwindcss` 和 `@tailwindcss/vite`
2. ✅ 在 `vite.config.ts` 中添加 `tailwindcss()` 插件
3. ✅ 在 CSS 文件中使用 `@import "tailwindcss"`
4. ✅ 使用 `@theme` 自定义主题
5. ✅ 开始使用 Tailwind 类！

不需要 `tailwind.config.js`，不需要 `postcss.config.js`，配置更简洁，性能更强大！
