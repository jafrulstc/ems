import { defineStore } from 'pinia';
import { ref, watch, computed } from 'vue';
import { useI18n } from 'vue-i18n';

export const useUIStore = defineStore('ui', () => {
  const { locale } = useI18n();

  // --- Theme ---
  const savedTheme = localStorage.getItem('theme') || 'light';
  const theme = ref<'light' | 'dark'>(savedTheme as 'light' | 'dark');

  const isDark = computed(() => theme.value === 'dark');

  const setTheme = (t: 'light' | 'dark') => {
    theme.value = t;
  };

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

  /** Returns Bangla name if locale is bn and name_bn exists, else English name */
  const displayName = (name: string, nameBn?: string | null) => {
    if (currentLocale.value === 'bn' && nameBn) return nameBn;
    return name;
  };

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    sidebarCollapsed,
    sidebarMobileOpen,
    toggleSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    currentLocale,
    setLanguage,
    displayName,
  };
});
