<template>
  <div
    class="rounded-card border p-3 transition-colors"
    :class="{
      'border-success bg-success/10': set.status === 'done',
      'border-danger bg-danger/10': set.status === 'failed',
      'border-apbborder bg-surface': set.status === 'pending',
    }"
  >
    <!-- ── CARDIO ROW ── -->
    <template v-if="isCardio">
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-muted w-5 shrink-0 text-center">{{ set.set_number }}</span>

        <!-- Duration in minutes -->
        <WeightRepsControl
          v-model="localDurationMin"
          :step="5"
          :min="0"
          unit="min"
          @update:modelValue="emitUpdate"
        />

        <!-- Resistance -->
        <WeightRepsControl
          v-model="localResistance"
          :step="1"
          :min="1"
          unit="res"
          @update:modelValue="emitUpdate"
        />

        <!-- Calories -->
        <WeightRepsControl
          v-model="localCalories"
          :step="10"
          :min="0"
          unit="kcal"
          @update:modelValue="emitUpdate"
        />

        <div class="flex gap-1 ml-auto shrink-0">
          <button
            @click="markDone"
            class="w-10 h-10 rounded-btn flex items-center justify-center text-lg transition-all active:scale-90"
            :class="set.status === 'done' ? 'bg-success text-white' : 'bg-surface2 text-muted hover:text-success'"
          >✓</button>
          <button
            @click="markFailed"
            class="w-10 h-10 rounded-btn flex items-center justify-center text-lg transition-all active:scale-90"
            :class="set.status === 'failed' ? 'bg-danger text-white' : 'bg-surface2 text-muted hover:text-danger'"
          >✗</button>
          <button @click="$emit('delete')" class="w-8 h-10 flex items-center justify-center text-muted hover:text-danger transition-colors" title="Supprimer"><AppIcon name="trash" :size="15" /></button>
        </div>
      </div>
    </template>

    <!-- ── STRENGTH ROW ── -->
    <template v-else>
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-muted w-5 shrink-0 text-center">{{ set.set_number }}</span>

        <WeightRepsControl
          v-model="localWeight"
          :step="fineMode ? 0.5 : 2.5"
          :min="0"
          unit="kg"
          @update:modelValue="emitUpdate"
        />

        <span class="text-muted text-base font-bold shrink-0">×</span>

        <WeightRepsControl
          v-model="localReps"
          :step="1"
          :min="0"
          unit="reps"
          @update:modelValue="emitUpdate"
        />

        <div class="flex gap-1 ml-auto shrink-0">
          <button
            @click="markDone"
            class="w-10 h-10 rounded-btn flex items-center justify-center text-lg transition-all active:scale-90"
            :class="set.status === 'done' ? 'bg-success text-white' : 'bg-surface2 text-muted hover:text-success'"
          >✓</button>
          <button
            @click="markFailed"
            class="w-10 h-10 rounded-btn flex items-center justify-center text-lg transition-all active:scale-90"
            :class="set.status === 'failed' ? 'bg-danger text-white' : 'bg-surface2 text-muted hover:text-danger'"
          >✗</button>
          <button @click="$emit('delete')" class="w-8 h-10 flex items-center justify-center text-muted hover:text-danger transition-colors" title="Supprimer"><AppIcon name="trash" :size="15" /></button>
        </div>
      </div>

      <!-- Fine mode + RPE -->
      <div class="mt-2 flex items-center gap-2 flex-wrap">
        <button
          @click="fineMode = !fineMode"
          class="text-xs px-2 py-1 rounded-btn border border-apbborder text-muted hover:text-apptext"
        >
          {{ fineMode ? '± 0.5 kg' : '± 2.5 kg' }}
        </button>
        <span class="text-xs text-muted">RPE:</span>
        <button
          v-for="r in rpeLevels"
          :key="r"
          @click="localRpe = r; emitUpdate()"
          class="text-xs w-7 h-7 rounded-btn transition-all"
          :class="localRpe === r ? 'bg-primary text-white' : 'bg-surface2 text-muted hover:text-apptext border border-apbborder'"
        >{{ r }}</button>
      </div>
    </template>

    <!-- Notes (shared, both modes) -->
    <input
      v-model="localNotes"
      @blur="emitNotes"
      type="text"
      placeholder="Note… (optionnel)"
      class="mt-1.5 w-full bg-transparent text-xs text-muted placeholder:text-muted/40 outline-none border-b border-transparent focus:border-apbborder transition-colors px-1"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import WeightRepsControl from './WeightRepsControl.vue'
import AppIcon from '@/components/ui/AppIcon.vue'

const props = defineProps({
  set:      { type: Object, required: true },
  exercise: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update', 'delete', 'done'])

const isCardio = computed(() => props.exercise?.muscle_group === 'Cardio')

// Strength fields
const localWeight = ref(props.set.weight_kg ?? 0)
const localReps   = ref(props.set.reps ?? 0)
const localRpe    = ref(props.set.rpe ?? null)
const fineMode    = ref(false)

// Cardio fields (duration stored as seconds, displayed as minutes)
const localDurationMin = ref(Math.round((props.set.duration_seconds ?? 0) / 60))
const localResistance  = ref(props.set.resistance ?? 5)
const localCalories    = ref(props.set.calories ?? 0)
const localNotes       = ref(props.set.notes ?? '')

const rpeLevels = [6, 7, 8, 9, 10]

watch(() => props.set, (s) => {
  localWeight.value      = s.weight_kg ?? 0
  localReps.value        = s.reps ?? 0
  localRpe.value         = s.rpe ?? null
  localDurationMin.value = Math.round((s.duration_seconds ?? 0) / 60)
  localResistance.value  = s.resistance ?? 5
  localCalories.value    = s.calories ?? 0
  localNotes.value       = s.notes ?? ''
})

function buildPayload(status) {
  if (isCardio.value) {
    return {
      duration_seconds: localDurationMin.value * 60,
      resistance:       localResistance.value,
      calories:         localCalories.value,
      status,
    }
  }
  return {
    weight_kg: localWeight.value,
    reps:      localReps.value,
    rpe:       localRpe.value,
    status,
  }
}

function emitUpdate() {
  emit('update', buildPayload(props.set.status))
}

function emitNotes() {
  if (localNotes.value !== (props.set.notes ?? '')) {
    emit('update', { notes: localNotes.value })
  }
}

function markDone() {
  const newStatus = props.set.status === 'done' ? 'pending' : 'done'
  emit('update', buildPayload(newStatus))
  if (newStatus === 'done') emit('done')
}

function markFailed() {
  emit('update', buildPayload(props.set.status === 'failed' ? 'pending' : 'failed'))
}
</script>
