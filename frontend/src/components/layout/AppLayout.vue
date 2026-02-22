<template>
  <!-- Mobile: full screen with bottom nav -->
  <!-- Desktop: sidebar left + content right -->
  <div class="min-h-dvh bg-bg text-apptext">
    <!-- Desktop top nav -->
    <TopNav class="hidden lg:flex" />

    <!-- Content area -->
    <main
      class="pb-20 lg:pb-0 lg:pt-16"
      :class="{ 'lg:max-w-6xl lg:mx-auto lg:px-6': !fullWidth }"
    >
      <slot />
    </main>

    <!-- Mobile bottom nav -->
    <BottomNav class="lg:hidden" />
  </div>
</template>

<script setup>
import TopNav from './TopNav.vue'
import BottomNav from './BottomNav.vue'

defineProps({
  fullWidth: { type: Boolean, default: false },
})
</script>
