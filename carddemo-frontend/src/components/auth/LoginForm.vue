<template>
  <div class="w-full max-w-md mx-auto">
    <BaseCard padding="lg">
      <template #header>
        <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100">
          Iniciar Sesión
        </h2>
      </template>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <BaseInput
          v-model="formData.username"
          type="text"
          label="Usuario"
          placeholder="Ingresa tu usuario"
          :error="errors.username"
          :disabled="isLoading"
          required
          @blur="validateField('username')"
        />

        <BaseInput
          v-model="formData.password"
          type="password"
          label="Contraseña"
          placeholder="Ingresa tu contraseña"
          :error="errors.password"
          :disabled="isLoading"
          required
          @blur="validateField('password')"
        />

        <div v-if="generalError" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p class="text-sm text-red-600 dark:text-red-400">
            {{ generalError }}
          </p>
        </div>

        <BaseButton
          type="submit"
          variant="primary"
          size="lg"
          :loading="isLoading"
          :disabled="isLoading || !isFormValid"
          full-width
        >
          {{ isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
        </BaseButton>
      </form>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { BaseCard, BaseInput, BaseButton } from '@/components/base'

const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const formData = ref({
  username: '',
  password: ''
})

const errors = ref({
  username: '',
  password: ''
})

const generalError = ref('')
const isLoading = ref(false)

const isFormValid = computed(() => {
  return formData.value.username.length > 0 &&
         formData.value.password.length > 0 &&
         !errors.value.username &&
         !errors.value.password
})

const validateField = (field: 'username' | 'password') => {
  if (field === 'username') {
    if (!formData.value.username) {
      errors.value.username = 'El usuario es requerido'
    } else if (formData.value.username.length < 3) {
      errors.value.username = 'El usuario debe tener al menos 3 caracteres'
    } else {
      errors.value.username = ''
    }
  } else if (field === 'password') {
    if (!formData.value.password) {
      errors.value.password = 'La contraseña es requerida'
    } else if (formData.value.password.length < 4) {
      errors.value.password = 'La contraseña debe tener al menos 4 caracteres'
    } else {
      errors.value.password = ''
    }
  }
}

const handleSubmit = async () => {
  // Validar todos los campos
  validateField('username')
  validateField('password')

  if (!isFormValid.value) {
    return
  }

  isLoading.value = true
  generalError.value = ''

  try {
    await authStore.login({
      username: formData.value.username,
      password: formData.value.password
    })

    notificationsStore.success(
      'Inicio de sesión exitoso',
      `Bienvenido, ${authStore.username}`
    )

    // Redirigir al dashboard
    router.push('/dashboard')
  } catch (error: any) {
    generalError.value = error.message || 'Error al iniciar sesión. Por favor, verifica tus credenciales.'
    
    notificationsStore.error(
      'Error de autenticación',
      generalError.value
    )
  } finally {
    isLoading.value = false
  }
}
</script>
