import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWorkoutStore = defineStore('workout', () => {
  const activeWorkoutId = ref(null)
  const activeWorkoutType = ref(null)

  function setActive(id, type) {
    activeWorkoutId.value = id
    activeWorkoutType.value = type
    localStorage.setItem('active_workout', JSON.stringify({ id, type }))
  }

  function clearActive() {
    activeWorkoutId.value = null
    activeWorkoutType.value = null
    localStorage.removeItem('active_workout')
  }

  function loadFromStorage() {
    const saved = localStorage.getItem('active_workout')
    if (saved) {
      const { id, type } = JSON.parse(saved)
      activeWorkoutId.value = id
      activeWorkoutType.value = type
      return true
    }
    return false
  }

  return { activeWorkoutId, activeWorkoutType, setActive, clearActive, loadFromStorage }
})
