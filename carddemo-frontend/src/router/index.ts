/**
 * Configuración de Vue Router con guards de autenticación
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Vistas
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import CardsView from '@/views/CardsView.vue'
import TransactionsView from '@/views/TransactionsView.vue'
import ProfileView from '@/views/ProfileView.vue'

/**
 * Definición de rutas
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      requiresAuth: false,
      title: 'Iniciar Sesión',
      transition: 'fade'
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: {
      requiresAuth: true,
      title: 'Dashboard',
      transition: 'slide'
    }
  },
  {
    path: '/cards',
    name: 'cards',
    component: CardsView,
    meta: {
      requiresAuth: true,
      title: 'Mis Tarjetas',
      transition: 'slide'
    }
  },
  {
    path: '/transactions',
    name: 'transactions',
    component: TransactionsView,
    meta: {
      requiresAuth: true,
      title: 'Transacciones',
      transition: 'slide'
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: {
      requiresAuth: true,
      title: 'Mi Perfil',
      transition: 'slide'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

/**
 * Crear instancia del router
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/**
 * Navigation guard global - Verificar autenticación
 */
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  // Actualizar título de la página
  if (to.meta.title) {
    document.title = `${to.meta.title} - CardDemo`
  }

  // Si la ruta requiere autenticación
  if (requiresAuth) {
    // Verificar si hay token válido
    if (!authStore.isAuthenticated) {
      // Intentar verificar el estado de autenticación
      const isValid = await authStore.checkAuthStatus()
      
      if (!isValid) {
        // Redirigir al login
        next({
          name: 'login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
  } else {
    // Si es la ruta de login y ya está autenticado, redirigir al dashboard
    if (to.name === 'login' && authStore.isAuthenticated) {
      next({ name: 'dashboard' })
      return
    }
  }

  next()
})

/**
 * Navigation guard después de cada navegación
 */
router.afterEach(() => {
  // Scroll al inicio de la página
  window.scrollTo(0, 0)
})

export default router
