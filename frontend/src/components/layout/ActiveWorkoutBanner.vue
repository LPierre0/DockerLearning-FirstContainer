<template>
  <div
    v-if="workoutStore.activeWorkoutId && !isOnActiveWorkout"
    class="fixed bottom-20 lg:bottom-auto lg:top-16 left-0 right-0 z-40
           bg-surface border-t lg:border-t-0 lg:border-b border-primary/40
           px-4 py-2 flex items-center gap-3 shadow-sm"
  >
    <span class="w-2 h-2 rounded-full bg-primary animate-pulse shrink-0" />
    <span class="flex-1 text-sm font-medium text-apptext truncate">
      Séance {{ workoutStore.activeWorkoutType }} en cours
    </span>
    <RouterLink
      :to="`/workout/active/${workoutStore.activeWorkoutId}`"
      class="text-xs px-3 py-1.5 border border-primary/40 text-primary rounded-btn hover:bg-primary/10 transition-colors shrink-0"
    >
      Reprendre
    </RouterLink>
    <button
      @click="terminate"
      :disabled="finishing"
      class="text-xs px-3 py-1.5 bg-primary text-white rounded-btn disabled:opacity-50 transition-colors shrink-0"
    >
      {{ finishing ? '…' : 'Terminer' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useWorkoutStore } from '@/stores/workoutStore'

const route = useRoute()
const workoutStore = useWorkoutStore()
const finishing = ref(false)

const isOnActiveWorkout = computed(() =>
  route.path === `/workout/active/${workoutStore.activeWorkoutId}`
)

async function terminate() {
  finishing.value = true
  try {
    await fetch(`/api/workouts/${workoutStore.activeWorkoutId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed_at: new Date().toISOString() }),
    })
    workoutStore.clearActive()
  } finally {
    finishing.value = false
  }
}
</script>
