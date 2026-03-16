<template>
  <AppLayout>
    <div v-if="loading" class="flex items-center justify-center py-20">
      <LoadingSpinner size="lg" />
    </div>

    <div v-else-if="workout" class="p-4 max-w-2xl mx-auto">
      <!-- Header -->
      <RouterLink to="/history" class="inline-flex items-center gap-1 text-sm text-muted hover:text-apptext mb-4">
        ← Retour à l'historique
      </RouterLink>

      <div class="flex items-center justify-between mb-6">
        <div>
          <span class="inline-block text-xs font-bold px-2 py-0.5 rounded-btn bg-primary/15 text-primary mb-1">
            {{ workout.type }}
          </span>
          <h1 class="text-xl font-bold text-apptext">{{ workout.name || workout.type }}</h1>
          <p class="text-sm text-muted">{{ formatDate(workout.started_at) }}</p>
        </div>
        <button
          @click="deleteWorkout"
          class="text-sm text-muted hover:text-danger transition-colors px-3 py-1.5 rounded-btn border border-transparent hover:border-danger/30"
          title="Supprimer la séance"
        >
          Supprimer
        </button>
      </div>

      <!-- Message post-séance -->
      <div
        v-if="justFinished && finishMessage"
        class="mb-6 p-4 rounded-card border"
        :class="finishMessage.positive ? 'bg-success/10 border-success/30' : 'bg-primary/10 border-primary/30'"
      >
        <p class="text-sm font-medium" :class="finishMessage.positive ? 'text-success' : 'text-primary'">
          {{ finishMessage.text }}
        </p>
      </div>

      <!-- Notes -->
      <div v-if="workout.notes" class="mb-6 p-3 rounded-card bg-surface border border-apbborder">
        <p class="text-sm text-muted whitespace-pre-wrap">{{ workout.notes }}</p>
      </div>

      <!-- Comparison with previous workout -->
      <div v-if="comparison" class="mb-6 p-3 rounded-card bg-surface border border-apbborder">
        <p class="text-xs font-semibold text-muted mb-2">vs séance du {{ formatShortDate(comparison.prevDate) }}</p>
        <div class="flex gap-4">
          <div class="text-center">
            <p class="text-sm font-bold" :class="comparison.deltaVolume >= 0 ? 'text-success' : 'text-danger'">
              {{ formatDelta(comparison.deltaVolume, 'kg') }}
            </p>
            <p class="text-xs text-muted">volume</p>
          </div>
          <div class="text-center">
            <p class="text-sm font-bold" :class="comparison.deltaSets >= 0 ? 'text-success' : 'text-danger'">
              {{ formatDelta(comparison.deltaSets, 'séries') }}
            </p>
            <p class="text-xs text-muted">séries réussies</p>
          </div>
        </div>
      </div>

      <!-- Sets grouped by exercise -->
      <div
        v-for="group in exerciseGroups"
        :key="group.exercise_id"
        class="mb-6"
      >
        <div class="flex items-center gap-3 mb-3">
          <ExerciseThumb :src="group.photo_url" :alt="group.exercise_name" :size="36" />
          <h2 class="font-semibold text-apptext">{{ group.exercise_name }}</h2>
        </div>
        <div class="space-y-2">
          <div
            v-for="s in group.sets"
            :key="s.id"
            class="flex items-center gap-4 px-4 py-2 rounded-card bg-surface border border-apbborder text-sm"
            :class="{
              'border-success/50 bg-success/5': s.status === 'done',
              'border-danger/50 bg-danger/5': s.status === 'failed',
            }"
          >
            <span class="text-muted w-4">{{ s.set_number }}</span>
            <template v-if="s.duration_seconds != null">
              <span class="text-apptext font-medium">{{ Math.round(s.duration_seconds / 60) }} min</span>
              <span class="text-muted">·</span>
              <span class="text-apptext font-medium">résistance {{ s.resistance }}</span>
              <span v-if="s.calories" class="text-muted">· {{ s.calories }} kcal</span>
            </template>
            <template v-else>
              <span class="text-apptext font-medium">{{ s.weight_kg }} kg</span>
              <span class="text-muted">×</span>
              <span class="text-apptext font-medium">{{ s.reps }} reps</span>
            </template>
            <span v-if="s.status === 'done'" class="ml-auto text-success text-base">✓</span>
            <span v-if="s.status === 'failed'" class="ml-auto text-danger text-base">✗</span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import ExerciseThumb from '@/components/ui/ExerciseThumb.vue'

const route = useRoute()
const router = useRouter()
const workout = ref(null)
const previousWorkout = ref(null)
const loading = ref(true)
const comparisonLoaded = ref(false)

const justFinished = computed(() => route.query.justFinished === 'true')

const exerciseGroups = computed(() => {
  if (!workout.value?.sets) return []
  const map = new Map()
  for (const s of workout.value.sets) {
    if (!map.has(s.exercise_id)) {
      map.set(s.exercise_id, {
        exercise_id: s.exercise_id,
        exercise_name: s.exercise_name,
        photo_url: s.exercise_photo_url ?? null,
        sets: [],
      })
    }
    map.get(s.exercise_id).sets.push(s)
  }
  return [...map.values()]
})

function totalVolume(sets) {
  return sets.filter(s => s.weight_kg && s.reps).reduce((acc, s) => acc + s.weight_kg * s.reps, 0)
}

const comparison = computed(() => {
  if (!workout.value?.completed_at || !previousWorkout.value?.sets || !workout.value.sets) return null
  const curVol = totalVolume(workout.value.sets)
  const prevVol = totalVolume(previousWorkout.value.sets)
  const curSets = workout.value.sets.filter(s => s.status === 'done').length
  const prevSets = previousWorkout.value.sets.filter(s => s.status === 'done').length
  return {
    deltaVolume: curVol - prevVol,
    deltaSets: curSets - prevSets,
    prevDate: previousWorkout.value.started_at,
  }
})

const finishMessage = computed(() => {
  if (!justFinished.value || !comparisonLoaded.value) return null
  if (!previousWorkout.value) {
    return { text: "Premiere seance de ce type, c'est parti !", positive: true }
  }
  if (!comparison.value) return null
  const { deltaVolume, deltaSets } = comparison.value
  if (deltaVolume > 0) {
    return {
      text: `Belle seance ! Tu as souleve +${Math.round(deltaVolume)} kg de plus que la derniere fois.`,
      positive: true,
    }
  }
  if (deltaSets > 0) {
    return {
      text: `Bien joue ! Tu as reussi ${deltaSets} serie${deltaSets > 1 ? 's' : ''} de plus que la derniere fois.`,
      positive: true,
    }
  }
  return {
    text: "Bonne seance ! Les stats fluctuent, l'important c'est d'y etre.",
    positive: false,
  }
})

function formatDate(d) {
  return new Intl.DateTimeFormat('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date(d))
}

function formatShortDate(d) {
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short' }).format(new Date(d))
}

function formatDelta(val, unit) {
  const sign = val > 0 ? '+' : ''
  return `${sign}${Math.round(val)} ${unit}`
}

async function deleteWorkout() {
  await fetch(`/api/workouts/${route.params.id}`, { method: 'DELETE' })
  router.push('/history')
}

onMounted(async () => {
  const res = await fetch(`/api/workouts/${route.params.id}`)
  workout.value = await res.json()
  loading.value = false

  if (workout.value.completed_at) {
    const prevRes = await fetch(`/api/workouts/${route.params.id}/previous`)
    if (prevRes.ok) previousWorkout.value = await prevRes.json()
  }
  comparisonLoaded.value = true
})
</script>
