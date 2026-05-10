import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

export const useUIStore = defineStore('ui', () => {
  const { locale } = useI18n();

  // --- Theme ---
  const savedTheme = localStorage.getItem('theme') || 'light';
  const theme = ref<'light' | 'dark'>(savedTheme as 'light' | 'dark');

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  };

  watch(theme, (newTheme) => {
    localStorage.setItem('theme', newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, { immediate: true });

  // --- Language ---
  const currentLocale = ref<'en' | 'bn'>(locale.value as 'en' | 'bn');

  const setLanguage = (lang: 'en' | 'bn') => {
    currentLocale.value = lang;
    locale.value = lang;
    localStorage.setItem('locale', lang);
  };

  return {
    theme,
    toggleTheme,
    currentLocale,
    setLanguage,
  };
});
