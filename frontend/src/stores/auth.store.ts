import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import { authService } from '@/services/auth.service';
import type { User, LoginRequest, RegisterRequest } from '@/types';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value);

  // Actions
  async function login(credentials: LoginRequest) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await authService.login(credentials);
      token.value = response.access_token;
      authService.setToken(response.access_token);
      await fetchCurrentUser();
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(data: RegisterRequest) {
    isLoading.value = true;
    error.value = null;
    try {
      await authService.register(data);
      // Auto-login after registration
      await login({ email: data.email, password: data.password });
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Registration failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchCurrentUser() {
    try {
      user.value = await authService.getCurrentUser();
    } catch (err) {
      logout();
    }
  }

  function logout() {
    user.value = null;
    token.value = null;
    authService.logout();
  }

  function initialize() {
    const storedToken = authService.getToken();
    if (storedToken) {
      token.value = storedToken;
      fetchCurrentUser();
    }
  }

  return {
    user,
    token,
    isLoading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    initialize,
    fetchCurrentUser,
  };
});
