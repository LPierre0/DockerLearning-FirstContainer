<template>
  <div class="min-h-dvh bg-bg flex flex-col items-center justify-center p-6">
    <div class="text-center mb-12">
      <h1 class="text-3xl font-bold text-apptext mb-2">FitCouple</h1>
      <p class="text-muted">Qui s'entraîne aujourd'hui ?</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="flex flex-col sm:flex-row gap-6 w-full max-w-sm sm:max-w-md">
      <button
        v-for="user in users"
        :key="user.id"
        @click="select(user)"
        class="flex-1 flex flex-col items-center justify-center gap-4 p-8 rounded-card border-2 transition-all duration-200 cursor-pointer"
        :class="user.theme_key === 'pierre'
          ? 'bg-slate-900 border-indigo-500 hover:border-indigo-400 hover:scale-105 text-slate-200'
          : 'bg-pink-50 border-pink-400 hover:border-pink-500 hover:scale-105 text-purple-900'"
      >
        <div
          class="w-16 h-16 rounded-full flex items-center justify-center text-3xl font-bold text-white"
          :class="user.theme_key === 'pierre' ? 'bg-indigo-500' : 'bg-pink-400'"
        >
          {{ user.name[0].toUpperCase() }}
        </div>
        <span class="text-xl font-semibold">{{ user.name }}</span>
      </button>
    </div>

    <p v-if="error" class="mt-8 text-sm text-red-400">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/profileStore'
import { useBoostStore } from '@/stores/boostStore'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const router = useRouter()
const profileStore = useProfileStore()
const boostStore = useBoostStore()

const users = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const res = await fetch('/api/users')
    users.value = await res.json()
  } catch {
    error.value = 'Impossible de charger les profils. Vérifie que le backend est lancé.'
  } finally {
    loading.value = false
  }
})

function select(user) {
  profileStore.selectProfile(user)
  boostStore.startPolling()
  router.push('/dashboard')
}
</script>
