<script setup lang="ts">
import { useI18n } from '@/composables/useI18n';

const { t } = useI18n();
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold text-white mb-8">{{ t('Settings', '設定') }}</h1>
      <div class="bg-gray-800 p-6 rounded-lg">
        <p class="text-gray-300">{{ t('Settings coming soon...', '設定即將推出...') }}</p>
      </div>
    </div>
  </div>
</template>
