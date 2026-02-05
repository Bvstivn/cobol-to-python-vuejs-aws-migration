<template>
  <div :class="cardClasses">
    <!-- Header -->
    <div v-if="title || $slots.header" :class="headerClasses">
      <slot name="header">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {{ title }}
        </h3>
      </slot>
    </div>
    
    <!-- Body -->
    <div :class="bodyClasses">
      <slot />
    </div>
    
    <!-- Footer -->
    <div v-if="$slots.footer" :class="footerClasses">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hoverable?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  padding: 'md',
  hoverable: false,
  clickable: false
})

const cardClasses = computed(() => {
  const classes = [
    'bg-white dark:bg-gray-800',
    'border border-gray-200 dark:border-gray-700',
    'rounded-lg shadow-sm',
    'transition-shadow'
  ]

  if (props.hoverable) {
    classes.push('hover:shadow-md')
  }

  if (props.clickable) {
    classes.push('cursor-pointer hover:shadow-md')
  }

  return classes.join(' ')
})

const headerClasses = computed(() => {
  const classes = ['border-b border-gray-200 dark:border-gray-700']

  if (props.padding === 'none') {
    classes.push('p-0')
  } else if (props.padding === 'sm') {
    classes.push('p-3')
  } else if (props.padding === 'md') {
    classes.push('p-4')
  } else if (props.padding === 'lg') {
    classes.push('p-6')
  }

  return classes.join(' ')
})

const bodyClasses = computed(() => {
  const classes = []

  if (props.padding === 'none') {
    classes.push('p-0')
  } else if (props.padding === 'sm') {
    classes.push('p-3')
  } else if (props.padding === 'md') {
    classes.push('p-4')
  } else if (props.padding === 'lg') {
    classes.push('p-6')
  }

  return classes.join(' ')
})

const footerClasses = computed(() => {
  const classes = ['border-t border-gray-200 dark:border-gray-700']

  if (props.padding === 'none') {
    classes.push('p-0')
  } else if (props.padding === 'sm') {
    classes.push('p-3')
  } else if (props.padding === 'md') {
    classes.push('p-4')
  } else if (props.padding === 'lg') {
    classes.push('p-6')
  }

  return classes.join(' ')
})
</script>
