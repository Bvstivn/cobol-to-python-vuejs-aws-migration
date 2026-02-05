<template>
  <Transition name="toast">
    <div
      v-if="visible"
      :class="toastClasses"
      role="alert"
      @mouseenter="pauseTimer"
      @mouseleave="resumeTimer"
    >
      <!-- Icon -->
      <div class="flex-shrink-0">
        <component :is="iconComponent" class="h-5 w-5" />
      </div>
      
      <!-- Content -->
      <div class="ml-3 flex-1">
        <p class="text-sm font-medium">
          {{ notification.title }}
        </p>
        <p v-if="notification.message" class="mt-1 text-sm opacity-90">
          {{ notification.message }}
        </p>
      </div>
      
      <!-- Close Button -->
      <div class="ml-4 flex-shrink-0 flex">
        <button
          type="button"
          class="inline-flex rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2"
          :class="closeButtonClasses"
          @click="close"
        >
          <span class="sr-only">Cerrar</span>
          <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import type { NotificationMessage } from '@/types'

interface Props {
  notification: NotificationMessage
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: [id: string]
}>()

const visible = ref(false)
const timer = ref<number | null>(null)
const remainingTime = ref(props.notification.duration || 0)
const startTime = ref(0)

const toastClasses = computed(() => {
  const classes = [
    'max-w-sm w-full shadow-lg rounded-lg pointer-events-auto',
    'ring-1 ring-black ring-opacity-5 overflow-hidden',
    'flex p-4'
  ]

  if (props.notification.type === 'success') {
    classes.push('bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200')
  } else if (props.notification.type === 'error') {
    classes.push('bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200')
  } else if (props.notification.type === 'warning') {
    classes.push('bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200')
  } else if (props.notification.type === 'info') {
    classes.push('bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200')
  }

  return classes.join(' ')
})

const closeButtonClasses = computed(() => {
  if (props.notification.type === 'success') {
    return 'text-green-500 hover:text-green-600 focus:ring-green-500'
  } else if (props.notification.type === 'error') {
    return 'text-red-500 hover:text-red-600 focus:ring-red-500'
  } else if (props.notification.type === 'warning') {
    return 'text-yellow-500 hover:text-yellow-600 focus:ring-yellow-500'
  } else {
    return 'text-blue-500 hover:text-blue-600 focus:ring-blue-500'
  }
})

const iconComponent = computed(() => {
  if (props.notification.type === 'success') {
    return h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      viewBox: '0 0 20 20',
      fill: 'currentColor',
      class: 'text-green-400'
    }, [
      h('path', {
        'fill-rule': 'evenodd',
        d: 'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z',
        'clip-rule': 'evenodd'
      })
    ])
  } else if (props.notification.type === 'error') {
    return h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      viewBox: '0 0 20 20',
      fill: 'currentColor',
      class: 'text-red-400'
    }, [
      h('path', {
        'fill-rule': 'evenodd',
        d: 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z',
        'clip-rule': 'evenodd'
      })
    ])
  } else if (props.notification.type === 'warning') {
    return h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      viewBox: '0 0 20 20',
      fill: 'currentColor',
      class: 'text-yellow-400'
    }, [
      h('path', {
        'fill-rule': 'evenodd',
        d: 'M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z',
        'clip-rule': 'evenodd'
      })
    ])
  } else {
    return h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      viewBox: '0 0 20 20',
      fill: 'currentColor',
      class: 'text-blue-400'
    }, [
      h('path', {
        'fill-rule': 'evenodd',
        d: 'M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z',
        'clip-rule': 'evenodd'
      })
    ])
  }
})

const close = () => {
  visible.value = false
  setTimeout(() => {
    emit('close', props.notification.id)
  }, 300) // Esperar a que termine la animación
}

const pauseTimer = () => {
  if (timer.value && !props.notification.persistent) {
    clearTimeout(timer.value)
    timer.value = null
    remainingTime.value -= Date.now() - startTime.value
  }
}

const resumeTimer = () => {
  if (!props.notification.persistent && remainingTime.value > 0) {
    startTime.value = Date.now()
    timer.value = window.setTimeout(close, remainingTime.value)
  }
}

onMounted(() => {
  visible.value = true
  
  if (!props.notification.persistent && props.notification.duration && props.notification.duration > 0) {
    startTime.value = Date.now()
    timer.value = window.setTimeout(close, remainingTime.value)
  }
})

onUnmounted(() => {
  if (timer.value) {
    clearTimeout(timer.value)
  }
})
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
