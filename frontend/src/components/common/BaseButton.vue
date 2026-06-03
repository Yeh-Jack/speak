<script setup lang="ts">
interface Props {
  type?: 'button' | 'submit' | 'reset';
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  loading: false,
  disabled: false,
  variant: 'primary',
  size: 'md',
});

const variantClasses = {
  primary: 'bg-learning-accent-primary hover:bg-learning-accent-primary/90 text-white shadow-md hover:shadow-lg',
  secondary: 'bg-learning-bg-primary hover:bg-learning-bg-secondary text-learning-text-primary border border-learning-bg-tertiary',
  ghost: 'bg-transparent hover:bg-learning-bg-primary text-learning-text-secondary hover:text-learning-text-primary',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-learning-accent-primary/50"
    :class="[variantClasses[variant], sizeClasses[size]]"
  >
    <span v-if="loading" class="mr-2">
      <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    <slot />
  </button>
</template>