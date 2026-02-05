<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        Mi Perfil
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Gestiona tu información personal
      </p>
    </div>

    <!-- Estado de carga -->
    <div v-if="accountStore.isLoading && !accountStore.account" class="space-y-6">
      <LoadingSkeleton type="card" />
      <LoadingSkeleton type="card" />
    </div>

    <!-- Error al cargar -->
    <div v-else-if="accountStore.error && !accountStore.account" class="text-center py-12">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-error-100 dark:bg-error-900/20 mb-4">
        <svg class="h-8 w-8 text-error-600 dark:text-error-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-error-600 dark:text-error-400 mb-4">{{ accountStore.error }}</p>
      <BaseButton variant="secondary" size="sm" @click="loadAccount">
        Reintentar
      </BaseButton>
    </div>

    <!-- Formulario de perfil -->
    <div v-else-if="accountStore.account" class="max-w-3xl">
      <!-- Información de cuenta (solo lectura) -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm mb-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Información de Cuenta
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Número de Cuenta
            </label>
            <p class="text-gray-900 dark:text-gray-100 font-mono">
              {{ accountStore.account.account_number }}
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Fecha de Creación
            </label>
            <p class="text-gray-900 dark:text-gray-100">
              {{ formattedCreatedAt }}
            </p>
          </div>
        </div>
      </div>

      <!-- Formulario editable -->
      <form @submit.prevent="handleSubmit" class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Información Personal
          </h2>
          <BaseButton
            v-if="!isEditing"
            type="button"
            variant="secondary"
            size="sm"
            @click="startEditing"
          >
            Editar
          </BaseButton>
        </div>

        <div class="space-y-4">
          <!-- Nombre -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BaseInput
              v-model="formData.first_name"
              label="Nombre"
              placeholder="Tu nombre"
              :disabled="!isEditing"
              :error="errors.first_name"
              required
            />
            <BaseInput
              v-model="formData.last_name"
              label="Apellido"
              placeholder="Tu apellido"
              :disabled="!isEditing"
              :error="errors.last_name"
              required
            />
          </div>

          <!-- Teléfono -->
          <BaseInput
            v-model="formData.phone"
            type="tel"
            label="Teléfono"
            placeholder="(555) 123-4567"
            :disabled="!isEditing"
            :error="errors.phone"
          />

          <!-- Dirección -->
          <BaseInput
            v-model="formData.address"
            label="Dirección"
            placeholder="Calle y número"
            :disabled="!isEditing"
            :error="errors.address"
          />

          <!-- Ciudad, Estado, Código Postal -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <BaseInput
              v-model="formData.city"
              label="Ciudad"
              placeholder="Ciudad"
              :disabled="!isEditing"
              :error="errors.city"
            />
            <BaseInput
              v-model="formData.state"
              label="Estado"
              placeholder="Estado"
              :disabled="!isEditing"
              :error="errors.state"
            />
            <BaseInput
              v-model="formData.zip_code"
              label="Código Postal"
              placeholder="12345"
              :disabled="!isEditing"
              :error="errors.zip_code"
            />
          </div>
        </div>

        <!-- Botones de acción -->
        <div v-if="isEditing" class="flex items-center justify-end gap-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <BaseButton
            type="button"
            variant="secondary"
            :disabled="isSaving"
            @click="cancelEditing"
          >
            Cancelar
          </BaseButton>
          <BaseButton
            type="submit"
            variant="primary"
            :disabled="isSaving || !hasChanges"
          >
            <span v-if="isSaving">Guardando...</span>
            <span v-else>Guardar Cambios</span>
          </BaseButton>
        </div>

        <!-- Mensaje de éxito -->
        <div v-if="showSuccessMessage" class="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div class="flex items-center">
            <svg class="h-5 w-5 text-green-600 dark:text-green-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <p class="text-sm text-green-600 dark:text-green-400">
              Perfil actualizado exitosamente
            </p>
          </div>
        </div>

        <!-- Mensaje de error -->
        <div v-if="accountStore.error && isEditing" class="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div class="flex items-center">
            <svg class="h-5 w-5 text-red-600 dark:text-red-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm text-red-600 dark:text-red-400">
              {{ accountStore.error }}
            </p>
          </div>
        </div>
      </form>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { AppLayout } from '@/components/layout'
import { BaseInput, BaseButton } from '@/components/base'
import { LoadingSkeleton } from '@/components/loading'
import { useAccountStore } from '@/stores/account'
import type { UpdateAccountData } from '@/types'

const accountStore = useAccountStore()

const isEditing = ref(false)
const isSaving = ref(false)
const showSuccessMessage = ref(false)

