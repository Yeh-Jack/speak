import { ref } from 'vue';

export function useAuth() {
  const user = ref<{ email: string } | null>({ email: 'user@example.com' });
  const isAuthenticated = ref(true);

  return {
    user,
    isAuthenticated,
    login: async () => {},
    logout: async () => {},
  };
}