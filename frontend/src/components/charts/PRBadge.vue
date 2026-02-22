<template>
  <div
    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-btn text-xs font-bold"
    :class="bgClass"
  >
    🏆 {{ weightKg }} kg × {{ reps }} reps
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  weightKg: { type: Number, required: true },
  reps: { type: Number, required: true },
})

const bgClass = computed(() => 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400')
</script>
