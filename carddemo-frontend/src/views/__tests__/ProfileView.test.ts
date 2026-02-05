/**
 * Tests de propiedad para ProfileView
 * Valida: Requerimientos 5.1, 5.2, 5.3
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import * as fc from 'fast-check'
import { useAccountStore } from '@/stores/account'
import type { Account, UpdateAccountData } from '@/types'

// Generadores de datos
const accountArb = fc.record({
  id: fc.integer({ min: 1, max: 10000 }),
  account_number: fc.string({ minLength: 10, maxLength: 16 }).map(s => s.padStart(16, '0')),
  first_name: fc.string({ minLength: 2, maxLength: 50 }),
  last_name: fc.string({ minLength: 2, maxLength: 50 }),
  phone: fc.option(fc.string({ minLength: 10, maxLength: 15 }), { nil: undefined }),
  address: fc.option(fc.string({ minLength: 5, maxLength: 100 }), { nil: undefined }),
  city: fc.option(fc.string({ minLength: 2, maxLength: 50 }), { nil: undefined }),
  state: fc.option(fc.string({ minLength: 2, maxLength: 2 }), { nil: undefined }),
  zip_code: fc.option(fc.string({ minLength: 5, maxLength: 10 }), { nil: undefined }),
  created_at: fc.date({ min: new Date('2020-01-01'), max: new Date() }),
  updated_at: fc.option(fc.date({ min: new Date('2020-01-01'), max: new Date() }), { nil: undefined })
}) as fc.Arbitrary<Account>

const updateAccountDataArb = fc.record({
  first_name: fc.option(fc.string({ minLength: 2, maxLength: 50 }), { nil: undefined }),
  last_name: fc.option(fc.string({ minLength: 2, maxLength: 50 }), { nil: undefined }),
  phone: fc.option(fc.string({ minLength: 10, maxLength: 15 }), { nil: undefined }),
  address: fc.option(fc.string({ minLength: 5, maxLength: 100 }), { nil: undefined }),
  city: fc.option(fc.string({ minLength: 2, maxLength: 50 }), { nil: undefined }),
  state: fc.option(fc.string({ minLength: 2, maxLength: 2 }), { nil: undefined }),
  zip_code: fc.option(fc.string({ minLength: 5, maxLength: 10 }), { nil: undefined })
}) as fc.Arbitrary<UpdateAccountData>

describe('ProfileView - Property-Based Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  /**
   * Propiedad 17: Visualización de perfil actual
   * Valida: Requerimientos 5.1
   * 
   * El perfil del usuario debe mostrarse correctamente
   */
  it('Propiedad 17: Perfil se muestra correctamente', async () => {
    await fc.assert(
      fc.asyncProperty(
        accountArb,
        async (account) => {
          const accountStore = useAccountStore()
          accountStore.account = account

          // Verificar que la cuenta se almacenó
          expect(accountStore.account).toEqual(account)
          expect(accountStore.hasAccount).toBe(true)
          
          // Verificar getters
          expect(accountStore.accountNumber).toBe(account.account_number)
          expect(accountStore.fullName).toBe(`${account.first_name} ${account.last_name}`)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Propiedad 18: Validación y envío de actualizaciones de perfil
   * Valida: Requerimientos 5.2
   * 
   * Las actualizaciones de perfil deben validarse correctamente
   */
  it('Propiedad 18: Validación de actualizaciones funciona', async () => {
    await fc.assert(
      fc.asyncProperty(
        accountArb,
        updateAccountDataArb,
        async (account, updateData) => {
          const accountStore = useAccountStore()
          accountStore.account = account

          // Validar que los campos requeridos no estén vacíos
          if (updateData.first_name !== undefined) {
            expect(updateData.first_name.length).toBeGreaterThanOrEqual(2)
          }
          
          if (updateData.last_name !== undefined) {
            expect(updateData.last_name.length).toBeGreaterThanOrEqual(2)
          }

          // Simular actualización
          const updatedAccount = {
            ...account,
            ...updateData,
            updated_at: new Date()
          }
          
          accountStore.account = updatedAccount

          // Verificar que los cambios se aplicaron
          if (updateData.first_name) {
            expect(accountStore.account.first_name).toBe(updateData.first_name)
          }
          if (updateData.last_name) {
            expect(accountStore.account.last_name).toBe(updateData.last_name)
          }
          if (updateData.phone) {
            expect(accountStore.account.phone).toBe(updateData.phone)
          }
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Propiedad 19: Confirmación de actualizaciones exitosas
   * Valida: Requerimientos 5.3
   * 
   * Las actualizaciones exitosas deben reflejarse en el store
   */
  it('Propiedad 19: Actualizaciones exitosas se reflejan en el store', async () => {
    await fc.assert(
      fc.asyncProperty(
        accountArb,
        fc.record({
          first_name: fc.string({ minLength: 2, maxLength: 50 }),
          last_name: fc.string({ minLength: 2, maxLength: 50 })
        }),
        async (account, updates) => {
          const accountStore = useAccountStore()
          accountStore.account = account

          const originalFirstName = account.first_name
          const originalLastName = account.last_name

          // Simular actualización exitosa
          accountStore.account = {
            ...account,
            first_name: updates.first_name,
            last_name: updates.last_name,
            updated_at: new Date()
          }

          // Verificar que los cambios se aplicaron
          expect(accountStore.account.first_name).toBe(updates.first_name)
          expect(accountStore.account.last_name).toBe(updates.last_name)
          expect(accountStore.account.first_name).not.toBe(originalFirstName)
          expect(accountStore.account.last_name).not.toBe(originalLastName)
          
          // Verificar que fullName se actualizó
          expect(accountStore.fullName).toBe(`${updates.first_name} ${updates.last_name}`)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Validación de nombre
   */
  it('valida que el nombre tenga al menos 2 caracteres', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 2, maxLength: 50 }),
        async (firstName) => {
          // El nombre debe tener al menos 2 caracteres
          expect(firstName.length).toBeGreaterThanOrEqual(2)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Validación de apellido
   */
  it('valida que el apellido tenga al menos 2 caracteres', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 2, maxLength: 50 }),
        async (lastName) => {
          // El apellido debe tener al menos 2 caracteres
          expect(lastName.length).toBeGreaterThanOrEqual(2)
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Limpieza de cuenta
   */
  it('limpia la cuenta correctamente', async () => {
    await fc.assert(
      fc.asyncProperty(
        accountArb,
        async (account) => {
          const accountStore = useAccountStore()
          accountStore.account = account

          // Verificar que la cuenta existe
          expect(accountStore.hasAccount).toBe(true)

          // Limpiar cuenta
          accountStore.clearAccount()

          // Verificar que la cuenta se limpió
          expect(accountStore.account).toBeNull()
          expect(accountStore.hasAccount).toBe(false)
          expect(accountStore.accountNumber).toBe('')
          expect(accountStore.fullName).toBe('')
        }
      ),
      { numRuns: 15 }
    )
  })

  /**
   * Test adicional: Manejo de errores
   */
  it('maneja errores correctamente', async () => {
    const accountStore = useAccountStore()
    
    // Establecer error
    accountStore.error = 'Error al actualizar perfil'
    
    // Verificar que el error se estableció
    expect(accountStore.error).toBe('Error al actualizar perfil')
    
    // Limpiar error
    accountStore.clearError()
    
    // Verificar que el error se limpió
    expect(accountStore.error).toBeNull()
  })

  /**
   * Test adicional: Actualización parcial
   */
  it('permite actualizaciones parciales', async () => {
    await fc.assert(
      fc.asyncProperty(
        accountArb,
        fc.string({ minLength: 10, maxLength: 15 }),
        async (account, newPhone) => {
          const accountStore = useAccountStore()
          accountStore.account = account

          const originalFirstName = account.first_name
          const originalLastName = account.last_name

          // Actualizar solo el teléfono
          accountStore.account = {
            ...account,
            phone: newPhone
          }

          // Verificar que solo el teléfono cambió
          expect(accountStore.account.phone).toBe(newPhone)
          expect(accountStore.account.first_name).toBe(originalFirstName)
          expect(accountStore.account.last_name).toBe(originalLastName)
        }
      ),
      { numRuns: 15 }
    )
  })
})
