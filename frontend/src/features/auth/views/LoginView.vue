<script setup lang="ts">
import LoginForm from '../components/LoginForm.vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950 px-4">
    <div class="w-full max-w-md bg-surface-0 dark:bg-surface-900 p-8 rounded-2xl shadow-xl border border-surface-200 dark:border-surface-800">
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-xl bg-primary-500 text-white flex items-center justify-center font-bold text-3xl mx-auto shadow-md mb-4">
          E
        </div>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Sign In</h1>
        <p class="text-surface-500 mt-2">{{ t('app.title') }}</p>
      </div>

      <LoginForm />
    </div>
  </div>
</template>
