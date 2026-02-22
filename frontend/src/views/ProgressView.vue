<template>
  <AppLayout>
    <div class="p-4 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-2">Progression</h1>
      <p class="text-sm text-muted mb-6">Tes records personnels</p>

      <LoadingSpinner v-if="loading" />

      <div v-else-if="prs.length" class="space-y-2">
        <RouterLink
          v-for="pr in prs"
          :key="pr.exercise_id"
          :to="`/progress/${pr.exercise_id}`"
          class="flex items-center justify-between p-4 bg-surface rounded-card border border-apbborder hover:border-primary/50 transition-colors"
        >
          <div>
            <div class="font-medium text-apptext text-sm">{{ pr.exercise_name }}</div>
            <div class="text-xs text-muted">{{ pr.muscle_group }}</div>
          </div>
          <PRBadge v-if="pr.weight_kg" :weight-kg="pr.weight_kg" :reps="pr.reps ?? 0" />
        </RouterLink>
      </div>

      <EmptyState
        v-else
        icon="📈"
        message="Commence à t'entraîner pour voir ta progression !"
      />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import PRBadge from '@/components/charts/PRBadge.vue'

const profileStore = useProfileStore()
const prs = ref([])
const loading = ref(true)

onMounted(async () => {
  const res = await fetch(`/api/progress/${profileStore.userId}/prs`)
  prs.value = await res.json()
  loading.value = false
})
</script>
