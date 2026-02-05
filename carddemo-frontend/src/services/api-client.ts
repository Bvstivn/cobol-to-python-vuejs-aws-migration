/**
 * Cliente API para comunicación con el backend CardDemo
 */
import axios, { AxiosError } from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import type {
  LoginCredentials,
  AuthResponse,
  User,
  Account,
  UpdateAccountData,
  CreditCard,
  Transaction,
  TransactionFilters,
  TransactionResponse,
  HealthStatus,
  ApiError,
  RequestOptions
} from '@/types'
import config from '@/config'

/**
 * Cliente API principal para todas las comunicaciones con el backend
 */
export class ApiClient {
  private axiosInstance: AxiosInstance
  private baseURL: string

  constructor(baseURL: string = config.api.baseUrl) {
    this.baseURL = baseURL
    this.axiosInstance = axios.create({
      baseURL,
      timeout: config.api.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  /**
   * Configurar interceptors para requests y responses
   */
  private setupInterceptors(): void {
    // Request interceptor - agregar token de autenticación
    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.getStoredToken()
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error: AxiosError) => {
        return Promise.reject(this.transformError(error))
      }
    )

    // Response interceptor - manejar errores globales
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error: AxiosError) => {
        // Manejar token expirado
        if (error.response?.status === 401) {
          this.removeStoredToken()
          // Emitir evento para que el store de auth maneje la redirección
          window.dispatchEvent(new CustomEvent('auth:token-expired'))
        }
        return Promise.reject(this.transformError(error))
      }
    )
  }

  /**
   * Transformar errores de Axios a formato ApiError
   */
  private transformError(error: AxiosError): ApiError {
    if (error.response) {
      // Error de respuesta del servidor
      const responseData = error.response.data as any
      return {
        code: responseData?.error?.code || `HTTP_${error.response.status}`,
        message: responseData?.error?.message || error.message,
        details: responseData?.error?.details || {},
        correlation_id: responseData?.error?.correlation_id,
        timestamp: responseData?.error?.timestamp ? new Date(responseData.error.timestamp) : new Date()
      }
    } else if (error.request) {
      // Error de red
      return {
        code: 'NETWORK_ERROR',
        message: 'No se pudo conectar con el servidor',
        details: { originalError: error.message },
        timestamp: new Date()
      }
    } else {
      // Error de configuración
      return {
        code: 'REQUEST_ERROR',
        message: error.message,
        details: {},
        timestamp: new Date()
      }
    }
  }

  /**
   * Obtener token almacenado
   */
  private getStoredToken(): string | null {
    return localStorage.getItem(config.auth.tokenStorageKey)
  }

  /**
   * Almacenar token
   */
  private setStoredToken(token: string): void {
    localStorage.setItem(config.auth.tokenStorageKey, token)
  }

  /**
   * Remover token almacenado
   */
  private removeStoredToken(): void {
    localStorage.removeItem(config.auth.tokenStorageKey)
  }

  // ============================================================================
  // MÉTODOS DE AUTENTICACIÓN
  // ============================================================================

  /**
   * Iniciar sesión con credenciales
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.axiosInstance.post<AuthResponse>('/auth/login', credentials)
    
    // Almacenar token automáticamente
    this.setStoredToken(response.data.access_token)
    
    return response.data
  }

  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    try {
      await this.axiosInstance.post('/auth/logout')
    } finally {
      // Siempre remover token, incluso si la petición falla
      this.removeStoredToken()
    }
  }

  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.axiosInstance.get<User>('/auth/me')
    return response.data
  }

  // ============================================================================
  // MÉTODOS DE CUENTA
  // ============================================================================

  /**
   * Obtener información de la cuenta del usuario actual
   */
  async getAccount(): Promise<Account> {
    const response = await this.axiosInstance.get<Account>('/accounts/me')
    
    // Convertir fechas de string a Date
    const account = response.data
    return {
      ...account,
      created_at: new Date(account.created_at),
      updated_at: account.updated_at ? new Date(account.updated_at) : undefined
    }
  }

  /**
   * Actualizar información de la cuenta
   */
  async updateAccount(data: UpdateAccountData): Promise<Account> {
    const response = await this.axiosInstance.put<Account>('/accounts/me', data)
    
    // Convertir fechas de string a Date
    const account = response.data
    return {
      ...account,
      created_at: new Date(account.created_at),
      updated_at: account.updated_at ? new Date(account.updated_at) : undefined
    }
  }

  // ============================================================================
  // MÉTODOS DE TARJETAS
  // ============================================================================

  /**
   * Obtener todas las tarjetas del usuario
   */
  async getCards(): Promise<CreditCard[]> {
    const response = await this.axiosInstance.get<CreditCard[]>('/cards')
    
    // Convertir fechas de string a Date
    return response.data.map(card => ({
      ...card,
      created_at: new Date(card.created_at)
    }))
  }

  /**
   * Obtener detalles de una tarjeta específica
   */
  async getCard(cardId: number): Promise<CreditCard> {
    const response = await this.axiosInstance.get<CreditCard>(`/cards/${cardId}`)
    
    // Convertir fechas de string a Date
    const card = response.data
    return {
      ...card,
      created_at: new Date(card.created_at)
    }
  }

  // ============================================================================
  // MÉTODOS DE TRANSACCIONES
  // ============================================================================

  /**
   * Obtener transacciones con filtros opcionales
   */
  async getTransactions(filters?: TransactionFilters): Promise<TransactionResponse> {
    const params = new URLSearchParams()
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }

    const response = await this.axiosInstance.get<TransactionResponse>(
      `/transactions?${params.toString()}`
    )
    
    // Convertir fechas de string a Date
    const data = response.data
    return {
      ...data,
      transactions: data.transactions.map(transaction => ({
        ...transaction,
        transaction_date: new Date(transaction.transaction_date),
        created_at: new Date(transaction.created_at)
      }))
    }
  }

  /**
   * Obtener detalles de una transacción específica
   */
  async getTransaction(transactionId: number): Promise<Transaction> {
    const response = await this.axiosInstance.get<Transaction>(`/transactions/${transactionId}`)
    
    // Convertir fechas de string a Date
    const transaction = response.data
    return {
      ...transaction,
      transaction_date: new Date(transaction.transaction_date),
      created_at: new Date(transaction.created_at)
    }
  }

  // ============================================================================
  // MÉTODOS DE SALUD
  // ============================================================================

  /**
   * Verificar estado de salud de la API
   */
  async healthCheck(): Promise<HealthStatus> {
    const response = await this.axiosInstance.get<HealthStatus>('/health')
    
    // Convertir fecha de string a Date
    const health = response.data
    return {
      ...health,
      timestamp: new Date(health.timestamp)
    }
  }

  // ============================================================================
  // MÉTODOS UTILITARIOS
  // ============================================================================

  /**
   * Verificar si hay un token válido almacenado
   */
  hasValidToken(): boolean {
    const token = this.getStoredToken()
    if (!token) return false

    try {
      // Decodificar JWT para verificar expiración
      const parts = token.split('.')
      if (parts.length !== 3 || !parts[1]) return false
      
      const payload = JSON.parse(atob(parts[1]))
      const now = Math.floor(Date.now() / 1000)
      
      // Verificar si el token expira pronto (buffer de 5 minutos)
      return payload.exp > (now + config.auth.tokenExpiryBuffer / 1000)
    } catch {
      return false
    }
  }

  /**
   * Obtener información del token actual
   */
  getTokenInfo(): { user_id: number; username: string; exp: number } | null {
    const token = this.getStoredToken()
    if (!token) return null

    try {
      const parts = token.split('.')
      if (parts.length !== 3 || !parts[1]) return null
      
      const payload = JSON.parse(atob(parts[1]))
      return {
        user_id: payload.sub,
        username: payload.username,
        exp: payload.exp
      }
    } catch {
      return null
    }
  }

  /**
   * Configurar token manualmente (útil para testing)
   */
  setToken(token: string): void {
    this.setStoredToken(token)
  }

  /**
   * Limpiar token manualmente
   */
  clearToken(): void {
    this.removeStoredToken()
  }
}

// Instancia singleton del cliente API
export const apiClient = new ApiClient()

// Export por defecto
export default apiClient