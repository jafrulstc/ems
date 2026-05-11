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

  // --- Sidebar ---
  const sidebarCollapsed = ref(false);
  const sidebarMobileOpen = ref(false);

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  };

  const toggleMobileSidebar = () => {
    sidebarMobileOpen.value = !sidebarMobileOpen.value;
  };

  const closeMobileSidebar = () => {
    sidebarMobileOpen.value = false;
  };

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
    sidebarCollapsed,
    sidebarMobileOpen,
    toggleSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    currentLocale,
    setLanguage,
  };
});
