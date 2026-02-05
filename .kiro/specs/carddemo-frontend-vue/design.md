# Documento de Diseño

## Resumen

El frontend Vue.js de CardDemo es una aplicación web moderna construida con Vue.js 3, TypeScript y Tailwind CSS que proporciona una interfaz de usuario completa para el sistema bancario CardDemo. La aplicación implementa un diseño responsivo mobile-first con soporte para temas claro/oscuro e internacionalización español/inglés.

## Arquitectura

### Arquitectura General

La aplicación sigue una arquitectura de componentes Vue.js con el patrón de composición API, organizada en capas claramente definidas:

```
┌─────────────────────────────────────┐
│           Capa de Presentación      │
│     (Componentes Vue + Tailwind)    │
├─────────────────────────────────────┤
│         Capa de Estado              │
│        (Pinia Stores)               │
├─────────────────────────────────────┤
│         Capa de Servicios           │
│    (API Client + Utilidades)       │
├─────────────────────────────────────┤
│         Capa de Datos               │
│      (API REST CardDemo)            │
└─────────────────────────────────────┘
```

### Stack Tecnológico

- **Framework**: Vue.js 3 con Composition API
- **Lenguaje**: TypeScript para type safety
- **Build Tool**: Vite para desarrollo y build optimizado
- **Estilos**: Tailwind CSS para diseño utility-first
- **Routing**: Vue Router 4 para navegación SPA
- **Estado**: Pinia para gestión de estado reactivo
- **HTTP**: Axios para comunicación con API
- **Gráficos**: Chart.js con vue-chartjs para visualizaciones
- **I18n**: Vue I18n para internacionalización
- **Testing**: Vitest + Vue Test Utils para testing

### Estructura de Directorios

```
src/
├── components/          # Componentes reutilizables
│   ├── ui/             # Componentes base (botones, inputs, etc.)
│   ├── charts/         # Componentes de gráficos
│   └── layout/         # Componentes de layout
├── views/              # Páginas/vistas principales
├── stores/             # Pinia stores
├── services/           # Servicios y API client
├── composables/        # Composables reutilizables
├── types/              # Definiciones de tipos TypeScript
├── locales/            # Archivos de traducción
├── assets/             # Assets estáticos
└── router/             # Configuración de rutas
```

## Componentes e Interfaces

### Componentes Principales

#### 1. Layout Components

**AppLayout.vue**
- Layout principal de la aplicación
- Incluye navegación, sidebar y área de contenido
- Maneja responsive design con Tailwind breakpoints
- Integra theme switcher y language selector

**AppNavigation.vue**
- Barra de navegación principal
- Menú responsive con hamburger para móvil
- Indicadores de estado de usuario
- Logout functionality

**AppSidebar.vue**
- Navegación lateral para desktop
- Colapsa en móvil
- Enlaces a secciones principales

#### 2. Authentication Components

**LoginForm.vue**
```typescript
interface LoginFormProps {
  loading?: boolean
}

interface LoginFormEmits {
  submit: [credentials: LoginCredentials]
}

interface LoginCredentials {
  username: string
  password: string
}
```

#### 3. Dashboard Components

**DashboardView.vue**
- Vista principal del dashboard
- Orchestrates múltiples widgets

**AccountSummary.vue**
```typescript
interface AccountSummaryProps {
  account: AccountInfo
  loading?: boolean
}

interface AccountInfo {
  balance: number
  accountNumber: string
  accountType: string
  lastUpdated: Date
}
```

**RecentTransactions.vue**
```typescript
interface RecentTransactionsProps {
  transactions: Transaction[]
  loading?: boolean
  limit?: number
}
```

#### 4. Card Components

**CardList.vue**
```typescript
interface CardListProps {
  cards: CreditCard[]
  loading?: boolean
}
```

**CardItem.vue**
```typescript
interface CardItemProps {
  card: CreditCard
  showDetails?: boolean
}

interface CreditCard {
  id: string
  cardNumber: string
  cardType: string
  expiryDate: string
  balance: number
  creditLimit: number
  status: 'active' | 'blocked' | 'expired'
}
```

#### 5. Transaction Components

