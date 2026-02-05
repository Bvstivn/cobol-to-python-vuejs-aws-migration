/**
 * Store de tarjetas con Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CreditCard } from '@/types'
import { CardService } from '@/services/card-service'

const cardService = new CardService()

export const useCardsStore = defineStore('cards', () => {
  // Estado
  const cards = ref<CreditCard[]>([])
  const selectedCard = ref<CreditCard | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchTime = ref<Date | null>(null)

  // Getters computados
  const hasCards = computed(() => cards.value.length > 0)
  const cardCount = computed(() => cards.value.length)
  const activeCards = computed(() => 
    cards.value.filter(card => card.status === 'ACTIVE')
  )
  const totalCreditLimit = computed(() => 
    cards.value.reduce((sum, card) => sum + card.credit_limit, 0)
  )
  const totalAvailableCredit = computed(() => 
    cards.value.reduce((sum, card) => sum + card.available_credit, 0)
  )
  const totalUsedCredit = computed(() => 
    totalCreditLimit.value - totalAvailableCredit.value
  )

  /**
   * Obtener todas las tarjetas
   */
  async function fetchCards(force = false): Promise<void> {
    // Evitar fetch duplicado si ya tenemos datos recientes (< 30 segundos)
    if (!force && cards.value.length > 0 && lastFetchTime.value) {
      const timeSinceLastFetch = Date.now() - lastFetchTime.value.getTime()
      if (timeSinceLastFetch < 30000) {
        return
      }
    }

    isLoading.value = true
    error.value = null

    try {
      cards.value = await cardService.getCards()
      lastFetchTime.value = new Date()
    } catch (err: any) {
      error.value = err.message || 'Error al obtener tarjetas'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener detalles de una tarjeta específica
   */
  async function fetchCard(cardId: number): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const card = await cardService.getCard(cardId)
      
      // Actualizar en la lista si existe
      const index = cards.value.findIndex(c => c.id === cardId)
      if (index !== -1) {
        cards.value[index] = card
      }
      
      // Actualizar tarjeta seleccionada si es la misma
      if (selectedCard.value?.id === cardId) {
        selectedCard.value = card
      }
    } catch (err: any) {
      error.value = err.message || 'Error al obtener detalles de la tarjeta'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Seleccionar una tarjeta
   */
  function selectCard(card: CreditCard | null): void {
    selectedCard.value = card
  }

  /**
   * Seleccionar tarjeta por ID
   */
  function selectCardById(cardId: number): void {
    const card = cards.value.find(c => c.id === cardId)
    selectedCard.value = card || null
  }

  /**
   * Limpiar datos de tarjetas
   */
  function clearCards(): void {
    cards.value = []
    selectedCard.value = null
    error.value = null
    lastFetchTime.value = null
  }

  /**
   * Limpiar error
   */
  function clearError(): void {
    error.value = null
  }

  return {
    // Estado
    cards,
    selectedCard,
    isLoading,
    error,
    lastFetchTime,
    // Getters
    hasCards,
    cardCount,
    activeCards,
    totalCreditLimit,
    totalAvailableCredit,
    totalUsedCredit,
    // Acciones
    fetchCards,
    fetchCard,
    selectCard,
    selectCardById,
    clearCards,
    clearError
  }
})
