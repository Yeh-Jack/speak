import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useLanguageStore = defineStore('language', () => {
  const showZh = ref(false);

  function toggleZh() {
    showZh.value = !showZh.value;
  }

  return { showZh, toggleZh };
});