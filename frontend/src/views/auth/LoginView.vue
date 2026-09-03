<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';

const email = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref('');

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  try {
    isLoading.value = true;
    error.value = '';
    await authStore.login(email.value, password.value);
    router.push({ name: 'dashboard' });
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Invalid login credentials.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>Welcome Back</h1>
        <p>Enter your details to access the EMS dashboard.</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">


        <div class="form-group">
          <label for="email">Email Address</label>
          <InputText id="email" type="email" v-model="email" required placeholder="name@school.com" />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <InputText id="password" type="password" v-model="password" required placeholder="••••••••" />
        </div>

        <Message v-if="error" severity="error" :closable="false" class="error-msg">{{ error }}</Message>

        <Button type="submit" :loading="isLoading" label="Sign In" class="submit-btn" />
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
  font-family: 'Inter', sans-serif;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 3rem 2.5rem;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05), 0 20px 48px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 420px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #102a43;
  margin: 0 0 0.5rem 0;
}

.login-header p {
  color: #627d98;
  margin: 0;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #334e68;
}

:deep(.p-inputtext) {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #bcccdc;
  transition: all 0.2s ease;
  font-family: inherit;
}

:deep(.p-inputtext:focus) {
  border-color: #3e82f7;
  box-shadow: 0 0 0 3px rgba(62, 130, 247, 0.15);
}

.error-msg {
  margin: 0;
}

.submit-btn {
  margin-top: 1rem;
  padding: 0.85rem;
  border-radius: 8px;
  font-weight: 600;
  background: #3e82f7;
  border: none;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: #2b6cb0;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(62, 130, 247, 0.3);
}
</style>
