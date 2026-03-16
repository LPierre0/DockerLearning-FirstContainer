<template>
  <AppLayout>
    <div class="p-4 max-w-3xl mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-6">Poids & suivi</h1>

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

      <div
        v-if="toast.visible"
        class="fixed top-20 left-1/2 -translate-x-1/2 z-[70] px-4 py-2 rounded-btn text-sm font-medium border shadow-sm"
        :class="toast.type === 'error'
          ? 'bg-danger/15 text-danger border-danger/30'
          : 'bg-success/15 text-success border-success/30'"
      >
        {{ toast.message }}
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else class="space-y-6">
        <div v-if="chartData.labels.length > 1" class="bg-surface rounded-card border border-apbborder p-4">
          <Line :data="chartData" :options="chartOptions" />
        </div>

        <div v-if="entries.length" class="bg-surface rounded-card border border-apbborder p-4 flex items-center justify-between">
          <div>
            <p class="text-xs text-muted mb-1">Dernier poids</p>
            <p class="text-3xl font-bold text-primary">
              {{ entries[0].weight_kg.toFixed(1) }}
              <span class="text-base font-normal text-muted">kg</span>
            </p>
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

        <div class="bg-surface rounded-card border border-apbborder p-4">
          <h2 class="text-sm font-semibold text-apptext mb-3">Objectif poids</h2>
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
              :disabled="targetWeight == null"
              class="h-10 px-4 bg-primary/20 text-primary border border-primary/40 rounded-btn font-medium text-sm disabled:opacity-50 active:scale-95 transition-transform shrink-0"
            >
              Enregistrer
            </button>
          </div>
        </div>

        <div class="bg-surface rounded-card border border-apbborder p-4">
          <h2 class="text-sm font-semibold text-apptext mb-3">Ajouter un poids</h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
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
            <div>
              <label class="text-xs text-muted block mb-1">Date</label>
              <input
                v-model="newDate"
                type="date"
                class="w-full h-10 px-3 bg-bg border border-apbborder rounded-btn text-apptext focus:outline-none focus:border-primary text-sm"
              />
            </div>
            <div class="flex items-end">
              <button
                @click="addEntry"
                :disabled="!newWeight || savingWeight"
                class="h-10 w-full px-4 bg-primary text-white rounded-btn font-medium text-sm disabled:opacity-50 active:scale-95 transition-transform"
              >
                {{ savingWeight ? 'Ajout...' : 'Ajouter' }}
              </button>
            </div>
          </div>
        </div>

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
        <EmptyState v-else icon="scale" message="Aucune mesure de poids" sub="Ajoute ton premier poids ci-dessus" />

        <section class="bg-surface rounded-card border border-apbborder p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-semibold text-apptext">Mensurations</h2>
            <button
              @click="openMeasurementWizard"
              class="text-xs text-primary border border-primary/30 px-3 py-1.5 rounded-btn hover:bg-primary/5 transition-colors"
            >
              Mesure guidée
            </button>
          </div>

          <div class="rounded-card border border-apbborder bg-bg px-3 py-2 mb-3">
            <p class="text-xs text-muted">
              Expérience mobile: guidage étape par étape avec rappel de placement du ruban.
            </p>
          </div>

          <div class="flex items-center justify-between">
            <p class="text-xs text-muted">Une saisie maximum par jour.</p>
            <button
              @click="openMeasurementWizard"
              :disabled="savingMeasurement"
              class="h-10 px-4 bg-primary text-white rounded-btn font-medium text-sm disabled:opacity-50 active:scale-95 transition-transform"
            >
              {{ savingMeasurement ? 'Enregistrement...' : 'Commencer la prise' }}
            </button>
          </div>
          <p v-if="measurementError" class="text-xs text-danger mt-2">{{ measurementError }}</p>

          <div class="mt-4">
            <div v-if="measurements.length" class="space-y-3">
              <div
                v-for="(entry, index) in measurements"
                :key="entry.id"
                class="rounded-card border border-apbborder p-3"
              >
                <div class="flex items-center justify-between mb-2">
                  <p class="text-xs text-muted">{{ formatDate(entry.logged_at) }}</p>
                  <button @click="deleteMeasurement(entry.id)" class="text-muted hover:text-danger transition-colors p-1 rounded">
                    <AppIcon name="trash" :size="16" />
                  </button>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  <div
                    v-for="field in measurementFields.filter(f => entry[f.key] != null)"
                    :key="`${entry.id}-${field.key}`"
                    class="rounded-btn bg-bg border border-apbborder px-2 py-1.5"
                  >
                    <p class="text-[11px] text-muted">{{ field.label }}</p>
                    <p class="text-sm font-semibold text-apptext">{{ formatCm(entry[field.key]) }}</p>
                    <p
                      v-if="measurementDelta(entry, index, field.key) != null"
                      class="text-[11px]"
                      :class="measurementDeltaClass(measurementDelta(entry, index, field.key))"
                    >
                      {{ formatCmDelta(measurementDelta(entry, index, field.key)) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-xs text-muted">Aucune mensuration enregistrée.</p>
          </div>
        </section>

        <section class="bg-surface rounded-card border border-apbborder p-4">
          <h2 class="text-sm font-semibold text-apptext mb-3">Analyse IA</h2>

          <div class="mb-3">
            <p class="text-xs text-muted mb-2">Template</p>
            <div class="flex gap-2">
              <button
                @click="insightTemplate = 'weekly'"
                class="px-3 py-1.5 rounded-btn text-sm border transition-colors"
                :class="insightTemplate === 'weekly'
                  ? 'bg-primary/15 text-primary border-primary/40'
                  : 'border-apbborder text-muted hover:text-apptext'"
              >
                Hebdo (4 semaines)
              </button>
              <button
                @click="insightTemplate = 'monthly'"
                class="px-3 py-1.5 rounded-btn text-sm border transition-colors"
                :class="insightTemplate === 'monthly'
                  ? 'bg-primary/15 text-primary border-primary/40'
                  : 'border-apbborder text-muted hover:text-apptext'"
              >
                Mensuel
              </button>
            </div>
          </div>

          <div v-if="insightTemplate === 'monthly'" class="mb-3">
            <p class="text-xs text-muted mb-2">Période</p>
            <div class="flex gap-2">
              <button
                v-for="opt in monthPeriods"
                :key="opt.value"
                @click="monthlyPeriod = opt.value"
                class="px-3 py-1.5 rounded-btn text-sm border transition-colors"
                :class="monthlyPeriod === opt.value
                  ? 'bg-primary/15 text-primary border-primary/40'
                  : 'border-apbborder text-muted hover:text-apptext'"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
          <p v-else class="text-xs text-muted mb-3">Période: 4 semaines</p>

          <button
            @click="copyInsightPrompt"
            :disabled="insightLoading"
            class="h-10 px-4 bg-primary text-white rounded-btn font-medium text-sm disabled:opacity-50 active:scale-95 transition-transform"
          >
            {{ insightLoading ? 'Génération...' : 'Copier le prompt IA' }}
          </button>
          <p class="text-xs text-muted mt-2">
            Le prompt inclut ton poids, tes mensurations et tes performances sur la période choisie.
          </p>
          <p v-if="insightError" class="text-xs text-danger mt-2">{{ insightError }}</p>
        </section>
      </div>
    </div>

    <Teleport to="body">
      <Transition name="backdrop">
        <div
          v-if="showMeasurementWizard"
          class="fixed inset-0 z-50 bg-black/50"
          @click="closeMeasurementWizard"
        />
      </Transition>
      <Transition name="sheet">
        <div
          v-if="showMeasurementWizard"
          class="fixed inset-x-0 bottom-0 z-[51] lg:inset-0 lg:flex lg:items-center lg:justify-center"
        >
          <div class="w-full lg:w-[34rem] bg-surface rounded-t-2xl lg:rounded-card p-5 max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold text-apptext">Mensurations guidées</h3>
              <button @click="closeMeasurementWizard" class="text-xs text-muted hover:text-apptext transition-colors">
                Fermer
              </button>
            </div>

            <p class="text-xs text-muted mb-2">
              Étape {{ wizardStep + 1 }}/{{ measurementFields.length }} · {{ currentWizardField.label }}
            </p>
            <div class="h-1.5 bg-bg rounded-full overflow-hidden mb-4">
              <div class="h-full bg-primary transition-all duration-300" :style="{ width: `${wizardProgress}%` }" />
            </div>

            <div class="mb-4">
              <label class="text-xs text-muted block mb-1">Date de la prise</label>
              <input
                v-model="wizardDate"
                type="date"
                class="w-full h-10 px-3 bg-bg border border-apbborder rounded-btn text-apptext focus:outline-none focus:border-primary text-sm"
              />
            </div>

            <div class="rounded-card border border-apbborder p-4">
              <p class="text-sm font-semibold text-apptext mb-1">{{ currentWizardField.label }}</p>
              <p class="text-xs text-muted mb-3">{{ currentWizardField.tip }}</p>
              <input
                v-model.number="wizardDraft[currentWizardField.key]"
                type="number"
                step="0.1"
                min="10"
                max="300"
                :placeholder="currentWizardField.placeholder"
                inputmode="decimal"
                class="w-full h-11 px-3 bg-bg border border-apbborder rounded-btn text-apptext focus:outline-none focus:border-primary text-sm"
              />
              <p class="text-[11px] text-muted mt-2">Tu peux laisser vide puis appuyer sur “Passer”.</p>
            </div>

            <p v-if="wizardError" class="text-xs text-danger mt-3">{{ wizardError }}</p>

            <div class="flex gap-2 mt-4">
              <button
                @click="wizardBack"
                class="flex-1 h-10 border border-apbborder text-muted rounded-btn text-sm hover:text-apptext"
              >
                {{ wizardStep === 0 ? 'Annuler' : 'Précédent' }}
              </button>
              <button
                @click="wizardNext"
                :disabled="savingMeasurement"
                class="flex-1 h-10 bg-primary text-white rounded-btn text-sm font-medium disabled:opacity-50"
              >
                {{ wizardPrimaryLabel }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AppLayout>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Line } from 'vue-chartjs'
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'

import AppLayout from '@/components/layout/AppLayout.vue'
import AppIcon from '@/components/ui/AppIcon.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import { useProfileStore } from '@/stores/profileStore'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const profileStore = useProfileStore()
const router = useRouter()

const loading = ref(true)
const entries = ref([])
const measurements = ref([])
const savingWeight = ref(false)
const savingMeasurement = ref(false)
const measurementError = ref('')
const wizardError = ref('')
const newWeight = ref(null)
const newDate = ref(new Date().toISOString().slice(0, 10))
const targetWeight = ref(null)
const showMeasurementWizard = ref(false)
const wizardDate = ref(new Date().toISOString().slice(0, 10))
const wizardStep = ref(0)

const insightTemplate = ref('weekly')
const monthlyPeriod = ref('1m')
const insightLoading = ref(false)
const insightError = ref('')

const toast = ref({
  visible: false,
  message: '',
  type: 'success',
})
let toastTimer

const measurementFields = [
  {
    key: 'chest_cm',
    label: 'Poitrine',
    placeholder: '100.0',
    tip: 'Mesure au point le plus large de la poitrine, ruban horizontal sans serrer.',
  },
  {
    key: 'waist_cm',
    label: 'Taille',
    placeholder: '82.0',
    tip: 'Mesure autour du nombril (ou du point le plus fin), sans rentrer le ventre.',
  },
  {
    key: 'hips_cm',
    label: 'Hanches',
    placeholder: '98.0',
    tip: 'Mesure au point le plus large du bassin/fessiers, pieds parallèles.',
  },
  {
    key: 'arm_cm',
    label: 'Bras',
    placeholder: '34.5',
    tip: 'Mesure au milieu du biceps, bras relâché le long du corps.',
  },
  {
    key: 'thigh_cm',
    label: 'Cuisse',
    placeholder: '57.0',
    tip: 'Mesure au milieu de la cuisse, en gardant toujours la même jambe.',
  },
  {
    key: 'calf_cm',
    label: 'Mollet',
    placeholder: '37.0',
    tip: 'Mesure au point le plus large du mollet, jambe détendue.',
  },
]

const monthPeriods = [
  { value: '1m', label: '1 mois' },
  { value: '3m', label: '3 mois' },
  { value: '6m', label: '6 mois' },
]

const wizardDraft = ref({
  chest_cm: null,
  waist_cm: null,
  hips_cm: null,
  arm_cm: null,
  thigh_cm: null,
  calf_cm: null,
})

const delta = computed(() => {
  if (entries.value.length < 2) return 0
  return entries.value[0].weight_kg - entries.value[1].weight_kg
})

const selectedInsightPeriod = computed(() => (
  insightTemplate.value === 'weekly' ? '4w' : monthlyPeriod.value
))

const currentWizardField = computed(() => measurementFields[wizardStep.value])
const wizardProgress = computed(() => ((wizardStep.value + 1) / measurementFields.length) * 100)
const wizardHasCurrentValue = computed(() => {
  const value = wizardDraft.value[currentWizardField.value.key]
  return value != null && !Number.isNaN(value)
})
const wizardIsLastStep = computed(() => wizardStep.value === measurementFields.length - 1)
const wizardPrimaryLabel = computed(() => {
  if (savingMeasurement.value) return 'Enregistrement...'
  if (wizardIsLastStep.value) return 'Enregistrer'
  return wizardHasCurrentValue.value ? 'Suivant' : 'Passer'
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
  if (targetWeight.value != null) {
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

function formatCm(v) {
  return `${Number(v).toFixed(1)} cm`
}

function measurementDelta(entry, index, fieldKey) {
  if (index >= measurements.value.length - 1) return null
  const current = entry[fieldKey]
  const previous = measurements.value[index + 1][fieldKey]
  if (current == null || previous == null) return null
  return current - previous
}

function formatCmDelta(value) {
  if (value == null) return ''
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(1)} cm`
}

function measurementDeltaClass(value) {
  if (value == null || value === 0) return 'text-muted'
  return value > 0 ? 'text-primary' : 'text-success'
}

function showToast(message, type = 'success') {
  toast.value = { visible: true, message, type }
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value.visible = false
  }, 2600)
}

function resetWizardDraft() {
  wizardDraft.value = {
    chest_cm: null,
    waist_cm: null,
    hips_cm: null,
    arm_cm: null,
    thigh_cm: null,
    calf_cm: null,
  }
}

function openMeasurementWizard() {
  measurementError.value = ''
  wizardError.value = ''
  wizardStep.value = 0
  wizardDate.value = new Date().toISOString().slice(0, 10)
  resetWizardDraft()
  showMeasurementWizard.value = true
}

function closeMeasurementWizard() {
  if (savingMeasurement.value) return
  showMeasurementWizard.value = false
}

function wizardBack() {
  if (wizardStep.value === 0) {
    closeMeasurementWizard()
    return
  }
  wizardStep.value -= 1
}

async function load() {
  loading.value = true
  const [weightsRes, usersRes, measurementsRes] = await Promise.all([
    fetch(`/api/body-weight?user_id=${profileStore.userId}`),
    fetch('/api/users'),
    fetch(`/api/body-measurements?user_id=${profileStore.userId}`),
  ])

  entries.value = weightsRes.ok ? await weightsRes.json() : []
  measurements.value = measurementsRes.ok ? await measurementsRes.json() : []

  const users = usersRes.ok ? await usersRes.json() : []
  const me = users.find(u => u.id === profileStore.userId)
  if (me?.target_weight_kg != null) {
    targetWeight.value = me.target_weight_kg
  }
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
  savingWeight.value = true
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
    savingWeight.value = false
  }
}

async function deleteEntry(id) {
  await fetch(`/api/body-weight/${id}`, { method: 'DELETE' })
  entries.value = entries.value.filter(e => e.id !== id)
}

function hasAtLeastOneMeasurementValue(draft) {
  return measurementFields.some(({ key }) => Number.isFinite(draft[key]))
}

async function submitMeasurement() {
  if (!hasAtLeastOneMeasurementValue(wizardDraft.value)) {
    wizardError.value = 'Ajoute au moins une mesure avant de sauvegarder.'
    return false
  }

  measurementError.value = ''
  wizardError.value = ''
  savingMeasurement.value = true

  const payload = {
    user_id: profileStore.userId,
    logged_at: wizardDate.value ? new Date(wizardDate.value).toISOString() : null,
  }
  for (const { key } of measurementFields) {
    payload[key] = Number.isFinite(wizardDraft.value[key]) ? wizardDraft.value[key] : null
  }

  try {
    const res = await fetch('/api/body-measurements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      if (res.status === 409) {
        measurementError.value = "Tu as déjà une mensuration pour cette date."
        wizardError.value = measurementError.value
      } else if (data?.detail) {
        const msg = typeof data.detail === 'string'
          ? data.detail
          : 'Impossible d’enregistrer la mensuration.'
        measurementError.value = msg
        wizardError.value = msg
      } else {
        measurementError.value = 'Impossible d’enregistrer la mensuration.'
        wizardError.value = measurementError.value
      }
      return false
    }

    await load()
    showToast('Mensurations enregistrées', 'success')
    showMeasurementWizard.value = false
    return true
  } finally {
    savingMeasurement.value = false
  }
}

async function wizardNext() {
  wizardError.value = ''
  if (!wizardIsLastStep.value) {
    wizardStep.value += 1
    return
  }
  await submitMeasurement()
}

async function deleteMeasurement(id) {
  await fetch(`/api/body-measurements/${id}`, { method: 'DELETE' })
  measurements.value = measurements.value.filter(m => m.id !== id)
}

async function copyText(text) {
  if (navigator?.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'absolute'
  textarea.style.left = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

async function copyInsightPrompt() {
  insightError.value = ''
  insightLoading.value = true
  try {
    const params = new URLSearchParams({
      user_id: String(profileStore.userId),
      template: insightTemplate.value,
      period: selectedInsightPeriod.value,
    })
    const res = await fetch(`/api/insights/prompt?${params.toString()}`)
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data?.detail || 'Impossible de générer le prompt.')
    }
    const data = await res.json()
    await copyText(data.prompt)
    showToast('Prompt IA copié dans le presse-papiers', 'success')
  } catch (err) {
    insightError.value = err instanceof Error ? err.message : 'Erreur pendant la copie du prompt.'
    showToast('Échec de copie du prompt', 'error')
  } finally {
    insightLoading.value = false
  }
}

onMounted(load)

onBeforeUnmount(() => {
  clearTimeout(toastTimer)
})

function doLogout() {
  profileStore.logout()
  router.push('/')
}
</script>
