<script setup lang="ts">
import LoginForm from '../components/LoginForm.vue';
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left: Branding panel -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-700 via-primary-600 to-teal-500 relative overflow-hidden items-center justify-center p-12">
      <!-- Decorative circles -->
      <div class="absolute top-[-10%] right-[-5%] w-96 h-96 bg-white/5 rounded-full" />
      <div class="absolute bottom-[-15%] left-[-10%] w-[500px] h-[500px] bg-white/5 rounded-full" />
      <div class="absolute top-[40%] right-[20%] w-32 h-32 bg-white/10 rounded-full" />

      <div class="relative z-10 text-center max-w-lg">
        <div class="w-20 h-20 rounded-2xl bg-white/20 backdrop-blur-sm text-white flex items-center justify-center text-5xl mx-auto mb-8 shadow-lg">
          <i class="pi pi-graduation-cap" />
        </div>
        <h1 class="text-4xl font-bold text-white mb-4 leading-tight">
          Education Management System
        </h1>
        <p class="text-primary-100 text-lg leading-relaxed">
          A modern platform to manage students, academics, and institutional operations efficiently.
        </p>

        <!-- Feature highlights -->
        <div class="mt-10 grid grid-cols-2 gap-4 text-left">
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <i class="pi pi-users text-white text-xl mb-2 block" />
            <p class="text-white font-medium text-sm">Student Management</p>
            <p class="text-primary-100 text-xs mt-1">Complete student lifecycle</p>
          </div>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <i class="pi pi-book text-white text-xl mb-2 block" />
            <p class="text-white font-medium text-sm">Academic Planning</p>
            <p class="text-primary-100 text-xs mt-1">Classes, sections & subjects</p>
          </div>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <i class="pi pi-chart-line text-white text-xl mb-2 block" />
            <p class="text-white font-medium text-sm">Analytics & Reports</p>
            <p class="text-primary-100 text-xs mt-1">Data-driven decisions</p>
          </div>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <i class="pi pi-shield text-white text-xl mb-2 block" />
            <p class="text-white font-medium text-sm">Role-Based Access</p>
            <p class="text-primary-100 text-xs mt-1">Secure & controlled</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Login form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-6 md:p-12 bg-white dark:bg-slate-950">
      <div class="w-full max-w-md">
        <!-- Mobile logo -->
        <div class="lg:hidden text-center mb-8">
          <div class="w-14 h-14 rounded-xl bg-primary-600 text-white flex items-center justify-center font-bold text-2xl mx-auto shadow-md mb-3">
            E
          </div>
          <h1 class="text-xl font-bold text-slate-900 dark:text-white">Education Management System</h1>
        </div>

        <LoginForm />

        <p class="mt-8 text-center text-xs text-slate-400 dark:text-slate-600">
          &copy; {{ new Date().getFullYear() }} EMS. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>
