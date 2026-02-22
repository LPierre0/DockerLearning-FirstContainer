<template>
  <button
    @click="sendBoost"
    :disabled="sending || !partnerName"
    class="w-full flex items-center justify-center gap-3 py-4 bg-primary text-white rounded-card text-base font-semibold shadow-lg active:scale-95 transition-all disabled:opacity-50"
  >
    <AppIcon name="bolt" :size="20" />
    <span>Boost {{ partnerName }}</span>
  </button>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  users: { type: Array, required: true },
})

const profileStore = useProfileStore()
const sending = ref(false)

const partner = computed(() => props.users.find(u => u.id !== profileStore.userId))
const partnerName = computed(() => partner.value?.name ?? '')

const BOOST_MESSAGES = [
  'Tu déchires ! Vas-y !',
  "T'es un(e) champion(ne) !",
  'Allez, encore un effort !',
  'Fier(e) de toi ! Keep going !',
  'La forme est là !',
  'Beast mode ON !',
]

async function sendBoost() {
  if (!partner.value) return
  sending.value = true
  try {
    await fetch('/api/boosts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from_user_id: profileStore.userId,
        to_user_id: partner.value.id,
        message: BOOST_MESSAGES[Math.floor(Math.random() * BOOST_MESSAGES.length)],
      }),
    })
  } finally {
    sending.value = false
  }
}
</script>
