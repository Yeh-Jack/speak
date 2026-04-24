<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth.store';
import BaseInput from '@/components/common/BaseInput.vue';
import BaseButton from '@/components/common/BaseButton.vue';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const isRegistering = ref(false);

async function handleSubmit() {
  try {
    if (isRegistering.value) {
      await authStore.register({ email: email.value, password: password.value });
    } else {
      await authStore.login({ email: email.value, password: password.value });
    }
    router.push({ name: 'dashboard' });
  } catch (err) {
    // Error is handled in the store
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900">
    <div class="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
      <h1 class="text-2xl font-bold text-white mb-6 text-center">
        {{ isRegistering ? 'Create Account' : 'Sign In' }}
      </h1>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <BaseInput
          v-model="email"
          type="email"
          label="Email"
          placeholder="Enter your email"
          required
        />
        
        <BaseInput
          v-model="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          required
        />
        
        <div v-if="authStore.error" class="text-red-400 text-sm">
          {{ authStore.error }}
        </div>
        
        <BaseButton
          type="submit"
          :loading="authStore.isLoading"
          class="w-full"
        >
          {{ isRegistering ? 'Create Account' : 'Sign In' }}
        </BaseButton>
      </form>
      
      <p class="mt-4 text-center text-gray-400 text-sm">
        {{ isRegistering ? 'Already have an account?' : "Don't have an account?" }}
        <button
          @click="isRegistering = !isRegistering"
          class="text-blue-400 hover:text-blue-300 ml-1"
        >
          {{ isRegistering ? 'Sign In' : 'Create one' }}
        </button>
      </p>
    </div>
  </div>
</template>
