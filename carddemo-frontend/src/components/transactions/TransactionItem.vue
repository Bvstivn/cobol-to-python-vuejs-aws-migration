<template>
  <div
    class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
    @click="handleClick"
  >
    <div class="flex items-start justify-between">
      <!-- Icono y detalles -->
      <div class="flex items-start space-x-3 flex-1">
        <!-- Icono según tipo -->
        <div
          class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
          :class="iconBgClass"
        >
          <svg class="w-5 h-5" :class="iconColorClass" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="transaction.transaction_type === 'PURCHASE'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            <path v-else-if="transaction.transaction_type === 'PAYMENT'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
          </svg>
        </div>

        <!-- Información -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <p class="text-sm font-semibold text-gray-900 dark:text-gray-100 truncate">
              {{ transaction.merchant_name }}
            </p>
            <p class="text-sm font-bold ml-2" :class="amountColorClass">
              {{ formattedAmount }}
            </p>
          </div>

          <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
            <span>{{ formattedDate }}</span>
            <span>•</span>
            <span class="px-2 py-0.5 rounded" :class="typeClasses">
              {{ typeLabel }}
            </span>
            <span>•</span>
            <span class="px-2 py-0.5 rounded" :class="statusClasses">
              {{ statusLabel }}
            </span>
          </div>

          <p v-if="transaction.description" class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
            {{ transaction.description }}
          </p>
        </div>
      </div>

      <!-- Flecha -->
      <div class="flex-shrink-0 ml-2">
        <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Transaction, TransactionType, TransactionStatus } from '@/types'

interface Props {
  transaction: Transaction
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [transaction: Transaction]
}>()

const iconBgClass = computed(() => {
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'bg-orange-100 dark:bg-orange-900/20',
    PAYMENT: 'bg-green-100 dark:bg-green-900/20',
    REFUND: 'bg-blue-100 dark:bg-blue-900/20'
  }
  return classes[props.transaction.transaction_type]
})

const iconColorClass = computed(() => {
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'text-orange-600 dark:text-orange-400',
    PAYMENT: 'text-green-600 dark:text-green-400',
    REFUND: 'text-blue-600 dark:text-blue-400'
  }
  return classes[props.transaction.transaction_type]
})

const amountColorClass = computed(() => {
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'text-orange-600 dark:text-orange-400',
    PAYMENT: 'text-green-600 dark:text-green-400',
    REFUND: 'text-blue-600 dark:text-blue-400'
  }
  return classes[props.transaction.transaction_type]
})

const formattedAmount = computed(() => {
  const sign = props.transaction.transaction_type === 'PURCHASE' ? '-' : '+'
  return `${sign}$${props.transaction.amount.toFixed(2)}`
})

const formattedDate = computed(() => {
  const date = new Date(props.transaction.transaction_date)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Hoy'
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `Hace ${diffDays} días`
  
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
})

const typeLabel = computed(() => {
  const labels: Record<TransactionType, string> = {
    PURCHASE: 'Compra',
    PAYMENT: 'Pago',
    REFUND: 'Reembolso'
  }
  return labels[props.transaction.transaction_type]
})

const typeClasses = computed(() => {
  const classes: Record<TransactionType, string> = {
    PURCHASE: 'bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400',
    PAYMENT: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400',
    REFUND: 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
  }
  return classes[props.transaction.transaction_type]
})

const statusLabel = computed(() => {
  const labels: Record<TransactionStatus, string> = {
    PENDING: 'Pendiente',
    COMPLETED: 'Completada',
    FAILED: 'Fallida'
  }
  return labels[props.transaction.status]
})

const statusClasses = computed(() => {
  const classes: Record<TransactionStatus, string> = {
    PENDING: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400',
    COMPLETED: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
  }
  return classes[props.transaction.status]
})

const handleClick = () => {
  emit('click', props.transaction)
}
</script>
