# 前端工具库

## Logger - 规范化日志工具

### 概述

Logger 是一个规范化的日志工具，提供清晰、易于查看的日志输出。它支持不同级别的日志、颜色标识、时间戳、上下文信息等功能。

### 特性

- ✅ **多级别日志**: DEBUG、INFO、SUCCESS、WARN、ERROR
- 🎨 **颜色标识**: 不同类型的日志使用不同的颜色和图标
- ⏰ **时间戳**: 自动添加精确到毫秒的时间戳
- 📦 **上下文信息**: 支持为不同模块创建独立的 logger
- 📊 **数据展示**: 自动格式化对象数据，使用 console.table 展示
- 🔍 **堆栈跟踪**: 错误和警告可选显示堆栈信息
- ⚡ **性能计时**: 内置性能计时功能
- 🎯 **分组日志**: 支持日志分组，便于查看相关日志
- 🔧 **可配置**: 支持自定义日志级别、时间戳、堆栈跟踪等

### 快速开始

#### 1. 基本使用

```typescript
import { log } from '@/utils/logger';

// 基本日志
log.debug('调试信息');
log.info('普通信息');
log.success('操作成功');
log.warn('警告信息');
log.error('错误信息');
```

#### 2. 带数据的日志

```typescript
import { log } from '@/utils/logger';

// 日志会自动格式化对象数据
log.info('用户登录成功', {
  用户名: 'testuser',
  角色: 'developer',
  登录时间: new Date().toISOString(),
});
```

#### 3. 创建特定上下文的 Logger

```typescript
import { createLogger } from '@/utils/logger';

// 为特定模块创建 logger
const apiLogger = createLogger('API');
const storeLogger = createLogger('Store');

apiLogger.info('API 模块初始化');
storeLogger.info('Store 模块初始化');
```

### API 参考

#### 日志方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `debug(message, data?)` | 调试级别日志 | `log.debug('调试信息', { key: 'value' })` |
| `info(message, data?)` | 信息级别日志 | `log.info('普通信息')` |
| `success(message, data?)` | 成功信息日志 | `log.success('操作成功')` |
| `warn(message, data?)` | 警告级别日志 | `log.warn('警告信息')` |
| `error(message, error?)` | 错误级别日志 | `log.error('错误信息', error)` |
| `api(method, url, data?)` | API 请求日志 | `log.api('GET', '/api/users')` |
| `router(from, to, data?)` | 路由导航日志 | `log.router('/home', '/about')` |
| `store(action, data?)` | Store 状态变更日志 | `log.store('用户登录', data)` |

#### 工具方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `group(label)` | 开始日志分组 | `log.group('用户操作')` |
| `groupEnd()` | 结束日志分组 | `log.groupEnd()` |
| `time(label)` | 开始性能计时 | `log.time('数据加载')` |
| `timeEnd(label)` | 结束性能计时 | `log.timeEnd('数据加载')` |

#### Logger 配置

```typescript
import { createLogger, LogLevel } from '@/utils/logger';

const logger = createLogger('MyModule', {
  level: LogLevel.DEBUG,        // 日志级别
  enableTimestamp: true,         // 启用时间戳
  enableStackTrace: false,       // 启用堆栈跟踪
  prefix: 'MyApp',              // 日志前缀
});
```

### 使用场景

#### 1. 在 Vue 组件中使用

```vue
<script setup lang="ts">
import { createLogger } from '@/utils/logger';
import { onMounted } from 'vue';

const logger = createLogger('TestCaseList');

onMounted(() => {
  logger.info('组件已挂载');
  loadData();
});

async function loadData() {
  logger.time('加载数据');
  
  try {
    // 加载数据逻辑
    logger.success('数据加载成功');
  } catch (error) {
    logger.error('数据加载失败', error);
  } finally {
    logger.timeEnd('加载数据');
  }
}
</script>
```

#### 2. 在 API 客户端中使用

