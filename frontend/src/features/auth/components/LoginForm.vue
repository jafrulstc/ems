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

const org_slug = ref('');
const email = ref('');
const password = ref('');
const errorMsg = ref('');

const handleSubmit = async () => {
  errorMsg.value = '';
  try {
    await authStore.login({ org_slug: org_slug.value, email: email.value, password: password.value });
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
      <label for="org_slug" class="text-sm font-medium">Organization Slug</label>
      <InputText id="org_slug" v-model="org_slug" required autocomplete="organization" />
    </div>

    <div class="flex flex-col gap-2">
      <label for="email" class="text-sm font-medium">Email Address</label>
      <InputText id="email" type="email" v-model="email" required autocomplete="email" />
    </div>

    <div class="flex flex-col gap-2">
      <label for="password" class="text-sm font-medium">Password</label>
      <Password id="password" v-model="password" :feedback="false" required autocomplete="current-password" toggleMask />
    </div>

    <Button type="submit" label="Sign In" :loading="authStore.loading" class="mt-4" />
  </form>
</template>
