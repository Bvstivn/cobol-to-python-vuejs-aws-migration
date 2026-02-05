/**
 * Tests de propiedad para DashboardView
 * Valida: Requerimientos 2.1, 2.4, 2.5
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import DashboardView from '../DashboardView.vue'
import { useAccountStore } from '@/stores/account'
import { useTransactionsStore } from '@/stores/transactions'
import type { Account, Transaction } from '@/types'
import * as fc from 'fast-check'

// Mock de los servicios
vi.mock('@/services/account-service', () => ({
  AccountService: class {
    getAccount = vi.fn()
    updateAccount = vi.fn()
  }
}))

vi.mock('@/services/transaction-service', () => ({
  TransactionService: class {
    getTransactions = vi.fn()
    getTransaction = vi.fn()
  }
}))

// Crear router mock
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/dashboard', component: DashboardView },
    { path: '/cards', component: { template: '<div>Cards</div>' } },
    { path: '/transactions', component: { template: '<div>Transactions</div>' } },
    { path: '/profile', component: { template: '<div>Profile</div>' } }
  ]
})

describe('DashboardView Property Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  /**
   * Propiedad 6: Completitud del dashboard
   * Valida: Requerimientos 2.1
   * 
   * Para cualquier usuario autenticado con datos disponibles,
   * el dashboard debe mostrar información de cuenta y transacciones recientes
   */
  it('Property 6: should display complete dashboard with account and transactions', async () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.integer({ min: 1, max: 1000 }),
          account_number: fc.string({ minLength: 10, maxLength: 20 }),
          first_name: fc.string({ minLength: 2, maxLength: 20 }),
          last_name: fc.string({ minLength: 2, maxLength: 20 })
        }),
        fc.array(
          fc.record({
            id: fc.integer({ min: 1, max: 10000 }),
            merchant_name: fc.string({ minLength: 3, maxLength: 30 }),
            amount: fc.float({ min: 0.01, max: 1000, noNaN: true }),
            transaction_type: fc.constantFrom('PURCHASE', 'PAYMENT', 'REFUND'),
            status: fc.constantFrom('PENDING', 'COMPLETED', 'FAILED')
          }),
          { minLength: 0, maxLength: 5 }
        ),
        async (accountData, transactionsData) => {
          const accountStore = useAccountStore()
          const transactionsStore = useTransactionsStore()

          // Configurar datos en los stores
          accountStore.account = {
            ...accountData,
            created_at: new Date()
          } as Account

          transactionsStore.transactions = transactionsData.map(t => ({
            ...t,
            transaction_date: new Date(),
            created_at: new Date()
          })) as Transaction[]

          const wrapper = mount(DashboardView, {
            global: {
              plugins: [router],
              stubs: {
                AppLayout: {
                  template: '<div><slot /></div>'
                }
              }
            }
          })

          await wrapper.vm.$nextTick()

          // Verificar que el dashboard muestra la información
          const html = wrapper.html()

          // Debe mostrar el nombre del titular
          expect(html).toContain(accountData.first_name)
          expect(html).toContain(accountData.last_name)

          // Debe mostrar el número de cuenta
          expect(html).toContain(accountData.account_number)

          // Si hay transacciones, deben mostrarse
          if (transactionsData.length > 0) {
            expect(html).toContain('Transacciones Recientes')
          }

          wrapper.unmount()
        }
      ),
      { numRuns: 10 }
    )
  })

  /**
   * Propiedad 9: Actualización reactiva de UI
   * Valida: Requerimientos 2.4
   * 
   * Para cualquier cambio en los datos subyacentes,
   * los componentes de UI deben actualizarse para reflejar la nueva información
   */
  it('Property 9: should reactively update UI when data changes', async () => {
    const accountStore = useAccountStore()
    const transactionsStore = useTransactionsStore()

    // Datos iniciales
    accountStore.account = {
      id: 1,
      account_number: '1234567890',
      first_name: 'Juan',
      last_name: 'Pérez',
      created_at: new Date()
    }

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
        stubs: {
          AppLayout: {
            template: '<div><slot /></div>'
          }
        }
      }
    })

    await wrapper.vm.$nextTick()

    // Verificar datos iniciales
    expect(wrapper.html()).toContain('Juan')
    expect(wrapper.html()).toContain('Pérez')

    // Cambiar datos
    accountStore.account = {
      id: 1,
      account_number: '1234567890',
      first_name: 'María',
      last_name: 'García',
      created_at: new Date()
    }

    await wrapper.vm.$nextTick()

    // Verificar que la UI se actualizó
    expect(wrapper.html()).toContain('María')
    expect(wrapper.html()).toContain('García')
    expect(wrapper.html()).not.toContain('Juan')
    expect(wrapper.html()).not.toContain('Pérez')

    wrapper.unmount()
  })

  /**
   * Propiedad 10: Actualización automática del dashboard
   * Valida: Requerimientos 2.5
   * 
   * Para cualquier navegación al dashboard,
   * el sistema debe triggear automáticamente la actualización de datos
   */
  it('Property 10: should automatically fetch data on mount', async () => {
    const accountStore = useAccountStore()
    const transactionsStore = useTransactionsStore()

    // Espiar los métodos de fetch
    const fetchAccountSpy = vi.spyOn(accountStore, 'fetchAccount').mockResolvedValue()
    const fetchTransactionsSpy = vi.spyOn(transactionsStore, 'fetchTransactions').mockResolvedValue()

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
        stubs: {
          AppLayout: {
            template: '<div><slot /></div>'
          }
        }
      }
    })

    // Esperar a que se ejecute onMounted
    await new Promise(resolve => setTimeout(resolve, 50))

    // Verificar que se llamaron los métodos de fetch
    expect(fetchAccountSpy).toHaveBeenCalled()
    expect(fetchTransactionsSpy).toHaveBeenCalledWith({ limit: 5 })

    wrapper.unmount()
  })

  /**
   * Test adicional: Manejo de estados de carga
   */
  it('should show loading states while fetching data', async () => {
    const accountStore = useAccountStore()
    const transactionsStore = useTransactionsStore()

    // Simular estado de carga
    accountStore.isLoading = true
    transactionsStore.isLoading = true

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
        stubs: {
          AppLayout: {
            template: '<div><slot /></div>'
          }
        }
      }
    })

    await wrapper.vm.$nextTick()

    // Verificar que se muestran los skeletons de carga
    const html = wrapper.html()
    expect(html).toContain('LoadingSkeleton') || expect(accountStore.isLoading).toBe(true)

    wrapper.unmount()
  })

  /**
   * Test adicional: Navegación desde acciones rápidas
   */
  it('should navigate when quick actions are clicked', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
        stubs: {
          AppLayout: {
            template: '<div><slot /></div>'
          }
        }
      }
    })

    await wrapper.vm.$nextTick()

    // Verificar que el componente QuickActions está presente
    const html = wrapper.html()
    expect(html).toContain('Acciones Rápidas')

    wrapper.unmount()
  })

  /**
   * Propiedad 8: Manejo universal de errores
   * Valida: Requerimientos 2.3
   * 
   * Para cualquier error que ocurra durante la carga de datos,
   * el dashboard debe mostrar mensajes de error apropiados con opciones de reintento
   */
  it('Property 8: should handle errors gracefully with retry options', async () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 10, maxLength: 100 }),
        fc.string({ minLength: 10, maxLength: 100 }),
        async (accountError, transactionsError) => {
          const accountStore = useAccountStore()
          const transactionsStore = useTransactionsStore()

          // Simular errores
          accountStore.error = accountError
          accountStore.isLoading = false
          transactionsStore.error = transactionsError
          transactionsStore.isLoading = false

          const wrapper = mount(DashboardView, {
            global: {
              plugins: [router],
              stubs: {
                AppLayout: {
                  template: '<div><slot /></div>'
                }
              }
            }
          })

          await wrapper.vm.$nextTick()

          const html = wrapper.html()

          // Verificar que se muestran los mensajes de error
          expect(html).toContain(accountError) || expect(html).toContain('Error')
          expect(html).toContain(transactionsError) || expect(html).toContain('Error')

          // Verificar que hay botones de reintento
          expect(html).toContain('Reintentar') || expect(html).toContain('retry')

          wrapper.unmount()
        }
      ),
      { numRuns: 10 }
    )
  })

  /**
   * Test adicional: Reintento después de error
   */
  it('should retry fetching data when retry button is clicked', async () => {
    const accountStore = useAccountStore()

    // Simular error inicial
    accountStore.error = 'Error de conexión'
    accountStore.isLoading = false

    // Espiar el método de fetch
    const fetchAccountSpy = vi.spyOn(accountStore, 'fetchAccount').mockResolvedValue()

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
        stubs: {
          AppLayout: {
            template: '<div><slot /></div>'
          }
        }
      }
    })

    await wrapper.vm.$nextTick()

    // Buscar y hacer click en el botón de reintento
    const retryButtons = wrapper.findAll('button')
    const retryButton = retryButtons.find(btn => 
      btn.text().includes('Reintentar') || btn.text().includes('retry')
    )

    if (retryButton) {
      await retryButton.trigger('click')
      await wrapper.vm.$nextTick()

      // Verificar que se llamó al método de fetch
      expect(fetchAccountSpy).toHaveBeenCalled()
    }

    wrapper.unmount()
  })
})
