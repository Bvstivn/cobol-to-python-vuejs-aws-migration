import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useThemeStore } from '../theme'
import * as fc from 'fast-check'

describe('ThemeStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('Propiedad 25: Alternancia de temas', () => {
    /**
     * **Validates: Requirements 8.1, 8.2**
     * 
     * Propiedad: La alternancia de temas debe ciclar correctamente entre light, dark y system
     * 
     * Estrategia:
     * - Generar secuencias de toggles
     * - Verificar que el ciclo sea: light -> dark -> system -> light
     * - Verificar que el tema efectivo se aplique correctamente
     */
    it('debe ciclar correctamente entre temas al hacer toggle', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 20 }),
          (toggleCount) => {
            const store = useThemeStore()
            store.initialize()

            // Empezar desde light
            store.setTheme('light')
            expect(store.currentTheme).toBe('light')

            // Aplicar toggles y verificar el ciclo
            for (let i = 0; i < toggleCount; i++) {
              const beforeTheme = store.currentTheme
              store.toggleTheme()
              const afterTheme = store.currentTheme

              // Verificar transición correcta
              if (beforeTheme === 'light') {
                expect(afterTheme).toBe('dark')
              } else if (beforeTheme === 'dark') {
                expect(afterTheme).toBe('system')
              } else if (beforeTheme === 'system') {
                expect(afterTheme).toBe('light')
              }
            }

            // Verificar que después de 3 toggles volvemos al inicio
            const finalPosition = toggleCount % 3
            if (finalPosition === 1) {
              expect(store.currentTheme).toBe('dark')
            } else if (finalPosition === 2) {
              expect(store.currentTheme).toBe('system')
            } else {
              expect(store.currentTheme).toBe('light')
            }
          }
        ),
        { numRuns: 15 }
      )
    })

    it('debe aplicar el tema efectivo correctamente según el modo', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('light', 'dark', 'system'),
          fc.constantFrom('light', 'dark'),
          (themeMode, systemTheme) => {
            const store = useThemeStore()
            store.initialize()

            // Configurar tema del sistema
            store.systemTheme = systemTheme

            // Establecer tema
            store.setTheme(themeMode as any)

            // Verificar tema efectivo
            if (themeMode === 'system') {
              expect(store.effectiveTheme).toBe(systemTheme)
            } else {
              expect(store.effectiveTheme).toBe(themeMode)
            }

            // Verificar isDark
            expect(store.isDark).toBe(store.effectiveTheme === 'dark')
          }
        ),
        { numRuns: 15 }
      )
    })
  })

  describe('Propiedad 26: Persistencia de preferencias de tema', () => {
    /**
     * **Validates: Requirements 8.3, 8.5**
     * 
     * Propiedad: Las preferencias de tema deben persistir en localStorage
     * 
     * Estrategia:
     * - Generar diferentes temas
     * - Establecer tema y verificar que se guarde en localStorage
     * - Crear nueva instancia del store y verificar que cargue el tema guardado
     */
    it('debe persistir el tema seleccionado en localStorage', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('light', 'dark', 'system'),
          (theme) => {
            const store = useThemeStore()
            store.initialize()

            // Establecer tema
            store.setTheme(theme as any)

            // Verificar que se guardó en localStorage
            const stored = localStorage.getItem('carddemo-theme')
            expect(stored).toBe(theme)

            // Crear nueva instancia y verificar que carga el tema
            const newStore = useThemeStore()
            newStore.initialize()
            expect(newStore.currentTheme).toBe(theme)
          }
        ),
        { numRuns: 15 }
      )
    })

    it('debe mantener la persistencia a través de múltiples cambios', () => {
      fc.assert(
        fc.property(
          fc.array(fc.constantFrom('light', 'dark', 'system'), { minLength: 1, maxLength: 10 }),
          (themes) => {
            const store = useThemeStore()
            store.initialize()

            // Aplicar cada tema en secuencia
            for (const theme of themes) {
              store.setTheme(theme as any)
              
              // Verificar persistencia inmediata
              const stored = localStorage.getItem('carddemo-theme')
              expect(stored).toBe(theme)
            }

            // Verificar que el último tema persiste
            const lastTheme = themes[themes.length - 1]
            const newStore = useThemeStore()
            newStore.initialize()
            expect(newStore.currentTheme).toBe(lastTheme)
          }
        ),
        { numRuns: 15 }
      )
    })

    it('debe usar tema por defecto si no hay nada en localStorage', () => {
      const store = useThemeStore()
      
      // Asegurar que localStorage está vacío
      localStorage.clear()
      
      store.initialize()
      
      // Debe usar 'system' como default
      expect(store.currentTheme).toBe('system')
    })
  })

  describe('Propiedad 23: Diseño responsive universal (tema)', () => {
    /**
     * **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
     * 
     * Propiedad: El sistema de temas debe funcionar correctamente en diferentes contextos
     * 
     * Estrategia:
     * - Verificar que el tema se aplica independientemente del estado inicial
     * - Verificar que los cambios de tema son inmediatos
     * - Verificar que el tema persiste entre recargas
     */
    it('debe aplicar temas correctamente independientemente del estado inicial', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('light', 'dark', 'system'),
          fc.constantFrom('light', 'dark', 'system'),
          (initialTheme, targetTheme) => {
            const store = useThemeStore()
            
            // Establecer tema inicial
            localStorage.setItem('carddemo-theme', initialTheme)
            store.initialize()
            expect(store.currentTheme).toBe(initialTheme)

            // Cambiar a tema objetivo
            store.setTheme(targetTheme as any)
            expect(store.currentTheme).toBe(targetTheme)

            // Verificar persistencia
            const stored = localStorage.getItem('carddemo-theme')
            expect(stored).toBe(targetTheme)
          }
        ),
        { numRuns: 15 }
      )
    })

    it('debe manejar cambios rápidos de tema sin perder estado', () => {
      fc.assert(
        fc.property(
          fc.array(fc.constantFrom('light', 'dark', 'system'), { minLength: 5, maxLength: 15 }),
          (themeSequence) => {
            const store = useThemeStore()
            store.initialize()

            // Aplicar cambios rápidos
            for (const theme of themeSequence) {
              store.setTheme(theme as any)
              expect(store.currentTheme).toBe(theme)
            }

            // Verificar que el último tema es el actual
            const lastTheme = themeSequence[themeSequence.length - 1]
            expect(store.currentTheme).toBe(lastTheme)
            expect(localStorage.getItem('carddemo-theme')).toBe(lastTheme)
          }
        ),
        { numRuns: 15 }
      )
    })
  })

  describe('Casos específicos de tema', () => {
    it('debe inicializar correctamente el tema', () => {
      const store = useThemeStore()
      store.initialize()

      expect(store.currentTheme).toBeDefined()
      expect(['light', 'dark', 'system']).toContain(store.currentTheme)
      expect(store.effectiveTheme).toBeDefined()
      expect(['light', 'dark']).toContain(store.effectiveTheme)
    })

    it('debe cambiar de light a dark correctamente', () => {
      const store = useThemeStore()
      store.initialize()

      store.setTheme('light')
      expect(store.currentTheme).toBe('light')
      expect(store.effectiveTheme).toBe('light')
      expect(store.isDark).toBe(false)

      store.setTheme('dark')
      expect(store.currentTheme).toBe('dark')
      expect(store.effectiveTheme).toBe('dark')
      expect(store.isDark).toBe(true)
    })

    it('debe respetar el tema del sistema cuando está en modo system', () => {
      const store = useThemeStore()
      store.initialize()

      store.setTheme('system')
      store.systemTheme = 'dark'
      expect(store.effectiveTheme).toBe('dark')
      expect(store.isDark).toBe(true)

      store.systemTheme = 'light'
      expect(store.effectiveTheme).toBe('light')
      expect(store.isDark).toBe(false)
    })
  })
})
