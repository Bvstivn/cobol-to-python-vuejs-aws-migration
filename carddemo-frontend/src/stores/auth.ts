/**
 * Store de autenticación con Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials } from '@/types'
import { apiClient } from '@/services/api-client'
import config from '@/config'

export const useAuthStore = defineStore('auth', () => {
  // Estado
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters computados
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const username = computed(() => user.value?.username || '')
  const userId = computed(() => user.value?.id || null)

  /**
   * Inicializar store - verificar token almacenado
   */
  function initialize(): void {
    const storedToken = localStorage.getItem(config.auth.tokenStorageKey)
    
    if (storedToken && apiClient.hasValidToken()) {
      token.value = storedToken
      // Intentar obtener información del usuario
      checkAuthStatus()
    } else {
      // Limpiar token inválido
      clearAuth()
    }
  }

  /**
   * Iniciar sesión con credenciales
   */
  async function login(credentials: LoginCredentials): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.login(credentials)
      
      // Guardar token y usuario
      token.value = response.access_token
      user.value = response.user
      
      // El apiClient ya guarda el token en localStorage
    } catch (err: any) {
      error.value = err.message || 'Error al iniciar sesión'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Cerrar sesión
   */
  async function logout(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      await apiClient.logout()
    } catch (err: any) {
      // Ignorar errores de logout - siempre limpiar localmente
      console.error('Error al cerrar sesión:', err)
    } finally {
      clearAuth()
      isLoading.value = false
    }
  }

  /**
   * Verificar estado de autenticación actual
   */
  async function checkAuthStatus(): Promise<boolean> {
    if (!token.value || !apiClient.hasValidToken()) {
      clearAuth()
      return false
    }

    try {
      const currentUser = await apiClient.getCurrentUser()
      user.value = currentUser
      return true
    } catch (err: any) {
      // Token inválido o expirado
      clearAuth()
      return false
    }
  }

  /**
   * Limpiar estado de autenticación
   */
  function clearAuth(): void {
    user.value = null
    token.value = null
    error.value = null
    apiClient.clearToken()
  }

  /**
   * Limpiar error
   */
  function clearError(): void {
    error.value = null
  }

  // Escuchar evento de token expirado
  if (typeof window !== 'undefined') {
    window.addEventListener('auth:token-expired', () => {
      clearAuth()
    })
  }

  return {
    // Estado
    user,
    token,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    username,
    userId,
    // Acciones
    initialize,
    login,
    logout,
    checkAuthStatus,
    clearAuth,
    clearError
  }
})
