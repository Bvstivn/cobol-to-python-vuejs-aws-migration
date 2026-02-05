/**
 * Store de notificaciones con Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NotificationMessage, NotificationType } from '@/types'

export const useNotificationsStore = defineStore('notifications', () => {
  // Estado
  const notifications = ref<NotificationMessage[]>([])
  const maxNotifications = ref(5)

  // Getters computados
  const hasNotifications = computed(() => notifications.value.length > 0)
  const notificationCount = computed(() => notifications.value.length)

  /**
   * Agregar una notificación
   */
  function addNotification(
    type: NotificationType,
    title: string,
    message: string,
    duration: number = 5000,
    persistent: boolean = false
  ): string {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    const notification: NotificationMessage = {
      id,
      type,
      title,
      message,
      duration,
      persistent,
      timestamp: new Date()
    }

    // Agregar al inicio de la lista
    notifications.value.unshift(notification)

    // Limitar el número de notificaciones
    if (notifications.value.length > maxNotifications.value) {
      notifications.value = notifications.value.slice(0, maxNotifications.value)
    }

    // Auto-descarte si no es persistente
    if (!persistent && duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }

  /**
   * Métodos de conveniencia para diferentes tipos
   */
  function success(title: string, message: string, duration?: number): string {
    return addNotification('success', title, message, duration)
  }

  function error(title: string, message: string, duration?: number): string {
    return addNotification('error', title, message, duration || 7000)
  }

  function warning(title: string, message: string, duration?: number): string {
    return addNotification('warning', title, message, duration)
  }

  function info(title: string, message: string, duration?: number): string {
    return addNotification('info', title, message, duration)
  }

  /**
   * Remover una notificación por ID
   */
  function removeNotification(id: string): void {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  /**
   * Limpiar todas las notificaciones
   */
  function clearAll(): void {
    notifications.value = []
  }

  /**
   * Limpiar notificaciones no persistentes
   */
  function clearNonPersistent(): void {
    notifications.value = notifications.value.filter(n => n.persistent)
  }

  return {
    // Estado
    notifications,
    maxNotifications,
    // Getters
    hasNotifications,
    notificationCount,
    // Acciones
    addNotification,
    success,
    error,
    warning,
    info,
    removeNotification,
    clearAll,
    clearNonPersistent
  }
})