**TransactionHistory.vue**
```typescript
interface TransactionHistoryProps {
  filters?: TransactionFilters
}

interface TransactionFilters {
  dateFrom?: Date
  dateTo?: Date
  minAmount?: number
  maxAmount?: number
  type?: string
}
```

**TransactionItem.vue**
```typescript
interface TransactionItemProps {
  transaction: Transaction
  detailed?: boolean
}

interface Transaction {
  id: string
  date: Date
  description: string
  amount: number
  type: 'debit' | 'credit'
  category: string
  cardId?: string
}
```

#### 6. Chart Components

**SpendingChart.vue**
```typescript
interface SpendingChartProps {
  data: ChartData
  type: 'pie' | 'bar' | 'line'
  period: 'week' | 'month' | 'year'
}

interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}
```

#### 7. UI Components

**BaseButton.vue**
```typescript
interface BaseButtonProps {
  variant: 'primary' | 'secondary' | 'danger' | 'ghost'
  size: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
}
```

**BaseInput.vue**
```typescript
interface BaseInputProps {
  modelValue: string
  type: 'text' | 'email' | 'password' | 'number'
  placeholder?: string
  error?: string
  required?: boolean
}
```

**BaseModal.vue**
```typescript
interface BaseModalProps {
  show: boolean
  title?: string
  size: 'sm' | 'md' | 'lg' | 'xl'
}
```

### Servicios y API Client

#### ApiClient Service

```typescript
class ApiClient {
  private baseURL: string
  private axiosInstance: AxiosInstance

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 10000,
    })
    this.setupInterceptors()
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthResponse>
  async logout(): Promise<void>
  async getCurrentUser(): Promise<User>

  // Account methods
  async getAccount(): Promise<Account>
  async updateAccount(data: UpdateAccountData): Promise<Account>

  // Card methods
  async getCards(): Promise<CreditCard[]>
  async getCard(cardId: string): Promise<CreditCard>

  // Transaction methods
  async getTransactions(filters?: TransactionFilters): Promise<TransactionResponse>
  async getTransaction(transactionId: string): Promise<Transaction>

  // Health check
  async healthCheck(): Promise<HealthStatus>
}
```

#### AuthService

```typescript
class AuthService {
  private tokenKey = 'carddemo_token'
  
  async login(credentials: LoginCredentials): Promise<AuthResponse>
  async logout(): Promise<void>
  getToken(): string | null
  setToken(token: string): void
  removeToken(): void
  isAuthenticated(): boolean
  isTokenExpired(): boolean
}
```

### Pinia Stores

#### Auth Store

```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false
  }),

  actions: {
    async login(credentials: LoginCredentials): Promise<void>
    async logout(): Promise<void>
    async fetchCurrentUser(): Promise<void>
    async checkAuthStatus(): Promise<void>
  }
})
```

#### Account Store

```typescript
interface AccountState {
  account: Account | null
  loading: boolean
  error: string | null
}

export const useAccountStore = defineStore('account', {
  state: (): AccountState => ({
    account: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchAccount(): Promise<void>
    async updateAccount(data: UpdateAccountData): Promise<void>
  }
})
```

#### Cards Store

```typescript
interface CardsState {
  cards: CreditCard[]
  selectedCard: CreditCard | null
  loading: boolean
  error: string | null
}

export const useCardsStore = defineStore('cards', {
  state: (): CardsState => ({
    cards: [],
    selectedCard: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchCards(): Promise<void>
    async fetchCard(cardId: string): Promise<void>
    selectCard(card: CreditCard): void
  }
})
```

#### Transactions Store

```typescript
interface TransactionsState {
  transactions: Transaction[]
  filters: TransactionFilters
  pagination: PaginationInfo
  loading: boolean
  error: string | null
}

export const useTransactionsStore = defineStore('transactions', {
  state: (): TransactionsState => ({
    transactions: [],
    filters: {},
    pagination: { page: 1, limit: 20, total: 0 },
    loading: false,
    error: null
  }),

  actions: {
    async fetchTransactions(): Promise<void>
    async fetchTransaction(transactionId: string): Promise<void>
    setFilters(filters: TransactionFilters): void
    clearFilters(): void
  }
})
```

## Modelos de Datos

### Tipos de Autenticación

