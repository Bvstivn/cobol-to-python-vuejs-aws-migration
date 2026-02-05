<template>
  <div :class="skeletonClasses">
    <div class="animate-pulse">
      <!-- Avatar/Circle -->
      <div v-if="type === 'avatar'" :class="avatarClasses"></div>
      
      <!-- Text Lines -->
      <div v-else-if="type === 'text'" class="space-y-3">
        <div v-for="i in lines" :key="i" :class="textLineClasses(i)"></div>
      </div>
      
      <!-- Card -->
      <div v-else-if="type === 'card'" class="space-y-4">
        <div class="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div class="space-y-2">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
      
      <!-- Table -->
      <div v-else-if="type === 'table'" class="space-y-3">
        <div v-for="i in rows" :key="i" class="flex space-x-4">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded flex-1"></div>
        </div>
      </div>
      
      <!-- Custom -->
      <div v-else-if="type === 'custom'">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'avatar' | 'text' | 'card' | 'table' | 'custom'
  lines?: number
  rows?: number
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  lines: 3,
  rows: 5,
  size: 'md'
})

const skeletonClasses = computed(() => {
  return 'w-full'
})

const avatarClasses = computed(() => {
  const classes = ['rounded-full bg-gray-200 dark:bg-gray-700']

  if (props.size === 'sm') {
    classes.push('h-8 w-8')
  } else if (props.size === 'md') {
    classes.push('h-12 w-12')
  } else if (props.size === 'lg') {
    classes.push('h-16 w-16')
  }

  return classes.join(' ')
})

const textLineClasses = (lineNumber: number) => {
  const classes = ['h-4 bg-gray-200 dark:bg-gray-700 rounded']

  // Última línea más corta
  if (lineNumber === props.lines) {
    classes.push('w-2/3')
  } else {
    classes.push('w-full')
  }

  return classes.join(' ')
}
</script>
