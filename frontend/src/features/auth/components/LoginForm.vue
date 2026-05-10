<script setup lang="ts">
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import { useAuthStore } from '@/features/auth/stores/auth.store';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const authStore = useAuthStore();
const router = useRouter();
const { t } = useI18n();

const username = ref('');
const password = ref('');
const errorMsg = ref('');

const handleSubmit = async () => {
  errorMsg.value = '';
  try {
    await authStore.login({ username: username.value, password: password.value });
    router.push('/');
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Login failed';
  }
};
</script>

<template>
  <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
    <div v-if="errorMsg" class="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-md text-sm mb-2">
      {{ errorMsg }}
    </div>

    <div class="flex flex-col gap-2">
      <label for="username" class="text-sm font-medium">Username or Email</label>
      <InputText id="username" v-model="username" required autocomplete="username" />
    </div>

    <div class="flex flex-col gap-2">
      <label for="password" class="text-sm font-medium">Password</label>
      <Password id="password" v-model="password" :feedback="false" required autocomplete="current-password" toggleMask />
    </div>

    <Button type="submit" label="Sign In" :loading="authStore.loading" class="mt-4" />
  </form>
</template>
