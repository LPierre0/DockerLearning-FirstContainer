<template>
  <AppLayout>
    <div class="p-4 max-w-lg mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-6">Mon poids</h1>

      <!-- Profile card + logout (mobile) -->
      <div class="bg-surface rounded-card border border-apbborder p-4 mb-6 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
            {{ profileStore.userName?.[0]?.toUpperCase() }}
          </div>
          <div>
            <p class="font-semibold text-apptext">{{ profileStore.userName }}</p>
            <p class="text-xs text-muted">Profil actif</p>
          </div>
        </div>
        <button
          @click="doLogout"
          class="text-sm text-muted hover:text-danger transition-colors border border-apbborder px-3 py-1.5 rounded-btn"
        >
          Changer de profil
        </button>
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else>
        <!-- Chart -->
        <div v-if="chartData.labels.length > 1" class="bg-surface rounded-card border border-apbborder p-4 mb-6">
          <Line :data="chartData" :options="chartOptions" />
        </div>

        <!-- Current / latest -->
        <div v-if="entries.length" class="bg-surface rounded-card border border-apbborder p-4 mb-6 flex items-center justify-between">
          <div>
            <p class="text-xs text-muted mb-1">Dernier poids</p>
            <p class="text-3xl font-bold text-primary">{{ entries[0].weight_kg.toFixed(1) }} <span class="text-base font-normal text-muted">kg</span></p>
            <p class="text-xs text-muted mt-1">{{ formatDate(entries[0].logged_at) }}</p>
          </div>
          <div v-if="entries.length > 1" class="text-right">
            <p class="text-xs text-muted mb-1">Variation</p>
            <p class="text-xl font-bold" :class="delta >= 0 ? 'text-danger' : 'text-success'">
              {{ delta >= 0 ? '+' : '' }}{{ delta.toFixed(1) }} kg
            </p>
            <p class="text-xs text-muted">vs précédent</p>
          </div>
        </div>

        <!-- Objectif poids -->
        <div class="bg-surface rounded-card border border-apbborder p-4 mb-6">
          <h2 class="text-sm font-semibold text-apptext mb-3">Objectif</h2>
          <div class="flex gap-3 items-end">
            <div class="flex-1">
              <label class="text-xs text-muted block mb-1">Poids cible (kg)</label>
              <input
                v-model.number="targetWeight"
                type="number"
                step="0.5"
                min="20"
                max="300"
                inputmode="decimal"
                placeholder="65.0"
                class="w-full h-10 px-3 bg-bg border border-apbborder rounded-btn text-apptext focus:outline-none focus:border-primary text-sm"
              />
            </div>
            <button
              @click="updateGoal"
              :disabled="!targetWeight"
              class="h-10 px-4 bg-primary/20 text-primary border border-primary/40 rounded-btn font-medium text-sm disabled:opacity-50 active:scale-95 transition-transform shrink-0"
            >
              Enregistrer
            </button>
          </div>
        </div>

        <!-- Add entry form -->
        <div class="bg-surface rounded-card border border-apbborder p-4 mb-6">
          <h2 class="text-sm font-semibold text-apptext mb-3">Ajouter une mesure</h2>
          <div class="flex gap-3 items-end">
            <div class="flex-1">
              <label class="text-xs text-muted block mb-1">Poids (kg)</label>
              <input
                v-model.number="newWeight"
                type="number"
                step="0.1"
                min="20"
                max="300"
                inputmode="decimal"
                placeholder="70.5"
                class="w-full h-10 px-3 bg-bg border border-apbborder rounded-btn text-apptext focus:outline-none focus:border-primary text-sm"
              />
            </div>
            <div class="flex-1">
              <label class="text-xs text-muted block mb-1">Date</label>
              <input
                v-model="newDate"
                type="date"
                class="w-full h-10 px-3 bg-bg border border-apbborder rounded-btn text-apptext focus:outline-none focus:border-primary text-sm"
              />
            </div>
            <button
              @click="addEntry"
              :disabled="!newWeight || saving"
              class="h-10 px-4 bg-primary text-white rounded-btn font-medium text-sm disabled:opacity-50 active:scale-95 transition-transform shrink-0"
            >
              Ajouter
            </button>
          </div>
        </div>

        <!-- History log -->
        <div v-if="entries.length" class="bg-surface rounded-card border border-apbborder divide-y divide-apbborder">
          <div
            v-for="e in entries"
            :key="e.id"
            class="flex items-center justify-between px-4 py-3"
          >
            <div>
              <span class="font-semibold text-apptext">{{ e.weight_kg.toFixed(1) }} kg</span>
              <span class="text-xs text-muted ml-3">{{ formatDate(e.logged_at) }}</span>
            </div>
            <button @click="deleteEntry(e.id)" class="text-muted hover:text-danger transition-colors flex items-center justify-center p-1 rounded">
              <AppIcon name="trash" :size="16" />
            </button>
          </div>
        </div>

        <EmptyState v-else icon="scale" message="Aucune mesure enregistrée" sub="Ajoute ton premier poids ci-dessus" />
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, LineElement, PointElement, LinearScale,
  CategoryScale, Tooltip, Filler,
} from 'chart.js'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import { useProfileStore } from '@/stores/profileStore'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const profileStore = useProfileStore()
const router = useRouter()
const entries = ref([])
const loading = ref(true)
const saving = ref(false)
const newWeight = ref(null)
const newDate = ref(new Date().toISOString().slice(0, 10))
const targetWeight = ref(null)

