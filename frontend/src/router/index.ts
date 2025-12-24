import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
  type RouteRecordRaw,
} from 'vue-router';
import { createLogger } from '@/utils/logger';

const logger = createLogger('Router');

/**
 * Route definitions with lazy loading for optimal performance
 * Routes are organized by feature area following the four-layer architecture
 */
const routes: RouteRecordRaw[] = [
  // Auth Routes
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },

  // Dashboard (Home) - Requires Auth
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: 'Morado测试平台',
      requiresAuth: true,
    },
  },

  // Layer 1: Header Management Routes
  {
    path: '/headers',
    name: 'HeaderList',
    component: () => import('@/views/Header/List.vue'),
    meta: {
      title: 'Header管理',
      requiresAuth: true,
    },
  },
  {
    path: '/headers/create',
    name: 'HeaderCreate',
    component: () => import('@/views/Header/Edit.vue'),
    meta: {
      title: '创建Header',
      requiresAuth: true,
    },
  },
  {
    path: '/headers/:id/edit',
    name: 'HeaderEdit',
    component: () => import('@/views/Header/Edit.vue'),
    meta: {
      title: '编辑Header',
      requiresAuth: true,
    },
  },

  // Layer 1: Body Management Routes
  {
    path: '/bodies',
    name: 'BodyList',
    component: () => import('@/views/Body/List.vue'),
    meta: {
      title: 'Body管理',
      requiresAuth: true,
    },
  },
  {
    path: '/bodies/create',
    name: 'BodyCreate',
    component: () => import('@/views/Body/Edit.vue'),
    meta: {
      title: '创建Body',
      requiresAuth: true,
    },
  },
  {
    path: '/bodies/:id/edit',
    name: 'BodyEdit',
    component: () => import('@/views/Body/Edit.vue'),
    meta: {
      title: '编辑Body',
      requiresAuth: true,
    },
  },

  // Layer 1: API Definition Routes
  {
    path: '/api-definitions',
    name: 'ApiDefinitionList',
    component: () => import('@/views/ApiDefinition/List.vue'),
    meta: {
      title: 'API定义管理',
      requiresAuth: true,
    },
  },
  {
    path: '/api-definitions/create',
    name: 'ApiDefinitionCreate',
    component: () => import('@/views/ApiDefinition/Edit.vue'),
    meta: {
      title: '创建API定义',
      requiresAuth: true,
    },
  },
  {
    path: '/api-definitions/:id/edit',
    name: 'ApiDefinitionEdit',
    component: () => import('@/views/ApiDefinition/Edit.vue'),
    meta: {
      title: '编辑API定义',
      requiresAuth: true,
    },
  },

  // Layer 2: Script Management Routes
  {
    path: '/scripts',
    name: 'ScriptList',
    component: () => import('@/views/Script/List.vue'),
    meta: {
      title: '脚本管理',
      requiresAuth: true,
    },
  },
  {
    path: '/scripts/create',
    name: 'ScriptCreate',
    component: () => import('@/views/Script/Edit.vue'),
    meta: {
      title: '创建脚本',
      requiresAuth: true,
    },
  },
  {
    path: '/scripts/:id/edit',
    name: 'ScriptEdit',
    component: () => import('@/views/Script/Edit.vue'),
    meta: {
      title: '编辑脚本',
      requiresAuth: true,
    },
  },
  {
    path: '/scripts/:id/debug',
    name: 'ScriptDebug',
    component: () => import('@/views/Script/Debug.vue'),
    meta: {
      title: '调试脚本',
      requiresAuth: true,
    },
  },

  // Layer 3: Component Management Routes
  {
    path: '/components',
    name: 'ComponentList',
    component: () => import('@/views/Component/List.vue'),
    meta: {
      title: '组件管理',
      requiresAuth: true,
    },
  },
  {
    path: '/components/create',
    name: 'ComponentCreate',
    component: () => import('@/views/Component/Edit.vue'),
    meta: {
      title: '创建组件',
      requiresAuth: true,
    },
  },
  {
    path: '/components/:id/edit',
    name: 'ComponentEdit',
    component: () => import('@/views/Component/Edit.vue'),
    meta: {
      title: '编辑组件',
      requiresAuth: true,
    },
  },
  {
    path: '/components/:id/debug',
    name: 'ComponentDebug',
    component: () => import('@/views/Component/Debug.vue'),
    meta: {
      title: '调试组件',
      requiresAuth: true,
    },
  },

  // Layer 4: Test Case Routes
  {
    path: '/test-cases',
    name: 'TestCaseList',
    component: () => import('@/views/TestCase/List.vue'),
    meta: {
      title: '测试用例',
      requiresAuth: true,
    },
  },
  {
    path: '/test-cases/create',
    name: 'TestCaseCreate',
    component: () => import('@/views/TestCase/Edit.vue'),
    meta: {
      title: '创建测试用例',
      requiresAuth: true,
    },
  },
  {
    path: '/test-cases/:id',
    name: 'TestCaseDetail',
    component: () => import('@/views/TestCase/Detail.vue'),
    meta: {
      title: '测试用例详情',
      requiresAuth: true,
    },
  },
  {
    path: '/test-cases/:id/edit',
    name: 'TestCaseEdit',
    component: () => import('@/views/TestCase/Edit.vue'),
    meta: {
      title: '编辑测试用例',
      requiresAuth: true,
    },
  },

  // Test Suite Routes
  {
    path: '/test-suites',
    name: 'TestSuiteList',
    component: () => import('@/views/TestSuite/List.vue'),
    meta: {
      title: '测试套件',
      requiresAuth: true,
    },
  },

  // Report Routes
  {
    path: '/reports',
    name: 'ReportDashboard',
    component: () => import('@/views/Report/Dashboard.vue'),
    meta: {
      title: '测试报告',
      requiresAuth: true,
    },
  },

  // 404 Not Found Route
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面未找到',
      requiresAuth: false,
    },
  },

  // Tailwind CSS Test Route (Development only)
  {
    path: '/tailwind-test',
    name: 'TailwindTest',
    component: () => import('@/views/TailwindTest.vue'),
    meta: {
      title: 'Tailwind CSS 测试',
      requiresAuth: false,
    },
  },

  // I18n Test Route (Development only)
  {
    path: '/i18n-test',
    name: 'I18nTest',
    component: () => import('@/views/I18nTest.vue'),
    meta: {
      title: 'I18n 测试',
      requiresAuth: false,
    },
  },
];

