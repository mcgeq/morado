# 认证系统说明

## 当前状态

项目使用基于 localStorage token 的认证机制，包含完整的登录/注册流程。

## 用户流程

### 1. 首次访问

```
用户访问任何页面
    ↓
检查是否已登录？
    ├─ 否 → 重定向到登录页面 (/login)
    └─ 是 → 显示请求的页面
```

### 2. 登录流程

```
访问登录页面 (/login)
    ↓
输入用户名和密码
    ↓
点击"登录"按钮
    ↓
验证成功？
    ├─ 是 → 保存 token → 跳转到目标页面
    └─ 否 → 显示错误信息
```

### 3. 注册流程

```
访问登录页面 (/login)
    ↓
切换到"注册"标签
    ↓
填写注册信息
    ↓
点击"注册"按钮
    ↓
注册成功 → 自动登录 → 跳转到首页
```

## 演示账号

为了方便测试，系统提供了演示账号：

- **用户名**: demo
- **密码**: demo123

## 路由保护

### 需要认证的路由

所有业务页面都需要认证（`requiresAuth: true`）：

- `/` - 首页（Dashboard）
- `/headers` - Header 管理
- `/bodies` - Body 管理
- `/api-definitions` - API 定义
- `/scripts` - 脚本管理
- `/components` - 组件管理
- `/test-cases` - 测试用例
- `/test-suites` - 测试套件
- `/reports` - 测试报告

### 不需要认证的路由

- `/login` - 登录/注册页面
- `/tailwind-test` - Tailwind CSS 测试页面
- `/404` - 404 页面

## 认证逻辑

### 路由守卫

```typescript
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;

  if (requiresAuth) {
    const isAuthenticated = checkAuthentication();

    if (!isAuthenticated) {
      // 未登录，重定向到登录页
      next({
        name: 'Login',
        query: { redirect: to.fullPath }, // 保存目标路径
      });
    } else {
      next();
    }
  } else {
    // 已登录用户访问登录页，重定向到首页
    if (to.name === 'Login' && checkAuthentication()) {
      next({ name: 'Dashboard' });
    } else {
      next();
    }
  }
});
```

### 认证检查

```typescript
function checkAuthentication(): boolean {
  const token = localStorage.getItem('auth_token');
  return !!token;
}
```

## 数据存储

### localStorage 存储的数据

1. **auth_token**: 认证令牌
   ```javascript
   localStorage.setItem('auth_token', 'token_1234567890');
   ```

2. **user_info**: 用户信息
   ```javascript
   localStorage.setItem('user_info', JSON.stringify({
     username: 'demo',
     email: 'demo@example.com',
     role: 'developer'
   }));
   ```

## 登录页面功能

### 登录表单

- 用户名输入
- 密码输入
- "记住我"选项
- "忘记密码"链接（占位）
- 演示账号提示

### 注册表单

- 用户名输入
- 邮箱输入
- 密码输入（至少6位）
- 确认密码输入
- 密码验证

### UI 特性

- ✅ 响应式设计
- ✅ 加载状态显示
- ✅ 错误信息提示
- ✅ 表单验证
- ✅ 平滑动画过渡

## 使用方法

### 1. 启动应用

```bash
cd frontend
bun run dev
```

### 2. 访问应用

打开浏览器访问 http://localhost:3000

### 3. 登录

- 使用演示账号登录：
  - 用户名: `demo`
  - 密码: `demo123`

- 或者注册新账号

### 4. 使用系统

登录成功后，可以访问所有功能页面。

## 登出流程

```
点击右上角"退出"按钮
    ↓
清除 localStorage 数据
    ├─ 删除 auth_token
    └─ 删除 user_info
    ↓
重定向到登录页面
```

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
