<template>
  <AppLayout>
    <div class="p-4 max-w-lg mx-auto pb-24">
      <h1 class="text-2xl font-bold text-apptext mb-1">Cycle</h1>
      <p class="text-sm text-muted mb-6">Données stockées uniquement sur cet appareil</p>

      <!-- Stats row -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <div class="bg-surface rounded-card border border-apbborder p-3 text-center">
          <p class="text-lg font-bold text-primary">{{ cycleStore.avgCycleLength }}j</p>
          <p class="text-xs text-muted">durée moy. cycle</p>
        </div>
        <div class="bg-surface rounded-card border border-apbborder p-3 text-center">
          <p class="text-lg font-bold text-primary">{{ cycleStore.nextPredicted ? formatShort(cycleStore.nextPredicted) : '—' }}</p>
          <p class="text-xs text-muted">prochain prévu</p>
        </div>
      </div>

      <!-- Calendar -->
      <div class="bg-surface rounded-card border border-apbborder p-4 mb-6">
        <div class="flex items-center justify-between mb-4">
          <button @click="prevMonth" class="text-muted hover:text-apptext px-2">←</button>
          <h2 class="font-semibold text-apptext capitalize">{{ monthLabel }}</h2>
          <button @click="nextMonth" class="text-muted hover:text-apptext px-2">→</button>
        </div>
        <!-- Day headers -->
        <div class="grid grid-cols-7 mb-1">
          <div v-for="d in ['L','M','M','J','V','S','D']" :key="d" class="text-center text-xs text-muted font-semibold py-1">{{ d }}</div>
        </div>
        <!-- Days grid -->
        <div class="grid grid-cols-7 gap-0.5">
          <div v-for="(cell, i) in calendarCells" :key="i"
            class="aspect-square rounded-[4px] flex items-center justify-center text-xs cursor-pointer transition-colors"
            :class="cellClass(cell)"
            @click="cell.day && toggleDay(cell.dateStr)"
          >
            <span v-if="cell.day">{{ cell.day }}</span>
          </div>
        </div>
        <!-- Legend -->
        <div class="flex flex-wrap gap-3 mt-3 text-xs text-muted">
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-danger/70 inline-block"></span> Règles</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-primary/50 inline-block"></span> Ovulation</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-accent/50 inline-block"></span> Pré-règles</span>
        </div>
      </div>

      <!-- Add cycle form -->
      <div class="bg-surface rounded-card border border-apbborder p-4 mb-6">
        <h3 class="font-semibold text-apptext mb-3">Ajouter un cycle</h3>
        <div class="flex flex-col gap-3">
          <label class="flex flex-col gap-1">
            <span class="text-xs text-muted">Début des règles</span>
            <input v-model="newStart" type="date" class="bg-surface2 rounded-btn px-3 py-2 text-sm text-apptext border border-apbborder outline-none focus:border-primary" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="text-xs text-muted">Fin des règles</span>
            <input v-model="newEnd" type="date" class="bg-surface2 rounded-btn px-3 py-2 text-sm text-apptext border border-apbborder outline-none focus:border-primary" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="text-xs text-muted">Notes (optionnel)</span>
            <input v-model="newNotes" type="text" placeholder="humeur, douleurs…" class="bg-surface2 rounded-btn px-3 py-2 text-sm text-apptext border border-apbborder outline-none focus:border-primary" />
          </label>
          <button
            @click="addCycle"
            :disabled="!newStart || !newEnd"
            class="btn-primary w-full disabled:opacity-40"
          >Ajouter</button>
        </div>
      </div>

      <!-- Past cycles list -->
      <div v-if="cycleStore.cycles.length" class="bg-surface rounded-card border border-apbborder p-4">
        <h3 class="font-semibold text-apptext mb-3">Historique</h3>
        <div class="space-y-2">
          <div
            v-for="(c, i) in [...cycleStore.cycles].reverse()"
            :key="i"
            class="flex items-center justify-between text-sm py-2 border-b border-apbborder last:border-0"
          >
            <div>
              <p class="text-apptext">{{ formatShort(c.start) }} → {{ formatShort(c.end) }}</p>
              <p v-if="c.notes" class="text-xs text-muted">{{ c.notes }}</p>
            </div>
            <button @click="cycleStore.removeCycle(cycleStore.cycles.length - 1 - i)" class="text-muted hover:text-danger text-xs px-2">✕</button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useCycleStore } from '@/stores/cycleStore'

const cycleStore = useCycleStore()

const today = new Date()
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth()) // 0-indexed

const newStart = ref('')
const newEnd = ref('')
const newNotes = ref('')

const monthLabel = computed(() =>
  new Date(viewYear.value, viewMonth.value, 1).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
)

function prevMonth() {
  if (viewMonth.value === 0) { viewMonth.value = 11; viewYear.value-- }
  else viewMonth.value--
}
function nextMonth() {
  if (viewMonth.value === 11) { viewMonth.value = 0; viewYear.value++ }
  else viewMonth.value++
}

const calendarCells = computed(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value, 1)
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  // Monday first: getDay() returns 0=Sun,1=Mon...
  let startPad = firstDay.getDay() - 1
  if (startPad < 0) startPad = 6

  const cells = []
  for (let i = 0; i < startPad; i++) cells.push({ day: null, dateStr: null })
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({ day: d, dateStr })
  }
  return cells
})

function cellClass(cell) {
  if (!cell.day) return ''
  const phase = cycleStore.phaseForDate(cell.dateStr)
  const isToday = cell.dateStr === today.toISOString().slice(0, 10)
  const base = isToday ? 'ring-1 ring-apptext' : ''
  if (phase === 'period') return `${base} bg-danger/50 text-white font-medium`
  if (phase === 'ovulation') return `${base} bg-primary/40 text-apptext font-medium`
  if (phase === 'pre-period') return `${base} bg-accent/40 text-apptext`
  return `${base} hover:bg-surface2 text-apptext`
}

function toggleDay(dateStr) {
  if (!newStart.value) {
    newStart.value = dateStr
  } else if (!newEnd.value && dateStr >= newStart.value) {
    newEnd.value = dateStr
  } else {
    newStart.value = dateStr
    newEnd.value = ''
  }
}

function addCycle() {
  if (!newStart.value || !newEnd.value) return
  cycleStore.addCycle(newStart.value, newEnd.value, newNotes.value)
  newStart.value = ''
  newEnd.value = ''
  newNotes.value = ''
}

function formatShort(d) {
  return new Date(d + 'T12:00:00').toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

onMounted(() => {
  cycleStore.load()
})
</script>