/**
 * Create router instance with history mode
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    // Restore scroll position when using browser back/forward
    if (savedPosition) {
      return savedPosition;
    }
    // Scroll to top for new routes
    return { top: 0 };
  },
});

/**
 * Global navigation guard - Authentication check
 * Runs before every route navigation
 */
router.beforeEach(
  (to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
    // Update document title
    if (to.meta.title) {
      document.title = `${to.meta.title} - Morado`;
    }

    // Check if route requires authentication
    const requiresAuth = to.meta.requiresAuth as boolean;

    if (requiresAuth) {
      const isAuthenticated = checkAuthentication();

      if (!isAuthenticated) {
        // Redirect to login page if not authenticated
        // Store the intended destination for redirect after login
        logger.warn('未认证用户尝试访问受保护页面', {
          path: to.path,
          name: to.name,
        });

        next({
          name: 'Login',
          query: { redirect: to.fullPath },
        });
      } else {
        next();
      }
    } else {
      // If user is authenticated and trying to access login page, redirect to dashboard
      if (to.name === 'Login' && checkAuthentication()) {
        next({ name: 'Dashboard' });
      } else {
        next();
      }
    }
  },
);

/**
 * Global after navigation guard
 * Runs after every route navigation
 */
router.afterEach((to: RouteLocationNormalized, from: RouteLocationNormalized) => {
  // Log navigation for debugging (can be removed in production)
  if (import.meta.env.DEV) {
    logger.router(from.path, to.path, {
      from: from.name,
      to: to.name,
      params: to.params,
      query: to.query,
    });
  }
});

/**
 * Check if user is authenticated
 * This is a placeholder implementation
 * Replace with actual authentication logic
 */
function checkAuthentication(): boolean {
  // 检查 localStorage 中的 token
  const token = localStorage.getItem('auth_token');
  return !!token;
}

/**
 * Navigation helper functions
 */
export const navigationHelpers = {
  /**
   * Navigate to home page
   */
  goHome() {
    router.push({ name: 'Home' });
  },

  /**
   * Navigate to previous page
   */
  goBack() {
    router.back();
  },

  /**
   * Navigate to a specific route by name
   */
  goTo(name: string, params?: Record<string, string | number>) {
    router.push({ name, params });
  },
};

export default router;
