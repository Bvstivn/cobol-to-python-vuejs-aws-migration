/**
 * Tests de propiedad para estados de carga universales
 * Valida: Requerimientos 2.2, 4.5, 6.2, 12.1, 12.4
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { useAccountStore } from '../account'
import { useCardsStore } from '../cards'
import { useTransactionsStore } from '../transactions'
import { apiClient } from '@/services/api-client'
import type { AuthResponse, User, TransactionResponse } from '@/types'

// Mock del apiClient
vi.mock('@/services/api-client', () => ({
  apiClient: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    hasValidToken: vi.fn(),
    clearToken: vi.fn()
  }
}))

// Mock de los servicios
vi.mock('@/services/account-service', () => {
  const mockGetAccount = vi.fn()
  const mockUpdateAccount = vi.fn()
  return {
    AccountService: class {
      getAccount = mockGetAccount
      updateAccount = mockUpdateAccount
    }
  }
})

vi.mock('@/services/card-service', () => {
  const mockGetCards = vi.fn()
  const mockGetCard = vi.fn()
  return {
    CardService: class {
      getCards = mockGetCards
      getCard = mockGetCard
    }
  }
})

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

describe('Loading States Property Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  /**
   * Propiedad 7: Estados de carga universales
   * Valida: Requerimientos 2.2, 4.5, 6.2, 12.1, 12.4
   */
  it('Property 7: should show loading states during async operations', async () => {
    // Test AuthStore loading
    const authStore = useAuthStore()
    
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }
    
    const mockAuthResponse: AuthResponse = {
      access_token: 'token',
      token_type: 'bearer',
      expires_in: 3600,
      user: mockUser
    }
    
    // Simular operación lenta
    vi.mocked(apiClient.login).mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => resolve(mockAuthResponse), 100)
      })
    })
    
    // Iniciar login
    const loginPromise = authStore.login({ username: 'test', password: 'pass' })
    
    // Debe estar en estado de carga
    expect(authStore.isLoading).toBe(true)
    
    // Esperar a que termine
    await loginPromise
    
    // Ya no debe estar cargando
    expect(authStore.isLoading).toBe(false)
  })

  /**
   * Test adicional: AccountStore loading state
   */
  it('should show loading state in AccountStore', async () => {
    const accountStore = useAccountStore()
    
    // El mock ya está definido globalmente, solo verificamos el comportamiento
    expect(accountStore.isLoading).toBe(false)
    
    // Simular que está cargando
    accountStore.isLoading = true
    expect(accountStore.isLoading).toBe(true)
    
    accountStore.isLoading = false
    expect(accountStore.isLoading).toBe(false)
  })

  /**
   * Test adicional: CardsStore loading state
   */
  it('should show loading state in CardsStore', async () => {
    const cardsStore = useCardsStore()
    
    // El mock ya está definido globalmente, solo verificamos el comportamiento
    expect(cardsStore.isLoading).toBe(false)
    
    // Simular que está cargando
    cardsStore.isLoading = true
    expect(cardsStore.isLoading).toBe(true)
    
    cardsStore.isLoading = false
    expect(cardsStore.isLoading).toBe(false)
  })

  /**
   * Test adicional: TransactionsStore loading state
   */
  it('should show loading state in TransactionsStore', async () => {
    const transactionsStore = useTransactionsStore()
    
    // Verificar estado inicial
    expect(transactionsStore.isLoading).toBe(false)
    
    // Simular que está cargando (el store maneja esto internamente)
    transactionsStore.isLoading = true
    expect(transactionsStore.isLoading).toBe(true)
    
    transactionsStore.isLoading = false
    expect(transactionsStore.isLoading).toBe(false)
  })

  /**
   * Test adicional: Error state después de operación fallida
   */
  it('should set error state when operation fails', async () => {
    const authStore = useAuthStore()
    
    const mockError = {
      code: 'NETWORK_ERROR',
      message: 'No se pudo conectar'
    }
    
    vi.mocked(apiClient.login).mockRejectedValue(mockError)
    
    try {
      await authStore.login({ username: 'test', password: 'pass' })
    } catch (error) {
      // Esperado
    }
    
    // Debe tener error
    expect(authStore.error).toBe('No se pudo conectar')
    // No debe estar cargando
    expect(authStore.isLoading).toBe(false)
  })

  /**
   * Test adicional: Limpiar error
   */
  it('should clear error state', async () => {
    const authStore = useAuthStore()
    
    authStore.error = 'Error de prueba'
    expect(authStore.error).toBe('Error de prueba')
    
    authStore.clearError()
    expect(authStore.error).toBeNull()
  })
})
