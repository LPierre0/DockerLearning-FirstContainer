<template>
  <div>
    <div class="grid gap-0.5" :style="{ gridTemplateColumns: `repeat(${weeks}, 1fr)`, gridTemplateRows: 'repeat(7, 1fr)', gridAutoFlow: 'column' }">
      <div
        v-for="(day, i) in cells"
        :key="i"
        :title="day.label"
        class="aspect-square rounded-[2px] transition-colors"
        :class="colorClass(day.count)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  activity: { type: Object, default: () => ({}) },
})

const weeks = 13
const DAYS = weeks * 7

const cells = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const result = []
  for (let i = DAYS - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    result.push({
      date: key,
      count: props.activity[key] ?? 0,
      label: key,
    })
  }
  // Reorder: display column-major (week columns, day rows)
  // cells[col * 7 + row] = day index col*7+row
  return result
})

function colorClass(count) {
  if (count === 0) return 'bg-surface2'
  if (count === 1) return 'bg-primary/40'
  if (count === 2) return 'bg-primary/70'
  return 'bg-primary'
}
</script>
