import { useLanguageStore } from '@/stores/language.store';

export function useI18n() {
  const languageStore = useLanguageStore();

  function t(en: string, zh: string): string {
    return languageStore.showZh ? `${en} / ${zh}` : en;
  }

  return { t, showZh: languageStore.showZh };
}