<template>
  <RouterView />
  <BoostNotification />
</template>

<script setup>
import { onMounted } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import { useBoostStore } from '@/stores/boostStore'
import BoostNotification from '@/components/dashboard/BoostNotification.vue'

const profileStore = useProfileStore()
const boostStore = useBoostStore()

onMounted(() => {
  profileStore.loadFromStorage()
  if (profileStore.userId) {
    boostStore.startPolling()
  }
})
</script>
