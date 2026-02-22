<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-surface border-t border-apbborder z-50 safe-area-pb">
    <div class="flex items-stretch">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex-1 flex flex-col items-center justify-center gap-1.5 py-3 text-xs font-medium transition-colors relative"
        :class="isActive(item.to) ? 'text-primary' : 'text-muted'"
      >
        <span
          v-if="isActive(item.to)"
          class="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 rounded-full bg-primary"
        />
        <AppIcon :name="item.icon" :size="20" />
        <span class="text-[11px] tracking-wide">{{ item.label }}</span>
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'
import AppIcon from '@/components/ui/AppIcon.vue'

const route = useRoute()
const profileStore = useProfileStore()

const navItems = computed(() => {
  const items = [
    { to: '/workout/new', icon: 'bolt',      label: 'Séance' },
    { to: '/history',     icon: 'clock',     label: 'Historique' },
    { to: '/progress',    icon: 'chart-bar', label: 'Progression' },
    { to: '/profile',     icon: 'scale',     label: 'Poids' },
    { to: '/dashboard',   icon: 'home',      label: 'Dashboard' },
  ]
  if (profileStore.themeKey === 'partner') {
    items.push({ to: '/cycle', icon: 'calendar', label: 'Cycle' })
  }
  return items
})

function isActive(path) {
  if (path === '/workout/new') {
    return route.path.startsWith('/workout')
  }
  return route.path.startsWith(path)
}
</script>
