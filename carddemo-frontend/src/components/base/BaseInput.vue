<template>
  <div class="w-full">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :step="step"
        :class="inputClasses"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined"
        :aria-required="required"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
      
      <div v-if="error" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
    
    <p v-if="error" :id="`${inputId}-error`" class="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
      {{ error }}
    </p>
    
    <p v-else-if="hint" :id="`${inputId}-hint`" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'date' | 'time' | 'datetime-local'
  label?: string
  placeholder?: string
  error?: string
  hint?: string
  disabled?: boolean
  required?: boolean
  step?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: []
  focus: []
}>()

const inputId = ref(`input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => {
  const classes = [
    'block w-full rounded-lg border px-3 py-2 text-gray-900 dark:text-gray-100',
    'placeholder-gray-400 dark:placeholder-gray-500',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'transition-colors'
  ]

  if (props.error) {
    classes.push('border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20 focus:ring-red-500 focus:border-red-500')
  } else {
    classes.push('border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:ring-blue-500 focus:border-blue-500')
  }

  return classes.join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = props.type === 'number' ? Number(target.value) : target.value
  emit('update:modelValue', value)
}

const handleBlur = () => {
  emit('blur')
}

const handleFocus = () => {
  emit('focus')
}
</script>