const delta = computed(() => {
  if (entries.value.length < 2) return 0
  return entries.value[0].weight_kg - entries.value[1].weight_kg
})

const primaryColor = computed(() => {
  const theme = document.documentElement.getAttribute('data-theme')
  return theme === 'partner' ? 'rgb(236,72,153)' : 'rgb(99,102,241)'
})

const chartData = computed(() => {
  const sorted = [...entries.value].reverse()
  const datasets = [{
    data: sorted.map(e => e.weight_kg),
    borderColor: primaryColor.value,
    backgroundColor: primaryColor.value.replace('rgb', 'rgba').replace(')', ',0.1)'),
    fill: true,
    tension: 0.3,
    pointRadius: 4,
  }]
  if (targetWeight.value) {
    datasets.push({
      data: sorted.map(() => targetWeight.value),
      borderColor: primaryColor.value.replace('rgb', 'rgba').replace(')', ',0.35)'),
      borderDash: [6, 4],
      pointRadius: 0,
      fill: false,
      tension: 0,
    })
  }
  return {
    labels: sorted.map(e => formatDateShort(e.logged_at)),
    datasets,
  }
})

const chartOptions = {
  responsive: true,
  plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
  scales: {
    y: { grid: { color: 'rgba(128,128,128,0.1)' }, ticks: { color: '#94a3b8' } },
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
  },
}

function formatDate(d) {
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(d))
}

function formatDateShort(d) {
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short' }).format(new Date(d))
}

async function load() {
  loading.value = true
  const [weightsRes, usersRes] = await Promise.all([
    fetch(`/api/body-weight?user_id=${profileStore.userId}`),
    fetch('/api/users'),
  ])
  entries.value = await weightsRes.json()
  const users = await usersRes.json()
  const me = users.find(u => u.id === profileStore.userId)
  if (me?.target_weight_kg) targetWeight.value = me.target_weight_kg
  loading.value = false
}

async function updateGoal() {
  await fetch(`/api/users/${profileStore.userId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_weight_kg: targetWeight.value }),
  })
}

async function addEntry() {
  if (!newWeight.value) return
  saving.value = true
  try {
    const res = await fetch('/api/body-weight', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: profileStore.userId,
        weight_kg: newWeight.value,
        logged_at: newDate.value ? new Date(newDate.value).toISOString() : null,
      }),
    })
    if (res.ok) {
      newWeight.value = null
      await load()
    }
  } finally {
    saving.value = false
  }
}

async function deleteEntry(id) {
  await fetch(`/api/body-weight/${id}`, { method: 'DELETE' })
  entries.value = entries.value.filter(e => e.id !== id)
}

onMounted(load)

function doLogout() {
  profileStore.logout()
  router.push('/')
}
</script>
