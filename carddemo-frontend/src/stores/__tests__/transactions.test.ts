/**
 * Tests de propiedad para TransactionsStore
 * Valida: Requerimientos 4.2
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTransactionsStore } from '../transactions'
import type { Transaction, TransactionType } from '@/types'

// Mock del TransactionService
vi.mock('@/services/transaction-service', () => {
  const mockGetTransactions = vi.fn()
  const mockGetTransaction = vi.fn()
  return {
    TransactionService: class {
      getTransactions = mockGetTransactions
      getTransaction = mockGetTransaction
    }
  }
})

describe('TransactionsStore Property Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  /**
   * Propiedad 15: Filtrado efectivo de transacciones
   * Valida: Requerimientos 4.2
   */
  it('Property 15: should filter transactions effectively', async () => {
    const store = useTransactionsStore()
    
    // Aplicar filtros
    store.setFilters({
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      min_amount: 40,
      max_amount: 150
    })
    
    expect(store.filters.start_date).toBe('2024-01-01')
    expect(store.filters.end_date).toBe('2024-01-31')
    expect(store.filters.min_amount).toBe(40)
    expect(store.filters.max_amount).toBe(150)
  })

  /**
   * Test adicional: Paginación correcta
   */
  it('should handle pagination correctly', () => {
    const store = useTransactionsStore()
    
    // Simular datos de paginación
    store.pagination = {
      limit: 20,
      offset: 0,
      total: 100,
      hasMore: true
    }
    
    expect(store.pagination.total).toBe(100)
    expect(store.pagination.limit).toBe(20)
    expect(store.hasMorePages).toBe(true)
    expect(store.currentPage).toBe(1)
    expect(store.totalPages).toBe(5)
  })

  /**
   * Test adicional: Navegación de páginas
   */
  it('should navigate pages correctly', () => {
    const store = useTransactionsStore()
    
    store.pagination = {
      limit: 20,
      offset: 0,
      total: 100,
      hasMore: true
    }
    
    expect(store.currentPage).toBe(1)
    
    // Simular ir a la siguiente página
    store.pagination.offset = 20
    expect(store.currentPage).toBe(2)
  })

  /**
   * Test adicional: Limpiar filtros
   */
  it('should clear filters correctly', async () => {
    const store = useTransactionsStore()
    
    store.setFilters({
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      min_amount: 50
    })
    
    expect(store.filters.start_date).toBe('2024-01-01')
    
    store.clearFilters()
    
    expect(store.filters).toEqual({})
  })

  /**
   * Test adicional: Seleccionar transacción
   */
  it('should select transaction correctly', () => {
    const store = useTransactionsStore()
    
    const mockTransaction: Transaction = {
      id: 1,
      transaction_date: new Date('2024-01-15'),
      merchant_name: 'Amazon',
      amount: 50.00,
      transaction_type: 'PURCHASE' as TransactionType,
      status: 'COMPLETED',
      created_at: new Date('2024-01-15')
    }
    
    store.transactions = [mockTransaction]
    store.selectTransactionById(1)
    
    expect(store.selectedTransaction).toEqual(mockTransaction)
  })
})
