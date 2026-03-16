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
    <div class="flex-1 overflow-y-auto overscroll-contain">
      <LoadingSpinner v-if="loading" />
      <div v-else class="p-3">
        <p class="text-[11px] text-muted mb-2">
          Trie: plus utilises d'abord
        </p>
        <div v-if="filtered.length" class="flex flex-col gap-3">
          <button
            v-for="ex in filtered"
            :key="ex.id"
            @click="$emit('select', ex)"
            class="w-full text-left rounded-card border border-apbborder bg-surface overflow-hidden hover:bg-surface2 active:scale-[0.995] transition-all"
          >
            <div class="relative h-36 bg-surface2">
              <img
                v-if="ex.photo_url"
                :src="ex.photo_url"
                :alt="ex.name"
                class="absolute inset-0 w-full h-full object-cover"
                loading="lazy"
              />
              <div
                v-else
                class="absolute inset-0 flex items-center justify-center text-muted text-xs font-medium tracking-wide"
              >
                Aucune photo
              </div>
              <span
                class="absolute top-2 right-2 shrink-0 text-[10px] px-2 py-0.5 rounded-full border backdrop-blur-sm"
                :class="(ex.usage_count || 0) > 0 ? 'border-primary/40 text-primary bg-primary/10' : 'border-apbborder text-muted bg-surface2'"
              >
                {{ (ex.usage_count || 0) > 0 ? `${ex.usage_count} usages` : 'Nouveau' }}
              </span>
            </div>
            <div class="p-3">
              <div class="font-semibold text-apptext text-base leading-tight truncate mb-1">
                {{ ex.name }}
              </div>
              <div class="text-xs text-muted">
                {{ ex.muscle_group }}
              </div>
            </div>
          </button>
        </div>
        <EmptyState
          v-else
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
  return [...list].sort((a, b) => {
    const usageDiff = (b.usage_count || 0) - (a.usage_count || 0)
    if (usageDiff !== 0) return usageDiff
    return a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
  })
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
