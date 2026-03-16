<template>
  <div class="flex flex-col h-full">
    <!-- Search -->
    <div class="p-4 border-b border-apbborder">
      <input
        v-model="search"
        type="text"
        placeholder="Rechercher un exercice..."
        class="w-full bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
      />
    </div>

    <!-- Muscle group tabs -->
    <div class="flex gap-1 px-4 py-2 overflow-x-auto border-b border-apbborder scrollbar-none">
      <button
        v-for="group in muscleGroups"
        :key="group"
        @click="activeGroup = group"
        class="shrink-0 px-3 py-1 text-xs rounded-btn transition-colors"
        :class="activeGroup === group ? 'bg-primary text-white' : 'bg-surface2 text-muted hover:text-apptext border border-apbborder'"
      >
        {{ group }}
      </button>
    </div>

    <!-- Exercise list -->
    <div class="flex-1 overflow-y-auto">
      <LoadingSpinner v-if="loading" />
      <div v-else>
        <button
          v-for="ex in filtered"
          :key="ex.id"
          @click="$emit('select', ex)"
          class="w-full text-left px-4 py-3 border-b border-apbborder/50 hover:bg-surface2 transition-colors"
        >
          <div class="flex items-center gap-3">
            <ExerciseThumb :src="ex.photo_url" :alt="ex.name" :size="38" />
            <div class="min-w-0">
              <div class="font-medium text-apptext text-sm truncate">{{ ex.name }}</div>
              <div class="text-xs text-muted">{{ ex.muscle_group }}</div>
            </div>
          </div>
        </button>
        <EmptyState
          v-if="!filtered.length"
          icon="🔍"
          message="Aucun exercice trouvé."
        />
      </div>
    </div>

    <!-- Footer : créer un exercice -->
    <div class="border-t border-apbborder p-3 shrink-0">
      <div v-if="!showCreate">
        <button
          @click="showCreate = true"
          class="w-full py-2 text-sm text-primary border border-primary/40 rounded-btn hover:bg-primary/10 transition-colors"
        >
          + Créer un exercice
        </button>
      </div>
      <div v-else class="flex flex-col gap-2">
        <input
          v-model="newName"
          type="text"
          placeholder="Nom de l'exercice"
          class="bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <select
          v-model="newGroup"
          class="bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none"
        >
          <option value="" disabled>Groupe musculaire</option>
          <option v-for="g in realGroups" :key="g" :value="g">{{ g }}</option>
        </select>
        <div class="flex gap-2">
          <button
            @click="createExercise"
            :disabled="!newName.trim() || !newGroup || creating"
            class="flex-1 py-2 bg-primary text-white rounded-btn text-sm font-semibold disabled:opacity-50"
          >
            {{ creating ? '...' : 'Créer' }}
          </button>
          <button
            @click="showCreate = false; newName = ''; newGroup = ''"
            class="px-4 py-2 border border-apbborder rounded-btn text-sm text-muted"
          >
            Annuler
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ExerciseThumb from '@/components/ui/ExerciseThumb.vue'

const emit = defineEmits(['select'])

const profileStore = useProfileStore()
const exercises = ref([])
const loading = ref(true)
const search = ref('')
const activeGroup = ref('Tous')

const muscleGroups = ['Tous', 'Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Cardio']
const realGroups = muscleGroups.slice(1)

const showCreate = ref(false)
const newName = ref('')
const newGroup = ref('')
const creating = ref(false)

const filtered = computed(() => {
  let list = exercises.value
  if (activeGroup.value !== 'Tous') {
    list = list.filter(e => e.muscle_group === activeGroup.value)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(e => e.name.toLowerCase().includes(q))
  }
  return list
})

onMounted(async () => {
  const res = await fetch(`/api/exercises?user_id=${profileStore.userId}`)
  exercises.value = await res.json()
  loading.value = false
})

async function createExercise() {
  if (!newName.value.trim() || !newGroup.value) return
  creating.value = true
  const res = await fetch('/api/exercises', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: newName.value.trim(),
      muscle_group: newGroup.value,
      created_by: profileStore.userId,
    }),
  })
  const created = await res.json()
  exercises.value.push(created)
  showCreate.value = false
  newName.value = ''
  newGroup.value = ''
  creating.value = false
  emit('select', created)
}
</script>
