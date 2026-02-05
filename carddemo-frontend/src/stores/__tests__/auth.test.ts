/**
 * Tests de propiedad para AuthStore
 * Valida: Requerimientos 1.1, 1.2, 1.4
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import { apiClient } from '@/services/api-client'
import type { AuthResponse, User } from '@/types'

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

describe('AuthStore Property Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  /**
   * Propiedad 1: Autenticación con credenciales válidas
   * Valida: Requerimientos 1.1
   */
  it('Property 1: should authenticate with valid credentials', async () => {
    const store = useAuthStore()
    
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }
    
    const mockResponse: AuthResponse = {
      access_token: 'mock-token-123',
      token_type: 'bearer',
      expires_in: 3600,
      user: mockUser
    }
    
    vi.mocked(apiClient.login).mockResolvedValue(mockResponse)
    
    await store.login({ username: 'testuser', password: 'password123' })
    
    expect(store.isAuthenticated).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(store.token).toBe('mock-token-123')
    expect(store.error).toBeNull()
  })

  /**
   * Propiedad 2: Rechazo de credenciales inválidas
   * Valida: Requerimientos 1.2
   */
  it('Property 2: should reject invalid credentials', async () => {
    const store = useAuthStore()
    
    const mockError = {
      code: 'INVALID_CREDENTIALS',
      message: 'Usuario o contraseña incorrectos'
    }
    
    vi.mocked(apiClient.login).mockRejectedValue(mockError)
    
    await expect(
      store.login({ username: 'invalid', password: 'wrong' })
    ).rejects.toEqual(mockError)
    
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.error).toBe('Usuario o contraseña incorrectos')
  })

  /**
   * Propiedad 4: Logout completo
   * Valida: Requerimientos 1.4
   */
  it('Property 4: should perform complete logout', async () => {
    const store = useAuthStore()
    
    // Simular usuario autenticado
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }
    
    const mockResponse: AuthResponse = {
      access_token: 'mock-token-123',
      token_type: 'bearer',
      expires_in: 3600,
      user: mockUser
    }
    
    vi.mocked(apiClient.login).mockResolvedValue(mockResponse)
    vi.mocked(apiClient.logout).mockResolvedValue()
    
    // Login primero
    await store.login({ username: 'testuser', password: 'password123' })
    expect(store.isAuthenticated).toBe(true)
    
    // Logout
    await store.logout()
    
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(apiClient.clearToken).toHaveBeenCalled()
  })

  /**
   * Test adicional: Verificar estado de autenticación
   */
  it('should check auth status correctly', async () => {
    const store = useAuthStore()
    
    const mockUser: User = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }
    
    // Simular token válido
    store.token = 'valid-token'
    vi.mocked(apiClient.hasValidToken).mockReturnValue(true)
    vi.mocked(apiClient.getCurrentUser).mockResolvedValue(mockUser)
    
    const isValid = await store.checkAuthStatus()
    
    expect(isValid).toBe(true)
    expect(store.user).toEqual(mockUser)
  })

  /**
   * Test adicional: Limpiar token inválido
   */
  it('should clear invalid token on check', async () => {
    const store = useAuthStore()
    
    store.token = 'invalid-token'
    vi.mocked(apiClient.hasValidToken).mockReturnValue(false)
    
    const isValid = await store.checkAuthStatus()
    
    expect(isValid).toBe(false)
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
  })

  /**
   * Test adicional: Manejar error de logout
   */
  it('should clear auth even if logout fails', async () => {
    const store = useAuthStore()
    
    // Simular usuario autenticado
    store.token = 'mock-token'
    store.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true
    }
    
    vi.mocked(apiClient.logout).mockRejectedValue(new Error('Network error'))
    
    await store.logout()
    
    // Debe limpiar el estado local incluso si falla la petición
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
  })
})