```typescript
interface User {
  id: string
  username: string
  email: string
  firstName: string
  lastName: string
  role: 'user' | 'admin'
  createdAt: Date
  updatedAt: Date
}

interface LoginCredentials {
  username: string
  password: string
}

interface AuthResponse {
  token: string
  user: User
  expiresAt: Date
}
```

### Tipos de Cuenta

```typescript
interface Account {
  id: string
  accountNumber: string
  accountType: string
  balance: number
  currency: string
  status: 'active' | 'inactive' | 'suspended'
  createdAt: Date
  updatedAt: Date
}

interface UpdateAccountData {
  firstName?: string
  lastName?: string
  email?: string
  phone?: string
  address?: Address
}

interface Address {
  street: string
  city: string
  state: string
  zipCode: string
  country: string
}
```

### Tipos de Tarjetas

```typescript
interface CreditCard {
  id: string
  cardNumber: string
  cardType: 'visa' | 'mastercard' | 'amex'
  expiryDate: string
  balance: number
  creditLimit: number
  availableCredit: number
  status: 'active' | 'blocked' | 'expired'
  issuedDate: Date
  lastUsed?: Date
}
```

### Tipos de Transacciones

```typescript
interface Transaction {
  id: string
  accountId: string
  cardId?: string
  date: Date
  description: string
  amount: number
  type: 'debit' | 'credit'
  category: string
  merchant?: string
  status: 'completed' | 'pending' | 'failed'
  reference: string
}

interface TransactionFilters {
  dateFrom?: Date
  dateTo?: Date
  minAmount?: number
  maxAmount?: number
  type?: 'debit' | 'credit'
  category?: string
  cardId?: string
}

interface TransactionResponse {
  transactions: Transaction[]
  pagination: PaginationInfo
}

interface PaginationInfo {
  page: number
  limit: number
  total: number
  totalPages: number
}
```

### Tipos de UI

```typescript
interface NotificationMessage {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  persistent?: boolean
}

interface LoadingState {
  isLoading: boolean
  message?: string
}

interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
}
```

## Propiedades de Corrección

*Una propiedad es una característica o comportamiento que debe mantenerse verdadero en todas las ejecuciones válidas de un sistema, esencialmente, una declaración formal sobre lo que el sistema debe hacer. Las propiedades sirven como puente entre las especificaciones legibles por humanos y las garantías de corrección verificables por máquina.*

Ahora voy a realizar el análisis de prework para determinar qué criterios de aceptación son testables como propiedades:

### Propiedades de Corrección

Basándome en el análisis de prework de los criterios de aceptación, las siguientes propiedades universales deben mantenerse:

**Propiedad 1: Autenticación con credenciales válidas**
*Para cualquier* conjunto de credenciales válidas, el proceso de login debe resultar en un token JWT almacenado y estado de autenticación establecido
**Valida: Requerimientos 1.1**

**Propiedad 2: Rechazo de credenciales inválidas**
*Para cualquier* conjunto de credenciales inválidas, el sistema debe rechazar el acceso y mostrar mensaje de error apropiado
**Valida: Requerimientos 1.2**

**Propiedad 3: Limpieza de sesión expirada**
*Para cualquier* token JWT expirado, el sistema debe limpiar el estado de autenticación y redirigir al login
**Valida: Requerimientos 1.3**

**Propiedad 4: Logout completo**
*Para cualquier* acción de logout, el sistema debe invalidar la sesión, limpiar tokens y redirigir al login
**Valida: Requerimientos 1.4**

**Propiedad 5: Persistencia de sesión válida**
*Para cualquier* token JWT válido durante refresh de página, el sistema debe mantener el estado de autenticación
**Valida: Requerimientos 1.5**

**Propiedad 6: Completitud del dashboard**
*Para cualquier* usuario autenticado con datos disponibles, el dashboard debe mostrar saldo de cuenta, transacciones recientes e información de tarjetas
**Valida: Requerimientos 2.1**

**Propiedad 7: Estados de carga universales**
*Para cualquier* operación de carga de datos (dashboard, transacciones, gráficos, assets), el sistema debe mostrar indicadores de carga apropiados durante el proceso
**Valida: Requerimientos 2.2, 4.5, 6.2, 12.1, 12.4**

