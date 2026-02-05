/**
 * Servicio de gestión de tarjetas para CardDemo Frontend
 */
import type { CreditCard, CardSummary, CardType } from '@/types'
import { apiClient } from './api-client'

/**
 * Servicio para operaciones relacionadas con tarjetas de crédito
 */
export class CardService {
  /**
   * Obtener todas las tarjetas del usuario
   */
  async getCards(): Promise<CreditCard[]> {
    return await apiClient.getCards()
  }

  /**
   * Obtener detalles de una tarjeta específica
   */
  async getCard(cardId: number): Promise<CreditCard> {
    return await apiClient.getCard(cardId)
  }

  /**
   * Generar resumen de tarjetas para dashboard
   */
  generateCardsSummary(cards: CreditCard[]): CardSummary[] {
    return cards.map(card => ({
      id: card.id,
      last_four_digits: this.extractLastFourDigits(card.masked_card_number),
      card_type: card.card_type,
      available_credit: card.available_credit,
      credit_limit: card.credit_limit,
      utilization_percentage: this.calculateUtilizationPercentage(
        card.credit_limit,
        card.available_credit
      )
    }))
  }

  /**
   * Calcular utilización total de crédito
   */
  calculateTotalUtilization(cards: CreditCard[]): {
    totalLimit: number
    totalAvailable: number
    totalUsed: number
    utilizationPercentage: number
  } {
    const totalLimit = cards.reduce((sum, card) => sum + card.credit_limit, 0)
    const totalAvailable = cards.reduce((sum, card) => sum + card.available_credit, 0)
    const totalUsed = totalLimit - totalAvailable

    return {
      totalLimit,
      totalAvailable,
      totalUsed,
      utilizationPercentage: totalLimit > 0 ? (totalUsed / totalLimit) * 100 : 0
    }
  }

  /**
   * Filtrar tarjetas por estado
   */
  filterCardsByStatus(cards: CreditCard[], status: string): CreditCard[] {
    return cards.filter(card => card.status === status)
  }

  /**
   * Obtener tarjetas activas
   */
  getActiveCards(cards: CreditCard[]): CreditCard[] {
    return this.filterCardsByStatus(cards, 'ACTIVE')
  }

  /**
   * Verificar si una tarjeta está próxima a expirar
   */
  isCardExpiringSoon(card: CreditCard, monthsThreshold: number = 3): boolean {
    const now = new Date()
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1 // getMonth() es 0-indexed

    const expiryDate = new Date(card.expiry_year, card.expiry_month - 1) // month es 0-indexed en Date
    const thresholdDate = new Date()
    thresholdDate.setMonth(thresholdDate.getMonth() + monthsThreshold)

    return expiryDate <= thresholdDate
  }

  /**
   * Obtener tarjetas próximas a expirar
   */
  getExpiringCards(cards: CreditCard[], monthsThreshold: number = 3): CreditCard[] {
    return cards.filter(card => this.isCardExpiringSoon(card, monthsThreshold))
  }

  /**
   * Formatear información de tarjeta para mostrar
   */
  formatCardForDisplay(card: CreditCard): {
    displayName: string
    formattedExpiry: string
    statusDisplay: string
    utilizationDisplay: string
    availableCreditFormatted: string
    creditLimitFormatted: string
  } {
    const displayName = `${this.getCardTypeDisplayName(card.card_type)} ${this.extractLastFourDigits(card.masked_card_number)}`
    
    const formattedExpiry = `${card.expiry_month.toString().padStart(2, '0')}/${card.expiry_year.toString().slice(-2)}`
    
    const statusDisplay = this.getStatusDisplayName(card.status)
    
    const utilizationPercentage = this.calculateUtilizationPercentage(card.credit_limit, card.available_credit)
    const utilizationDisplay = `${utilizationPercentage.toFixed(1)}%`
    
    const availableCreditFormatted = this.formatCurrency(card.available_credit)
    const creditLimitFormatted = this.formatCurrency(card.credit_limit)

    return {
      displayName,
      formattedExpiry,
      statusDisplay,
      utilizationDisplay,
      availableCreditFormatted,
      creditLimitFormatted
    }
  }

  /**
   * Extraer últimos 4 dígitos del número enmascarado
   */
  private extractLastFourDigits(maskedNumber: string): string {
    const match = maskedNumber.match(/\d{4}$/)
    return match ? match[0] : '****'
  }

  /**
   * Calcular porcentaje de utilización
   */
  private calculateUtilizationPercentage(creditLimit: number, availableCredit: number): number {
    if (creditLimit === 0) return 0
    const usedCredit = creditLimit - availableCredit
    return (usedCredit / creditLimit) * 100
  }

  /**
   * Obtener nombre de display para tipo de tarjeta
   */
  private getCardTypeDisplayName(cardType: CardType): string {
    const displayNames: Record<CardType, string> = {
      'VISA': 'Visa',
      'MASTERCARD': 'Mastercard',
      'AMEX': 'American Express',
      'DISCOVER': 'Discover'
    }
    return displayNames[cardType] || cardType
  }

  /**
   * Obtener nombre de display para estado de tarjeta
   */
  private getStatusDisplayName(status: string): string {
    const statusNames: Record<string, string> = {
      'ACTIVE': 'Activa',
      'BLOCKED': 'Bloqueada',
      'EXPIRED': 'Expirada'
    }
    return statusNames[status] || status
  }

  /**
   * Formatear cantidad como moneda
   */
  private formatCurrency(amount: number): string {
    return new Intl.NumberFormat('es-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  /**
   * Obtener color para estado de utilización
   */
  getUtilizationColor(utilizationPercentage: number): string {
    if (utilizationPercentage >= 90) return 'text-red-600'
    if (utilizationPercentage >= 70) return 'text-yellow-600'
    if (utilizationPercentage >= 50) return 'text-blue-600'
    return 'text-green-600'
  }

  /**
   * Obtener color para estado de tarjeta
   */
  getStatusColor(status: string): string {
    const statusColors: Record<string, string> = {
      'ACTIVE': 'text-green-600',
      'BLOCKED': 'text-red-600',
      'EXPIRED': 'text-gray-600'
    }
    return statusColors[status] || 'text-gray-600'
  }

  /**
   * Validar si una tarjeta puede realizar transacciones
   */
  canMakeTransactions(card: CreditCard): boolean {
    return card.status === 'ACTIVE' && 
           card.available_credit > 0 && 
           !this.isCardExpiringSoon(card, 0) // No expirada
  }
}

// Instancia singleton del servicio de tarjetas
export const cardService = new CardService()

// Export por defecto
export default cardService