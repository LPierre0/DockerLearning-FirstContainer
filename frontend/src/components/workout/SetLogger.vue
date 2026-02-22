<template>
  <div class="flex flex-col gap-2 p-4 bg-surface rounded-card border border-apbborder">
    <!-- Exercise header -->
    <div class="flex items-center justify-between mb-1">
      <div>
        <h3 class="font-semibold text-apptext">{{ exercise.name }}</h3>
        <span class="text-xs text-muted">{{ exercise.muscle_group }}</span>
      </div>
      <button
        @click="removeExercise"
        :disabled="removing"
        class="text-xs text-muted hover:text-danger transition-colors disabled:opacity-50 px-2 py-1"
        title="Supprimer l'exercice"
      >
        Supprimer
      </button>
    </div>

    <!-- Sets -->
    <SetRow
      v-for="set in sets"
      :key="set.id"
      :set="set"
      :exercise="exercise"
      @update="(data) => updateSet(set.id, data)"
      @delete="deleteSet(set.id)"
      @done="onSetDone"
    />

    <!-- Rest timer -->
    <RestTimer
      v-if="restActive"
      :duration="restDuration"
      @skip="restActive = false"
      @done="restActive = false"
    />

    <!-- Add set button -->
    <button
      @click="addSet"
      :disabled="saving"
      class="mt-1 py-2 text-sm text-primary border border-primary/40 rounded-btn hover:bg-primary/10 transition-colors disabled:opacity-50"
    >
      + Ajouter une série
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SetRow from './SetRow.vue'
import RestTimer from './RestTimer.vue'

const props = defineProps({
  workoutId: { type: Number, required: true },
  exercise: { type: Object, required: true },
  initialSets: { type: Array, default: () => [] },
})

const emit = defineEmits(['setAdded', 'removeExercise'])

const sets = ref([...props.initialSets])
const saving = ref(false)
const removing = ref(false)
const restActive = ref(false)
const restDuration = ref(parseInt(localStorage.getItem('rest_duration') || '90'))

function onSetDone() {
  restActive.value = true
}

async function addSet() {
  saving.value = true
  const last = sets.value.at(-1)
  const isCardio = props.exercise.muscle_group === 'Cardio'
  const payload = isCardio
    ? {
        exercise_id:      props.exercise.id,
        set_number:       sets.value.length + 1,
        duration_seconds: last?.duration_seconds ?? 1800,
        resistance:       last?.resistance ?? 5,
        calories:         last?.calories ?? 0,
        status:           'pending',
      }
    : {
        exercise_id: props.exercise.id,
        set_number:  sets.value.length + 1,
        weight_kg:   last?.weight_kg ?? 0,
        reps:        last?.reps ?? 0,
        rpe:         null,
        status:      'pending',
      }
  try {
    const res = await fetch(`/api/workouts/${props.workoutId}/sets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const newSet = await res.json()
    sets.value.push(newSet)
    emit('setAdded', newSet)
  } finally {
    saving.value = false
  }
}

async function updateSet(setId, data) {
  const idx = sets.value.findIndex(s => s.id === setId)
  if (idx === -1) return
  // Optimistic update
  sets.value[idx] = { ...sets.value[idx], ...data }
  await fetch(`/api/sets/${setId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

async function deleteSet(setId) {
  sets.value = sets.value.filter(s => s.id !== setId)
  await fetch(`/api/sets/${setId}`, { method: 'DELETE' })
  // Renumber
  sets.value.forEach((s, i) => { s.set_number = i + 1 })
}

async function removeExercise() {
  removing.value = true
  await Promise.all(sets.value.map(s => fetch(`/api/sets/${s.id}`, { method: 'DELETE' })))
  emit('removeExercise', props.exercise.id)
}
</script>
