<template>
  <span class="font-mono text-sm text-muted">{{ formatted }}</span>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps({
  startedAt: { type: String, required: true },
})

const elapsed = ref(0)
let timer = null

// Backend returns naive UTC strings (no timezone suffix).
// Appending 'Z' tells the browser to treat them as UTC,
// preventing a +1h offset in UTC+1 timezones.
function toUTC(str) {
  if (!str) return str
  return /[Z+]/.test(str) ? str : str + 'Z'
}

onMounted(() => {
  const start = new Date(toUTC(props.startedAt)).getTime()
  function tick() {
    elapsed.value = Math.floor((Date.now() - start) / 1000)
  }
  tick()
  timer = setInterval(tick, 1000)
})

onUnmounted(() => clearInterval(timer))

const formatted = computed(() => {
  const total = Math.max(0, elapsed.value)
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  if (h > 0) return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
  return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
})
</script>
