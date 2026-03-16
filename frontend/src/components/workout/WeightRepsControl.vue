<template>
  <div class="flex flex-col items-center gap-0.5 select-none">
    <div class="flex items-center">
      <button
        @click="decrement"
        class="w-10 h-10 flex items-center justify-center bg-surface2 border border-apbborder text-apptext text-lg font-bold active:brightness-90 active:scale-95 transition-all leading-none"
        style="border-radius: var(--radius-btn) 0 0 var(--radius-btn)"
      >−</button>
      <input
        :value="displayValue"
        @focus="$event.target.select()"
        @change="onManualInput($event.target.value)"
        type="number"
        :step="step"
        :min="min"
        inputmode="decimal"
        class="w-16 h-10 text-center text-sm font-bold text-apptext bg-surface border-y border-apbborder focus:outline-none focus:border-primary tabular-nums"
      />
      <button
        @click="increment"
        class="w-10 h-10 flex items-center justify-center bg-surface2 border border-apbborder text-apptext text-lg font-bold active:brightness-90 active:scale-95 transition-all leading-none"
        style="border-radius: 0 var(--radius-btn) var(--radius-btn) 0"
      >+</button>
    </div>
    <span class="text-[10px] text-muted">{{ unit }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  step:       { type: Number, default: 1 },
  min:        { type: Number, default: 0 },
  unit:       { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const displayValue = computed(() => {
  if (props.unit === 'kg') return Number(props.modelValue).toFixed(1)
  return props.modelValue
})

function increment() {
  emit('update:modelValue', Math.round((props.modelValue + props.step) * 100) / 100)
}

function decrement() {
  const next = Math.round((props.modelValue - props.step) * 100) / 100
  emit('update:modelValue', Math.max(props.min, next))
}

function onManualInput(raw) {
  const parsed = props.unit === 'kg' ? parseFloat(raw) : parseInt(raw, 10)
  if (!isNaN(parsed)) {
    emit('update:modelValue', Math.max(props.min, parsed))
  }
}
</script>
