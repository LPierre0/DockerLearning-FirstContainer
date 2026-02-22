<template>
  <AppLayout>
    <div class="p-4 max-w-4xl mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-6">Dashboard</h1>

      <LoadingSpinner v-if="loading" />

      <div v-else>
        <!-- User cards grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <div v-for="u in dashboardData.users" :key="u.id" class="flex flex-col gap-3">
            <UserActivityCard
              :user="u"
              :stats="u.stats"
              :recent-workouts="u.recent_workouts"
            />
            <div class="bg-surface rounded-card border border-apbborder p-3">
              <p class="text-xs text-muted mb-2">Activité (13 semaines)</p>
              <ActivityHeatmap :activity="activityByUser[u.id] || {}" />
            </div>
          </div>
        </div>

        <!-- Boost button -->
        <div class="mb-6">
          <BoostButton :users="dashboardData.users" />
        </div>

        <!-- Recent boosts feed -->
        <div v-if="dashboardData.recent_boosts.length" class="bg-surface rounded-card border border-apbborder p-4">
          <h2 class="text-sm font-semibold text-apptext mb-3">Boosts récents</h2>
          <div class="space-y-2">
            <div
              v-for="b in dashboardData.recent_boosts"
              :key="b.id"
              class="flex items-start gap-3 text-sm"
            >
              <AppIcon name="bolt" :size="16" class="text-primary shrink-0 mt-0.5" />
              <div>
                <span class="font-medium text-primary">{{ b.from_name }}</span>
                <span class="text-muted"> : </span>
                <span class="text-apptext">{{ b.message }}</span>
              </div>
              <span class="text-xs text-muted ml-auto shrink-0">{{ formatDate(b.sent_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import UserActivityCard from '@/components/dashboard/UserActivityCard.vue'
import BoostButton from '@/components/dashboard/BoostButton.vue'
import ActivityHeatmap from '@/components/dashboard/ActivityHeatmap.vue'

const dashboardData = ref(null)
const loading = ref(true)
const activityByUser = ref({})

function formatDate(d) {
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(d))
}

onMounted(async () => {
  const res = await fetch('/api/dashboard')
  dashboardData.value = await res.json()
  loading.value = false

  const users = dashboardData.value.users || []
  const results = await Promise.all(
    users.map(u => fetch(`/api/users/${u.id}/activity`).then(r => r.json()).then(data => ({ id: u.id, data })))
  )
  const map = {}
  for (const { id, data } of results) map[id] = data
  activityByUser.value = map
})
</script>
