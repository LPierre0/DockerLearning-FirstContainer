<template>
  <div class="flex flex-col items-center gap-0.5 select-none">
    <button
      @click="increment"
      class="w-8 h-8 rounded-btn bg-surface2 text-apptext text-base font-bold active:scale-90 transition-transform flex items-center justify-center border border-apbborder leading-none"
    >+</button>

    <input
      :value="displayValue"
      @focus="$event.target.select()"
      @change="onManualInput($event.target.value)"
      type="number"
      :step="step"
      :min="min"
      inputmode="decimal"
      class="w-14 h-9 text-center text-base font-bold text-apptext bg-surface border border-apbborder rounded-btn focus:outline-none focus:border-primary tabular-nums"
    />

    <button
      @click="decrement"
      class="w-8 h-8 rounded-btn bg-surface2 text-apptext text-base font-bold active:scale-90 transition-transform flex items-center justify-center border border-apbborder leading-none"
    >−</button>

    <span class="text-[10px] text-muted mt-0.5">{{ unit }}</span>
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
