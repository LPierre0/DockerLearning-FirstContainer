import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProfileStore = defineStore('profile', () => {
  const userId   = ref(null)
  const userName = ref(null)
  const themeKey = ref(null)

  function selectProfile(user) {
    userId.value   = user.id
    userName.value = user.name
    themeKey.value = user.theme_key
    localStorage.setItem('fitness_profile', JSON.stringify(user))
    applyTheme(user.theme_key)
  }

  function applyTheme(key) {
    document.documentElement.setAttribute('data-theme', key)
  }

  function loadFromStorage() {
    const saved = localStorage.getItem('fitness_profile')
    if (saved) {
      const user = JSON.parse(saved)
      userId.value   = user.id
      userName.value = user.name
      themeKey.value = user.theme_key
      applyTheme(user.theme_key)
      return true
    }
    return false
  }

  function logout() {
    userId.value = null
    userName.value = null
    themeKey.value = null
    localStorage.removeItem('fitness_profile')
    document.documentElement.removeAttribute('data-theme')
  }

  return { userId, userName, themeKey, selectProfile, loadFromStorage, logout }
})
