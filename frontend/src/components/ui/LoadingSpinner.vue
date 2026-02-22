<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div
      class="animate-spin rounded-full border-2 border-current border-t-transparent"
      :class="sizeClass"
      style="color: rgb(var(--color-primary))"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: { type: String, default: 'md' },
  fullPage: { type: Boolean, default: false },
})

const sizeClass = computed(() => ({
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
}[props.size]))

const containerClass = computed(() =>
  props.fullPage ? 'min-h-screen' : 'py-8'
)
</script>
