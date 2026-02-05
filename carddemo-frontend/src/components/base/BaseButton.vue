<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    :aria-busy="loading"
    :aria-disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="mr-2" role="status" aria-label="Cargando">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  disabled: false,
  loading: false,
  fullWidth: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const classes = [
    'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed'
  ]

  // Variantes
  if (props.variant === 'primary') {
    classes.push('bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500')
  } else if (props.variant === 'secondary') {
    classes.push('bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600')
  } else if (props.variant === 'danger') {
    classes.push('bg-red-600 text-white hover:bg-red-700 focus:ring-red-500')
  } else if (props.variant === 'ghost') {
    classes.push('bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800')
  }

  // Tamaños
  if (props.size === 'sm') {
    classes.push('px-3 py-1.5 text-sm')
  } else if (props.size === 'md') {
    classes.push('px-4 py-2 text-base')
  } else if (props.size === 'lg') {
    classes.push('px-6 py-3 text-lg')
  }

  // Ancho completo
  if (props.fullWidth) {
    classes.push('w-full')
  }

  return classes.join(' ')
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
