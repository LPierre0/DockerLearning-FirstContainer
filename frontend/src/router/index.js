import { createRouter, createWebHistory } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'

const routes = [
  {
    path: '/',
    name: 'profile-selection',
    component: () => import('@/views/ProfileSelectionView.vue'),
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/workout/new',
    name: 'workout-new',
    component: () => import('@/views/workout/NewWorkoutView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/workout/active/:id',
    name: 'workout-active',
    component: () => import('@/views/workout/ActiveWorkoutView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/HistoryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history/:id',
    name: 'workout-detail',
    component: () => import('@/views/WorkoutDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/exercises',
    name: 'exercises',
    component: () => import('@/views/ExerciseLibraryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/progress',
    name: 'progress',
    component: () => import('@/views/ProgressView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/progress/:id',
    name: 'exercise-progress',
    component: () => import('@/views/ExerciseProgressView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/BodyWeightView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cycle',
    name: 'cycle',
    component: () => import('@/views/CycleView.vue'),
    meta: { requiresAuth: true, requiresPartner: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const saved = localStorage.getItem('fitness_profile')
    if (!saved) {
      return { name: 'profile-selection' }
    }
    if (to.meta.requiresPartner) {
      const user = JSON.parse(saved)
      if (user.theme_key !== 'partner') {
        return { name: 'dashboard' }
      }
    }
  }
  if (to.name === 'profile-selection') {
    const saved = localStorage.getItem('fitness_profile')
    if (saved) {
      return { name: 'dashboard' }
    }
  }
})

export default router
