<script setup lang="ts">
import { useLanguageStore } from '@/stores/language.store';

defineProps<{
  en: string;
  zh: string;
}>();

const languageStore = useLanguageStore();
</script>

<template>
  <span v-if="languageStore.showZh">{{ en }} / {{ zh }}</span>
  <span v-else>{{ en }}</span>
</template>