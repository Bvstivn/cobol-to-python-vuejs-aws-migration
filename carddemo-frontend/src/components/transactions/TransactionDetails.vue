<template>
  <BaseModal
    :model-value="isOpen"
    :title="`Detalles de Transacción #${transaction?.id || ''}`"
    size="lg"
    @close="handleClose"
  >
    <div v-if="transaction" class="space-y-6">
      <!-- Encabezado con icono y monto -->
      <div class="flex items-center justify-between pb-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center space-x-4">
          <!-- Icono según tipo -->
          <div
            class="flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center"
            :class="iconBgClass"
          >
            <svg class="w-8 h-8" :class="iconColorClass" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="transaction.transaction_type === 'PURCHASE'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              <path v-else-if="transaction.transaction_type === 'PAYMENT'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
          </div>

          <div>
            <h3 class="text-2xl font-bold text-gray-900 dark:text-gray-100" :class="amountColorClass">
              {{ formattedAmount }}
            </h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ typeLabel }}
            </p>
          </div>
        </div>

        <!-- Estado -->
        <div>
          <span
            class="px-3 py-1 rounded-full text-sm font-semibold"
            :class="statusClasses"
          >
            {{ statusLabel }}
          </span>
        </div>
      </div>

      <!-- Información del comercio -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Información del Comercio
        </h4>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">Comercio:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ transaction.merchant_name }}
            </span>
          </div>
          <div v-if="transaction.description" class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">Descripción:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100 text-right max-w-xs">
              {{ transaction.description }}
            </span>
          </div>
        </div>
      </div>

      <!-- Detalles de la transacción -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Detalles de la Transacción
        </h4>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">ID de Transacción:</span>
            <span class="text-sm font-mono font-medium text-gray-900 dark:text-gray-100">
              #{{ transaction.id }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">Fecha de Transacción:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ formattedTransactionDate }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">Fecha de Registro:</span>
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ formattedCreatedAt }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">Tipo:</span>
            <span class="text-sm px-2 py-0.5 rounded" :class="typeClasses">
              {{ typeLabel }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">Estado:</span>
            <span class="text-sm px-2 py-0.5 rounded" :class="statusClasses">
              {{ statusLabel }}
            </span>
          </div>
        </div>
      </div>

      <!-- Información del monto -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Información del Monto
        </h4>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600 dark:text-gray-400">Monto:</span>
            <span class="text-xl font-bold" :class="amountColorClass">
              {{ formattedAmount }}
            </span>
          </div>
          <div v-if="transaction.transaction_type === 'PURCHASE'" class="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
            Este monto fue debitado de tu tarjeta
          </div>
          <div v-else-if="transaction.transaction_type === 'PAYMENT'" class="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
            Este monto fue acreditado a tu tarjeta
          </div>
          <div v-else class="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700">
            Este monto fue reembolsado a tu tarjeta
          </div>
        </div>
      </div>
    </div>

    <!-- Acciones del modal -->
    <template #footer>
      <div class="flex justify-end gap-3">
        <BaseButton variant="secondary" @click="handleClose">
          Cerrar
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseModal, BaseButton } from '@/components/base'
import type { Transaction, TransactionType, TransactionStatus } from '@/types'

interface Props {
  isOpen: boolean
  transaction: Transaction | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const iconBgClass = computed(() => {
  if (!props.transaction) return ''
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'bg-orange-100 dark:bg-orange-900/20',
    PAYMENT: 'bg-green-100 dark:bg-green-900/20',
    REFUND: 'bg-blue-100 dark:bg-blue-900/20'
  }
  return classes[props.transaction.transaction_type]
})

const iconColorClass = computed(() => {
  if (!props.transaction) return ''
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'text-orange-600 dark:text-orange-400',
    PAYMENT: 'text-green-600 dark:text-green-400',
    REFUND: 'text-blue-600 dark:text-blue-400'
  }
  return classes[props.transaction.transaction_type]
})

const amountColorClass = computed(() => {
  if (!props.transaction) return ''
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'text-orange-600 dark:text-orange-400',
    PAYMENT: 'text-green-600 dark:text-green-400',
    REFUND: 'text-blue-600 dark:text-blue-400'
  }
  return classes[props.transaction.transaction_type]
})

const formattedAmount = computed(() => {
  if (!props.transaction) return ''
  const sign = props.transaction.transaction_type === 'PURCHASE' ? '-' : '+'
  return `${sign}$${props.transaction.amount.toFixed(2)}`
})

const formattedTransactionDate = computed(() => {
  if (!props.transaction) return ''
  return new Date(props.transaction.transaction_date).toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const formattedCreatedAt = computed(() => {
  if (!props.transaction) return ''
  return new Date(props.transaction.created_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const typeLabel = computed(() => {
  if (!props.transaction) return ''
  const labels: Record<TransactionType, string> = {
    PURCHASE: 'Compra',
    PAYMENT: 'Pago',
    REFUND: 'Reembolso'
  }
  return labels[props.transaction.transaction_type]
})

const typeClasses = computed(() => {
  if (!props.transaction) return ''
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400',
    PAYMENT: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400',
    REFUND: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
  }
  return classes[props.transaction.transaction_type]
})

const statusLabel = computed(() => {
  if (!props.transaction) return ''
  const labels: Record<TransactionStatus, string> = {
    PENDING: 'Pendiente',
    COMPLETED: 'Completada',
    FAILED: 'Fallida'
  }
  return labels[props.transaction.status]
})

const statusClasses = computed(() => {
  if (!props.transaction) return ''
  const classes: Record<TransactionStatus, string> = {
    PENDING: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400',
    COMPLETED: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
  }
  return classes[props.transaction.status]
})

const handleClose = () => {
  emit('close')
}
</script>
