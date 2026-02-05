<template>
  <AppLayout>
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        Dashboard
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Bienvenido, {{ greeting }}
      </p>
    </div>

    <!-- Grid de widgets -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Columna izquierda: Resumen de cuenta -->
      <div class="lg:col-span-1">
        <AccountSummary
          :account="accountStore.account"
          :is-loading="accountStore.isLoading"
          :error="accountStore.error"
          @retry="handleAccountRetry"
        />
      </div>

      <!-- Columna derecha: Transacciones y acciones -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Transacciones recientes -->
        <RecentTransactions
          :transactions="recentTransactions"
          :is-loading="transactionsStore.isLoading"
          :error="transactionsStore.error"
          @retry="handleTransactionsRetry"
          @transaction-click="handleTransactionClick"
        />

        <!-- Acciones rápidas -->
        <QuickActions @action-click="handleQuickAction" />
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AppLayout } from '@/components/layout'
import { AccountSummary, RecentTransactions, QuickActions } from '@/components/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useAccountStore } from '@/stores/account'
import { useTransactionsStore } from '@/stores/transactions'
import { useNotificationsStore } from '@/stores/notifications'
import type { Transaction } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const accountStore = useAccountStore()
const transactionsStore = useTransactionsStore()
const notificationsStore = useNotificationsStore()

const greeting = computed(() => {
  if (authStore.user) {
    return authStore.user.username
  }
  return 'Usuario'
})

const recentTransactions = computed(() => {
  return transactionsStore.transactions.slice(0, 5)
})

const handleAccountRetry = async () => {
  try {
    await accountStore.fetchAccount()
  } catch (error: any) {
    notificationsStore.error('Error', 'No se pudo cargar la información de la cuenta')
  }
}

const handleTransactionsRetry = async () => {
  try {
    await transactionsStore.fetchTransactions({ limit: 5 })
  } catch (error: any) {
    notificationsStore.error('Error', 'No se pudieron cargar las transacciones')
  }
}

const handleTransactionClick = (transaction: Transaction) => {
  transactionsStore.selectTransaction(transaction)
  router.push('/transactions')
}

const handleQuickAction = (actionId: string) => {
  const routes: Record<string, string> = {
    'view-cards': '/cards',
    'view-transactions': '/transactions',
    'update-profile': '/profile',
    'contact-support': '/profile'
  }

  const route = routes[actionId]
  if (route) {
    router.push(route)
  }
}

// Cargar datos al montar
onMounted(async () => {
  try {
    // Cargar cuenta y transacciones en paralelo
    await Promise.all([
      accountStore.fetchAccount(),
      transactionsStore.fetchTransactions({ limit: 5 })
    ])
  } catch (error: any) {
    // Los errores ya se manejan en los stores individuales
  }
})
</script>
