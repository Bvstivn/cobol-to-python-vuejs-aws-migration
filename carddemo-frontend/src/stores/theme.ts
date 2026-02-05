import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { ThemeMode } from '@/types'

const THEME_STORAGE_KEY = 'carddemo-theme'

export const useThemeStore = defineStore('theme', () => {
  // Estado
  const currentTheme = ref<ThemeMode>('system')
  const systemTheme = ref<'light' | 'dark'>('light')

  // Computed
  const effectiveTheme = computed<'light' | 'dark'>(() => {
    if (currentTheme.value === 'system') {
      return systemTheme.value
    }
    return currentTheme.value
  })

  const isDark = computed(() => effectiveTheme.value === 'dark')

  // Detectar tema del sistema
  const detectSystemTheme = () => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
      systemTheme.value = isDarkMode ? 'dark' : 'light'
    }
  }

  // Aplicar tema al DOM
  const applyTheme = (theme: 'light' | 'dark') => {
    if (typeof document !== 'undefined') {
      if (theme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  // Cargar tema desde localStorage
  const loadTheme = () => {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null
      if (stored && ['light', 'dark', 'system'].includes(stored)) {
        currentTheme.value = stored
      }
    }
  }

  // Guardar tema en localStorage
  const saveTheme = (theme: ThemeMode) => {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(THEME_STORAGE_KEY, theme)
    }
  }

  // Acciones
  const setTheme = (theme: ThemeMode) => {
    currentTheme.value = theme
    saveTheme(theme)
    applyTheme(effectiveTheme.value)
  }

  const toggleTheme = () => {
    if (currentTheme.value === 'light') {
      setTheme('dark')
    } else if (currentTheme.value === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  const initialize = () => {
    detectSystemTheme()
    loadTheme()
    applyTheme(effectiveTheme.value)

    // Escuchar cambios en el tema del sistema
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handler = (e: MediaQueryListEvent) => {
        systemTheme.value = e.matches ? 'dark' : 'light'
        if (currentTheme.value === 'system') {
          applyTheme(effectiveTheme.value)
        }
      }
      mediaQuery.addEventListener('change', handler)
    }
  }

  // Watch para aplicar cambios de tema
  watch(effectiveTheme, (newTheme) => {
    applyTheme(newTheme)
  })

  return {
    // Estado
    currentTheme,
    systemTheme,
    effectiveTheme,
    isDark,
    
    // Acciones
    setTheme,
    toggleTheme,
    initialize
  }
})
