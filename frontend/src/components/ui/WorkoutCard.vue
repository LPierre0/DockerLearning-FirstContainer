<template>
  <div class="bg-surface border border-apbborder border-l-2 border-l-primary/30 rounded-card p-4 hover:border-primary/50 transition-colors cursor-pointer">
    <div class="flex items-start justify-between mb-3">
      <div>
        <span class="inline-block text-xs font-bold px-2 py-0.5 rounded-btn bg-primary/15 text-primary mb-1">
          {{ workout.type }}
        </span>
        <h3 v-if="workout.name" class="font-semibold text-apptext text-sm">{{ workout.name }}</h3>
      </div>
      <span class="text-xs text-muted tabular-nums">{{ formatDate(workout.completed_at || workout.started_at) }}</span>
    </div>
    <div class="flex items-center gap-4 text-xs text-muted">
      <span class="flex items-center gap-1">
        <AppIcon name="squares" :size="13" />
        {{ workout.exercise_count }} exercice{{ workout.exercise_count !== 1 ? 's' : '' }}
      </span>
      <span class="flex items-center gap-1">
        <AppIcon name="list-bullet" :size="13" />
        {{ workout.set_count }} série{{ workout.set_count !== 1 ? 's' : '' }}
      </span>
      <span v-if="workout.completed_at" class="flex items-center gap-1">
        <AppIcon name="clock" :size="13" />
        {{ duration }}
      </span>
    </div>
    <p v-if="workout.notes" class="mt-2 text-xs text-muted italic truncate">{{ workout.notes }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  workout: { type: Object, required: true },
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(dateStr))
}

const duration = computed(() => {
  if (!props.workout.completed_at || !props.workout.started_at) return ''
  const ms = new Date(props.workout.completed_at) - new Date(props.workout.started_at)
  const min = Math.floor(ms / 60000)
  const h = Math.floor(min / 60)
  const m = min % 60
  return h > 0 ? `${h}h${String(m).padStart(2,'0')}` : `${m} min`
})
</script>
