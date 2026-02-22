<template>
  <AppLayout>
    <div class="p-4 max-w-lg mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-2">Nouvelle séance</h1>
      <p class="text-muted text-sm mb-6">Choisis le type de séance</p>

      <div class="grid grid-cols-2 gap-3">
        <div
          v-for="type in workoutTypes"
          :key="type.label"
          class="rounded-card border-2 border-apbborder bg-surface overflow-hidden"
        >
          <!-- Main create button -->
          <button
            @click="create(type.label)"
            :disabled="creating"
            class="w-full flex items-center justify-center p-5 hover:border-primary hover:bg-primary/5 active:scale-95 transition-all disabled:opacity-50"
          >
            <span class="font-bold text-base text-apptext">{{ type.label }}</span>
          </button>

          <!-- Reprendre last template -->
          <button
            v-if="lastWorkouts[type.label]"
            @click="createFromTemplate(type.label, lastWorkouts[type.label].id)"
            :disabled="creating"
            class="w-full border-t border-apbborder px-3 py-2 text-left hover:bg-primary/5 disabled:opacity-50 transition-colors"
          >
            <span class="text-xs text-primary font-medium block">↩ Reprendre</span>
            <span class="text-[11px] text-muted">
              {{ lastWorkouts[type.label].set_count }} séries ·
              {{ formatAgo(lastWorkouts[type.label].completed_at) }}
            </span>
          </button>
        </div>
      </div>

      <p v-if="error" class="mt-4 text-sm text-danger">{{ error }}</p>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'
import { useWorkoutStore } from '@/stores/workoutStore'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = useRouter()
const profileStore = useProfileStore()
const workoutStore = useWorkoutStore()

const creating = ref(false)
const error = ref(null)
const lastWorkouts = ref({})

const workoutTypes = [
  { label: 'Push' },
  { label: 'Pull' },
  { label: 'Legs' },
  { label: 'Full Body' },
  { label: 'Cardio' },
  { label: 'Custom' },
]

onMounted(async () => {
  // Fetch last workout for each type in parallel (silently ignore 404s)
  await Promise.all(
    workoutTypes.map(async ({ label }) => {
      try {
        const res = await fetch(`/api/workouts/last?user_id=${profileStore.userId}&type=${encodeURIComponent(label)}`)
        if (res.ok) lastWorkouts.value[label] = await res.json()
      } catch { /* ignore */ }
    })
  )
})

function formatAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "aujourd'hui"
  if (days === 1) return 'hier'
  return `il y a ${days}j`
}

async function create(type, templateId = null) {
  creating.value = true
  error.value = null
  try {
    const body = { user_id: profileStore.userId, type }
    if (templateId) body.template_id = templateId
    const res = await fetch('/api/workouts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error()
    const workout = await res.json()
    workoutStore.setActive(workout.id, workout.type)
    router.push(`/workout/active/${workout.id}`)
  } catch {
    error.value = 'Impossible de créer la séance.'
  } finally {
    creating.value = false
  }
}

function createFromTemplate(type, templateId) {
  create(type, templateId)
}
</script>
