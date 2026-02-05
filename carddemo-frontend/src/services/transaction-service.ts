/**
 * Servicio de gestión de transacciones para CardDemo Frontend
 */
import type { 
  Transaction, 
  TransactionFilters, 
  TransactionResponse, 
  TransactionSummary,
  TransactionCategory,
  TransactionType,
  TransactionStatus
} from '@/types'
import { apiClient } from './api-client'

/**
 * Servicio para operaciones relacionadas con transacciones
 */
export class TransactionService {
  /**
   * Obtener transacciones con filtros opcionales
   */
  async getTransactions(filters?: TransactionFilters): Promise<TransactionResponse> {
    return await apiClient.getTransactions(filters)
  }

  /**
   * Obtener detalles de una transacción específica
   */
  async getTransaction(transactionId: number): Promise<Transaction> {
    return await apiClient.getTransaction(transactionId)
  }

  /**
   * Generar resumen de transacciones para dashboard
   */
  generateTransactionSummary(transactions: Transaction[]): TransactionSummary {
    const now = new Date()
    const currentMonth = now.getMonth()
    const currentYear = now.getFullYear()

    // Filtrar transacciones del mes actual
    const thisMonthTransactions = transactions.filter(transaction => {
      const transactionDate = new Date(transaction.transaction_date)
      return transactionDate.getMonth() === currentMonth && 
             transactionDate.getFullYear() === currentYear
    })

    // Calcular total gastado este mes (solo compras)
    const totalSpentThisMonth = thisMonthTransactions
      .filter(t => t.transaction_type === 'PURCHASE')
      .reduce((sum, t) => sum + t.amount, 0)

    // Obtener transacciones recientes (últimas 5)
    const recentTransactions = [...transactions]
      .sort((a, b) => new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime())
      .slice(0, 5)

    // Encontrar transacción más grande
    const largestTransaction = transactions.reduce((largest, current) => {
      return current.amount > (largest?.amount || 0) ? current : largest
    }, null as Transaction | null)

    return {
      recent_transactions: recentTransactions,
      total_spent_this_month: totalSpentThisMonth,
      transaction_count_this_month: thisMonthTransactions.length,
      largest_transaction: largestTransaction
    }
  }

  /**
   * Categorizar transacciones por comerciante
   */
  categorizeTransactions(transactions: Transaction[]): TransactionCategory[] {
    const categoryMap = new Map<string, { total: number; count: number }>()

    // Agrupar por nombre de comerciante
    transactions.forEach(transaction => {
      const category = this.categorizeByMerchant(transaction.merchant_name)
      const existing = categoryMap.get(category) || { total: 0, count: 0 }
      
      categoryMap.set(category, {
        total: existing.total + transaction.amount,
        count: existing.count + 1
      })
    })

    // Calcular total para porcentajes
    const totalAmount = Array.from(categoryMap.values())
      .reduce((sum, cat) => sum + cat.total, 0)

    // Convertir a array y calcular porcentajes
    return Array.from(categoryMap.entries())
      .map(([name, data]) => ({
        name,
        total_amount: data.total,
        transaction_count: data.count,
        percentage: totalAmount > 0 ? (data.total / totalAmount) * 100 : 0
      }))
      .sort((a, b) => b.total_amount - a.total_amount) // Ordenar por monto descendente
  }

  /**
   * Filtrar transacciones por rango de fechas
   */
  filterByDateRange(transactions: Transaction[], startDate: Date, endDate: Date): Transaction[] {
    return transactions.filter(transaction => {
      const transactionDate = new Date(transaction.transaction_date)
      return transactionDate >= startDate && transactionDate <= endDate
    })
  }

  /**
   * Filtrar transacciones por tipo
   */
  filterByType(transactions: Transaction[], type: TransactionType): Transaction[] {
    return transactions.filter(transaction => transaction.transaction_type === type)
  }

  /**
   * Filtrar transacciones por rango de monto
   */
  filterByAmountRange(transactions: Transaction[], minAmount: number, maxAmount: number): Transaction[] {
    return transactions.filter(transaction => 
      transaction.amount >= minAmount && transaction.amount <= maxAmount
    )
  }

  /**
   * Buscar transacciones por texto
   */
  searchTransactions(transactions: Transaction[], searchTerm: string): Transaction[] {
    const term = searchTerm.toLowerCase()
    return transactions.filter(transaction =>
      transaction.merchant_name.toLowerCase().includes(term) ||
      transaction.description?.toLowerCase().includes(term) ||
      transaction.amount.toString().includes(term)
    )
  }

