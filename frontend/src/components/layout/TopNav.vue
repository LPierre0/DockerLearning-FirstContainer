<template>
  <header class="fixed top-0 left-0 right-0 h-16 bg-surface border-b border-apbborder z-50 px-6">
    <div class="max-w-6xl mx-auto h-full flex items-center justify-between">
      <span class="font-bold text-primary text-lg tracking-tight">FitCouple</span>

      <nav class="flex items-center gap-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="px-3 py-1.5 rounded-btn text-sm font-medium transition-colors"
          :class="isActive(item.to) ? 'bg-primary text-white' : 'text-muted hover:text-apptext hover:bg-surface2'"
        >
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="flex items-center gap-3">
        <RouterLink to="/exercises" class="text-muted hover:text-apptext text-sm">
          Exercices
        </RouterLink>
        <button
          @click="doLogout"
          class="text-xs text-muted hover:text-danger transition-colors"
          title="Changer de profil"
        >
          Déconnexion
        </button>
        <div
          class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm"
          :title="profileStore.userName"
        >
          {{ profileStore.userName?.[0]?.toUpperCase() }}
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'

const route = useRoute()
const router = useRouter()
const profileStore = useProfileStore()

const navItems = computed(() => {
  const items = [
    { to: '/workout/new', label: 'Séance' },
    { to: '/history',     label: 'Historique' },
    { to: '/progress',    label: 'Progression' },
    { to: '/profile',     label: 'Poids' },
    { to: '/dashboard',   label: 'Dashboard' },
  ]
  if (profileStore.themeKey === 'partner') {
    items.push({ to: '/cycle', label: 'Cycle' })
  }
  return items
})

function isActive(path) {
  if (path === '/workout/new') return route.path.startsWith('/workout')
  return route.path.startsWith(path)
}

function doLogout() {
  profileStore.logout()
  router.push('/')
}
</script>
