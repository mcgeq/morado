# 认证系统说明

## 当前状态

项目目前使用简单的 localStorage token 认证机制，这是一个**占位实现**，用于开发阶段。

## 开发模式行为

在开发模式下（`import.meta.env.DEV === true`），认证检查已被**自动通过**，这样可以方便开发和测试所有页面，无需每次都登录。

```typescript
// frontend/src/router/index.ts
function checkAuthentication(): boolean {
  // 开发模式下，暂时允许所有访问
  if (import.meta.env.DEV) {
    return true;
  }

  // 生产模式下，检查 localStorage 中的 token
  const token = localStorage.getItem('auth_token');
  return !!token;
}
```

## 生产模式行为

在生产模式下，系统会检查 `localStorage` 中的 `auth_token`：
- ✅ 如果存在 token，允许访问需要认证的页面
- ❌ 如果不存在 token，重定向到首页，并保存原始目标路径

## 路由认证配置

每个路由可以通过 `meta.requiresAuth` 配置是否需要认证：

```typescript
{
  path: '/test-cases',
  name: 'TestCaseList',
  component: () => import('@/views/TestCase/List.vue'),
  meta: {
    title: '测试用例',
    requiresAuth: true,  // 需要认证
  },
}
```

## 当前认证流程

### 1. 用户访问需要认证的页面

```
用户访问 /test-cases
    ↓
路由守卫检查 requiresAuth
    ↓
调用 checkAuthentication()
    ↓
开发模式？
    ├─ 是 → 允许访问 ✅
    └─ 否 → 检查 localStorage.auth_token
        ├─ 存在 → 允许访问 ✅
        └─ 不存在 → 重定向到首页 ❌
```

### 2. 模拟登录（开发用）

在 DefaultLayout 中点击"登录"按钮：

```typescript
const handleLogin = () => {
  // 设置一个假的 token
  localStorage.setItem('auth_token', 'dummy_token');
  router.push({ name: 'Home' });
};
```

### 3. 登出

```typescript
const handleLogout = () => {
  // 清除 token
  localStorage.removeItem('auth_token');
  router.push({ name: 'Home' });
};
```

## 如何测试认证

### 方法 1：开发模式（推荐）

直接启动开发服务器，所有页面都可以访问：

```bash
bun run dev
```

### 方法 2：模拟登录

1. 访问首页
2. 点击右上角的"登录"按钮
3. 系统会设置一个假的 token
4. 现在可以访问所有需要认证的页面

### 方法 3：手动设置 token

在浏览器控制台执行：

```javascript
localStorage.setItem('auth_token', 'test_token');
location.reload();
```

## 需要认证的路由

以下路由需要认证（`requiresAuth: true`）：

- `/headers` - Header 管理
- `/bodies` - Body 管理
- `/api-definitions` - API 定义
- `/scripts` - 脚本管理
- `/components` - 组件管理
- `/test-cases` - 测试用例
- `/test-suites` - 测试套件
- `/reports` - 测试报告

## 不需要认证的路由

以下路由不需要认证（`requiresAuth: false`）：

- `/` - 首页
- `/tailwind-test` - Tailwind CSS 测试页面
- `/404` - 404 页面

## 实现真实认证系统

当需要实现真实的认证系统时，需要修改以下部分：

### 1. 更新 checkAuthentication 函数

```typescript
// frontend/src/router/index.ts
function checkAuthentication(): boolean {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    return false;
  }

  // TODO: 验证 token 是否有效
  // 可以调用后端 API 验证 token
  // 或者检查 token 是否过期
  
  return true;
}
```

### 2. 实现登录 API 调用

```typescript
// frontend/src/api/auth.ts
import axios from 'axios';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await axios.post<AuthResponse>('/api/v1/auth/login', credentials);
  return response.data;
}

export async function logout(): Promise<void> {
  await axios.post('/api/v1/auth/logout');
}

export async function getCurrentUser(): Promise<User> {
  const response = await axios.get<User>('/api/v1/auth/me');
  return response.data;
}
```

### 3. 使用 Pinia Store 管理认证状态

```typescript
// frontend/src/stores/user.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { login as apiLogin, logout as apiLogout } from '@/api/auth';

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(null);
  const user = ref<User | null>(null);

  async function login(credentials: LoginCredentials) {
    const response = await apiLogin(credentials);
    token.value = response.access_token;
    localStorage.setItem('auth_token', response.access_token);
    
    // 获取用户信息
    await fetchUserProfile();
  }

  async function logout() {
    await apiLogout();
    token.value = null;
    user.value = null;
    localStorage.removeItem('auth_token');
  }

  return { token, user, login, logout };
});
```

### 4. 添加 Axios 拦截器

```typescript
// frontend/src/api/index.ts
import axios from 'axios';

// 请求拦截器 - 添加 token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理 401 错误
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token 无效或过期，清除并重定向到登录页
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);
```

## 安全建议

1. **不要在 localStorage 中存储敏感信息**
   - 只存储 token，不存储密码或其他敏感数据

2. **实现 token 刷新机制**
   - 使用 refresh token 自动刷新 access token
   - 避免用户频繁登录

3. **添加 CSRF 保护**
   - 在表单提交时添加 CSRF token

4. **使用 HTTPS**
   - 生产环境必须使用 HTTPS 传输

5. **实现登录限流**
   - 防止暴力破解攻击

6. **添加日志记录**
   - 记录所有认证相关的操作

## 当前限制

⚠️ **注意**：当前的认证系统是一个简单的占位实现，**不适合生产环境**。

存在的问题：
- ❌ 没有真实的 token 验证
- ❌ 没有 token 过期检查
- ❌ 没有刷新 token 机制
- ❌ 没有与后端 API 集成
- ❌ 开发模式下完全绕过认证

## 下一步

1. 实现后端认证 API
2. 集成前端认证流程
3. 添加登录页面
4. 实现 token 刷新
5. 添加权限管理
6. 实现记住登录状态

## 总结

- ✅ 开发模式下，所有页面都可以直接访问
- ✅ 生产模式下，需要 token 才能访问受保护的页面
- ✅ 可以通过点击"登录"按钮模拟登录
- ⚠️ 当前实现仅用于开发，不适合生产环境
