<script setup lang="ts">
import { useUIStore } from '@/stores/ui.store';
import { useAuthStore } from '@/features/auth/stores/auth.store';
import { useI18n } from 'vue-i18n';
import Button from 'primevue/button';
import Select from 'primevue/select';
import Menu from 'primevue/menu';
import { computed, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const uiStore = useUIStore();
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();

const userMenuRef = ref();

const languages = computed(() => [
  { name: 'EN', code: 'en' },
  { name: 'বাং', code: 'bn' }
]);

const currentLang = computed({
  get: () => languages.value.find(l => l.code === uiStore.currentLocale),
  set: (val) => {
    if (val) uiStore.setLanguage(val.code as 'en' | 'bn');
  }
});

const userInitials = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.email || 'U';
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
});

const userMenuItems = computed(() => [
  { label: authStore.user?.full_name || 'User', disabled: true, class: 'font-semibold' },
  { separator: true },
  { label: authStore.user?.email || '', disabled: true, class: 'text-xs text-slate-400' },
  { separator: true },
  { label: t('app.theme.light'), icon: 'pi pi-sun', command: () => { if (uiStore.theme === 'dark') uiStore.toggleTheme(); } },
  { label: t('app.theme.dark'), icon: 'pi pi-moon', command: () => { if (uiStore.theme === 'light') uiStore.toggleTheme(); } },
  { separator: true },
  { label: 'Sign Out', icon: 'pi pi-sign-out', command: () => { authStore.logout(); router.push('/login'); } }
]);

const pageTitle = computed(() => {
  const name = route.name as string;
  if (!name) return '';
  const map: Record<string, string> = {
    home: 'Dashboard',
    'academic.classes': 'Classes',
    'academic.sections': 'Sections',
    'academic.subjects': 'Subjects',
    'academic.students': 'Students',
    'academic.guardians': 'Guardians',
    'reports.academic': 'Academic Reports',
    'reports.exam': 'Exam Reports',
  };
  return map[name] || name;
});

const toggleUserMenu = (event: Event) => {
  userMenuRef.value.toggle(event);
};
</script>

<template>
  <header class="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 md:px-6 z-30 shrink-0">
    <!-- Left: Hamburger + Page title -->
    <div class="flex items-center gap-3">
      <Button
        @click="uiStore.toggleMobileSidebar"
        icon="pi pi-bars"
        severity="secondary"
        text
        rounded
        class="lg:hidden"
        aria-label="Toggle Menu"
      />
      <Button
        @click="uiStore.toggleSidebar"
        icon="pi pi-bars"
        severity="secondary"
        text
        rounded
        class="hidden lg:inline-flex"
        aria-label="Toggle Sidebar"
      />
      <div class="hidden sm:block">
        <h2 class="text-lg font-semibold text-slate-800 dark:text-slate-200 leading-tight">{{ pageTitle }}</h2>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-2">
      <!-- Language selector -->
      <Select
        v-model="currentLang"
        :options="languages"
        optionLabel="name"
        class="w-20 text-sm"
      />

      <!-- Notification placeholder -->
      <Button
        icon="pi pi-bell"
        severity="secondary"
        text
        rounded
        badge="0"
        aria-label="Notifications"
        class="text-slate-500"
      />

      <!-- User avatar -->
      <button
        @click="toggleUserMenu"
        class="ml-1 flex items-center gap-2 cursor-pointer rounded-full p-1 hover:bg-slate-100 dark:hover:bg-slate-800"
        aria-label="User menu"
      >
        <div class="avatar-initials bg-primary-600 text-white text-xs">
          {{ userInitials }}
        </div>
      </button>

      <Menu ref="userMenuRef" :model="userMenuItems" :popup="true" class="min-w-52" />
    </div>
  </header>
</template>
