<template>
  <div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
    <!-- Información de página -->
    <div class="text-sm text-gray-600 dark:text-gray-400">
      Mostrando {{ startItem }} - {{ endItem }} de {{ total }} transacciones
    </div>

    <!-- Controles de paginación -->
    <div class="flex items-center space-x-2">
      <BaseButton
        variant="secondary"
        size="sm"
        :disabled="currentPage <= 1"
        @click="handlePrevious"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </BaseButton>

      <div class="flex items-center space-x-1">
        <template v-for="page in visiblePages" :key="page">
          <button
            v-if="typeof page === 'number'"
            class="px-3 py-1 rounded text-sm font-medium transition-colors"
            :class="page === currentPage
              ? 'bg-primary-600 text-white'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            @click="handlePageClick(page)"
          >
            {{ page }}
          </button>
          <span v-else class="px-2 text-gray-400">...</span>
        </template>
      </div>

      <BaseButton
        variant="secondary"
        size="sm"
        :disabled="!hasMore"
        @click="handleNext"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseButton } from '@/components/base'

interface Props {
  currentPage: number
  totalPages: number
  total: number
  limit: number
  offset: number
  hasMore: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'page-change': [page: number]
  'next': []
  'previous': []
}>()

const startItem = computed(() => {
  return props.total === 0 ? 0 : props.offset + 1
})

const endItem = computed(() => {
  return Math.min(props.offset + props.limit, props.total)
})

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const maxVisible = 7
  
  if (props.totalPages <= maxVisible) {
    // Mostrar todas las páginas
    for (let i = 1; i <= props.totalPages; i++) {
      pages.push(i)
    }
  } else {
    // Mostrar páginas con elipsis
    if (props.currentPage <= 3) {
      // Cerca del inicio
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(props.totalPages)
    } else if (props.currentPage >= props.totalPages - 2) {
      // Cerca del final
      pages.push(1)
      pages.push('...')
      for (let i = props.totalPages - 4; i <= props.totalPages; i++) {
        pages.push(i)
      }
    } else {
      // En el medio
      pages.push(1)
      pages.push('...')
      for (let i = props.currentPage - 1; i <= props.currentPage + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(props.totalPages)
    }
  }
  
  return pages
})

const handlePrevious = () => {
  if (props.currentPage > 1) {
    emit('previous')
  }
}

const handleNext = () => {
  if (props.hasMore) {
    emit('next')
  }
}

const handlePageClick = (page: number) => {
  if (page !== props.currentPage) {
    emit('page-change', page)
  }
}
</script>
