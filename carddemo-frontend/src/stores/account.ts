/**
 * Store de cuenta con Pinia
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Account, UpdateAccountData } from '@/types'
import { AccountService } from '@/services/account-service'

const accountService = new AccountService()

export const useAccountStore = defineStore('account', () => {
  // Estado
  const account = ref<Account | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchTime = ref<Date | null>(null)

  // Getters computados
  const hasAccount = computed(() => !!account.value)
  const accountNumber = computed(() => account.value?.account_number || '')
  const fullName = computed(() => {
    if (!account.value) return ''
    return `${account.value.first_name} ${account.value.last_name}`
  })

  /**
   * Obtener información de la cuenta
   */
  async function fetchAccount(force = false): Promise<void> {
    // Evitar fetch duplicado si ya tenemos datos recientes (< 30 segundos)
    if (!force && account.value && lastFetchTime.value) {
      const timeSinceLastFetch = Date.now() - lastFetchTime.value.getTime()
      if (timeSinceLastFetch < 30000) {
        return
      }
    }

    isLoading.value = true
    error.value = null

    try {
      account.value = await accountService.getAccount()
      lastFetchTime.value = new Date()
    } catch (err: any) {
      error.value = err.message || 'Error al obtener información de la cuenta'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Actualizar información de la cuenta
   */
  async function updateAccount(data: UpdateAccountData): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      account.value = await accountService.updateAccount(data)
      lastFetchTime.value = new Date()
    } catch (err: any) {
      error.value = err.message || 'Error al actualizar la cuenta'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Limpiar datos de la cuenta
   */
  function clearAccount(): void {
    account.value = null
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
    account,
    isLoading,
    error,
    lastFetchTime,
    // Getters
    hasAccount,
    accountNumber,
    fullName,
    // Acciones
    fetchAccount,
    updateAccount,
    clearAccount,
    clearError
  }
})
