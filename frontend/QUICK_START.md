# Morado 前端快速启动指南

## 前置要求

- Node.js 18+ 或 Bun 1.0+
- Git

## 安装依赖

使用 Bun（推荐）：

```bash
cd frontend
bun install
```

或使用 npm：

```bash
cd frontend
npm install
```

## 开发模式

启动开发服务器：

```bash
bun run dev
```

或：

```bash
npm run dev
```

应用将在 http://localhost:3000 启动。

## 测试 Tailwind CSS 配置

访问 http://localhost:3000/tailwind-test 查看 Tailwind CSS 4 的测试页面，验证所有样式是否正常工作。

## 构建生产版本

```bash
bun run build
```

或：

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

## 预览生产构建

```bash
bun run preview
```

或：

```bash
npm run preview
```

## 代码质量检查

### 格式化代码

```bash
bun run format
```

### 检查代码格式

```bash
bun run format:check
```

### Lint 检查

```bash
bun run lint
```

### 自动修复 Lint 问题

```bash
bun run lint:fix
```

### 完整检查（格式化 + Lint）

```bash
bun run check
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API 客户端
│   ├── assets/         # 资源文件
│   ├── components/     # Vue 组件
│   │   ├── common/     # 通用组件
│   │   └── business/   # 业务组件
│   ├── layouts/        # 布局组件
│   ├── router/         # 路由配置
│   ├── stores/         # Pinia 状态管理
│   ├── styles/         # 全局样式
│   │   └── main.css    # Tailwind CSS 入口
│   ├── types/          # TypeScript 类型
│   ├── utils/          # 工具函数
│   │   ├── logger.ts   # 日志工具
│   │   └── README.md   # 工具文档
│   ├── views/          # 页面视图
│   ├── App.vue         # 根组件
│   └── main.ts         # 应用入口
├── index.html          # HTML 模板
├── vite.config.ts      # Vite 配置
├── tsconfig.json       # TypeScript 配置
├── biome.json          # Biome 配置
└── package.json        # 项目依赖
```

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 8.0
- **包管理器**: Bun
- **样式**: Tailwind CSS 4
- **UI 组件**: Headless UI for Vue
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **代码质量**: Biome
- **类型检查**: TypeScript 5.9

## 开发规范

### 组件命名

- 使用 PascalCase 命名组件文件：`MyComponent.vue`
- 组件名应该是多个单词：`UserProfile.vue` 而不是 `User.vue`

### 样式规范

- 优先使用 Tailwind CSS 工具类
- 避免编写自定义 CSS，除非必要
- 使用 `@layer` 添加自定义样式

### 日志规范

使用规范化的日志工具：

```typescript
import { log } from '@/utils/logger';

log.info('信息');
log.success('成功');
log.warn('警告');
log.error('错误');
```

详细文档：`src/utils/README.md`

### 代码提交前

运行完整检查：

```bash
bun run check
```

确保所有检查通过后再提交代码。

## 常用命令

| 命令 | 说明 |
|------|------|
| `bun run dev` | 启动开发服务器 |
| `bun run build` | 构建生产版本 |
| `bun run preview` | 预览生产构建 |
| `bun run format` | 格式化代码 |
| `bun run lint` | Lint 检查 |
| `bun run check` | 完整检查 |

## 环境变量

创建 `.env.local` 文件（不提交到 Git）：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Morado 测试平台
```

在代码中使用：

```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

## 常见问题

### Q: 开发服务器启动失败？

A: 检查端口 3000 是否被占用，或在 `vite.config.ts` 中修改端口。

### Q: Tailwind CSS 样式不生效？

A: 确保：
1. 已安装 `tailwindcss` 和 `@tailwindcss/vite`
2. `vite.config.ts` 中添加了 `tailwindcss()` 插件
3. `main.ts` 中导入了 `./styles/main.css`
4. 重启开发服务器

### Q: TypeScript 报错？

A: 运行 `bun run build` 查看详细错误信息。

### Q: 如何调试？

A: 使用浏览器开发者工具，或使用 Vue DevTools 扩展。

## 获取帮助

- 查看 `TAILWIND_CONFIG.md` 了解 Tailwind CSS 4 配置
- 查看 `src/utils/README.md` 了解日志工具使用
- 查看各个目录下的 README 文件

## 下一步

1. 熟悉项目结构
2. 查看 Tailwind CSS 测试页面
3. 阅读日志工具文档
4. 开始开发功能！

祝开发愉快！🚀
