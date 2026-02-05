/**
 * Manejador de errores para CardDemo Frontend
 */
import type { ApiError, NotificationMessage } from '@/types'

/**
 * Manejador de errores de red con lógica de backoff exponencial
 */
export class NetworkErrorHandler {
  private static readonly MAX_RETRIES = 3
  private static readonly BASE_DELAY = 1000 // 1 segundo
  private static readonly MAX_DELAY = 10000 // 10 segundos

  /**
   * Verificar si un error es de red
   */
  static isNetworkError(error: ApiError): boolean {
    return error.code === 'NETWORK_ERROR' || 
           error.code.startsWith('HTTP_5') || // Errores 5xx del servidor
           error.code === 'TIMEOUT_ERROR'
  }

  /**
   * Verificar si se debe reintentar la petición
   */
  static shouldRetry(error: ApiError, attempt: number): boolean {
    if (attempt >= this.MAX_RETRIES) return false
    
    // Solo reintentar errores de red y errores 5xx del servidor
    if (!this.isNetworkError(error)) return false
    
    // No reintentar errores de autenticación
    if (error.code === 'HTTP_401' || error.code === 'HTTP_403') return false
    
    return true
  }

  /**
   * Calcular delay para reintento con backoff exponencial
   */
  static getRetryDelay(attempt: number): number {
    const delay = this.BASE_DELAY * Math.pow(2, attempt - 1)
    const jitter = Math.random() * 0.1 * delay // Agregar jitter del 10%
    return Math.min(delay + jitter, this.MAX_DELAY)
  }

  /**
   * Ejecutar función con reintentos automáticos
   */
  static async withRetry<T>(
    fn: () => Promise<T>,
    context: string = 'API request'
  ): Promise<T> {
    let lastError: ApiError
    
    for (let attempt = 1; attempt <= this.MAX_RETRIES + 1; attempt++) {
      try {
        return await fn()
      } catch (error) {
        lastError = error as ApiError
        
        if (!this.shouldRetry(lastError, attempt)) {
          throw lastError
        }
        
        const delay = this.getRetryDelay(attempt)
        console.warn(`${context} failed (attempt ${attempt}), retrying in ${delay}ms:`, lastError.message)
        
        await this.sleep(delay)
      }
    }
    
    throw lastError!
  }

  /**
   * Función de sleep para delays
   */
  private static sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

/**
 * Manejador de errores de API
 */
export class ApiErrorHandler {
  /**
   * Transformar error de API a mensaje de notificación
   */
  static toNotification(error: ApiError, context?: string): NotificationMessage {
    const id = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    let title = 'Error'
    let message = error.message
    let type: 'error' | 'warning' = 'error'

    // Personalizar mensaje según el código de error
    switch (error.code) {
      case 'NETWORK_ERROR':
        title = 'Error de Conexión'
        message = 'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
        break
        
      case 'HTTP_401':
        title = 'Sesión Expirada'
        message = 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
        break
        
      case 'HTTP_403':
        title = 'Acceso Denegado'
        message = 'No tienes permisos para realizar esta acción.'
        break
        
      case 'HTTP_404':
        title = 'No Encontrado'
        message = 'El recurso solicitado no fue encontrado.'
        break
        
      case 'HTTP_429':
        title = 'Demasiadas Peticiones'
        message = 'Has realizado demasiadas peticiones. Intenta nuevamente en unos momentos.'
        type = 'warning'
        break
        
      case 'HTTP_500':
      case 'HTTP_502':
      case 'HTTP_503':
      case 'HTTP_504':
        title = 'Error del Servidor'
        message = 'El servidor está experimentando problemas. Intenta nuevamente más tarde.'
        break
        
      case 'VALIDATION_ERROR':
        title = 'Datos Inválidos'
        message = 'Los datos proporcionados no son válidos. Revisa la información e intenta nuevamente.'
        break
        
      case 'TIMEOUT_ERROR':
        title = 'Tiempo Agotado'
        message = 'La petición tardó demasiado en responder. Intenta nuevamente.'
        break
    }

    // Agregar contexto si se proporciona
    if (context) {
      message = `${context}: ${message}`
    }

    return {
      id,
      type,
      title,
      message,
      timestamp: new Date(),
      duration: type === 'error' ? 8000 : 5000, // Errores se muestran más tiempo
      persistent: error.code === 'HTTP_401' // Errores de auth son persistentes
    }
  }

