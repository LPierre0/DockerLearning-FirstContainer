<template>
  <RouterView />
  <BoostNotification />
</template>

<script setup>
import { onMounted } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import { useBoostStore } from '@/stores/boostStore'
import { useWorkoutStore } from '@/stores/workoutStore'
import BoostNotification from '@/components/dashboard/BoostNotification.vue'

const profileStore = useProfileStore()
const boostStore = useBoostStore()
const workoutStore = useWorkoutStore()

onMounted(() => {
  profileStore.loadFromStorage()
  workoutStore.loadFromStorage()
  if (profileStore.userId) {
    boostStore.startPolling()
  }
})
</script>
