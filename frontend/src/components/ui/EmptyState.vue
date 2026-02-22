<template>
  <div class="flex flex-col items-center justify-center gap-4 py-14 text-center">
    <div class="w-14 h-14 rounded-full bg-surface2 flex items-center justify-center shrink-0">
      <AppIcon :name="icon" :size="24" class="text-muted" />
    </div>
    <div class="space-y-1">
      <p class="text-apptext text-sm font-medium">{{ message }}</p>
      <p v-if="sub" class="text-muted text-xs">{{ sub }}</p>
    </div>
    <slot />
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  icon:    { type: String, default: 'inbox' },
  message: { type: String, default: 'Rien à afficher pour le moment.' },
  sub:     { type: String, default: '' },
})
</script>
