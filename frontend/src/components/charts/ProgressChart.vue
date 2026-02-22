<template>
  <div class="relative">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Filler,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  dataset: { type: Array, default: () => [] },
  label: { type: String, default: '' },
})

const primaryColor = () => {
  const theme = document.documentElement.getAttribute('data-theme')
  return theme === 'partner' ? 'rgb(236,72,153)' : 'rgb(99,102,241)'
}

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: props.label,
      data: props.dataset,
      borderColor: primaryColor(),
      backgroundColor: primaryColor().replace('rgb', 'rgba').replace(')', ',0.1)'),
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => `${ctx.parsed.y} kg`,
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { color: 'rgb(100,116,139)', maxRotation: 45 },
    },
    y: {
      grid: { color: 'rgba(100,116,139,0.1)' },
      ticks: { color: 'rgb(100,116,139)', callback: (v) => `${v} kg` },
    },
  },
}
</script>
