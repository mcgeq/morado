# 清除认证状态

## 问题
开发服务器启动后直接显示首页，而不是登录页面。

## 原因
localStorage 中存在旧的 `auth_token`，导致路由守卫认为用户已登录。

## 解决方案

### 方法 1：在浏览器控制台清除（推荐）

1. 打开浏览器开发者工具（按 F12）
2. 切换到 Console（控制台）标签
3. 输入以下命令并回车：

```javascript
localStorage.clear()
location.reload()
```

### 方法 2：手动清除 localStorage

1. 打开浏览器开发者工具（按 F12）
2. 切换到 Application（应用）标签
3. 在左侧找到 Storage > Local Storage > http://localhost:3000
4. 删除 `auth_token` 和 `user_info` 两个键
5. 刷新页面（F5）

### 方法 3：使用隐私模式

1. 打开浏览器的隐私/无痕模式
2. 访问 http://localhost:3000
3. 这样会使用全新的 localStorage

## 登录测试账号

清除认证后，使用以下账号登录：

- **用户名**: demo
- **密码**: demo123

## 验证

清除认证后，访问 http://localhost:3000 应该会：
1. 自动重定向到 /login
2. 显示登录/注册界面
3. 可以使用 demo/demo123 登录
