<template>
  <div class="bg-surface border border-apbborder rounded-card p-4 hover:shadow-sm hover:-translate-y-0.5 transition-all duration-200 cursor-pointer">
    <div class="flex items-start justify-between mb-2">
      <div class="flex-1 min-w-0">
        <span class="inline-block text-xs font-bold px-2 py-0.5 rounded-btn bg-primary/15 text-primary mb-1">
          {{ workout.type }}
        </span>
        <h3 v-if="workout.name" class="font-semibold text-apptext text-sm truncate">{{ workout.name }}</h3>
      </div>
      <span class="text-xs text-muted tabular-nums shrink-0 ml-3">{{ formatDate(workout.completed_at || workout.started_at) }}</span>
    </div>
    <div class="flex items-center gap-2 text-xs text-muted">
      <span>{{ workout.exercise_count }} exo{{ workout.exercise_count !== 1 ? 's' : '' }}</span>
      <span class="opacity-30">|</span>
      <span>{{ workout.set_count }} série{{ workout.set_count !== 1 ? 's' : '' }}</span>
      <template v-if="workout.completed_at">
        <span class="opacity-30">|</span>
        <span>{{ duration }}</span>
      </template>
    </div>
    <p v-if="workout.notes" class="mt-2 text-xs text-muted italic truncate">{{ workout.notes }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  workout: { type: Object, required: true },
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Intl.DateTimeFormat('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' }).format(new Date(dateStr))
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
