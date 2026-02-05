/**
 * Tests de propiedad para NotificationsStore
 * Valida: Requerimientos 10.1, 10.2, 10.3, 10.4, 10.5
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotificationsStore } from '../notifications'

describe('NotificationsStore Property Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  /**
   * Propiedad 30: Notificaciones de estado de operaciones
   * Valida: Requerimientos 10.1, 10.2
   */
  it('Property 30: should show notifications for operation status', () => {
    const store = useNotificationsStore()

    // Agregar notificación de éxito
    const successId = store.success('Operación exitosa', 'La cuenta se actualizó correctamente')
    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0]?.type).toBe('success')
    expect(store.notifications[0]?.title).toBe('Operación exitosa')

    // Agregar notificación de error
    const errorId = store.error('Error', 'No se pudo conectar con el servidor')
    expect(store.notifications).toHaveLength(2)
    expect(store.notifications[0]?.type).toBe('error')

    // Agregar notificación de advertencia
    const warningId = store.warning('Advertencia', 'Tu sesión expirará pronto')
    expect(store.notifications).toHaveLength(3)
    expect(store.notifications[0]?.type).toBe('warning')

    // Agregar notificación de información
    const infoId = store.info('Información', 'Nueva actualización disponible')
    expect(store.notifications).toHaveLength(4)
    expect(store.notifications[0]?.type).toBe('info')
  })

  /**
   * Propiedad 31: Gestión de cola de notificaciones
   * Valida: Requerimientos 10.3, 10.4, 10.5
   */
  it('Property 31: should manage notification queue correctly', () => {
    const store = useNotificationsStore()

    // Agregar múltiples notificaciones
    for (let i = 0; i < 7; i++) {
      store.info(`Notificación ${i}`, `Mensaje ${i}`)
    }

    // Debe limitar a maxNotifications (5)
    expect(store.notifications).toHaveLength(5)
    expect(store.notifications[0]?.title).toBe('Notificación 6')
    expect(store.notifications[4]?.title).toBe('Notificación 2')
  })

  /**
   * Test adicional: Auto-descarte de notificaciones
   */
  it('should auto-dismiss non-persistent notifications', () => {
    const store = useNotificationsStore()

    // Agregar notificación con duración de 1000ms
    const id = store.addNotification('info', 'Test', 'Message', 1000, false)
    expect(store.notifications).toHaveLength(1)

    // Avanzar el tiempo
    vi.advanceTimersByTime(1000)

    // La notificación debe haberse eliminado
    expect(store.notifications).toHaveLength(0)
  })

  /**
   * Test adicional: Notificaciones persistentes no se auto-descartan
   */
  it('should not auto-dismiss persistent notifications', () => {
    const store = useNotificationsStore()

    // Agregar notificación persistente
    const id = store.addNotification('warning', 'Persistente', 'No se descarta', 1000, true)
    expect(store.notifications).toHaveLength(1)

    // Avanzar el tiempo
    vi.advanceTimersByTime(2000)

    // La notificación debe seguir ahí
    expect(store.notifications).toHaveLength(1)
  })

  /**
   * Test adicional: Remover notificación específica
   */
  it('should remove specific notification by ID', () => {
    const store = useNotificationsStore()

    const id1 = store.info('Notificación 1', 'Mensaje 1')
    const id2 = store.info('Notificación 2', 'Mensaje 2')
    const id3 = store.info('Notificación 3', 'Mensaje 3')

    expect(store.notifications).toHaveLength(3)

    // Remover la segunda notificación
    store.removeNotification(id2)

    expect(store.notifications).toHaveLength(2)
    expect(store.notifications.find(n => n.id === id2)).toBeUndefined()
  })

  /**
   * Test adicional: Limpiar todas las notificaciones
   */
  it('should clear all notifications', () => {
    const store = useNotificationsStore()

    store.info('Notificación 1', 'Mensaje 1')
    store.info('Notificación 2', 'Mensaje 2')
    store.info('Notificación 3', 'Mensaje 3')

    expect(store.notifications).toHaveLength(3)

    store.clearAll()

    expect(store.notifications).toHaveLength(0)
  })

  /**
   * Test adicional: Limpiar solo notificaciones no persistentes
   */
  it('should clear only non-persistent notifications', () => {
    const store = useNotificationsStore()

    store.addNotification('info', 'Normal', 'Se descarta', 5000, false)
    store.addNotification('warning', 'Persistente', 'No se descarta', 5000, true)
    store.addNotification('info', 'Normal 2', 'Se descarta', 5000, false)

    expect(store.notifications).toHaveLength(3)

    store.clearNonPersistent()

    expect(store.notifications).toHaveLength(1)
    expect(store.notifications[0]?.persistent).toBe(true)
  })

  /**
   * Test adicional: Duraciones personalizadas por tipo
   */
  it('should use custom durations for different types', () => {
    const store = useNotificationsStore()

    // Error debe tener duración más larga por defecto (7000ms)
    const errorId = store.error('Error', 'Mensaje de error')
    const errorNotification = store.notifications.find(n => n.id === errorId)
    expect(errorNotification?.duration).toBe(7000)

    // Success debe usar duración por defecto (5000ms)
    const successId = store.success('Éxito', 'Mensaje de éxito')
    const successNotification = store.notifications.find(n => n.id === successId)
    expect(successNotification?.duration).toBe(5000)
  })
})
