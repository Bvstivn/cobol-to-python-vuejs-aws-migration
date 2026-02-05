<template>
  <Teleport to="body">
    <div
      class="fixed top-0 right-0 z-50 p-4 space-y-4 pointer-events-none"
      aria-live="assertive"
      aria-atomic="true"
    >
      <TransitionGroup name="notification-list">
        <Toast
          v-for="notification in notifications"
          :key="notification.id"
          :notification="notification"
          @close="handleClose"
        />
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import Toast from './Toast.vue'

const notificationsStore = useNotificationsStore()

const notifications = computed(() => notificationsStore.notifications)

const handleClose = (id: string) => {
  notificationsStore.removeNotification(id)
}
</script>

<style scoped>
.notification-list-move,
.notification-list-enter-active,
.notification-list-leave-active {
  transition: all 0.3s ease;
}

.notification-list-enter-from,
.notification-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.notification-list-leave-active {
  position: absolute;
}
</style>
