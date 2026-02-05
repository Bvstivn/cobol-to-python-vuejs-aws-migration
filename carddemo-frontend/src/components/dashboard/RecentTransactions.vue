<template>
  <BaseCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Transacciones Recientes
        </h3>
        <RouterLink
          to="/transactions"
          class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
        >
          Ver todas
        </RouterLink>
      </div>
    </template>

    <div v-if="isLoading" class="space-y-3">
      <LoadingSkeleton v-for="i in 5" :key="i" type="text" />
    </div>

    <div v-else-if="error" class="text-center py-8">
      <p class="text-error-600 dark:text-error-400 mb-4">{{ error }}</p>
      <BaseButton variant="secondary" size="sm" @click="handleRetry">
        Reintentar
      </BaseButton>
    </div>

    <div v-else-if="transactions.length > 0" class="space-y-3">
      <div
        v-for="transaction in transactions"
        :key="transaction.id"
        class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
        @click="handleTransactionClick(transaction)"
      >
        <div class="flex items-center space-x-3 flex-1 min-w-0">
          <!-- Icono según tipo -->
          <div
            :class="[
              'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
              getTransactionIconBg(transaction.transaction_type)
            ]"
          >
            <component :is="getTransactionIcon(transaction.transaction_type)" class="h-5 w-5" />
          </div>

          <!-- Información -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
              {{ transaction.merchant_name }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatDate(transaction.transaction_date) }}
            </p>
          </div>
        </div>

        <!-- Monto -->
        <div class="text-right ml-4">
          <p
            :class="[
              'text-sm font-semibold',
              getAmountColor(transaction.transaction_type)
            ]"
          >
            {{ formatAmount(transaction.amount, transaction.transaction_type) }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ getStatusLabel(transaction.status) }}
          </p>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">No hay transacciones recientes</p>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { BaseCard, BaseButton } from '@/components/base'
import { LoadingSkeleton } from '@/components/loading'
import type { Transaction, TransactionType, TransactionStatus } from '@/types'

interface Props {
  transactions: Transaction[]
  isLoading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  error: null
})

const emit = defineEmits<{
  retry: []
  transactionClick: [transaction: Transaction]
}>()

const getTransactionIcon = (type: TransactionType) => {
  const icons = {
    PURCHASE: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      `
    },
    PAYMENT: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `
    },
    REFUND: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      `
    }
  }
  return icons[type]
}

const getTransactionIconBg = (type: TransactionType) => {
  const colors = {
    PURCHASE: 'bg-error-100 dark:bg-error-900/20 text-error-600 dark:text-error-400',
    PAYMENT: 'bg-success-100 dark:bg-success-900/20 text-success-600 dark:text-success-400',
    REFUND: 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
  }
  return colors[type]
}

const getAmountColor = (type: TransactionType) => {
  const colors = {
    PURCHASE: 'text-error-600 dark:text-error-400',
    PAYMENT: 'text-success-600 dark:text-success-400',
    REFUND: 'text-blue-600 dark:text-blue-400'
  }
  return colors[type]
}

const formatAmount = (amount: number, type: TransactionType) => {
  const sign = type === 'PURCHASE' ? '-' : '+'
  return `${sign}$${amount.toFixed(2)}`
}

const formatDate = (date: Date) => {
  const d = new Date(date)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - d.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Hoy'
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `Hace ${diffDays} días`
  
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

const getStatusLabel = (status: TransactionStatus) => {
  const labels = {
    PENDING: 'Pendiente',
    COMPLETED: 'Completada',
    FAILED: 'Fallida'
  }
  return labels[status]
}

const handleRetry = () => {
  emit('retry')
}

const handleTransactionClick = (transaction: Transaction) => {
  emit('transactionClick', transaction)
}
</script>
