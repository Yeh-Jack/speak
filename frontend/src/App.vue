<script setup lang="ts">
import { RouterView } from 'vue-router';
import { useVideoStore } from '@/stores/video.store';
import { useI18n } from '@/composables/useI18n';
import AppHeader from '@/components/layout/AppHeader.vue';

const videoStore = useVideoStore();
const { t } = useI18n();
</script>

<template>
  <div id="app">
    <AppHeader />
    <div
      v-if="videoStore.isCreatingVideo"
      class="fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-learning-accent-primary/20 to-learning-accent-primary/10 backdrop-blur-sm border-2 border-learning-accent-primary rounded-xl shadow-lg shadow-learning-accent-primary/20"
    >
      <div class="relative">
        <div class="animate-spin w-6 h-6 border-2 border-learning-accent-primary border-t-transparent rounded-full"></div>
        <div class="absolute inset-0 animate-ping w-6 h-6 border-2 border-learning-accent-primary/50 rounded-full"></div>
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-bold text-learning-accent-primary">{{ t('Processing', '處理中') }}</span>
        <span class="text-xs text-learning-text-secondary">{{ videoStore.createProgress }}</span>
      </div>
    </div>

    <div
      v-if="videoStore.createError"
      class="fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-red-500/20 to-red-500/10 backdrop-blur-sm border-2 border-red-500 rounded-xl shadow-lg shadow-red-500/20 max-w-md"
    >
      <svg class="w-6 h-6 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span class="text-sm text-red-400">{{ videoStore.createError }}</span>
      <button @click="videoStore.setCreatingVideo(false)" class="ml-2 text-sm text-learning-text-muted hover:text-learning-text-primary flex-shrink-0 px-2 py-1 rounded-lg bg-learning-bg-primary/50">✕</button>
    </div>

    <RouterView />
  </div>
</template>

<style>
#app {
  min-height: 100vh;
}

@keyframes ping {
  75%, 100% {
    transform: scale(1.5);
    opacity: 0;
  }
}
.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}
</style>