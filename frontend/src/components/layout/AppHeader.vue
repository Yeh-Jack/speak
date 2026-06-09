<script setup lang="ts">
import { useLanguageStore } from '@/stores/language.store';
import { useI18n } from '@/composables/useI18n';
import { useRoute } from 'vue-router';

const languageStore = useLanguageStore();
const { t } = useI18n();
const route = useRoute();

const isLearningPage = route.path.startsWith('/videos/');
</script>

<template>
  <header class="sticky top-0 z-40 bg-learning-bg-secondary border-b border-learning-bg-tertiary">
    <div class="container mx-auto px-4 py-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <router-link to="/" class="text-xl font-bold font-display text-learning-text-primary">
          Speak
        </router-link>
        <template v-if="isLearningPage">
          <span class="text-learning-text-muted">/</span>
          <span class="text-learning-text-secondary">{{ t('Learning', '學習') }}</span>
        </template>
      </div>
      <nav class="flex items-center gap-6">
        <router-link to="/" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
          {{ t('Dashboard', '首頁') }}
        </router-link>
        <router-link to="/speaking" class="text-learning-text-secondary hover:text-learning-text-primary transition-colors">
          {{ t('Speaking', '口說') }}
        </router-link>
      </nav>
      <div class="flex items-center gap-3">
        <button
          @click="languageStore.toggleZh()"
          class="px-3 py-1.5 text-sm rounded border transition-colors"
          :class="languageStore.showZh
            ? 'bg-learning-accent-primary text-white border-learning-accent-primary'
            : 'bg-learning-bg-primary text-learning-text-secondary border-learning-bg-tertiary hover:border-learning-accent-primary'"
        >
          中文
        </button>
        <div class="w-8 h-8 rounded-full bg-learning-accent-primary flex items-center justify-center text-white font-medium">
          U
        </div>
      </div>
    </div>
  </header>
</template>