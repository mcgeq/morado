/**
 * User Store
 *
 * Manages user authentication state, profile information, and permissions.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

// User Types
export interface User {
  id: number;
  uuid: string;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  role: 'admin' | 'developer' | 'tester' | 'viewer';
  permissions: string[];
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
}

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isAuthenticated = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isDeveloper = computed(() => user.value?.role === 'developer');
  const isTester = computed(() => user.value?.role === 'tester');
  const isViewer = computed(() => user.value?.role === 'viewer');

  const hasPermission = computed(() => {
    return (permission: string): boolean => {
      if (!user.value) return false;
      return user.value.permissions.includes(permission) || user.value.role === 'admin';
    };
  });

  const userInitials = computed(() => {
    if (!user.value) return '';
    if (user.value.full_name) {
      const names = user.value.full_name.split(' ');
      return names
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    return user.value.username.slice(0, 2).toUpperCase();
  });

  // Actions
  async function login(_credentials: LoginCredentials): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      // TODO: Replace with actual API call
      // const response = await apiClient.post<AuthToken>('/auth/login', credentials);
      // const authToken = response.data;

      // Mock implementation for now
      const authToken: AuthToken = {
        access_token: 'mock_token_' + Date.now(),
        token_type: 'Bearer',
        expires_in: 3600,
      };

      token.value = authToken.access_token;
      localStorage.setItem('auth_token', authToken.access_token);

      // Fetch user profile
      await fetchUserProfile();

      isAuthenticated.value = true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout(): Promise<void> {
    try {
      // TODO: Call logout API endpoint
      // await apiClient.post('/auth/logout');

      // Clear state
      user.value = null;
      token.value = null;
      isAuthenticated.value = false;
      localStorage.removeItem('auth_token');
    } catch (err) {
      console.error('Logout error:', err);
      // Clear state anyway
      user.value = null;
      token.value = null;
      isAuthenticated.value = false;
      localStorage.removeItem('auth_token');
    }
  }

  async function fetchUserProfile(): Promise<void> {
    try {
      // TODO: Replace with actual API call
      // const response = await apiClient.get<User>('/auth/me');
      // user.value = response.data;

      // Mock implementation for now
      user.value = {
        id: 1,
        uuid: 'user-uuid-123',
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'developer',
        permissions: ['read', 'write', 'execute'],
        is_active: true,
        created_at: new Date().toISOString(),
      };
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch user profile';
      throw err;
    }
  }

  async function updateProfile(updates: Partial<User>): Promise<void> {
    if (!user.value) throw new Error('No user logged in');

    isLoading.value = true;
    error.value = null;

    try {
      // TODO: Replace with actual API call
      // const response = await apiClient.patch<User>(`/users/${user.value.id}`, updates);
      // user.value = response.data;

      // Mock implementation for now
      user.value = { ...user.value, ...updates };
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update profile';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function changePassword(_currentPassword: string, _newPassword: string): Promise<void> {
    if (!user.value) throw new Error('No user logged in');

    isLoading.value = true;
    error.value = null;

    try {
      // TODO: Replace with actual API call
      // await apiClient.post('/auth/change-password', {
      //   current_password: currentPassword,
      //   new_password: newPassword,
      // });

      // Mock implementation for now
      console.log('Password changed successfully');
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to change password';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function initializeFromStorage(): void {
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      token.value = storedToken;
      isAuthenticated.value = true;
      // Fetch user profile in background
      fetchUserProfile().catch(() => {
        // If profile fetch fails, clear auth state
        logout();
      });
    }
  }

  function clearError(): void {
    error.value = null;
  }

  // Return store interface
  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading,
    error,

    // Computed
    isAdmin,
    isDeveloper,
    isTester,
    isViewer,
    hasPermission,
    userInitials,

    // Actions
    login,
    logout,
    fetchUserProfile,
    updateProfile,
    changePassword,
    initializeFromStorage,
    clearError,
  };
});