// Usar un tipo interno que garantiza strings (no undefined)
interface FormDataInternal {
  first_name: string
  last_name: string
  phone: string
  address: string
  city: string
  state: string
  zip_code: string
}

const formData = ref<FormDataInternal>({
  first_name: '',
  last_name: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  zip_code: ''
})

const errors = ref<Record<string, string>>({})

const formattedCreatedAt = computed(() => {
  if (!accountStore.account) return ''
  return new Date(accountStore.account.created_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const hasChanges = computed(() => {
  if (!accountStore.account) return false
  
  return (
    formData.value.first_name !== accountStore.account.first_name ||
    formData.value.last_name !== accountStore.account.last_name ||
    formData.value.phone !== (accountStore.account.phone || '') ||
    formData.value.address !== (accountStore.account.address || '') ||
    formData.value.city !== (accountStore.account.city || '') ||
    formData.value.state !== (accountStore.account.state || '') ||
    formData.value.zip_code !== (accountStore.account.zip_code || '')
  )
})

onMounted(async () => {
  await loadAccount()
})

watch(() => accountStore.account, (account) => {
  if (account) {
    resetFormData()
  }
}, { immediate: true })

async function loadAccount() {
  try {
    await accountStore.fetchAccount()
  } catch (error) {
    console.error('Error loading account:', error)
  }
}

function resetFormData() {
  if (!accountStore.account) return
  
  formData.value = {
    first_name: accountStore.account.first_name,
    last_name: accountStore.account.last_name,
    phone: accountStore.account.phone || '',
    address: accountStore.account.address || '',
    city: accountStore.account.city || '',
    state: accountStore.account.state || '',
    zip_code: accountStore.account.zip_code || ''
  }
}

function startEditing() {
  isEditing.value = true
  showSuccessMessage.value = false
  accountStore.clearError()
}

function cancelEditing() {
  isEditing.value = false
  resetFormData()
  errors.value = {}
  accountStore.clearError()
}

function validateForm(): boolean {
  errors.value = {}
  let isValid = true

  // Validar nombre
  if (!formData.value.first_name || formData.value.first_name.trim().length < 2) {
    errors.value.first_name = 'El nombre debe tener al menos 2 caracteres'
    isValid = false
  }

  // Validar apellido
  if (!formData.value.last_name || formData.value.last_name.trim().length < 2) {
    errors.value.last_name = 'El apellido debe tener al menos 2 caracteres'
    isValid = false
  }

  // Validar teléfono (opcional pero si se proporciona debe ser válido)
  if (formData.value.phone && formData.value.phone.trim()) {
    const phoneRegex = /^[\d\s\-\(\)]+$/
    if (!phoneRegex.test(formData.value.phone)) {
      errors.value.phone = 'Formato de teléfono inválido'
      isValid = false
    }
  }

  // Validar código postal (opcional pero si se proporciona debe ser válido)
  if (formData.value.zip_code && formData.value.zip_code.trim()) {
    const zipRegex = /^\d{5}(-\d{4})?$/
    if (!zipRegex.test(formData.value.zip_code)) {
      errors.value.zip_code = 'Código postal inválido (formato: 12345 o 12345-6789)'
      isValid = false
    }
  }

  return isValid
}

async function handleSubmit() {
  if (!validateForm()) {
    return
  }

  isSaving.value = true
  showSuccessMessage.value = false
  accountStore.clearError()

  try {
    // Preparar datos para enviar (solo campos no vacíos)
    const updateData: UpdateAccountData = {}
    
    if (formData.value.first_name) updateData.first_name = formData.value.first_name.trim()
    if (formData.value.last_name) updateData.last_name = formData.value.last_name.trim()
    if (formData.value.phone) updateData.phone = formData.value.phone.trim()
    if (formData.value.address) updateData.address = formData.value.address.trim()
    if (formData.value.city) updateData.city = formData.value.city.trim()
    if (formData.value.state) updateData.state = formData.value.state.trim()
    if (formData.value.zip_code) updateData.zip_code = formData.value.zip_code.trim()

    await accountStore.updateAccount(updateData)
    
    isEditing.value = false
    showSuccessMessage.value = true
    
    // Ocultar mensaje de éxito después de 5 segundos
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 5000)
  } catch (error: any) {
    console.error('Error updating account:', error)
    
    // Manejar errores específicos por campo si la API los proporciona
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      
      // Si el error es un array de errores de validación
      if (Array.isArray(detail)) {
        detail.forEach((err: any) => {
          if (err.loc && err.loc.length > 1) {
            const fieldName = err.loc[1]
            errors.value[fieldName] = err.msg || 'Error de validación'
          }
        })
      } else if (typeof detail === 'string') {
        // Error general
        accountStore.error = detail
      }
    }
  } finally {
    isSaving.value = false
  }
}
</script>
