import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth.store';
import type { LoginRequest, RegisterRequest } from '@/types';

export function useAuth() {
  const store = useAuthStore();

  return {
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    isLoading: computed(() => store.isLoading),
    error: computed(() => store.error),
    login: store.login,
    register: store.register,
    logout: store.logout,
    initialize: store.initialize,
  };
}
