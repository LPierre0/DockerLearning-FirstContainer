import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useProfileStore } from './profileStore'

export const useBoostStore = defineStore('boost', () => {
  const unreadBoosts = ref([])
  let pollInterval = null

  async function fetchBoosts() {
    const profileStore = useProfileStore()
    if (!profileStore.userId) return
    try {
      const res = await fetch(`/api/boosts/${profileStore.userId}`)
      if (!res.ok) return
      const boosts = await res.json()
      unreadBoosts.value = boosts.filter(b => !b.read_at)
    } catch {
      // silently ignore network errors during polling
    }
  }

  async function markRead(boostId) {
    await fetch(`/api/boosts/${boostId}/read`, { method: 'PATCH' })
    unreadBoosts.value = unreadBoosts.value.filter(b => b.id !== boostId)
  }

  function startPolling() {
    fetchBoosts()
    pollInterval = setInterval(fetchBoosts, 30_000)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  return { unreadBoosts, fetchBoosts, markRead, startPolling, stopPolling }
})
