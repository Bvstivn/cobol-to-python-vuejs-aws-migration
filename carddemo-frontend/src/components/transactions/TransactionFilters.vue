<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm space-y-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        Filtros
      </h3>
      <BaseButton
        v-if="hasActiveFilters"
        variant="secondary"
        size="sm"
        @click="handleClearFilters"
      >
        Limpiar Filtros
      </BaseButton>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Fecha inicio -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Fecha Inicio
        </label>
        <input
          v-model="localFilters.start_date"
          type="date"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="handleFilterChange"
        />
      </div>

      <!-- Fecha fin -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Fecha Fin
        </label>
        <input
          v-model="localFilters.end_date"
          type="date"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="handleFilterChange"
        />
      </div>

      <!-- Tipo de transacción -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Tipo
        </label>
        <select
          v-model="localFilters.transaction_type"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="handleFilterChange"
        >
          <option value="">Todos</option>
          <option value="PURCHASE">Compra</option>
          <option value="PAYMENT">Pago</option>
          <option value="REFUND">Reembolso</option>
        </select>
      </div>

      <!-- Tarjeta -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Tarjeta
        </label>
        <select
          v-model="localFilters.card_id"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="handleFilterChange"
        >
          <option :value="undefined">Todas</option>
          <option v-for="card in cards" :key="card.id" :value="card.id">
            {{ card.card_type }} - {{ card.masked_card_number.slice(-4) }}
          </option>
        </select>
      </div>

      <!-- Monto mínimo -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Monto Mínimo
        </label>
        <input
          v-model.number="localFilters.min_amount"
          type="number"
          step="0.01"
          placeholder="0.00"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="handleFilterChange"
        />
      </div>

      <!-- Monto máximo -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Monto Máximo
        </label>
        <input
          v-model.number="localFilters.max_amount"
          type="number"
          step="0.01"
          placeholder="0.00"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          @change="handleFilterChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { BaseButton } from '@/components/base'
import type { TransactionFilters, CreditCard } from '@/types'

interface Props {
  filters: TransactionFilters
  cards?: CreditCard[]
}

const props = withDefaults(defineProps<Props>(), {
  cards: () => []
})

const emit = defineEmits<{
  'update:filters': [filters: TransactionFilters]
  'clear': []
}>()

const localFilters = ref<TransactionFilters>({ ...props.filters })

const hasActiveFilters = computed(() => {
  return Object.keys(localFilters.value).some(key => {
    const value = localFilters.value[key as keyof TransactionFilters]
    return value !== undefined && value !== '' && value !== null
  })
})

watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

function handleFilterChange() {
  // Limpiar valores vacíos
  const cleanedFilters: TransactionFilters = {}
  Object.entries(localFilters.value).forEach(([key, value]) => {
    if (value !== undefined && value !== '' && value !== null) {
      cleanedFilters[key as keyof TransactionFilters] = value as any
    }
  })
  
  emit('update:filters', cleanedFilters)
}

function handleClearFilters() {
  localFilters.value = {}
  emit('clear')
}
</script>
