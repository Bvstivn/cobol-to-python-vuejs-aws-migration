<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        Mis Tarjetas
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Gestiona tus tarjetas de crédito
      </p>
    </div>

    <!-- Resumen de crédito -->
    <div v-if="cardsStore.hasCards && !cardsStore.isLoading" class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Crédito Total</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
          ${{ cardsStore.totalCreditLimit.toFixed(2) }}
        </p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Crédito Disponible</p>
        <p class="text-2xl font-bold text-green-600 dark:text-green-400">
          ${{ cardsStore.totalAvailableCredit.toFixed(2) }}
        </p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Crédito Utilizado</p>
        <p class="text-2xl font-bold text-orange-600 dark:text-orange-400">
          ${{ cardsStore.totalUsedCredit.toFixed(2) }}
        </p>
      </div>
    </div>

    <!-- Lista de tarjetas -->
    <CardList
      :cards="cardsStore.cards"
      :is-loading="cardsStore.isLoading"
      :error="cardsStore.error"
      @retry="handleRetry"
      @card-click="handleCardClick"
    />

    <!-- Modal de detalles -->
    <CardDetails
      :is-open="showDetailsModal"
      :card="cardsStore.selectedCard"
      @close="handleCloseDetails"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AppLayout } from '@/components/layout'
import { CardList, CardDetails } from '@/components/cards'
import { useCardsStore } from '@/stores/cards'
import type { CreditCard } from '@/types'

const cardsStore = useCardsStore()
const showDetailsModal = ref(false)

onMounted(async () => {
  await loadCards()
})

async function loadCards() {
  try {
    await cardsStore.fetchCards()
  } catch (error) {
    console.error('Error loading cards:', error)
  }
}

function handleRetry() {
  loadCards()
}

function handleCardClick(card: CreditCard) {
  cardsStore.selectCard(card)
  showDetailsModal.value = true
}

function handleCloseDetails() {
  showDetailsModal.value = false
}
</script>
