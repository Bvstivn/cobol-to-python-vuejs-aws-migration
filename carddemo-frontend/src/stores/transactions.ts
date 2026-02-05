/**
 * Store de transacciones con Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Transaction, TransactionFilters, TransactionResponse } from '@/types'
import { TransactionService } from '@/services/transaction-service'

const transactionService = new TransactionService()

export const useTransactionsStore = defineStore('transactions', () => {
  // Estado
  const transactions = ref<Transaction[]>([])
  const selectedTransaction = ref<Transaction | null>(null)
  const filters = ref<TransactionFilters>({})
  const pagination = ref({
    limit: 20,
    offset: 0,
    total: 0,
    hasMore: false
  })
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchTime = ref<Date | null>(null)

  // Getters computados
  const hasTransactions = computed(() => transactions.value.length > 0)
  const transactionCount = computed(() => transactions.value.length)
  const hasMorePages = computed(() => pagination.value.hasMore)
  const currentPage = computed(() => Math.floor(pagination.value.offset / pagination.value.limit) + 1)
  const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.limit))

  /**
   * Obtener transacciones con filtros
   */
  async function fetchTransactions(newFilters?: TransactionFilters, force = false): Promise<void> {
    // Actualizar filtros si se proporcionan
    if (newFilters) {
      filters.value = { ...filters.value, ...newFilters }
      // Reset offset al cambiar filtros (excepto si se proporciona offset explícito)
      if (newFilters.offset === undefined && Object.keys(newFilters).some(k => k !== 'limit')) {
        filters.value.offset = 0
      }
    }

    // Evitar fetch duplicado si ya tenemos datos recientes (< 10 segundos) y mismos filtros
    if (!force && transactions.value.length > 0 && lastFetchTime.value) {
      const timeSinceLastFetch = Date.now() - lastFetchTime.value.getTime()
      if (timeSinceLastFetch < 10000) {
        return
      }
    }

    isLoading.value = true
    error.value = null

    try {
      const response: TransactionResponse = await transactionService.getTransactions(filters.value)
      
      transactions.value = response.transactions
      pagination.value = {
        limit: response.limit,
        offset: response.offset,
        total: response.total,
        hasMore: response.has_more
      }
      lastFetchTime.value = new Date()
    } catch (err: any) {
      error.value = err.message || 'Error al obtener transacciones'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener detalles de una transacción específica
   */
  async function fetchTransaction(transactionId: number): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const transaction = await transactionService.getTransaction(transactionId)
      
      // Actualizar en la lista si existe
      const index = transactions.value.findIndex(t => t.id === transactionId)
      if (index !== -1) {
        transactions.value[index] = transaction
      }
      
      // Actualizar transacción seleccionada si es la misma
      if (selectedTransaction.value?.id === transactionId) {
        selectedTransaction.value = transaction
      }
    } catch (err: any) {
      error.value = err.message || 'Error al obtener detalles de la transacción'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Establecer filtros
   */
  function setFilters(newFilters: TransactionFilters): void {
    filters.value = { ...newFilters }
  }

  /**
   * Limpiar filtros
   */
  function clearFilters(): void {
    filters.value = {}
  }

  /**
   * Ir a la siguiente página
   */
  async function nextPage(): Promise<void> {
    if (hasMorePages.value) {
      const newOffset = pagination.value.offset + pagination.value.limit
      await fetchTransactions({ offset: newOffset })
    }
  }

  /**
   * Ir a la página anterior
   */
  async function previousPage(): Promise<void> {
    if (pagination.value.offset > 0) {
      const newOffset = Math.max(0, pagination.value.offset - pagination.value.limit)
      await fetchTransactions({ offset: newOffset })
    }
  }

  /**
   * Ir a una página específica
   */
  async function goToPage(page: number): Promise<void> {
    const totalPages = Math.ceil(pagination.value.total / pagination.value.limit)
    if (page >= 1 && page <= totalPages) {
      const newOffset = (page - 1) * pagination.value.limit
      await fetchTransactions({ offset: newOffset })
    }
  }

  /**
   * Seleccionar una transacción
   */
  function selectTransaction(transaction: Transaction | null): void {
    selectedTransaction.value = transaction
  }

  /**
   * Seleccionar transacción por ID
   */
  function selectTransactionById(transactionId: number): void {
    const transaction = transactions.value.find(t => t.id === transactionId)
    selectedTransaction.value = transaction || null
  }

  /**
   * Limpiar datos de transacciones
   */
  function clearTransactions(): void {
    transactions.value = []
    selectedTransaction.value = null
    filters.value = {}
    pagination.value = {
      limit: 20,
      offset: 0,
      total: 0,
      hasMore: false
    }
    error.value = null
    lastFetchTime.value = null
  }

  /**
   * Limpiar error
   */
  function clearError(): void {
    error.value = null
  }

  return {
    // Estado
    transactions,
    selectedTransaction,
    filters,
    pagination,
    isLoading,
    error,
    lastFetchTime,
    // Getters
    hasTransactions,
    transactionCount,
    hasMorePages,
    currentPage,
    totalPages,
    // Acciones
    fetchTransactions,
    fetchTransaction,
    setFilters,
    clearFilters,
    nextPage,
    previousPage,
    goToPage,
    selectTransaction,
    selectTransactionById,
    clearTransactions,
    clearError
  }
})
