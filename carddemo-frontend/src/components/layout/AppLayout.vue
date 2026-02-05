<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar para desktop -->
    <aside
      :class="sidebarClasses"
      role="navigation"
      aria-label="Navegación principal"
      @click.self="closeMobileMenu"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
          <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">
            CardDemo
          </h1>
          <button
            class="lg:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label="Cerrar menú"
            @click="closeMobileMenu"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-2 py-4 space-y-1 overflow-y-auto" aria-label="Menú de navegación">
          <RouterLink
            v-for="item in navigationItems"
            :key="item.path"
            :to="item.path"
            :class="getNavItemClasses(item.path)"
            :aria-current="route.path === item.path ? 'page' : undefined"
            @click="closeMobileMenu"
          >
            <component :is="item.icon" class="h-5 w-5" aria-hidden="true" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>

        <!-- User section -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex items-center space-x-3 mb-3">
            <div class="flex-shrink-0">
              <div 
                class="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold"
                role="img"
                :aria-label="`Avatar de ${authStore.username}`"
              >
                {{ userInitials }}
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ authStore.username }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Usuario
              </p>
            </div>
          </div>
          <BaseButton
            variant="ghost"
            size="sm"
            full-width
            aria-label="Cerrar sesión"
            @click="handleLogout"
          >
            Cerrar Sesión
          </BaseButton>
        </div>
      </div>
    </aside>

    <!-- Backdrop para móvil -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
      role="presentation"
      aria-hidden="true"
      @click="closeMobileMenu"
    ></div>

    <!-- Main content -->
    <div class="lg:pl-64">
      <!-- Header -->
      <header class="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between h-16 px-4">
          <!-- Mobile menu button -->
          <button
            class="lg:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label="Abrir menú de navegación"
            aria-expanded="false"
            @click="toggleMobileMenu"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Page title -->
          <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ currentPageTitle }}
          </h2>

          <!-- Right section -->
          <div class="flex items-center space-x-4">
            <ThemeToggle />
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="p-4 lg:p-6" role="main" aria-label="Contenido principal">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { BaseButton } from '@/components/base'
import { ThemeToggle } from '@/components/theme'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const mobileMenuOpen = ref(false)

const navigationItems = [
  {
    label: 'Dashboard',
    path: '/dashboard',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      `
    }
  },
  {
    label: 'Mis Tarjetas',
    path: '/cards',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      `
    }
  },
  {
    label: 'Transacciones',
    path: '/transactions',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      `
    }
  },
  {
    label: 'Mi Perfil',
    path: '/profile',
    icon: {
      template: `
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      `
    }
  }
]

const sidebarClasses = computed(() => {
  const classes = [
    'fixed inset-y-0 left-0 z-30 w-64',
    'bg-white dark:bg-gray-800',
    'border-r border-gray-200 dark:border-gray-700',
    'transform transition-transform duration-300 ease-in-out',
    'lg:translate-x-0'
  ]

  if (mobileMenuOpen.value) {
    classes.push('translate-x-0')
  } else {
    classes.push('-translate-x-full')
  }

  return classes.join(' ')
})

const currentPageTitle = computed(() => {
  const item = navigationItems.find(item => item.path === route.path)
  return item?.label || 'CardDemo'
})

const userInitials = computed(() => {
  const username = authStore.username
  if (!username) return '?'
  return username.substring(0, 2).toUpperCase()
})

const getNavItemClasses = (path: string) => {
  const isActive = route.path === path
  const classes = [
    'flex items-center space-x-3 px-3 py-2 rounded-lg',
    'text-sm font-medium transition-colors'
  ]

  if (isActive) {
    classes.push('bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400')
  } else {
    classes.push('text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700')
  }

  return classes.join(' ')
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    notificationsStore.success('Sesión cerrada', 'Has cerrado sesión exitosamente')
    router.push('/login')
  } catch (error: any) {
    notificationsStore.error('Error', 'No se pudo cerrar la sesión')
  }
}
</script>
