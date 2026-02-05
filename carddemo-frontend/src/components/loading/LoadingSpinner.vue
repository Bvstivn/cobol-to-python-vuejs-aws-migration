<template>
  <div :class="containerClasses">
    <svg
      :class="spinnerClasses"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
    <p v-if="message" :class="messageClasses">
      {{ message }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  message?: string
  centered?: boolean
  fullScreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  centered: false,
  fullScreen: false
})

const containerClasses = computed(() => {
  const classes = ['flex flex-col items-center justify-center']

  if (props.fullScreen) {
    classes.push('fixed inset-0 bg-white dark:bg-gray-900 z-50')
  } else if (props.centered) {
    classes.push('w-full h-full')
  }

  return classes.join(' ')
})

const spinnerClasses = computed(() => {
  const classes = ['animate-spin text-blue-600 dark:text-blue-400']

  if (props.size === 'sm') {
    classes.push('h-4 w-4')
  } else if (props.size === 'md') {
    classes.push('h-8 w-8')
  } else if (props.size === 'lg') {
    classes.push('h-12 w-12')
  } else if (props.size === 'xl') {
    classes.push('h-16 w-16')
  }

  return classes.join(' ')
})

const messageClasses = computed(() => {
  const classes = ['mt-2 text-gray-600 dark:text-gray-400']

  if (props.size === 'sm') {
    classes.push('text-sm')
  } else if (props.size === 'md') {
    classes.push('text-base')
  } else if (props.size === 'lg') {
    classes.push('text-lg')
  } else if (props.size === 'xl') {
    classes.push('text-xl')
  }

  return classes.join(' ')
})
</script>
