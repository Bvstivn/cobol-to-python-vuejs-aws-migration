<template>
  <BaseModal
    :model-value="isOpen"
    :title="`Detalles de Tarjeta ${card?.card_type || ''}`"
    @close="handleClose"
  >
    <div v-if="card" class="space-y-6">
      <!-- Tarjeta visual -->
      <div
        class="relative bg-gradient-to-br rounded-xl p-6 shadow-lg"
        :class="cardGradient"
      >
        <!-- Chip simulado -->
        <div class="absolute top-6 left-6 w-12 h-10 bg-yellow-400/30 rounded-md"></div>

        <!-- Logo del tipo de tarjeta -->
        <div class="flex justify-end mb-8">
          <div class="text-white/90 font-bold text-xl">
            {{ card.card_type }}
          </div>
        </div>

        <!-- Número de tarjeta enmascarado -->
        <div class="mb-6">
          <p class="text-white/70 text-xs mb-1">Número de Tarjeta</p>
          <p class="text-white font-mono text-lg tracking-wider">
            {{ card.masked_card_number }}
          </p>
        </div>

        <!-- Información inferior -->
        <div class="flex justify-between items-end">
          <!-- Fecha de expiración -->
          <div>
            <p class="text-white/70 text-xs mb-1">Válida hasta</p>
            <p class="text-white font-mono text-sm">
              {{ formattedExpiry }}
            </p>
          </div>

          <!-- Estado -->
          <div>
            <span
              class="px-2 py-1 rounded text-xs font-semibold"
              :class="statusClasses"
            >
              {{ statusLabel }}
            </span>
          </div>
        </div>
      </div>

      <!-- Información de crédito -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Información de Crédito
        </h3>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Límite de Crédito</p>
            <p class="text-xl font-bold text-gray-900 dark:text-gray-100">
              ${{ card.credit_limit.toFixed(2) }}
            </p>
          </div>

          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Crédito Disponible</p>
            <p class="text-xl font-bold text-green-600 dark:text-green-400">
              ${{ card.available_credit.toFixed(2) }}
            </p>
          </div>

          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Crédito Utilizado</p>
            <p class="text-xl font-bold text-orange-600 dark:text-orange-400">
              ${{ usedCredit.toFixed(2) }}
            </p>
          </div>

          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Utilización</p>
            <p class="text-xl font-bold" :class="utilizationColorClass">
              {{ utilizationPercentage.toFixed(1) }}%
            </p>
          </div>
        </div>

        <!-- Barra de utilización -->
        <div>
          <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
            <span>Utilización de Crédito</span>
            <span>{{ utilizationPercentage.toFixed(1) }}%</span>
          </div>
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              class="h-full transition-all"
              :class="utilizationBarColor"
              :style="{ width: `${utilizationPercentage}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Información adicional -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Información Adicional
        </h3>

        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">ID de Tarjeta:</span>
            <span class="font-mono text-gray-900 dark:text-gray-100">{{ card.id }}</span>
          </div>

          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Fecha de Creación:</span>
            <span class="text-gray-900 dark:text-gray-100">{{ formattedCreatedAt }}</span>
          </div>

          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">Estado:</span>
            <span
              class="px-2 py-0.5 rounded text-xs font-semibold"
              :class="statusClasses"
            >
              {{ statusLabel }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Acciones del modal -->
    <template #footer>
      <div class="flex justify-end gap-3">
        <BaseButton variant="secondary" @click="handleClose">
          Cerrar
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseModal, BaseButton } from '@/components/base'
import type { CreditCard, CardStatus } from '@/types'

interface Props {
  isOpen: boolean
  card: CreditCard | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const cardGradient = computed(() => {
  if (!props.card) return 'from-gray-600 to-gray-800'
  
  const gradients = {
    VISA: 'from-blue-600 to-blue-800',
    MASTERCARD: 'from-red-600 to-orange-700',
    AMEX: 'from-green-600 to-teal-700',
    DISCOVER: 'from-purple-600 to-pink-700'
  }
  return gradients[props.card.card_type] || 'from-gray-600 to-gray-800'
})

const formattedExpiry = computed(() => {
  if (!props.card) return ''
  const month = props.card.expiry_month.toString().padStart(2, '0')
  const year = props.card.expiry_year.toString().slice(-2)
  return `${month}/${year}`
})

const formattedCreatedAt = computed(() => {
  if (!props.card) return ''
  return new Date(props.card.created_at).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const statusLabel = computed(() => {
  if (!props.card) return ''
  const labels: Record<CardStatus, string> = {
    ACTIVE: 'Activa',
    BLOCKED: 'Bloqueada',
    EXPIRED: 'Expirada'
  }
  return labels[props.card.status]
})

const statusClasses = computed(() => {
  if (!props.card) return ''
  const classes: Record<CardStatus, string> = {
    ACTIVE: 'bg-green-500/90 text-white',
    BLOCKED: 'bg-red-500/90 text-white',
    EXPIRED: 'bg-gray-500/90 text-white'
  }
  return classes[props.card.status]
})

const usedCredit = computed(() => {
  if (!props.card) return 0
  return props.card.credit_limit - props.card.available_credit
})

const utilizationPercentage = computed(() => {
  if (!props.card || props.card.credit_limit === 0) return 0
  return Math.min(100, (usedCredit.value / props.card.credit_limit) * 100)
})

const utilizationBarColor = computed(() => {
  const percentage = utilizationPercentage.value
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-yellow-500'
  return 'bg-green-500'
})

const utilizationColorClass = computed(() => {
  const percentage = utilizationPercentage.value
  if (percentage >= 90) return 'text-red-600 dark:text-red-400'
  if (percentage >= 70) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-green-600 dark:text-green-400'
})

const handleClose = () => {
  emit('close')
}
</script>
