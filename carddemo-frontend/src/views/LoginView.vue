<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          CardDemo
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          Sistema de Gestión Bancaria
        </p>
      </div>

      <LoginForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/auth/LoginForm.vue'
</script>
