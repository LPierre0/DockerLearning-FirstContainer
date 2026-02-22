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
          <div class="font-medium text-apptext text-sm">{{ ex.name }}</div>
          <div class="text-xs text-muted">{{ ex.muscle_group }}</div>
        </button>
        <EmptyState
          v-if="!filtered.length"
          icon="🔍"
          message="Aucun exercice trouvé."
        />
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
</script>
