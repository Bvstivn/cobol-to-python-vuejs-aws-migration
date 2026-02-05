<template>
  <div>
    <!-- Estados de carga y error -->
    <div v-if="isLoading" class="space-y-4">
      <LoadingSkeleton v-for="i in 5" :key="i" type="card" />
    </div>

    <div v-else-if="error" class="text-center py-12">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-error-100 dark:bg-error-900/20 mb-4">
        <svg class="h-8 w-8 text-error-600 dark:text-error-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-error-600 dark:text-error-400 mb-4">{{ error }}</p>
      <BaseButton variant="secondary" size="sm" @click="handleRetry">
        Reintentar
      </BaseButton>
    </div>

    <!-- Lista de transacciones -->
    <div v-else-if="transactions.length > 0" class="space-y-3">
      <TransactionItem
        v-for="transaction in transactions"
        :key="transaction.id"
        :transaction="transaction"
        @click="handleTransactionClick"
      />
    </div>

    <!-- Estado vacío -->
    <div v-else class="text-center py-12">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
        <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <p class="text-gray-500 dark:text-gray-400 mb-2">{{ emptyMessage }}</p>
      <p class="text-sm text-gray-400 dark:text-gray-500">{{ emptyHint }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import TransactionItem from './TransactionItem.vue'
import { BaseButton } from '@/components/base'
import { LoadingSkeleton } from '@/components/loading'
import type { Transaction } from '@/types'

interface Props {
  transactions: Transaction[]
  isLoading?: boolean
  error?: string | null
  emptyMessage?: string
  emptyHint?: string
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  error: null,
  emptyMessage: 'No se encontraron transacciones',
  emptyHint: 'Intenta ajustar los filtros de búsqueda'
})

const emit = defineEmits<{
  retry: []
  transactionClick: [transaction: Transaction]
}>()

const handleRetry = () => {
  emit('retry')
}

const handleTransactionClick = (transaction: Transaction) => {
  emit('transactionClick', transaction)
}
</script>
