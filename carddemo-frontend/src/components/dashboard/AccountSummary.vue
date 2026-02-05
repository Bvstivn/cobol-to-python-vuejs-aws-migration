<template>
  <BaseCard>
    <template #header>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Resumen de Cuenta
      </h3>
    </template>

    <div v-if="isLoading" class="space-y-4">
      <LoadingSkeleton type="text" />
      <LoadingSkeleton type="text" />
      <LoadingSkeleton type="text" />
    </div>

    <div v-else-if="error" class="text-center py-8">
      <p class="text-error-600 dark:text-error-400 mb-4">{{ error }}</p>
      <BaseButton variant="secondary" size="sm" @click="handleRetry">
        Reintentar
      </BaseButton>
    </div>

    <div v-else-if="account" class="space-y-4">
      <!-- Información del titular -->
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Titular</p>
        <p class="text-lg font-medium text-gray-900 dark:text-gray-100">
          {{ fullName }}
        </p>
      </div>

      <!-- Número de cuenta -->
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Número de Cuenta</p>
        <p class="text-lg font-mono text-gray-900 dark:text-gray-100">
          {{ account.account_number }}
        </p>
      </div>

      <!-- Información de contacto -->
      <div v-if="account.phone" class="pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="mb-2">
          <p class="text-sm text-gray-500 dark:text-gray-400">Teléfono</p>
          <p class="text-sm text-gray-900 dark:text-gray-100">{{ account.phone }}</p>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">No hay información de cuenta disponible</p>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseCard, BaseButton } from '@/components/base'
import { LoadingSkeleton } from '@/components/loading'
import type { Account } from '@/types'

interface Props {
  account: Account | null
  isLoading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  error: null
})

const emit = defineEmits<{
  retry: []
}>()

const fullName = computed(() => {
  if (!props.account) return ''
  return `${props.account.first_name} ${props.account.last_name}`
})

const handleRetry = () => {
  emit('retry')
}
</script>