**Propiedad 8: Manejo universal de errores**
*Para cualquier* error de API o indisponibilidad de datos, el sistema debe mostrar mensajes de error específicos y opciones de recuperación apropiadas
**Valida: Requerimientos 2.3, 3.3, 5.4, 10.2, 11.3, 11.5**

**Propiedad 9: Actualización reactiva de UI**
*Para cualquier* cambio en los datos subyacentes, todos los componentes de UI relevantes deben actualizarse para reflejar la nueva información
**Valida: Requerimientos 2.4, 6.5, 8.5**

**Propiedad 10: Actualización automática del dashboard**
*Para cualquier* navegación al dashboard, el sistema debe triggear automáticamente la actualización de datos
**Valida: Requerimientos 2.5**

**Propiedad 11: Visualización completa de tarjetas**
*Para cualquier* usuario con tarjetas de crédito, el visor debe mostrar todas las tarjetas con sus detalles básicos
**Valida: Requerimientos 3.1**

**Propiedad 12: Detalles de tarjeta seleccionada**
*Para cualquier* tarjeta seleccionada, el sistema debe mostrar información detallada incluyendo límites y saldos
**Valida: Requerimientos 3.2**

**Propiedad 13: Enmascaramiento de información sensible**
*Para cualquier* información sensible mostrada (números de tarjeta, datos personales), el sistema debe aplicar enmascaramiento apropiado
**Valida: Requerimientos 3.4, 5.5**

**Propiedad 14: Paginación de transacciones**
*Para cualquier* acceso al historial de transacciones, el sistema debe mostrar las transacciones de forma paginada con detalles básicos
**Valida: Requerimientos 4.1**

**Propiedad 15: Filtrado efectivo de transacciones**
*Para cualquier* filtro aplicado al historial de transacciones, los resultados mostrados deben cumplir exactamente con los criterios del filtro
**Valida: Requerimientos 4.2**

**Propiedad 16: Detalles de transacción seleccionada**
*Para cualquier* transacción seleccionada, el sistema debe mostrar información detallada completa de la transacción
**Valida: Requerimientos 4.3**

**Propiedad 17: Visualización de perfil actual**
*Para cualquier* usuario autenticado, el perfil debe mostrar toda la información actual del usuario
**Valida: Requerimientos 5.1**

**Propiedad 18: Validación y envío de actualizaciones de perfil**
*Para cualquier* actualización válida de perfil, el sistema debe validar los datos y enviarlos a la API
**Valida: Requerimientos 5.2**

**Propiedad 19: Confirmación de actualizaciones exitosas**
*Para cualquier* actualización de perfil exitosa, el sistema debe mostrar confirmación y actualizar la visualización
**Valida: Requerimientos 5.3**

**Propiedad 20: Generación de gráficos financieros**
*Para cualquier* conjunto de datos financieros válidos, el sistema debe generar gráficos interactivos que representen los patrones de gasto
**Valida: Requerimientos 6.1**

**Propiedad 21: Contenido de respaldo para gráficos**
*Para cualquier* situación donde los datos de gráficos no están disponibles, el sistema debe mostrar contenido de respaldo apropiado
**Valida: Requerimientos 6.3**

**Propiedad 22: Interactividad de gráficos**
*Para cualquier* interacción del usuario con gráficos (hover, click), el sistema debe proporcionar información detallada relevante
**Valida: Requerimientos 6.4**

**Propiedad 23: Diseño responsive universal**
*Para cualquier* viewport (móvil, tablet, escritorio) y orientación, el sistema debe adaptar el diseño apropiadamente para optimizar la experiencia del usuario
**Valida: Requerimientos 7.1, 7.2, 7.3, 7.4**

**Propiedad 24: Respuesta a gestos táctiles**
*Para cualquier* gesto táctil en dispositivos compatibles, el sistema debe responder apropiadamente según el contexto
**Valida: Requerimientos 7.5**

**Propiedad 25: Alternancia de temas**
*Para cualquier* acción de cambio de tema, el sistema debe alternar entre modo claro y oscuro y actualizar todos los componentes consistentemente
**Valida: Requerimientos 8.1, 8.5**

**Propiedad 26: Persistencia de preferencias de tema**
*Para cualquier* cambio de tema, el sistema debe persistir la preferencia en almacenamiento local y aplicarla en cargas futuras
**Valida: Requerimientos 8.2, 8.3**

