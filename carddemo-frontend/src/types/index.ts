/**
 * Tipos TypeScript para la aplicación CardDemo Frontend
 */

// ============================================================================
// TIPOS DE AUTENTICACIÓN
// ============================================================================

/**
 * Información del usuario autenticado
 * Compatible con UserResponse de la API
 */
export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
}

/**
 * Credenciales de login del usuario
 * Compatible con UserLogin de la API
 */
export interface LoginCredentials {
  username: string
  password: string
}

/**
 * Respuesta de autenticación exitosa
 * Compatible con TokenResponse de la API
 */
export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

/**
 * Estado de autenticación en el store
 */
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  tokenExpiresAt: Date | null
}

/**
 * Información de sesión persistida
 */
export interface SessionInfo {
  token: string
  user: User
  expiresAt: Date
}

/**
 * Estados de autenticación posibles
 */
export type AuthStatus = 
  | 'idle'
  | 'authenticating'
  | 'authenticated'
  | 'unauthenticated'
  | 'expired'
  | 'error'

/**
 * Errores específicos de autenticación
 */
export interface AuthError {
  code: 'INVALID_CREDENTIALS' | 'TOKEN_EXPIRED' | 'SESSION_INVALID' | 'NETWORK_ERROR'
  message: string
  details?: Record<string, any>
}

// ============================================================================
// TIPOS DE CUENTA
// ============================================================================

/**
 * Información de cuenta del usuario
 * Compatible con AccountResponse de la API
 */
export interface Account {
  id: number
  account_number: string
  first_name: string
  last_name: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zip_code?: string
  created_at: Date
  updated_at?: Date
}

/**
 * Datos para actualización de cuenta
 * Compatible con AccountUpdate de la API
 */
export interface UpdateAccountData {
  first_name?: string
  last_name?: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zip_code?: string
}

/**
 * Estado de cuenta en el store
 */
export interface AccountState {
  account: Account | null
  loading: boolean
  error: string | null
  lastUpdated?: Date
}

// ============================================================================
// TIPOS DE TARJETAS
// ============================================================================

/**
 * Tipos de tarjeta disponibles
 * Compatible con CardType enum de la API
 */
export type CardType = 'VISA' | 'MASTERCARD' | 'AMEX' | 'DISCOVER'

/**
 * Estados de tarjeta disponibles
 * Compatible con CardStatus enum de la API
 */
export type CardStatus = 'ACTIVE' | 'BLOCKED' | 'EXPIRED'

/**
 * Información de tarjeta de crédito
 * Compatible con CardResponse de la API
 */
export interface CreditCard {
  id: number
  masked_card_number: string
  card_type: CardType
  expiry_month: number
  expiry_year: number
  status: CardStatus
  credit_limit: number
  available_credit: number
  created_at: Date
}

/**
 * Estado de tarjetas en el store
 */
export interface CardsState {
  cards: CreditCard[]
  selectedCard: CreditCard | null
  loading: boolean
  error: string | null
  lastUpdated?: Date
}

/**
 * Información resumida de tarjeta para dashboard
 */
export interface CardSummary {
  id: number
  last_four_digits: string
  card_type: CardType
  available_credit: number
  credit_limit: number
  utilization_percentage: number
}

// ============================================================================
// TIPOS DE TRANSACCIONES
// ============================================================================

/**
 * Tipos de transacción disponibles
 * Compatible con TransactionType enum de la API
 */
export type TransactionType = 'PURCHASE' | 'PAYMENT' | 'REFUND'

/**
 * Estados de transacción disponibles
 * Compatible con TransactionStatus enum de la API
 */
export type TransactionStatus = 'PENDING' | 'COMPLETED' | 'FAILED'

/**
 * Información de transacción
 * Compatible con TransactionResponse de la API
 */
export interface Transaction {
  id: number
  transaction_date: Date
  merchant_name: string
  amount: number
  transaction_type: TransactionType
  status: TransactionStatus
  description?: string
  created_at: Date
}

/**
 * Filtros para búsqueda de transacciones
 * Compatible con TransactionFilters de la API
 */
