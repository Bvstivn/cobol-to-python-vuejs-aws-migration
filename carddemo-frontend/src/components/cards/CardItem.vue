<template>
  <div
    class="relative bg-gradient-to-br rounded-xl p-6 shadow-lg cursor-pointer transform transition-all hover:scale-105 hover:shadow-xl"
    :class="cardGradient"
    @click="handleClick"
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
        {{ formattedCardNumber }}
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

    <!-- Crédito disponible -->
    <div class="mt-4 pt-4 border-t border-white/20">
      <div class="flex justify-between items-center">
        <div>
          <p class="text-white/70 text-xs">Crédito Disponible</p>
          <p class="text-white font-semibold text-lg">
            ${{ card.available_credit.toFixed(2) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-white/70 text-xs">Límite</p>
          <p class="text-white text-sm">
            ${{ card.credit_limit.toFixed(2) }}
          </p>
        </div>
      </div>
      
      <!-- Barra de utilización -->
      <div class="mt-2 h-2 bg-white/20 rounded-full overflow-hidden">
        <div
          class="h-full transition-all"
          :class="utilizationColor"
          :style="{ width: `${utilizationPercentage}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CreditCard, CardStatus } from '@/types'

interface Props {
  card: CreditCard
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [card: CreditCard]
}>()

const cardGradient = computed(() => {
  const gradients = {
    VISA: 'from-blue-600 to-blue-800',
    MASTERCARD: 'from-red-600 to-orange-700',
    AMEX: 'from-green-600 to-teal-700',
    DISCOVER: 'from-purple-600 to-pink-700'
  }
  return gradients[props.card.card_type] || 'from-gray-600 to-gray-800'
})

const formattedCardNumber = computed(() => {
  // El número ya viene enmascarado de la API (ej: "**** **** **** 1234")
  return props.card.masked_card_number
})

const formattedExpiry = computed(() => {
  const month = props.card.expiry_month.toString().padStart(2, '0')
  const year = props.card.expiry_year.toString().slice(-2)
  return `${month}/${year}`
})

const statusLabel = computed(() => {
  const labels: Record<CardStatus, string> = {
    ACTIVE: 'Activa',
    BLOCKED: 'Bloqueada',
    EXPIRED: 'Expirada'
  }
  return labels[props.card.status]
})

const statusClasses = computed(() => {
  const classes: Record<CardStatus, string> = {
    ACTIVE: 'bg-green-500/90 text-white',
    BLOCKED: 'bg-red-500/90 text-white',
    EXPIRED: 'bg-gray-500/90 text-white'
  }
  return classes[props.card.status]
})

const utilizationPercentage = computed(() => {
  const used = props.card.credit_limit - props.card.available_credit
  return Math.min(100, (used / props.card.credit_limit) * 100)
})

const utilizationColor = computed(() => {
  const percentage = utilizationPercentage.value
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-yellow-500'
  return 'bg-green-500'
})

const handleClick = () => {
  emit('click', props.card)
}
</script>
