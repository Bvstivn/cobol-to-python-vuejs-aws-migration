<template>
  <BaseCard>
    <template #header>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Acciones Rápidas
      </h3>
    </template>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <button
        v-for="action in actions"
        :key="action.id"
        class="flex items-center space-x-3 p-4 rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-all group"
        @click="handleActionClick(action.id)"
      >
        <div
          class="flex-shrink-0 w-12 h-12 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center group-hover:bg-blue-200 dark:group-hover:bg-blue-900/30 transition-colors"
        >
          <component :is="action.icon" class="h-6 w-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div class="flex-1 text-left">
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ action.label }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ action.description }}
          </p>
        </div>
      </button>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { BaseCard } from '@/components/base'

interface QuickAction {
  id: string
  label: string
  description: string
  icon: any
}

const emit = defineEmits<{
  actionClick: [actionId: string]
}>()

const actions: QuickAction[] = [
  {
    id: 'view-cards',
    label: 'Ver Tarjetas',
    description: 'Gestiona tus tarjetas',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      `
    }
  },
  {
    id: 'view-transactions',
    label: 'Ver Transacciones',
    description: 'Historial completo',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      `
    }
  },
  {
    id: 'update-profile',
    label: 'Actualizar Perfil',
    description: 'Edita tu información',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      `
    }
  },
  {
    id: 'contact-support',
    label: 'Soporte',
    description: 'Contacta con nosotros',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      `
    }
  }
]

const handleActionClick = (actionId: string) => {
  emit('actionClick', actionId)
}
</script>
