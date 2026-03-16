<template>
  <div class="flex items-center justify-between px-3 py-2 bg-primary/10 border border-primary/30 rounded-card text-sm">
    <div class="flex items-center gap-3">
      <span class="text-primary font-bold tabular-nums text-base">{{ formatted }}</span>
      <span class="text-xs text-muted">Repos</span>
    </div>
    <div class="flex items-center gap-2">
      <button @click="adjust(-15)" class="text-xs text-muted hover:text-apptext px-1">−15s</button>
      <button @click="adjust(+15)" class="text-xs text-muted hover:text-apptext px-1">+15s</button>
      <button @click="$emit('skip')" class="text-xs text-primary hover:text-primary/70 font-medium px-2 py-0.5 rounded-btn border border-primary/30">
        Skip
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  duration: { type: Number, default: 90 },
})

const emit = defineEmits(['skip', 'done'])

let endTime = Date.now() + props.duration * 1000
const remaining = ref(props.duration)
let timer = null

const formatted = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

function tick() {
  const r = Math.ceil((endTime - Date.now()) / 1000)
  remaining.value = Math.max(0, r)
  if (remaining.value <= 0) {
    clearInterval(timer)
    emit('done')
  }
}

function adjust(delta) {
  endTime += delta * 1000
  remaining.value = Math.max(5, Math.ceil((endTime - Date.now()) / 1000))
}

onMounted(() => {
  tick()
  timer = setInterval(tick, 500)
  document.addEventListener('visibilitychange', tick)
})

onUnmounted(() => {
  clearInterval(timer)
  document.removeEventListener('visibilitychange', tick)
})
</script>
