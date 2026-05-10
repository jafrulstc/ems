<script setup lang="ts">
import { useUIStore } from '@/stores/ui.store';
import { useI18n } from 'vue-i18n';
import Button from 'primevue/button';
import Select from 'primevue/select';
import { computed } from 'vue';

const uiStore = useUIStore();
const { t } = useI18n();

const languages = computed(() => [
  { name: t('app.language.en'), code: 'en' },
  { name: t('app.language.bn'), code: 'bn' }
]);

const currentLang = computed({
  get: () => languages.value.find(l => l.code === uiStore.currentLocale),
  set: (val) => {
    if (val) uiStore.setLanguage(val.code as 'en' | 'bn');
  }
});
</script>

<template>
  <div class="h-[70px] bg-surface-0 dark:bg-surface-900 shadow-sm border-b border-surface-200 dark:border-surface-800 flex items-center justify-between px-6 transition-colors duration-200 z-10 sticky top-0">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-lg bg-primary-500 text-white flex items-center justify-center font-bold text-xl shadow-md">
        E
      </div>
      <span class="text-xl font-semibold text-surface-900 dark:text-surface-0 hidden sm:block">
        {{ t('app.title') }}
      </span>
    </div>

    <div class="flex items-center gap-4">
      <Select 
        v-model="currentLang" 
        :options="languages" 
        optionLabel="name" 
        class="w-32" 
      />
      
      <Button 
        @click="uiStore.toggleTheme" 
        :icon="uiStore.theme === 'light' ? 'pi pi-moon' : 'pi pi-sun'"
        severity="secondary" 
        text 
        rounded 
        aria-label="Toggle Theme"
      />
    </div>
  </div>
</template>
