<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 overflow-y-auto"
        role="presentation"
        @click.self="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" aria-hidden="true"></div>
        
        <!-- Modal Container -->
        <div class="flex min-h-full items-center justify-center p-4">
          <div
            :class="modalClasses"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="title ? 'modal-title' : undefined"
            @click.stop
          >
            <!-- Header -->
            <div v-if="title || $slots.header" class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <slot name="header">
                <h3 id="modal-title" class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {{ title }}
                </h3>
              </slot>
              
              <button
                v-if="closable"
                type="button"
                class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                aria-label="Cerrar modal"
                @click="close"
              >
                <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Body -->
            <div class="p-4">
              <slot />
            </div>
            
            <!-- Footer -->
            <div v-if="$slots.footer" class="flex items-center justify-end gap-2 p-4 border-t border-gray-200 dark:border-gray-700">
              <slot name="footer" />
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  closable?: boolean
  closeOnBackdrop?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closable: true,
  closeOnBackdrop: true
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

const modalClasses = computed(() => {
  const classes = [
    'relative bg-white dark:bg-gray-800 rounded-lg shadow-xl',
    'transform transition-all w-full'
  ]

  // Tamaños
  if (props.size === 'sm') {
    classes.push('max-w-sm')
  } else if (props.size === 'md') {
    classes.push('max-w-md')
  } else if (props.size === 'lg') {
    classes.push('max-w-lg')
  } else if (props.size === 'xl') {
    classes.push('max-w-xl')
  }

  return classes.join(' ')
})

const close = () => {
  emit('update:modelValue', false)
  emit('close')
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    close()
  }
}

// Prevenir scroll del body cuando el modal está abierto
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.3s ease;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95);
}
</style>
