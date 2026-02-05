<template>
  <div>
    <!-- Estados de carga y error -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <LoadingSkeleton v-for="i in 3" :key="i" type="card" />
    </div>

    <div v-else-if="error" class="text-center py-12">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-error-100 dark:bg-error-900/20 mb-4">
        <svg class="h-8 w-8 text-error-600 dark:text-error-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-error-600 dark:text-error-400 mb-4">{{ error }}</p>
      <BaseButton variant="secondary" size="sm" @click="handleRetry">
        Reintentar
      </BaseButton>
    </div>

    <!-- Lista de tarjetas -->
    <div v-else-if="cards.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <CardItem
        v-for="card in cards"
        :key="card.id"
        :card="card"
        @click="handleCardClick"
      />
    </div>

    <!-- Estado vacío -->
    <div v-else class="text-center py-12">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
        <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      </div>
      <p class="text-gray-500 dark:text-gray-400 mb-2">No tienes tarjetas registradas</p>
      <p class="text-sm text-gray-400 dark:text-gray-500">Contacta con soporte para solicitar una tarjeta</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import CardItem from './CardItem.vue'
import { BaseButton } from '@/components/base'
import { LoadingSkeleton } from '@/components/loading'
import type { CreditCard } from '@/types'

interface Props {
  cards: CreditCard[]
  isLoading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  error: null
})

const emit = defineEmits<{
  retry: []
  cardClick: [card: CreditCard]
}>()

const handleRetry = () => {
  emit('retry')
}

const handleCardClick = (card: CreditCard) => {
  emit('cardClick', card)
}
</script>