```typescript
import { createLogger } from '@/utils/logger';

class ApiClient {
  private logger = createLogger('ApiClient');

  async request(method: string, url: string, data?: unknown) {
    this.logger.api(method, url, data);

    try {
      const response = await fetch(url, {
        method,
        body: JSON.stringify(data),
      });
      
      const result = await response.json();
      this.logger.success('请求成功', result);
      return result;
    } catch (error) {
      this.logger.error('请求失败', error);
      throw error;
    }
  }
}
```

#### 3. 在 Pinia Store 中使用

```typescript
import { defineStore } from 'pinia';
import { createLogger } from '@/utils/logger';

export const useUserStore = defineStore('user', () => {
  const logger = createLogger('UserStore');

  async function login(username: string, password: string) {
    logger.info('开始登录', { username });

    try {
      // 登录逻辑
      logger.success('登录成功', { username });
    } catch (error) {
      logger.error('登录失败', error);
      throw error;
    }
  }

  return { login };
});
```

#### 4. 在路由守卫中使用

```typescript
import { createLogger } from '@/utils/logger';

const logger = createLogger('RouterGuard');

router.beforeEach((to, from, next) => {
  logger.router(from.path, to.path, {
    from: from.name,
    to: to.name,
  });

  // 权限检查逻辑
  next();
});
```

### 日志级别

Logger 支持以下日志级别（按优先级从低到高）：

- `DEBUG (0)`: 调试信息，仅在开发环境显示
- `INFO (1)`: 普通信息
- `WARN (2)`: 警告信息
- `ERROR (3)`: 错误信息
- `NONE (4)`: 不显示任何日志

设置日志级别后，只有等于或高于该级别的日志才会显示。

```typescript
import { createLogger, LogLevel } from '@/utils/logger';

// 只显示警告和错误
const logger = createLogger('Production', {
  level: LogLevel.WARN,
});

logger.debug('不会显示');
logger.info('不会显示');
logger.warn('会显示');
logger.error('会显示');
```

### 最佳实践

1. **为每个模块创建独立的 Logger**
   ```typescript
   const logger = createLogger('ModuleName');
   ```

2. **使用合适的日志级别**
   - `debug`: 详细的调试信息
   - `info`: 一般性信息
   - `success`: 操作成功的反馈
   - `warn`: 警告信息，不影响功能但需要注意
   - `error`: 错误信息，影响功能正常运行

3. **记录关键操作**
   - 用户登录/登出
   - API 请求
   - 路由导航
   - 数据加载
   - 错误和异常

4. **使用性能计时**
   ```typescript
   logger.time('操作名称');
   // 执行操作
   logger.timeEnd('操作名称');
   ```

5. **记录详细的错误信息**
   ```typescript
   try {
     // 操作
   } catch (error) {
     logger.error('操作失败', {
       error,
       message: error instanceof Error ? error.message : '未知错误',
       stack: error instanceof Error ? error.stack : undefined,
     });
   }
   ```

6. **生产环境配置**
   - 在生产环境中，建议将日志级别设置为 `WARN` 或 `ERROR`
   - 启用错误监控服务（如 Sentry）来收集生产环境的错误

### 环境配置

Logger 会根据环境自动调整默认配置：

- **开发环境 (DEV)**: 默认级别为 `DEBUG`，显示所有日志
- **生产环境 (PROD)**: 默认级别为 `INFO`，只显示重要信息

你可以通过配置覆盖默认行为：

```typescript
const logger = createLogger('MyModule', {
  level: import.meta.env.PROD ? LogLevel.WARN : LogLevel.DEBUG,
});
```

### 示例代码

完整的使用示例请参考 `logger.example.ts` 文件。

### 注意事项

1. 避免在循环中使用日志，可能会影响性能
2. 敏感信息（如密码、token）不要记录到日志中
3. 在生产环境中，建议配置错误监控服务来收集错误日志
4. 日志数据对象应该是可序列化的，避免循环引用

### 未来计划

- [ ] 支持日志持久化到本地存储
- [ ] 支持日志上传到服务器
- [ ] 支持自定义日志格式
- [ ] 支持日志过滤和搜索
- [ ] 集成错误监控服务（Sentry）
