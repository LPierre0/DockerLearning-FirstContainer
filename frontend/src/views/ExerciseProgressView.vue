<template>
  <AppLayout>
    <div class="p-4 max-w-2xl mx-auto">
      <RouterLink to="/progress" class="inline-flex items-center gap-1 text-sm text-muted hover:text-apptext mb-4">
        ← Retour
      </RouterLink>

      <LoadingSpinner v-if="loading" size="lg" />

      <div v-else-if="data">
        <div class="mb-6 flex items-center gap-3">
          <ExerciseThumb :src="data.exercise.photo_url" :alt="data.exercise.name" :size="54" />
          <div>
            <h1 class="text-xl font-bold text-apptext">{{ data.exercise.name }}</h1>
            <span class="text-xs text-muted">{{ data.exercise.muscle_group }}</span>
          </div>
        </div>

        <!-- PR Banner -->
        <div
          v-if="data.pr"
          class="flex items-center gap-3 p-4 bg-surface rounded-card border border-apbborder mb-6"
        >
          <span class="text-2xl">🏆</span>
          <div>
            <div class="text-xs text-muted font-medium mb-0.5">Record personnel</div>
            <PRBadge :weight-kg="data.pr.weight_kg" :reps="data.pr.reps ?? 0" />
          </div>
        </div>

        <!-- Chart -->
        <div v-if="chartLabels.length" class="bg-surface rounded-card border border-apbborder p-4 mb-6">
          <h2 class="text-sm font-semibold text-apptext mb-4">Charge maximale par séance</h2>
          <ProgressChart :labels="chartLabels" :dataset="chartDataset" :label="data.exercise.name" />
        </div>

        <!-- Recent sets table -->
        <div class="bg-surface rounded-card border border-apbborder p-4">
          <h2 class="text-sm font-semibold text-apptext mb-3">Dernières séances</h2>
          <div v-if="data.history.length" class="space-y-2">
            <div
              v-for="entry in data.history.slice().reverse().slice(0, 10)"
              :key="entry.date"
              class="flex items-center justify-between text-sm"
            >
              <span class="text-muted text-xs">{{ formatDate(entry.date) }}</span>
              <span class="text-apptext font-medium">{{ entry.max_weight ?? '-' }} kg</span>
              <span class="text-muted text-xs">Vol. {{ Math.round(entry.total_volume ?? 0) }} kg</span>
            </div>
          </div>
          <EmptyState v-else icon="📊" message="Pas encore de données." />
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import PRBadge from '@/components/charts/PRBadge.vue'
import ProgressChart from '@/components/charts/ProgressChart.vue'
import ExerciseThumb from '@/components/ui/ExerciseThumb.vue'

const route = useRoute()
const profileStore = useProfileStore()
const data = ref(null)
const loading = ref(true)

const chartLabels = computed(() =>
  data.value?.history.map(e => formatDate(e.date)) ?? []
)
const chartDataset = computed(() =>
  data.value?.history.map(e => e.max_weight ?? 0) ?? []
)

function formatDate(d) {
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short' }).format(new Date(d))
}

onMounted(async () => {
  const res = await fetch(`/api/progress/${profileStore.userId}/exercise/${route.params.id}`)
  data.value = await res.json()
  loading.value = false
})
</script>
