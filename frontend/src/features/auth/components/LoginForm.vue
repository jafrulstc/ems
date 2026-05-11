<script setup lang="ts">
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import { useAuthStore } from '@/features/auth/stores/auth.store';
import { useRouter, useRoute } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const org_slug = ref('');
const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const errorMsg = ref('');

const handleSubmit = async () => {
  errorMsg.value = '';
  try {
    await authStore.login({ org_slug: org_slug.value, email: email.value, password: password.value });
    const redirect = (route.query.redirect as string) || '/';
    router.push(redirect);
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || 'Login failed. Please check your credentials.';
  }
};
</script>

<template>
  <form @submit.prevent="handleSubmit" class="flex flex-col gap-5">
    <div class="mb-2">
      <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Welcome back</h2>
      <p class="text-slate-500 dark:text-slate-400 mt-1 text-sm">Sign in to your organization account</p>
    </div>

    <!-- Error display -->
    <div v-if="errorMsg" class="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
      <i class="pi pi-exclamation-circle text-red-500 mt-0.5" />
      <p class="text-red-600 dark:text-red-400 text-sm">{{ errorMsg }}</p>
    </div>

    <!-- Org slug -->
    <div class="flex flex-col gap-1.5">
      <label for="org_slug" class="text-sm font-medium text-slate-700 dark:text-slate-300">Organization Slug</label>
      <div class="relative">
        <i class="pi pi-building absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm" />
        <InputText id="org_slug" v-model="org_slug" required autocomplete="organization" class="w-full pl-9" placeholder="your-school" />
      </div>
    </div>

    <!-- Email -->
    <div class="flex flex-col gap-1.5">
      <label for="email" class="text-sm font-medium text-slate-700 dark:text-slate-300">Email Address</label>
      <div class="relative">
        <i class="pi pi-envelope absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm" />
        <InputText id="email" type="email" v-model="email" required autocomplete="email" class="w-full pl-9" placeholder="you@school.com" />
      </div>
    </div>

    <!-- Password -->
    <div class="flex flex-col gap-1.5">
      <label for="password" class="text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
      <Password id="password" v-model="password" :feedback="false" required autocomplete="current-password" toggleMask class="w-full" />
    </div>

    <!-- Remember me -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Checkbox inputId="remember" v-model="rememberMe" :binary="true" />
        <label for="remember" class="text-sm text-slate-600 dark:text-slate-400 cursor-pointer">Remember me</label>
      </div>
      <a href="#" class="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium">Forgot password?</a>
    </div>

    <!-- Submit -->
    <Button type="submit" label="Sign In" :loading="authStore.loading" class="mt-1 h-11" />
  </form>
</template>
