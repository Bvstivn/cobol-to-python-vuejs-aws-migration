/**
 * Servicio de autenticación para CardDemo Frontend
 */
import type { LoginCredentials, AuthResponse, User, SessionInfo } from '@/types'
import { apiClient } from './api-client'
import config from '@/config'

/**
 * Servicio de autenticación que maneja login, logout y gestión de sesiones
 */
export class AuthService {
  private readonly tokenKey = config.auth.tokenStorageKey
  private readonly sessionKey = 'carddemo_session'

  /**
   * Iniciar sesión con credenciales
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const authResponse = await apiClient.login(credentials)
      
      // Guardar información de sesión
      this.saveSession({
        token: authResponse.access_token,
        user: authResponse.user,
        expiresAt: new Date(Date.now() + authResponse.expires_in * 1000)
      })
      
      return authResponse
    } catch (error) {
      // Limpiar cualquier sesión previa en caso de error
      this.clearSession()
      throw error
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    try {
      await apiClient.logout()
    } catch (error) {
      // Log del error pero no fallar el logout
      console.warn('Error durante logout en servidor:', error)
    } finally {
      // Siempre limpiar sesión local
      this.clearSession()
    }
  }

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser(): Promise<User> {
    return await apiClient.getCurrentUser()
  }

  /**
   * Verificar si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    const session = this.getSession()
    if (!session) return false

    // Verificar si el token no ha expirado
    return session.expiresAt > new Date()
  }

  /**
   * Verificar si el token está próximo a expirar
   */
  isTokenExpiring(): boolean {
    const session = this.getSession()
    if (!session) return false

    const now = new Date()
    const bufferTime = config.auth.tokenExpiryBuffer
    const expiryWithBuffer = new Date(session.expiresAt.getTime() - bufferTime)

    return now >= expiryWithBuffer
  }

  /**
   * Obtener token actual
   */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey)
  }

  /**
   * Obtener información de sesión actual
   */
  getSession(): SessionInfo | null {
    try {
      const sessionData = localStorage.getItem(this.sessionKey)
      if (!sessionData) return null

      const session = JSON.parse(sessionData)
      return {
        ...session,
        expiresAt: new Date(session.expiresAt)
      }
    } catch {
      return null
    }
  }

  /**
   * Obtener usuario actual de la sesión
   */
  getCurrentUserFromSession(): User | null {
    const session = this.getSession()
    return session?.user || null
  }

  /**
   * Verificar estado de autenticación y limpiar si es necesario
   */
  async checkAuthStatus(): Promise<boolean> {
    if (!this.isAuthenticated()) {
      this.clearSession()
      return false
    }

    // Si el token está próximo a expirar, intentar refrescar
    if (this.isTokenExpiring()) {
      try {
        // En JWT stateless, no hay refresh token, así que verificamos con el servidor
        await this.getCurrentUser()
        return true
      } catch {
        // Si falla, limpiar sesión
        this.clearSession()
        return false
      }
    }

    return true
  }

  /**
   * Guardar información de sesión
   */
  private saveSession(session: SessionInfo): void {
    localStorage.setItem(this.sessionKey, JSON.stringify({
      ...session,
      expiresAt: session.expiresAt.toISOString()
    }))
  }

  /**
   * Limpiar toda la información de sesión
   */
  private clearSession(): void {
    localStorage.removeItem(this.tokenKey)
    localStorage.removeItem(this.sessionKey)
    apiClient.clearToken()
  }

  /**
   * Manejar expiración de token (llamado por eventos)
   */
  handleTokenExpiration(): void {
    this.clearSession()
    // Emitir evento para que los componentes puedan reaccionar
    window.dispatchEvent(new CustomEvent('auth:session-expired'))
  }
}

// Instancia singleton del servicio de autenticación
export const authService = new AuthService()

// Configurar listener para eventos de token expirado
window.addEventListener('auth:token-expired', () => {
  authService.handleTokenExpiration()
})

// Export por defecto
export default authService