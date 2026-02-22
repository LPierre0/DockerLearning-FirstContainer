<template>
  <button
    :class="[
      'inline-flex items-center justify-center font-medium rounded-btn transition-all duration-150',
      'focus:outline-none focus:ring-2 focus:ring-primary/50',
      sizeClasses,
      variantClasses,
      { 'opacity-50 cursor-not-allowed': disabled },
    ]"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    // primary | secondary | ghost | danger | success
  },
  size: {
    type: String,
    default: 'md',
    // sm | md | lg | xl
  },
  disabled: Boolean,
})

const sizeClasses = computed(() => ({
  sm: 'p-2 text-sm gap-1',
  md: 'px-4 py-2.5 text-sm gap-2',
  lg: 'px-6 py-3 text-base gap-2',
  xl: 'px-8 py-4 text-lg gap-3',
}[props.size]))

const variantClasses = computed(() => ({
  primary: 'bg-primary text-white hover:opacity-90 active:scale-95',
  secondary: 'bg-surface2 text-apptext border border-apbborder hover:bg-primary/10 active:scale-95',
  ghost: 'text-apptext hover:bg-surface2 active:scale-95',
  danger: 'bg-danger text-white hover:opacity-90 active:scale-95',
  success: 'bg-success text-white hover:opacity-90 active:scale-95',
}[props.variant]))
</script>
