<template>
  <div
    class="bg-surface rounded-card border-2 p-5 flex flex-col gap-4"
    :class="user.theme_key === 'pierre' ? 'border-indigo-500/30' : 'border-pink-400/30'"
  >
    <!-- User header -->
    <div class="flex items-center gap-3">
      <div
        class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
        :class="user.theme_key === 'pierre' ? 'bg-indigo-500' : 'bg-pink-400'"
      >
        {{ user.name[0].toUpperCase() }}
      </div>
      <div>
        <div class="font-semibold text-apptext">{{ user.name }}</div>
        <div class="text-xs text-muted">{{ stats.total_workouts }} séances · {{ stats.total_sets }} séries</div>
      </div>
      <!-- Streak badge -->
      <div v-if="stats.current_streak > 0" class="ml-auto flex items-center gap-1.5 text-sm">
        <AppIcon name="fire" :size="16" class="text-orange-400" />
        <span class="font-bold text-apptext">{{ stats.current_streak }}j</span>
      </div>
    </div>

    <!-- Recent workouts -->
    <div v-if="recentWorkouts.length">
      <div class="text-xs font-semibold text-muted uppercase mb-2">Dernières séances</div>
      <div class="space-y-1">
        <div
          v-for="w in recentWorkouts"
          :key="w.id"
          class="flex items-center justify-between text-sm py-1.5 border-b border-apbborder/50"
        >
          <span class="text-xs px-2 py-0.5 rounded-btn bg-primary/10 text-primary font-medium">{{ w.type }}</span>
          <span class="text-muted text-xs">{{ formatDate(w.completed_at) }}</span>
        </div>
      </div>
    </div>
    <div v-else class="text-sm text-muted">Pas encore de séances.</div>
  </div>
</template>

<script setup>
import AppIcon from '@/components/ui/AppIcon.vue'

defineProps({
  user: { type: Object, required: true },
  stats: { type: Object, required: true },
  recentWorkouts: { type: Array, default: () => [] },
})

function formatDate(d) {
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short' }).format(new Date(d))
}
</script>
