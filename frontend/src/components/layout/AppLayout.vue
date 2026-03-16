<template>
  <!-- Mobile: full screen with bottom nav -->
  <!-- Desktop: sidebar left + content right -->
  <div class="min-h-dvh bg-bg text-apptext">
    <!-- Desktop top nav -->
    <TopNav class="hidden lg:flex" />

    <!-- Content area -->
    <main
      class="lg:pt-16"
      :class="[
        mobileNavPadding ? 'pb-20 lg:pb-0' : 'pb-0',
        !fullWidth ? 'lg:max-w-6xl lg:mx-auto lg:px-6' : '',
      ]"
    >
      <slot />
    </main>

    <!-- Mobile bottom nav -->
    <BottomNav class="lg:hidden" />

    <!-- Active workout persistent banner -->
    <ActiveWorkoutBanner />
  </div>
</template>

<script setup>
import TopNav from './TopNav.vue'
import BottomNav from './BottomNav.vue'
import ActiveWorkoutBanner from './ActiveWorkoutBanner.vue'

defineProps({
  fullWidth: { type: Boolean, default: false },
  mobileNavPadding: { type: Boolean, default: true },
})
</script>
