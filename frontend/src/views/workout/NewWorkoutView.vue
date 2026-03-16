<template>
  <AppLayout>
    <div class="p-4 max-w-lg mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-2">Nouvelle séance</h1>
      <p class="text-muted text-sm mb-6">Choisis le type de séance</p>

      <!-- ─── Favoris ─────────────────────────────────────────────────────────── -->
      <div v-if="favorites.length" class="mb-6">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-sm font-semibold text-muted uppercase tracking-wide">Favoris</h2>
          <button
            @click="showNewFavorite = true"
            class="text-xs text-primary hover:text-primary/70 font-medium"
          >+ Nouveau</button>
        </div>
        <div class="space-y-2">
          <div
            v-for="fav in favorites"
            :key="fav.id"
            class="flex items-center rounded-card border border-apbborder bg-surface overflow-hidden"
          >
            <button
              @click="launchFavorite(fav)"
              :disabled="creating"
              class="flex-1 flex items-center gap-3 px-4 py-3 text-left hover:bg-primary/5 disabled:opacity-50 transition-colors"
            >
              <div>
                <span class="font-semibold text-apptext block">{{ fav.name }}</span>
                <span class="text-xs text-muted">
                  {{ fav.workout_type }}
                  <template v-if="lastWorkouts[fav.workout_type]">
                    · {{ formatAgo(lastWorkouts[fav.workout_type].completed_at) }}
                  </template>
                </span>
              </div>
            </button>
            <button
              @click="deleteFavorite(fav.id)"
              class="px-3 py-3 text-muted hover:text-danger transition-colors shrink-0"
              title="Supprimer le favori"
            >×</button>
          </div>
        </div>
      </div>

      <div v-else class="mb-4">
        <button
          @click="showNewFavorite = true"
          class="w-full text-sm text-muted hover:text-primary border border-dashed border-apbborder rounded-card py-3 transition-colors"
        >
          + Créer un favori
        </button>
      </div>

      <!-- ─── Types ──────────────────────────────────────────────────────────── -->
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

    <!-- ─── Modal nouveau favori ─────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="backdrop">
        <div
          v-if="showNewFavorite"
          class="fixed inset-0 z-50 bg-black/50"
          @click="showNewFavorite = false"
        />
      </Transition>
      <Transition name="sheet">
        <div
          v-if="showNewFavorite"
          class="fixed inset-x-0 bottom-0 z-[51] lg:inset-0 lg:flex lg:items-center lg:justify-center"
        >
          <div class="w-full lg:w-96 bg-surface rounded-t-2xl lg:rounded-card p-6">
            <h2 class="font-semibold text-apptext mb-4">Nouveau favori</h2>
            <div class="space-y-3">
              <input
                v-model="newFavName"
                type="text"
                placeholder="Nom (ex: Push A, Pull cardio…)"
                class="w-full px-3 py-2 rounded-btn border border-apbborder bg-background text-apptext placeholder:text-muted/50 outline-none focus:border-primary text-sm"
                autofocus
              />
              <select
                v-model="newFavType"
                class="w-full px-3 py-2 rounded-btn border border-apbborder bg-background text-apptext outline-none focus:border-primary text-sm"
              >
                <option v-for="type in workoutTypes" :key="type.label" :value="type.label">
                  {{ type.label }}
                </option>
              </select>
            </div>
            <div class="flex gap-2 mt-4">
              <button
                @click="showNewFavorite = false"
                class="flex-1 py-2 rounded-btn border border-apbborder text-muted text-sm hover:text-apptext"
              >Annuler</button>
              <button
                @click="saveFavorite"
                :disabled="!newFavName.trim()"
                class="flex-1 py-2 rounded-btn bg-primary text-white text-sm font-medium disabled:opacity-50"
              >Créer</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
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
const favorites = ref([])

const showNewFavorite = ref(false)
const newFavName = ref('')
const newFavType = ref('Push')

const workoutTypes = [
  { label: 'Push' },
  { label: 'Pull' },
  { label: 'Legs' },
  { label: 'Full Body' },
  { label: 'Cardio' },
  { label: 'Custom' },
]

onMounted(async () => {
  await Promise.all([
    loadFavorites(),
    ...workoutTypes.map(async ({ label }) => {
      try {
        const res = await fetch(`/api/workouts/last?user_id=${profileStore.userId}&type=${encodeURIComponent(label)}`)
        if (res.ok) lastWorkouts.value[label] = await res.json()
      } catch { /* ignore */ }
    }),
  ])
})

async function loadFavorites() {
  try {
    const res = await fetch(`/api/favorites?user_id=${profileStore.userId}`)
    if (res.ok) favorites.value = await res.json()
  } catch { /* ignore */ }
}

function formatAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return "aujourd'hui"
  if (days === 1) return 'hier'
  return `il y a ${days}j`
}

async function create(type, templateId = null, name = null) {
  creating.value = true
  error.value = null
  try {
    const body = { user_id: profileStore.userId, type }
    if (templateId) body.template_id = templateId
    if (name) body.name = name
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

async function launchFavorite(fav) {
  const last = lastWorkouts.value[fav.workout_type]
  if (last) {
    await create(fav.workout_type, last.id, fav.name)
  } else {
    await create(fav.workout_type, null, fav.name)
  }
}

async function saveFavorite() {
  if (!newFavName.value.trim()) return
  try {
    const res = await fetch('/api/favorites', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: profileStore.userId,
        name: newFavName.value.trim(),
        workout_type: newFavType.value,
      }),
    })
    if (res.ok) {
      await loadFavorites()
      showNewFavorite.value = false
      newFavName.value = ''
      newFavType.value = 'Push'
    }
  } catch { /* ignore */ }
}

async function deleteFavorite(id) {
  try {
    await fetch(`/api/favorites/${id}`, { method: 'DELETE' })
    favorites.value = favorites.value.filter(f => f.id !== id)
  } catch { /* ignore */ }
}
</script>