export interface TransactionFilters {
  start_date?: string
  end_date?: string
  card_id?: number
  transaction_type?: TransactionType
  min_amount?: number
  max_amount?: number
  limit?: number
  offset?: number
}

/**
 * Respuesta de lista de transacciones con paginación
 * Compatible con TransactionListResponse de la API
 */
export interface TransactionResponse {
  transactions: Transaction[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

/**
 * Estado de transacciones en el store
 */
export interface TransactionsState {
  transactions: Transaction[]
  filters: TransactionFilters
  pagination: PaginationInfo
  loading: boolean
  error: string | null
  lastUpdated?: Date
}

/**
 * Información de paginación
 */
export interface PaginationInfo {
  page: number
  limit: number
  total: number
  totalPages: number
  hasMore: boolean
}

/**
 * Resumen de transacciones para dashboard
 */
export interface TransactionSummary {
  recent_transactions: Transaction[]
  total_spent_this_month: number
  transaction_count_this_month: number
  largest_transaction: Transaction | null
}

/**
 * Categorías de transacciones para análisis
 */
export interface TransactionCategory {
  name: string
  total_amount: number
  transaction_count: number
  percentage: number
}

// ============================================================================
// TIPOS DE UI Y NOTIFICACIONES
// ============================================================================

/**
 * Tipos de notificación disponibles
 */
export type NotificationType = 'success' | 'error' | 'warning' | 'info'

/**
 * Mensaje de notificación
 */
export interface NotificationMessage {
  id: string
  type: NotificationType
  title: string
  message: string
  duration?: number
  persistent?: boolean
  actions?: NotificationAction[]
  timestamp: Date
}

/**
 * Acción disponible en una notificación
 */
export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary' | 'danger'
}

/**
 * Estado del sistema de notificaciones
 */
export interface NotificationState {
  notifications: NotificationMessage[]
  maxNotifications: number
}

/**
 * Estado de carga genérico
 */
export interface LoadingState {
  isLoading: boolean
  message?: string
  progress?: number
}

/**
 * Estados de carga específicos por operación
 */
export interface LoadingStates {
  auth: LoadingState
  account: LoadingState
  cards: LoadingState
  transactions: LoadingState
  charts: LoadingState
  profile: LoadingState
}

/**
 * Error de API estructurado
 */
export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  correlation_id?: string
  timestamp?: Date
}

/**
 * Error de validación de formulario
 */
export interface ValidationError {
  field: string
  message: string
  code: string
}

/**
 * Estado de error genérico
 */
export interface ErrorState {
  hasError: boolean
  error: ApiError | null
  validationErrors: ValidationError[]
}

// ============================================================================
// TIPOS DE TEMA
// ============================================================================

/**
 * Modos de tema disponibles
 */
export type ThemeMode = 'light' | 'dark' | 'system'

/**
 * Configuración de tema
 */
export interface ThemeConfig {
  mode: ThemeMode
  primaryColor?: string
  accentColor?: string
}

/**
 * Estado del gestor de temas
 */
export interface ThemeState {
  currentTheme: ThemeMode
  systemTheme: 'light' | 'dark'
  config: ThemeConfig
}

// ============================================================================
// TIPOS DE INTERNACIONALIZACIÓN
// ============================================================================

/**
 * Idiomas soportados
 */
export type Locale = 'es' | 'en'

/**
 * Configuración de i18n
 */
export interface I18nConfig {
  locale: Locale
  fallbackLocale: Locale
  availableLocales: Locale[]
  dateFormat: string
  currencyFormat: string
  numberFormat: string
}

/**
 * Estado del sistema de i18n
 */
export interface I18nState {
  currentLocale: Locale
  config: I18nConfig
  loading: boolean
}

// ============================================================================
// TIPOS DE GRÁFICOS
// ============================================================================

/**
 * Datos para gráficos
 */
export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

/**
 * Dataset de gráfico
 */
export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  borderWidth?: number
  fill?: boolean
}

/**
 * Opciones de configuración de gráficos
 */
