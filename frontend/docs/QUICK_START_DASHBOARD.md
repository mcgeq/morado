# Dashboard Quick Start Guide

## 快速开始

### 1. 安装依赖（已完成）

所有必需的依赖已经安装：

```bash
# 生产依赖
✓ echarts@6.0.0
✓ vue-echarts@8.0.1

# 开发依赖
✓ fast-check@4.5.2
✓ @types/echarts@5.0.0
✓ @testing-library/vue@8.1.0
✓ jsdom@27.3.0
✓ @vitest/ui@4.0.16
```

### 2. 运行测试

```bash
# 运行所有测试
bun run test:run

# 运行测试并观察变化
bun run test

# 使用 UI 界面运行测试
bun run test:ui

# 运行测试并生成覆盖率报告
bun run test:coverage
```

### 3. 使用 Dashboard Store

```typescript
import { useDashboardStore } from '@/stores/dashboard';

const store = useDashboardStore();

// 加载数据（使用缓存）
await store.refreshDashboard();

// 强制刷新（忽略缓存）
await store.refreshDashboard(false);

// 访问数据
console.log(store.userData);
console.log(store.statistics);
```

### 4. 使用 ECharts

```vue
<template>
  <v-chart :option="chartOption" style="height: 400px" />
</template>

<script setup lang="ts">
import type { EChartsOption } from 'echarts';

const chartOption: EChartsOption = {
  title: { text: '示例图表' },
  tooltip: {},
  xAxis: { type: 'category', data: ['周一', '周二', '周三'] },
  yAxis: { type: 'value' },
  series: [{ data: [120, 200, 150], type: 'line' }],
};
</script>
```

### 5. 编写属性测试

```typescript
import * as fc from 'fast-check';

it('属性测试示例', () => {
  fc.assert(
    fc.property(
      fc.nat(), // 生成自然数
      (num) => {
        // 测试属性
        return num >= 0; // 属性应该成立
      }
    ),
    { numRuns: 100 } // 运行 100 次
  );
});
```

## 项目结构

```
frontend/src/
├── plugins/
│   └── echarts.ts              # ECharts 全局配置
├── stores/
│   ├── dashboard.ts            # Dashboard Pinia store
│   └── __tests__/              # 测试文件
├── types/
│   └── dashboard.d.ts          # TypeScript 类型定义
└── test/
    └── setup.ts                # 测试设置
```

## 可用的 npm 脚本

```bash
bun run dev              # 启动开发服务器
bun run build            # 构建生产版本
bun run test             # 运行测试（观察模式）
bun run test:run         # 运行测试（单次）
bun run test:ui          # 使用 UI 运行测试
bun run test:coverage    # 生成测试覆盖率报告
bun run lint             # 运行代码检查
bun run format           # 格式化代码
```

## 下一步

1. ✅ 安装依赖和配置
2. ⏭️ 创建数据模型和 TypeScript 接口
3. ⏭️ 实现 Dashboard 组件
4. ⏭️ 创建图表组件
5. ⏭️ 实现响应式设计
6. ⏭️ 编写测试

## 常见问题

### Q: ECharts 图表不显示？
A: 确保容器有明确的高度：
```vue
<v-chart :option="option" style="height: 400px" />
```

### Q: TypeScript 报错？
A: 确保 `@types/echarts` 已安装并在 `tsconfig.app.json` 中配置。

### Q: 测试失败？
A: 在测试前清除 localStorage：
```typescript
beforeEach(() => {
  localStorage.clear();
});
```

## 资源链接

- [ECharts 文档](https://echarts.apache.org/zh/index.html)
- [vue-echarts 文档](https://github.com/ecomfe/vue-echarts)
- [fast-check 文档](https://fast-check.dev/)
- [Vitest 文档](https://vitest.dev/)
- [Pinia 文档](https://pinia.vuejs.org/zh/)