  /**
   * Formatear transacción para mostrar
   */
  formatTransactionForDisplay(transaction: Transaction): {
    formattedDate: string
    formattedAmount: string
    typeDisplay: string
    statusDisplay: string
    amountColor: string
    statusColor: string
  } {
    const formattedDate = this.formatDate(transaction.transaction_date)
    const formattedAmount = this.formatCurrency(transaction.amount)
    const typeDisplay = this.getTypeDisplayName(transaction.transaction_type)
    const statusDisplay = this.getStatusDisplayName(transaction.status)
    const amountColor = this.getAmountColor(transaction.transaction_type)
    const statusColor = this.getStatusColor(transaction.status)

    return {
      formattedDate,
      formattedAmount,
      typeDisplay,
      statusDisplay,
      amountColor,
      statusColor
    }
  }

  /**
   * Validar filtros de transacciones
   */
  validateFilters(filters: TransactionFilters): { isValid: boolean; errors: Record<string, string> } {
    const errors: Record<string, string> = {}

    // Validar rango de fechas
    if (filters.start_date && filters.end_date) {
      const startDate = new Date(filters.start_date)
      const endDate = new Date(filters.end_date)
      
      if (startDate > endDate) {
        errors.dateRange = 'La fecha de inicio debe ser anterior a la fecha de fin'
      }
    }

    // Validar rango de montos
    if (filters.min_amount !== undefined && filters.max_amount !== undefined) {
      if (filters.min_amount > filters.max_amount) {
        errors.amountRange = 'El monto mínimo debe ser menor al monto máximo'
      }
    }

    // Validar montos negativos
    if (filters.min_amount !== undefined && filters.min_amount < 0) {
      errors.minAmount = 'El monto mínimo no puede ser negativo'
    }

    if (filters.max_amount !== undefined && filters.max_amount < 0) {
      errors.maxAmount = 'El monto máximo no puede ser negativo'
    }

    // Validar límites de paginación
    if (filters.limit !== undefined && (filters.limit < 1 || filters.limit > 100)) {
      errors.limit = 'El límite debe estar entre 1 y 100'
    }

    if (filters.offset !== undefined && filters.offset < 0) {
      errors.offset = 'El offset no puede ser negativo'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * Categorizar por nombre de comerciante
   */
  private categorizeByMerchant(merchantName: string): string {
    const merchant = merchantName.toLowerCase()
    
    // Categorías comunes
    if (merchant.includes('amazon') || merchant.includes('ebay') || merchant.includes('shop')) {
      return 'Compras en línea'
    }
    if (merchant.includes('restaurant') || merchant.includes('food') || merchant.includes('cafe')) {
      return 'Restaurantes'
    }
    if (merchant.includes('gas') || merchant.includes('fuel') || merchant.includes('shell') || merchant.includes('exxon')) {
      return 'Gasolina'
    }
    if (merchant.includes('grocery') || merchant.includes('market') || merchant.includes('walmart')) {
      return 'Supermercados'
    }
    if (merchant.includes('pharmacy') || merchant.includes('cvs') || merchant.includes('walgreens')) {
      return 'Farmacia'
    }
    if (merchant.includes('hotel') || merchant.includes('airline') || merchant.includes('travel')) {
      return 'Viajes'
    }
    
    return 'Otros'
  }

  /**
   * Formatear fecha
   */
  private formatDate(date: Date): string {
    return new Intl.DateTimeFormat('es-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(new Date(date))
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
   * Obtener nombre de display para tipo de transacción
   */
  private getTypeDisplayName(type: TransactionType): string {
    const typeNames: Record<TransactionType, string> = {
      'PURCHASE': 'Compra',
      'PAYMENT': 'Pago',
      'REFUND': 'Reembolso'
    }
    return typeNames[type] || type
  }

  /**
   * Obtener nombre de display para estado de transacción
   */
  private getStatusDisplayName(status: TransactionStatus): string {
    const statusNames: Record<TransactionStatus, string> = {
      'PENDING': 'Pendiente',
      'COMPLETED': 'Completada',
      'FAILED': 'Fallida'
    }
    return statusNames[status] || status
  }

  /**
   * Obtener color para monto según tipo
   */
  private getAmountColor(type: TransactionType): string {
    const colors: Record<TransactionType, string> = {
      'PURCHASE': 'text-red-600', // Gasto
      'PAYMENT': 'text-blue-600', // Pago
      'REFUND': 'text-green-600'  // Reembolso
    }
    return colors[type] || 'text-gray-600'
  }

  /**
   * Obtener color para estado
   */
  private getStatusColor(status: TransactionStatus): string {
    const colors: Record<TransactionStatus, string> = {
      'PENDING': 'text-yellow-600',
      'COMPLETED': 'text-green-600',
      'FAILED': 'text-red-600'
    }
    return colors[status] || 'text-gray-600'
  }
}

// Instancia singleton del servicio de transacciones
export const transactionService = new TransactionService()

// Export por defecto
export default transactionService