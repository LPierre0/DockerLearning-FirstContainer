<template>
  <div
    class="shrink-0 rounded-lg overflow-hidden border border-apbborder bg-surface2 flex items-center justify-center"
    :style="{ width: `${size}px`, height: `${size}px` }"
  >
    <img
      v-if="safeSrc"
      :src="safeSrc"
      :alt="alt"
      class="w-full h-full object-cover"
      loading="lazy"
      @error="hasError = true"
    />
    <span v-else class="text-[10px] font-semibold tracking-wide text-muted">EX</span>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  src: { type: String, default: null },
  alt: { type: String, default: 'Exercise photo' },
  size: { type: Number, default: 44 },
})

const hasError = ref(false)

watch(() => props.src, () => {
  hasError.value = false
})

const safeSrc = computed(() => (props.src && !hasError.value ? props.src : null))
</script>