**Propiedad 27: Actualización de idioma completa**
*Para cualquier* selección de idioma, el sistema debe actualizar todo el contenido de texto, formatos de fecha, número y moneda al idioma seleccionado
**Valida: Requerimientos 9.1, 9.3**

**Propiedad 28: Detección automática de idioma**
*Para cualquier* carga de aplicación, el sistema debe detectar y aplicar el idioma preferido del usuario o el detectado del sistema
**Valida: Requerimientos 9.2**

**Propiedad 29: Manejo elegante de traducciones faltantes**
*Para cualquier* traducción faltante, el sistema debe manejar la situación elegantemente sin romper la funcionalidad
**Valida: Requerimientos 9.5**

**Propiedad 30: Notificaciones de estado de operaciones**
*Para cualquier* operación de API (exitosa o fallida), el sistema debe mostrar notificaciones apropiadas con el estado y detalles relevantes
**Valida: Requerimientos 10.1, 10.2**

**Propiedad 31: Gestión de cola de notificaciones**
*Para cualquier* conjunto de múltiples notificaciones, el sistema debe encolarlas, mostrarlas apropiadamente y permitir auto-descarte y descarte manual
**Valida: Requerimientos 10.3, 10.4, 10.5**

**Propiedad 32: Headers de autenticación en peticiones**
*Para cualquier* petición a la API que requiera autenticación, el cliente debe incluir headers de autenticación apropiados
**Valida: Requerimientos 11.1**

**Propiedad 33: Reintento con backoff exponencial**
*Para cualquier* fallo de petición API por problemas de red, el cliente debe implementar lógica de reintento con backoff exponencial
**Valida: Requerimientos 11.2**

**Propiedad 34: Validación y transformación de respuestas exitosas**
*Para cualquier* respuesta exitosa de la API, el cliente debe validar y transformar los datos apropiadamente antes de usarlos
**Valida: Requerimientos 11.4**

**Propiedad 35: Paginación para conjuntos de datos grandes**
*Para cualquier* conjunto de datos grande, el sistema debe implementar paginación o scroll virtual para mantener el rendimiento
**Valida: Requerimientos 12.3**

**Propiedad 36: Carga prioritaria de recursos**
*Para cualquier* inicialización de aplicación, el sistema debe cargar recursos críticos primero y diferir los no críticos
**Valida: Requerimientos 12.5**

## Manejo de Errores

### Estrategia de Manejo de Errores

La aplicación implementa un sistema de manejo de errores en múltiples capas:

#### 1. Errores de API
```typescript
interface ApiErrorResponse {
  code: string
  message: string
  details?: Record<string, any>
  timestamp: Date
}

class ApiErrorHandler {
  static handle(error: AxiosError): ApiErrorResponse {
    // Manejo específico por código de estado HTTP
    // Transformación a formato consistente
    // Logging de errores
  }
}
```

#### 2. Errores de Validación
```typescript
interface ValidationError {
  field: string
  message: string
  code: string
}

class FormValidator {
  static validateLoginForm(data: LoginCredentials): ValidationError[]
  static validateProfileForm(data: UpdateAccountData): ValidationError[]
}
```

#### 3. Errores de Red
```typescript
class NetworkErrorHandler {
  static isNetworkError(error: Error): boolean
  static shouldRetry(error: Error, attempt: number): boolean
  static getRetryDelay(attempt: number): number // Exponential backoff
}
```

#### 4. Errores de Estado
```typescript
// En cada store de Pinia
interface StoreErrorState {
  error: string | null
  isError: boolean
}

// Composable para manejo de errores
export function useErrorHandler() {
  const showError = (message: string, details?: any) => {
    // Mostrar notificación de error
    // Log del error
    // Opcional: envío a servicio de monitoreo
  }
  
  const clearError = () => {
    // Limpiar estado de error
  }
  
  return { showError, clearError }
}
```

### Tipos de Errores y Respuestas

1. **Errores de Autenticación (401)**
   - Redirect automático a login
   - Limpieza de tokens
   - Mensaje de sesión expirada

2. **Errores de Autorización (403)**
   - Mensaje de permisos insuficientes
   - Redirect a página apropiada

3. **Errores de Validación (400)**
   - Mostrar errores específicos por campo
   - Highlight de campos con error

