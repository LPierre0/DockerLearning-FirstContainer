<template>
  <AppLayout>
    <div class="p-4 max-w-2xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-apptext">Historique</h1>
        <a
          :href="`/api/workouts/export?user_id=${profileStore.userId}`"
          download="workouts.csv"
          class="text-xs text-muted hover:text-primary border border-apbborder hover:border-primary/50 px-3 py-1.5 rounded-btn transition-colors"
        >
          Exporter CSV
        </a>
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else-if="workouts.length" class="space-y-3">
        <div
          v-for="w in workouts"
          :key="w.id"
          class="relative"
        >
          <RouterLink :to="`/history/${w.id}`">
            <WorkoutCard :workout="w" />
          </RouterLink>
          <button
            @click.prevent="deleteWorkout(w.id)"
            class="absolute bottom-3 right-3 p-1 rounded text-muted hover:text-danger transition-colors"
            title="Supprimer la séance"
          >
            <AppIcon name="trash" :size="16" />
          </button>
        </div>

        <button
          v-if="hasMore"
          @click="loadMore"
          :disabled="loadingMore"
          class="w-full py-3 text-sm text-primary border border-primary/30 rounded-card hover:bg-primary/5 disabled:opacity-50"
        >
          {{ loadingMore ? 'Chargement...' : 'Voir plus' }}
        </button>
      </div>

      <EmptyState
        v-else
        icon="clock"
        message="Pas encore de séances. Lance ta première séance !"
      >
        <RouterLink
          to="/workout/new"
          class="mt-2 inline-block px-4 py-2 bg-primary text-white rounded-btn text-sm"
        >
          Commencer
        </RouterLink>
      </EmptyState>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import WorkoutCard from '@/components/ui/WorkoutCard.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const profileStore = useProfileStore()
const workouts = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const offset = ref(0)
const LIMIT = 20
const hasMore = ref(false)

async function load(reset = false) {
  const o = reset ? 0 : offset.value
  const res = await fetch(`/api/workouts?user_id=${profileStore.userId}&limit=${LIMIT}&offset=${o}`)
  const data = await res.json()
  if (reset) workouts.value = data
  else workouts.value.push(...data)
  hasMore.value = data.length === LIMIT
  offset.value = o + data.length
}

async function loadMore() {
  loadingMore.value = true
  await load()
  loadingMore.value = false
}

async function deleteWorkout(id) {
  await fetch(`/api/workouts/${id}`, { method: 'DELETE' })
  workouts.value = workouts.value.filter(w => w.id !== id)
  offset.value = Math.max(0, offset.value - 1)
}

onMounted(async () => {
  await load(true)
  loading.value = false
})
</script>
