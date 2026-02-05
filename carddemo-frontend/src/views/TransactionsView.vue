<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        Historial de Transacciones
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Consulta y filtra tus transacciones
      </p>
    </div>

    <!-- Filtros -->
    <div class="mb-6">
      <TransactionFilters
        :filters="transactionsStore.filters"
        :cards="cardsStore.cards"
        @update:filters="handleFiltersUpdate"
        @clear="handleClearFilters"
      />
    </div>

    <!-- Lista de transacciones -->
    <div class="mb-6">
      <TransactionList
        :transactions="transactionsStore.transactions"
        :is-loading="transactionsStore.isLoading"
        :error="transactionsStore.error"
        @retry="handleRetry"
        @transaction-click="handleTransactionClick"
      />
    </div>

    <!-- Paginación -->
    <div v-if="transactionsStore.hasTransactions && !transactionsStore.isLoading">
      <TransactionPagination
        :current-page="transactionsStore.currentPage"
        :total-pages="transactionsStore.totalPages"
        :total="transactionsStore.pagination.total"
        :limit="transactionsStore.pagination.limit"
        :offset="transactionsStore.pagination.offset"
        :has-more="transactionsStore.hasMorePages"
        @page-change="handlePageChange"
        @next="handleNextPage"
        @previous="handlePreviousPage"
      />
    </div>

    <!-- Modal de detalles -->
    <TransactionDetails
      :is-open="showDetailsModal"
      :transaction="transactionsStore.selectedTransaction"
      @close="handleCloseDetails"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AppLayout } from '@/components/layout'
import { TransactionFilters, TransactionList, TransactionPagination, TransactionDetails } from '@/components/transactions'
import { useTransactionsStore } from '@/stores/transactions'
import { useCardsStore } from '@/stores/cards'
import type { TransactionFilters as TFilters, Transaction } from '@/types'

const transactionsStore = useTransactionsStore()
const cardsStore = useCardsStore()
const showDetailsModal = ref(false)

onMounted(async () => {
  // Cargar tarjetas para los filtros
  if (!cardsStore.hasCards) {
    await cardsStore.fetchCards().catch(() => {})
  }
  
  // Cargar transacciones
  await loadTransactions()
})

async function loadTransactions() {
  try {
    await transactionsStore.fetchTransactions()
  } catch (error) {
    console.error('Error loading transactions:', error)
  }
}

async function handleFiltersUpdate(filters: TFilters) {
  try {
    await transactionsStore.fetchTransactions(filters)
  } catch (error) {
    console.error('Error applying filters:', error)
  }
}

async function handleClearFilters() {
  transactionsStore.clearFilters()
  await loadTransactions()
}

function handleRetry() {
  loadTransactions()
}

function handleTransactionClick(transaction: Transaction) {
  transactionsStore.selectTransaction(transaction)
  showDetailsModal.value = true
}

function handleCloseDetails() {
  showDetailsModal.value = false
}

async function handlePageChange(page: number) {
  try {
    await transactionsStore.goToPage(page)
  } catch (error) {
    console.error('Error changing page:', error)
  }
}

async function handleNextPage() {
  try {
    await transactionsStore.nextPage()
  } catch (error) {
    console.error('Error going to next page:', error)
  }
}

async function handlePreviousPage() {
  try {
    await transactionsStore.previousPage()
  } catch (error) {
    console.error('Error going to previous page:', error)
  }
}
</script>