4. **Errores de Servidor (500)**
   - Mensaje genérico de error del servidor
   - Opción de reintento
   - Logging para debugging

5. **Errores de Red**
   - Mensaje de conectividad
   - Reintento automático con backoff
   - Modo offline si es aplicable

## Estrategia de Testing

### Enfoque Dual de Testing

La aplicación utiliza un enfoque dual que combina:

#### 1. Unit Tests (Vitest + Vue Test Utils)
- **Propósito**: Verificar ejemplos específicos, casos edge y condiciones de error
- **Enfoque**: Testing de componentes individuales y funciones utilitarias
- **Casos específicos**:
  - Renderizado correcto de componentes con props específicas
  - Manejo de casos edge (datos vacíos, valores nulos)
  - Validación de formularios con inputs específicos
  - Integración entre componentes padre-hijo

#### 2. Property-Based Tests (fast-check)
- **Propósito**: Verificar propiedades universales a través de múltiples inputs generados
- **Configuración**: Mínimo 100 iteraciones por test de propiedad
- **Cobertura**: Validación de comportamientos que deben mantenerse para cualquier input válido

#### Configuración de Property Tests

Cada test de propiedad debe:
- Ejecutar mínimo 100 iteraciones debido a la randomización
- Referenciar su propiedad correspondiente del documento de diseño
- Usar el formato de tag: **Feature: carddemo-frontend-vue, Property {número}: {texto de la propiedad}**

#### Ejemplos de Tests de Propiedad

```typescript
// Ejemplo: Propiedad 13 - Enmascaramiento de información sensible
describe('Property 13: Sensitive Information Masking', () => {
  it('should mask sensitive information for any displayed card number', () => {
    fc.assert(fc.property(
      fc.string({ minLength: 16, maxLength: 16 }), // Card number generator
      (cardNumber) => {
        const maskedNumber = maskCardNumber(cardNumber)
        expect(maskedNumber).toMatch(/\*{4,}/)
        expect(maskedNumber).not.toContain(cardNumber.substring(4, 12))
      }
    ), { numRuns: 100 })
  })
})

// Ejemplo: Propiedad 15 - Filtrado efectivo de transacciones
describe('Property 15: Effective Transaction Filtering', () => {
  it('should return only transactions matching filter criteria for any valid filter', () => {
    fc.assert(fc.property(
      fc.array(transactionGenerator), // Generate random transactions
      fc.record({ // Generate random filter
        dateFrom: fc.option(fc.date()),
        dateTo: fc.option(fc.date()),
        minAmount: fc.option(fc.float({ min: 0 })),
        type: fc.option(fc.constantFrom('debit', 'credit'))
      }),
      (transactions, filter) => {
        const filtered = filterTransactions(transactions, filter)
        filtered.forEach(transaction => {
          if (filter.dateFrom) expect(transaction.date >= filter.dateFrom).toBe(true)
          if (filter.dateTo) expect(transaction.date <= filter.dateTo).toBe(true)
          if (filter.minAmount) expect(transaction.amount >= filter.minAmount).toBe(true)
          if (filter.type) expect(transaction.type).toBe(filter.type)
        })
      }
    ), { numRuns: 100 })
  })
})
```

#### Balance de Testing

- **Unit tests**: Útiles para ejemplos específicos y casos edge
- **Property tests**: Manejan la cobertura de muchos inputs diferentes
- **Enfoque de unit tests**:
  - Ejemplos específicos que demuestran comportamiento correcto
  - Puntos de integración entre componentes
  - Casos edge y condiciones de error
- **Enfoque de property tests**:
  - Propiedades universales que se mantienen para todos los inputs
  - Cobertura comprehensiva de inputs a través de randomización

### Herramientas de Testing

- **Vitest**: Framework de testing rápido y moderno
- **Vue Test Utils**: Utilidades oficiales para testing de componentes Vue
- **fast-check**: Librería de property-based testing para TypeScript
- **@testing-library/vue**: Testing centrado en el usuario
- **MSW (Mock Service Worker)**: Mocking de API requests

### Configuración de Testing

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'html', 'lcov'],
      threshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
})
```

Cada propiedad de corrección debe ser implementada por UN SOLO test de propiedad, y estos requerimientos deben ser explícitos en la estrategia de testing.