export interface ChartOptions {
  responsive: boolean
  maintainAspectRatio: boolean
  plugins?: {
    legend?: {
      display: boolean
      position?: 'top' | 'bottom' | 'left' | 'right'
    }
    tooltip?: {
      enabled: boolean
    }
  }
  scales?: Record<string, any>
}

/**
 * Tipos de gráfico disponibles
 */
export type ChartType = 'pie' | 'doughnut' | 'bar' | 'line' | 'area'

/**
 * Configuración de gráfico completa
 */
export interface ChartConfig {
  type: ChartType
  data: ChartData
  options: ChartOptions
}

/**
 * Estado de gráficos en el store
 */
export interface ChartsState {
  spendingChart: ChartConfig | null
  categoryChart: ChartConfig | null
  trendChart: ChartConfig | null
  loading: boolean
  error: string | null
}

// ============================================================================
// TIPOS DE FORMULARIOS
// ============================================================================

/**
 * Campo de formulario genérico
 */
export interface FormField<T = any> {
  name: string
  value: T
  error?: string
  touched: boolean
  dirty: boolean
  required: boolean
  disabled?: boolean
}

/**
 * Estado de formulario genérico
 */
export interface FormState<T = Record<string, any>> {
  fields: Record<keyof T, FormField>
  isValid: boolean
  isSubmitting: boolean
  errors: Record<string, string>
  touched: boolean
  dirty: boolean
}

/**
 * Opciones de validación
 */
export interface ValidationOptions {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => string | null
}

/**
 * Reglas de validación por campo
 */
export type ValidationRules<T> = {
  [K in keyof T]?: ValidationOptions
}

// ============================================================================
// TIPOS DE SALUD DEL SISTEMA
// ============================================================================

/**
 * Estado de salud del sistema
 * Compatible con HealthResponse de la API
 */
export interface HealthStatus {
  status: string
  service: string
  version: string
  timestamp: Date
}

/**
 * Estado de salud detallado
 * Compatible con DetailedHealthResponse de la API
 */
export interface DetailedHealthStatus extends HealthStatus {
  database: {
    status: string
    response_time_ms: number
  }
  uptime: number
}

// ============================================================================
// TIPOS DE NAVEGACIÓN Y ROUTING
// ============================================================================

/**
 * Información de ruta
 */
export interface RouteInfo {
  name: string
  path: string
  title: string
  icon?: string
  requiresAuth: boolean
  roles?: string[]
}

/**
 * Breadcrumb para navegación
 */
export interface Breadcrumb {
  label: string
  to?: string
  active: boolean
}

/**
 * Estado de navegación
 */
export interface NavigationState {
  currentRoute: RouteInfo | null
  breadcrumbs: Breadcrumb[]
  sidebarOpen: boolean
  mobileMenuOpen: boolean
}

// ============================================================================
// TIPOS DE CONFIGURACIÓN DE APLICACIÓN
// ============================================================================

/**
 * Configuración de la aplicación
 */
export interface AppConfig {
  app: {
    title: string
    version: string
    description: string
  }
  api: {
    baseUrl: string
    timeout: number
  }
  auth: {
    tokenStorageKey: string
    tokenExpiryBuffer: number
  }
  i18n: {
    defaultLocale: Locale
    fallbackLocale: Locale
    availableLocales: Locale[]
  }
  theme: {
    defaultTheme: ThemeMode
    storageKey: string
  }
  dev: {
    devMode: boolean
    debugMode: boolean
  }
}

// ============================================================================
// TIPOS UTILITARIOS
// ============================================================================

/**
 * Función de callback genérica
 */
export type Callback<T = void> = (data?: T) => void

/**
 * Función de callback con error
 */
export type ErrorCallback = (error: Error) => void

/**
 * Función de callback de éxito
 */
export type SuccessCallback<T = any> = (data: T) => void

/**
 * Opciones de petición HTTP
 */
export interface RequestOptions {
  timeout?: number
  retries?: number
  retryDelay?: number
  headers?: Record<string, string>
}

/**
 * Respuesta HTTP genérica
 */
export interface ApiResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: Record<string, string>
}