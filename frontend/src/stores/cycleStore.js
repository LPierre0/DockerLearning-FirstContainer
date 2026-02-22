import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useProfileStore } from './profileStore'

export const useCycleStore = defineStore('cycle', () => {
  const cycles = ref([]) // [{ start: "2025-01-15", end: "2025-01-19", notes: "" }]

  function storageKey() {
    const profileStore = useProfileStore()
    return `fitness_cycle_${profileStore.userId}`
  }

  function load() {
    const raw = localStorage.getItem(storageKey())
    if (raw) {
      try {
        cycles.value = JSON.parse(raw)
      } catch {
        cycles.value = []
      }
    } else {
      cycles.value = []
    }
  }

  function save() {
    localStorage.setItem(storageKey(), JSON.stringify(cycles.value))
  }

  function addCycle(start, end, notes = '') {
    cycles.value.push({ start, end, notes })
    cycles.value.sort((a, b) => a.start.localeCompare(b.start))
    save()
  }

  function removeCycle(index) {
    cycles.value.splice(index, 1)
    save()
  }

  function updateCycle(index, data) {
    cycles.value[index] = { ...cycles.value[index], ...data }
    save()
  }

  const avgCycleLength = computed(() => {
    if (cycles.value.length < 2) return 28
    const starts = cycles.value.map(c => new Date(c.start)).sort((a, b) => a - b)
    let total = 0
    for (let i = 1; i < starts.length; i++) {
      total += (starts[i] - starts[i - 1]) / (1000 * 60 * 60 * 24)
    }
    return Math.round(total / (starts.length - 1))
  })

  const nextPredicted = computed(() => {
    if (cycles.value.length === 0) return null
    const lastStart = cycles.value.at(-1).start
    const d = new Date(lastStart)
    d.setDate(d.getDate() + avgCycleLength.value)
    return d.toISOString().slice(0, 10)
  })

  // Returns the phase for a given date string: 'period', 'ovulation', 'pre-period', 'normal'
  function phaseForDate(dateStr) {
    // Check if it's within a logged period
    for (const c of cycles.value) {
      if (dateStr >= c.start && dateStr <= c.end) return 'period'
    }
    // Check predictions relative to each cycle start
    for (const c of cycles.value) {
      const start = new Date(c.start)
      const ovulationDay = new Date(start)
      ovulationDay.setDate(start.getDate() + Math.round(avgCycleLength.value / 2) - 2)
      const ovulationEnd = new Date(start)
      ovulationEnd.setDate(start.getDate() + Math.round(avgCycleLength.value / 2) + 1)
      const prePeriodStart = new Date(start)
      prePeriodStart.setDate(start.getDate() + avgCycleLength.value - 5)
      const prePeriodEnd = new Date(start)
      prePeriodEnd.setDate(start.getDate() + avgCycleLength.value - 1)

      const d = new Date(dateStr)
      if (d >= ovulationDay && d <= ovulationEnd) return 'ovulation'
      if (d >= prePeriodStart && d <= prePeriodEnd) return 'pre-period'
    }
    return 'normal'
  }

  return { cycles, load, addCycle, removeCycle, updateCycle, avgCycleLength, nextPredicted, phaseForDate }
})