  /**
   * Obtener mensaje de error amigable para el usuario
   */
  static getUserFriendlyMessage(error: ApiError): string {
    const messages: Record<string, string> = {
      'NETWORK_ERROR': 'Problema de conexión. Verifica tu internet.',
      'HTTP_401': 'Sesión expirada. Inicia sesión nuevamente.',
      'HTTP_403': 'No tienes permisos para esta acción.',
      'HTTP_404': 'Información no encontrada.',
      'HTTP_429': 'Demasiadas peticiones. Espera un momento.',
      'HTTP_500': 'Error del servidor. Intenta más tarde.',
      'VALIDATION_ERROR': 'Datos inválidos. Revisa la información.',
      'TIMEOUT_ERROR': 'Tiempo agotado. Intenta nuevamente.'
    }

    return messages[error.code] || 'Ha ocurrido un error inesperado.'
  }

  /**
   * Determinar si el error requiere acción del usuario
   */
  static requiresUserAction(error: ApiError): boolean {
    const actionRequiredCodes = [
      'HTTP_401', // Necesita login
      'HTTP_403', // Necesita permisos
      'VALIDATION_ERROR' // Necesita corregir datos
    ]
    
    return actionRequiredCodes.includes(error.code)
  }

  /**
   * Obtener acciones sugeridas para el error
   */
  static getSuggestedActions(error: ApiError): string[] {
    const actions: Record<string, string[]> = {
      'NETWORK_ERROR': [
        'Verifica tu conexión a internet',
        'Intenta recargar la página',
        'Contacta soporte si el problema persiste'
      ],
      'HTTP_401': [
        'Inicia sesión nuevamente',
        'Verifica tus credenciales'
      ],
      'HTTP_403': [
        'Contacta al administrador',
        'Verifica tus permisos de cuenta'
      ],
      'HTTP_404': [
        'Verifica que la información existe',
        'Intenta buscar nuevamente',
        'Contacta soporte si debería existir'
      ],
      'HTTP_429': [
        'Espera unos minutos antes de intentar nuevamente',
        'Reduce la frecuencia de tus peticiones'
      ],
      'HTTP_500': [
        'Intenta nuevamente en unos minutos',
        'Contacta soporte si el problema persiste'
      ],
      'VALIDATION_ERROR': [
        'Revisa que todos los campos estén completos',
        'Verifica el formato de los datos',
        'Consulta los requisitos de cada campo'
      ],
      'TIMEOUT_ERROR': [
        'Verifica tu conexión a internet',
        'Intenta nuevamente',
        'Contacta soporte si el problema persiste'
      ]
    }

    return actions[error.code] || ['Intenta nuevamente', 'Contacta soporte si el problema persiste']
  }

  /**
   * Log de error para debugging
   */
  static logError(error: ApiError, context?: string): void {
    const logData = {
      timestamp: new Date().toISOString(),
      context: context || 'Unknown',
      code: error.code,
      message: error.message,
      details: error.details,
      correlation_id: error.correlation_id
    }

    console.error('API Error:', logData)

    // En producción, aquí se podría enviar a un servicio de logging
    if (import.meta.env.PROD && error.correlation_id) {
      // Ejemplo: enviar a servicio de monitoreo
      // analyticsService.trackError(logData)
    }
  }
}

/**
 * Composable para manejo de errores en componentes
 */
export function useErrorHandler() {
  /**
   * Manejar error y mostrar notificación
   */
  const handleError = (error: ApiError, context?: string): NotificationMessage => {
    // Log del error
    ApiErrorHandler.logError(error, context)
    
    // Crear notificación
    const notification = ApiErrorHandler.toNotification(error, context)
    
    // Aquí se podría integrar con el store de notificaciones
    // notificationStore.addNotification(notification)
    
    return notification
  }

  /**
   * Ejecutar función con manejo de errores automático
   */
  const withErrorHandling = async <T>(
    fn: () => Promise<T>,
    context?: string,
    showNotification: boolean = true
  ): Promise<T | null> => {
    try {
      return await NetworkErrorHandler.withRetry(fn, context)
    } catch (error) {
      const apiError = error as ApiError
      
      if (showNotification) {
        handleError(apiError, context)
      }
      
      return null
    }
  }

  return {
    handleError,
    withErrorHandling,
    isNetworkError: NetworkErrorHandler.isNetworkError,
    shouldRetry: NetworkErrorHandler.shouldRetry,
    getUserFriendlyMessage: ApiErrorHandler.getUserFriendlyMessage,
    getSuggestedActions: ApiErrorHandler.getSuggestedActions
  }
}