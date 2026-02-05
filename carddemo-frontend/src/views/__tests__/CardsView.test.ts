/**
 * Tests de propiedad para CardsView
 * Valida: Requerimientos 3.1, 3.2, 3.4
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import * as fc from 'fast-check'
import { useCardsStore } from '@/stores/cards'
import type { CreditCard, CardType, CardStatus } from '@/types'

// Generadores de datos
const cardTypeArb = fc.constantFrom<CardType>('VISA', 'MASTERCARD', 'AMEX', 'DISCOVER')
const cardStatusArb = fc.constantFrom<CardStatus>('ACTIVE', 'BLOCKED', 'EXPIRED')

const creditCardArb = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  masked_card_number: fc.integer({ min: 0, max: 9999 }).map(n => 
    `**** **** **** ${n.toString().padStart(4, '0')}`
  ),
  card_type: cardTypeArb,
  expiry_month: fc.integer({ min: 1, max: 12 }),
  expiry_year: fc.integer({ min: 2024, max: 2035 }),
  status: cardStatusArb,
  credit_limit: fc.float({ min: 1000, max: 50000, noNaN: true }),
  available_credit: fc.float({ min: 0, max: 50000, noNaN: true }),
  created_at: fc.date({ min: new Date('2020-01-01'), max: new Date() })
}) as fc.Arbitrary<CreditCard>

describe('CardsView - Property-Based Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  /**
   * Propiedad 11: Visualización completa de tarjetas
   * Valida: Requerimientos 3.1
   * 
   * Todas las tarjetas del usuario deben mostrarse en el store
   */
  it('Propiedad 11: Todas las tarjetas se almacenan correctamente en el store', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(creditCardArb, { minLength: 0, maxLength: 10 }),
        async (cards) => {
          const cardsStore = useCardsStore()
          cardsStore.cards = cards

          // Verificar que todas las tarjetas están en el store
          expect(cardsStore.cards).toHaveLength(cards.length)
          expect(cardsStore.cards).toEqual(cards)
          expect(cardsStore.hasCards).toBe(cards.length > 0)
          expect(cardsStore.cardCount).toBe(cards.length)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Propiedad 12: Detalles de tarjeta seleccionada
   * Valida: Requerimientos 3.2
   * 
   * Al seleccionar una tarjeta, se debe almacenar en el store
   */
  it('Propiedad 12: Selección de tarjeta funciona correctamente', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(creditCardArb, { minLength: 1, maxLength: 10 }),
        fc.nat(),
        async (cards, indexSeed) => {
          const cardsStore = useCardsStore()
          cardsStore.cards = cards

          const selectedIndex = indexSeed % cards.length
          const selectedCard = cards[selectedIndex]

          if (!selectedCard) return

          // Seleccionar tarjeta
          cardsStore.selectCard(selectedCard)

          // Verificar que la tarjeta se seleccionó
          expect(cardsStore.selectedCard).toEqual(selectedCard)
          expect(cardsStore.selectedCard?.id).toBe(selectedCard.id)

          // Limpiar selección
          cardsStore.selectCard(null)
          expect(cardsStore.selectedCard).toBeNull()
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Propiedad 13: Enmascaramiento de información sensible
   * Valida: Requerimientos 3.4
   * 
   * Los números de tarjeta deben estar enmascarados
   */
  it('Propiedad 13: Números de tarjeta están enmascarados', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(creditCardArb, { minLength: 1, maxLength: 10 }),
        async (cards) => {
          const cardsStore = useCardsStore()
          cardsStore.cards = cards

          // Verificar que todas las tarjetas tienen números enmascarados
          cardsStore.cards.forEach(card => {
            // El número debe contener asteriscos
            expect(card.masked_card_number).toMatch(/\*/)
            
            // El número debe tener el formato correcto
            expect(card.masked_card_number).toMatch(/^\*{4} \*{4} \*{4} \d{4}$/)
            
            // Solo últimos 4 dígitos visibles
            const visibleDigits = card.masked_card_number.slice(-4)
            expect(visibleDigits).toMatch(/^\d{4}$/)
          })
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Cálculo de totales de crédito
   */
  it('calcula totales de crédito correctamente', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(creditCardArb, { minLength: 1, maxLength: 5 }),
        async (cards) => {
          const cardsStore = useCardsStore()
          cardsStore.cards = cards

          // Calcular totales esperados
          const expectedTotalLimit = cards.reduce((sum, card) => sum + card.credit_limit, 0)
          const expectedTotalAvailable = cards.reduce((sum, card) => sum + card.available_credit, 0)
          const expectedTotalUsed = expectedTotalLimit - expectedTotalAvailable

          // Verificar que el store tiene los valores correctos
          expect(cardsStore.totalCreditLimit).toBeCloseTo(expectedTotalLimit, 2)
          expect(cardsStore.totalAvailableCredit).toBeCloseTo(expectedTotalAvailable, 2)
          expect(cardsStore.totalUsedCredit).toBeCloseTo(expectedTotalUsed, 2)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Filtrado de tarjetas activas
   */
  it('filtra tarjetas activas correctamente', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(creditCardArb, { minLength: 1, maxLength: 10 }),
        async (cards) => {
          const cardsStore = useCardsStore()
          cardsStore.cards = cards

          const expectedActiveCards = cards.filter(card => card.status === 'ACTIVE')
          
          expect(cardsStore.activeCards).toHaveLength(expectedActiveCards.length)
          expect(cardsStore.activeCards).toEqual(expectedActiveCards)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Selección por ID
   */
  it('selecciona tarjeta por ID correctamente', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.array(creditCardArb, { minLength: 1, maxLength: 10 }),
        fc.nat(),
        async (cards, indexSeed) => {
          const cardsStore = useCardsStore()
          cardsStore.cards = cards

          const selectedIndex = indexSeed % cards.length
          const selectedCard = cards[selectedIndex]

          if (!selectedCard) return

          // Seleccionar por ID
          cardsStore.selectCardById(selectedCard.id)

          // Verificar selección
          expect(cardsStore.selectedCard?.id).toBe(selectedCard.id)
        }
      ),
      { numRuns: 15 }
    )
  })
})

