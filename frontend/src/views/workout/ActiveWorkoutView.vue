<template>
  <AppLayout full-width>
    <div v-if="loading" class="flex items-center justify-center min-h-dvh">
      <LoadingSpinner size="lg" />
    </div>

    <div v-else-if="workout" class="flex flex-col min-h-dvh">
      <!-- Sticky header -->
      <div class="sticky top-0 bg-surface border-b border-apbborder z-40 px-4 py-3 flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2">
            <span class="font-bold text-apptext">{{ workout.type }}</span>
            <span v-if="workout.name" class="text-sm text-muted">· {{ workout.name }}</span>
          </div>
          <WorkoutTimer :started-at="workout.started_at" />
        </div>
        <button
          @click="finish"
          :disabled="finishing"
          class="px-4 py-2 bg-primary text-white rounded-btn text-sm font-semibold disabled:opacity-50"
        >
          Terminer
        </button>
      </div>

      <!-- Notes inline -->
      <div class="px-4 pt-3 pb-0">
        <textarea
          v-model="notes"
          @blur="saveNotes"
          placeholder="Notes (optionnel)…"
          rows="1"
          class="w-full bg-transparent text-sm text-muted placeholder:text-muted/40 resize-none outline-none border-b border-transparent focus:border-apbborder transition-colors"
        />
      </div>

      <!-- Exercise sets -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4 pb-32">
        <SetLogger
          v-for="group in exerciseGroups"
          :key="group.exercise.id"
          :workout-id="workout.id"
          :exercise="group.exercise"
          :initial-sets="group.sets"
          @remove-exercise="removeExerciseFromWorkout"
        />

        <EmptyState
          v-if="!exerciseGroups.length"
          icon="🏋️"
          message="Ajoute un exercice pour commencer ta séance."
        />
      </div>

      <!-- Floating "Add exercise" button -->
      <div class="fixed bottom-24 lg:bottom-8 left-1/2 -translate-x-1/2 z-50">
        <button
          @click="showSelector = true"
          class="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-btn shadow-xl font-semibold text-sm"
        >
          + Exercice
        </button>
      </div>
    </div>

    <!-- Exercise selector drawer (mobile) / modal (desktop) -->
    <Teleport to="body">
      <div
        v-if="showSelector"
        class="fixed inset-0 z-50 flex items-end lg:items-center justify-center"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50" @click="showSelector = false" />

        <!-- Sheet -->
        <div class="relative z-10 w-full lg:w-[480px] h-3/4 lg:h-[600px] bg-surface rounded-t-2xl lg:rounded-card overflow-hidden flex flex-col">
          <div class="flex items-center justify-between p-4 border-b border-apbborder">
            <h2 class="font-semibold text-apptext">Choisir un exercice</h2>
            <button @click="showSelector = false" class="text-muted hover:text-apptext text-xl">×</button>
          </div>
          <ExerciseSelector @select="addExercise" class="flex-1 overflow-hidden" />
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkoutStore } from '@/stores/workoutStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import SetLogger from '@/components/workout/SetLogger.vue'
import ExerciseSelector from '@/components/workout/ExerciseSelector.vue'
import WorkoutTimer from '@/components/workout/WorkoutTimer.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const workoutStore = useWorkoutStore()

const workout = ref(null)
const loading = ref(true)
const showSelector = ref(false)
const finishing = ref(false)
const notes = ref('')

// Groups sets by exercise id; muscle_group comes from the set's exercise_muscle_group
const exerciseGroups = computed(() => {
  if (!workout.value) return []
  const map = new Map()
  for (const s of workout.value.sets) {
    if (!map.has(s.exercise_id)) {
      map.set(s.exercise_id, {
        exercise: {
          id:           s.exercise_id,
          name:         s.exercise_name,
          muscle_group: s.exercise_muscle_group ?? '',
        },
        sets: [],
      })
    }
    map.get(s.exercise_id).sets.push(s)
  }
  return [...map.values()]
})

onMounted(async () => {
  const { id } = route.params
  const res = await fetch(`/api/workouts/${id}`)
  workout.value = await res.json()
  notes.value = workout.value.notes || ''
  loading.value = false
})

async function addExercise(exercise) {
  showSelector.value = false
  const isCardio = exercise.muscle_group === 'Cardio'
  const res = await fetch(`/api/workouts/${workout.value.id}/sets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(isCardio
      ? { exercise_id: exercise.id, set_number: 1, duration_seconds: 1800, resistance: 5, calories: 0, status: 'pending' }
      : { exercise_id: exercise.id, set_number: 1, weight_kg: 0, reps: 0, status: 'pending' }
    ),
  })
  const newSet = await res.json()
  // exercise_muscle_group comes from the API response now
  if (!workout.value.sets) workout.value.sets = []
  workout.value.sets.push(newSet)
}

function removeExerciseFromWorkout(exerciseId) {
  workout.value.sets = workout.value.sets.filter(s => s.exercise_id !== exerciseId)
}

async function saveNotes() {
  await fetch(`/api/workouts/${workout.value.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes: notes.value }),
  })
}

async function finish() {
  finishing.value = true
  await fetch(`/api/workouts/${workout.value.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed_at: new Date().toISOString(), notes: notes.value }),
  })
  workoutStore.clearActive()
  router.push(`/history/${workout.value.id}`)
}
</script>
