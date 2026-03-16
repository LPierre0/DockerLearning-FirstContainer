<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-surface border-t border-apbborder z-50 safe-area-pb">
    <div class="flex items-stretch">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex-1 flex flex-col items-center justify-center py-2 text-xs font-medium active:scale-95 transition-transform"
      >
        <span
          class="flex flex-col items-center gap-1 px-3 py-1.5 rounded-full transition-all duration-200"
          :class="isActive(item.to) ? 'bg-primary/15' : ''"
        >
          <AppIcon
            :name="item.icon"
            :size="isActive(item.to) ? 22 : 20"
            :class="isActive(item.to) ? 'text-primary' : 'text-muted'"
          />
          <span
            class="text-[11px] tracking-wide"
            :class="isActive(item.to) ? 'text-primary' : 'text-muted'"
          >{{ item.label }}</span>
        </span>
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'
import { useWorkoutStore } from '@/stores/workoutStore'
import AppIcon from '@/components/ui/AppIcon.vue'

const route = useRoute()
const profileStore = useProfileStore()
const workoutStore = useWorkoutStore()

const navItems = computed(() => {
  const seanceTo = workoutStore.activeWorkoutId
    ? `/workout/active/${workoutStore.activeWorkoutId}`
    : '/workout/new'
  const items = [
    { to: seanceTo,       icon: 'bolt',      label: 'Séance' },
    { to: '/history',     icon: 'clock',     label: 'Historique' },
    { to: '/progress',    icon: 'chart-bar', label: 'Progression' },
    { to: '/profile',     icon: 'scale',     label: 'Poids' },
    { to: '/exercises',   icon: 'list-bullet', label: 'Exercices' },
  ]
  if (profileStore.themeKey === 'partner') {
    items.push({ to: '/cycle', icon: 'calendar', label: 'Cycle' })
  }
  return items
})

function isActive(path) {
  if (path.startsWith('/workout')) {
    return route.path.startsWith('/workout')
  }
  return route.path.startsWith(path)
}
</script>
