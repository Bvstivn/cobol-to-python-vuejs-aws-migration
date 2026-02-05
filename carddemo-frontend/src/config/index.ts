/**
 * Configuración de la aplicación CardDemo Frontend
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
    defaultLocale: string
    fallbackLocale: string
    availableLocales: string[]
  }
  theme: {
    defaultTheme: 'light' | 'dark' | 'system'
    storageKey: string
  }
  dev: {
    devMode: boolean
    debugMode: boolean
  }
}

const config: AppConfig = {
  app: {
    title: import.meta.env.VITE_APP_TITLE || 'CardDemo',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    description: import.meta.env.VITE_APP_DESCRIPTION || 'Sistema de gestión bancaria CardDemo',
  },
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 10000,
  },
  auth: {
    tokenStorageKey: import.meta.env.VITE_TOKEN_STORAGE_KEY || 'carddemo_token',
    tokenExpiryBuffer: parseInt(import.meta.env.VITE_TOKEN_EXPIRY_BUFFER) || 300000, // 5 minutos
  },
  i18n: {
    defaultLocale: import.meta.env.VITE_DEFAULT_LOCALE || 'es',
    fallbackLocale: import.meta.env.VITE_FALLBACK_LOCALE || 'en',
    availableLocales: ['es', 'en'],
  },
  theme: {
    defaultTheme: 'system',
    storageKey: 'carddemo_theme',
  },
  dev: {
    devMode: import.meta.env.VITE_DEV_MODE === 'true',
    debugMode: import.meta.env.VITE_DEBUG_MODE === 'true',
  },
}

export default config