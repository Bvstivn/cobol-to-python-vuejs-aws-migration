<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { NotificationContainer } from '@/components/notifications'

const authStore = useAuthStore()
const themeStore = useThemeStore()

// Inicializar stores al montar la app
onMounted(() => {
  authStore.initialize()
  themeStore.initialize()
})
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <RouterView v-slot="{ Component, route }">
      <Transition
        :name="(route.meta.transition as string) || 'fade'"
        mode="out-in"
      >
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
    <NotificationContainer />
  </div>
</template>

<style scoped>
/* Transiciones de página */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>
