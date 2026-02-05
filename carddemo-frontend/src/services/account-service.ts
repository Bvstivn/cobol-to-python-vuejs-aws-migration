/**
 * Servicio de gestión de cuentas para CardDemo Frontend
 */
import type { Account, UpdateAccountData } from '@/types'
import { apiClient } from './api-client'

/**
 * Servicio para operaciones relacionadas con cuentas de usuario
 */
export class AccountService {
  /**
   * Obtener información de la cuenta del usuario actual
   */
  async getAccount(): Promise<Account> {
    return await apiClient.getAccount()
  }

  /**
   * Actualizar información de la cuenta del usuario actual
   */
  async updateAccount(data: UpdateAccountData): Promise<Account> {
    return await apiClient.updateAccount(data)
  }

  /**
   * Validar datos de actualización de cuenta
   */
  validateAccountData(data: UpdateAccountData): { isValid: boolean; errors: Record<string, string> } {
    const errors: Record<string, string> = {}

    // Validar nombre
    if (data.first_name !== undefined) {
      if (!data.first_name || data.first_name.trim().length === 0) {
        errors.first_name = 'El nombre es requerido'
      } else if (data.first_name.length > 50) {
        errors.first_name = 'El nombre no puede exceder 50 caracteres'
      }
    }

    // Validar apellido
    if (data.last_name !== undefined) {
      if (!data.last_name || data.last_name.trim().length === 0) {
        errors.last_name = 'El apellido es requerido'
      } else if (data.last_name.length > 50) {
        errors.last_name = 'El apellido no puede exceder 50 caracteres'
      }
    }

    // Validar teléfono
    if (data.phone !== undefined && data.phone) {
      const phoneRegex = /^\+?[\d\s\-\(\)]{10,20}$/
      if (!phoneRegex.test(data.phone)) {
        errors.phone = 'El formato del teléfono no es válido'
      }
    }

    // Validar estado (código de 2 letras)
    if (data.state !== undefined && data.state) {
      if (data.state.length !== 2) {
        errors.state = 'El estado debe ser un código de 2 letras'
      }
    }

    // Validar código postal
    if (data.zip_code !== undefined && data.zip_code) {
      const zipRegex = /^\d{5}(-\d{4})?$/
      if (!zipRegex.test(data.zip_code)) {
        errors.zip_code = 'El código postal debe tener formato 12345 o 12345-6789'
      }
    }

    // Validar dirección
    if (data.address !== undefined && data.address) {
      if (data.address.length < 5) {
        errors.address = 'La dirección debe tener al menos 5 caracteres'
      } else if (data.address.length > 200) {
        errors.address = 'La dirección no puede exceder 200 caracteres'
      }
    }

    // Validar ciudad
    if (data.city !== undefined && data.city) {
      if (data.city.length < 2) {
        errors.city = 'La ciudad debe tener al menos 2 caracteres'
      } else if (data.city.length > 50) {
        errors.city = 'La ciudad no puede exceder 50 caracteres'
      }
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * Formatear información de cuenta para mostrar
   */
  formatAccountForDisplay(account: Account): {
    fullName: string
    formattedPhone?: string
    fullAddress?: string
    accountAge: string
  } {
    const fullName = `${account.first_name} ${account.last_name}`
    
    const formattedPhone = account.phone 
      ? this.formatPhoneNumber(account.phone)
      : undefined

    const fullAddress = this.buildFullAddress(account)
    
    const accountAge = this.calculateAccountAge(account.created_at)

    return {
      fullName,
      formattedPhone,
      fullAddress,
      accountAge
    }
  }

  /**
   * Formatear número de teléfono
   */
  private formatPhoneNumber(phone: string): string {
    // Remover caracteres no numéricos
    const digits = phone.replace(/\D/g, '')
    
    // Formatear según longitud
    if (digits.length === 10) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
    } else if (digits.length === 11 && digits[0] === '1') {
      return `+1 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`
    }
    
    return phone // Devolver original si no se puede formatear
  }

  /**
   * Construir dirección completa
   */
  private buildFullAddress(account: Account): string | undefined {
    const parts = [
      account.address,
      account.city,
      account.state,
      account.zip_code
    ].filter(Boolean)

    return parts.length > 0 ? parts.join(', ') : undefined
  }

  /**
   * Calcular antigüedad de la cuenta
   */
  private calculateAccountAge(createdAt: Date): string {
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - createdAt.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays < 30) {
      return `${diffDays} día${diffDays !== 1 ? 's' : ''}`
    } else if (diffDays < 365) {
      const months = Math.floor(diffDays / 30)
      return `${months} mes${months !== 1 ? 'es' : ''}`
    } else {
      const years = Math.floor(diffDays / 365)
      return `${years} año${years !== 1 ? 's' : ''}`
    }
  }
}

// Instancia singleton del servicio de cuentas
export const accountService = new AccountService()

// Export por defecto
export default accountService