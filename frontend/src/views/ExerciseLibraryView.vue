<template>
  <AppLayout>
    <div class="p-4 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-2">Exercices</h1>
      <p class="text-sm text-muted mb-6">Bibliothèque complète + tes exercices personnalisés</p>

      <!-- Search + filter -->
      <div class="flex gap-2 mb-4">
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher..."
          class="flex-1 bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
      </div>

      <!-- Muscle group filter -->
      <div class="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-none">
        <button
          v-for="group in muscleGroups"
          :key="group"
          @click="activeGroup = group"
          class="shrink-0 px-3 py-1 text-xs rounded-btn transition-colors"
          :class="activeGroup === group ? 'bg-primary text-white' : 'bg-surface border border-apbborder text-muted hover:text-apptext'"
        >
          {{ group }}
        </button>
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else class="space-y-1 mb-8">
        <div
          v-for="ex in filtered"
          :key="ex.id"
          class="flex items-center justify-between px-4 py-3 bg-surface rounded-card border border-apbborder"
        >
          <div>
            <span class="font-medium text-apptext text-sm">{{ ex.name }}</span>
            <span class="ml-2 text-xs text-muted">{{ ex.muscle_group }}</span>
          </div>
          <button
            v-if="ex.is_custom && ex.created_by === profileStore.userId"
            @click="deleteExercise(ex.id)"
            class="text-muted hover:text-danger text-sm"
          >
            🗑
          </button>
        </div>
        <EmptyState v-if="!filtered.length" icon="🔍" message="Aucun exercice trouvé." />
      </div>

      <!-- Add custom exercise form -->
      <div class="bg-surface border border-apbborder rounded-card p-4">
        <h2 class="font-semibold text-apptext mb-4">Ajouter un exercice</h2>
        <div class="flex flex-col gap-3">
          <input
            v-model="newName"
            type="text"
            placeholder="Nom de l'exercice"
            class="bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
          <select
            v-model="newGroup"
            class="bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="" disabled>Groupe musculaire</option>
            <option v-for="g in realGroups" :key="g" :value="g">{{ g }}</option>
          </select>
          <button
            @click="addExercise"
            :disabled="!newName.trim() || !newGroup"
            class="py-2 bg-primary text-white rounded-btn text-sm font-semibold disabled:opacity-50"
          >
            Ajouter
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const profileStore = useProfileStore()
const exercises = ref([])
const loading = ref(true)
const search = ref('')
const activeGroup = ref('Tous')
const newName = ref('')
const newGroup = ref('')

const muscleGroups = ['Tous', 'Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Cardio']
const realGroups = muscleGroups.slice(1)

const filtered = computed(() => {
  let list = exercises.value
  if (activeGroup.value !== 'Tous') list = list.filter(e => e.muscle_group === activeGroup.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(e => e.name.toLowerCase().includes(q))
  }
  return list
})

async function load() {
  const res = await fetch(`/api/exercises?user_id=${profileStore.userId}`)
  exercises.value = await res.json()
}

async function addExercise() {
  if (!newName.value.trim() || !newGroup.value) return
  await fetch('/api/exercises', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: newName.value.trim(),
      muscle_group: newGroup.value,
      created_by: profileStore.userId,
    }),
  })
  newName.value = ''
  newGroup.value = ''
  await load()
}

async function deleteExercise(id) {
  await fetch(`/api/exercises/${id}?user_id=${profileStore.userId}`, { method: 'DELETE' })
  await load()
}

onMounted(async () => {
  await load()
  loading.value = false
})
</script>
