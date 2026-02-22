<template>
  <Teleport to="body">
    <div
      v-for="boost in boostStore.unreadBoosts"
      :key="boost.id"
      class="fixed top-4 left-1/2 -translate-x-1/2 z-[100] w-80 bg-surface border border-primary/50 rounded-card shadow-xl p-4 animate-bounce-in"
    >
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1">
          <p class="text-xs font-semibold text-primary mb-1">Boost de {{ boost.from_name }} !</p>
          <p class="text-sm text-apptext">{{ boost.message }}</p>
        </div>
        <button
          @click="boostStore.markRead(boost.id)"
          class="text-muted hover:text-apptext text-lg leading-none mt-0.5"
        >
          ×
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useBoostStore } from '@/stores/boostStore'
const boostStore = useBoostStore()
</script>

<style scoped>
@keyframes bounceIn {
  0% { transform: translateX(-50%) translateY(-20px); opacity: 0; }
  70% { transform: translateX(-50%) translateY(4px); }
  100% { transform: translateX(-50%) translateY(0); opacity: 1; }
}
.animate-bounce-in {
  animation: bounceIn 0.4s ease-out forwards;
}
</style>
