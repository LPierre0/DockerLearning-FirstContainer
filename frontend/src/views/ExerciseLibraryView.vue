<template>
  <AppLayout>
    <div class="p-4 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-apptext mb-2">Exercices</h1>
      <p class="text-sm text-muted mb-2">Bibliothèque complète + tes exercices personnalisés</p>
      <p class="text-xs text-muted mb-6">Les photos des exercices prédéfinis sont partagées entre profils.</p>

      <div
        v-if="photoFeedback.message"
        class="mb-4 px-3 py-2 rounded-btn text-xs border"
        :class="photoFeedback.type === 'error'
          ? 'bg-danger/10 border-danger/30 text-danger'
          : 'bg-success/10 border-success/30 text-success'"
      >
        {{ photoFeedback.message }}
      </div>

      <div class="flex gap-2 mb-4">
        <input
          v-model="search"
          type="text"
          placeholder="Rechercher..."
          class="flex-1 bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
      </div>

      <div class="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-none">
        <button
          v-for="group in muscleGroups"
          :key="group"
          @click="activeGroup = group"
          class="shrink-0 px-3 py-1 text-xs rounded-btn transition-colors"
          :class="activeGroup === group ? 'bg-primary text-white' : 'bg-surface border border-apbborder text-muted hover:text-apptext'"
        >
          {{ group }}
        </button>
      </div>

      <LoadingSpinner v-if="loading" />

      <div v-else class="space-y-2 mb-8">
        <div
          v-for="ex in filtered"
          :key="ex.id"
          class="px-3 py-3 bg-surface rounded-card border border-apbborder"
        >
          <div class="flex items-center gap-3">
            <ExerciseThumb :src="ex.photo_url" :alt="ex.name" :size="52" />

            <div class="min-w-0 flex-1">
              <p class="font-medium text-apptext text-sm truncate">{{ ex.name }}</p>
              <p class="text-xs text-muted">{{ ex.muscle_group }}</p>
            </div>
          </div>

          <div class="mt-3 flex flex-wrap gap-2">
            <label
              class="px-3 h-8 inline-flex items-center rounded-btn border border-primary/40 text-primary text-xs cursor-pointer hover:bg-primary/10 transition-colors"
              :class="{ 'opacity-60 pointer-events-none': uploadingExerciseId === ex.id }"
            >
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,image/*"
                class="hidden"
                @change="onPhotoSelected(ex, $event)"
              >
              {{ uploadingExerciseId === ex.id ? 'Upload...' : (ex.photo_url ? 'Changer photo' : 'Ajouter photo') }}
            </label>

            <button
              v-if="ex.photo_url"
              @click="deletePhoto(ex)"
              :disabled="uploadingExerciseId === ex.id"
              class="px-3 h-8 inline-flex items-center rounded-btn border border-apbborder text-xs text-muted hover:text-danger hover:border-danger/40 transition-colors disabled:opacity-50"
            >
              Supprimer photo
            </button>

            <button
              v-if="ex.is_custom && ex.created_by === profileStore.userId"
              @click="deleteExercise(ex.id)"
              class="px-3 h-8 inline-flex items-center rounded-btn border border-apbborder text-xs text-muted hover:text-danger transition-colors"
            >
              Supprimer exercice
            </button>
          </div>
        </div>
        <EmptyState v-if="!filtered.length" icon="🔍" message="Aucun exercice trouvé." />
      </div>

      <div class="bg-surface border border-apbborder rounded-card p-4">
        <h2 class="font-semibold text-apptext mb-4">Ajouter un exercice</h2>
        <div class="flex flex-col gap-3">
          <input
            v-model="newName"
            type="text"
            placeholder="Nom de l'exercice"
            class="bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
          <select
            v-model="newGroup"
            class="bg-surface2 text-apptext border border-apbborder rounded-btn px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="" disabled>Groupe musculaire</option>
            <option v-for="g in realGroups" :key="g" :value="g">{{ g }}</option>
          </select>
          <button
            @click="addExercise"
            :disabled="!newName.trim() || !newGroup"
            class="py-2 bg-primary text-white rounded-btn text-sm font-semibold disabled:opacity-50"
          >
            Ajouter
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useProfileStore } from '@/stores/profileStore'
import AppLayout from '@/components/layout/AppLayout.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ExerciseThumb from '@/components/ui/ExerciseThumb.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'

const MAX_UPLOAD_BYTES = 5 * 1024 * 1024

const profileStore = useProfileStore()
const exercises = ref([])
const loading = ref(true)
const search = ref('')
const activeGroup = ref('Tous')
const newName = ref('')
const newGroup = ref('')
const uploadingExerciseId = ref(null)
const photoFeedback = ref({ message: '', type: 'success' })

const muscleGroups = ['Tous', 'Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Cardio']
const realGroups = muscleGroups.slice(1)

const filtered = computed(() => {
  let list = exercises.value
  if (activeGroup.value !== 'Tous') list = list.filter(e => e.muscle_group === activeGroup.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(e => e.name.toLowerCase().includes(q))
  }
  return list
})

function setPhotoFeedback(message, type = 'success') {
  photoFeedback.value = { message, type }
}

function replaceExercise(updated) {
  exercises.value = exercises.value.map(ex => (ex.id === updated.id ? updated : ex))
}

function readErrorDetail(data) {
  if (!data?.detail) return null
  if (typeof data.detail === 'string') return data.detail
  return 'Erreur API'
}

async function loadImage(file) {
  return await new Promise((resolve, reject) => {
    const img = new Image()
    const objectUrl = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(objectUrl)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(objectUrl)
      reject(new Error('Impossible de lire l’image'))
    }
    img.src = objectUrl
  })
}

async function canvasToJpegBlob(canvas, quality) {
  return await new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('Conversion image impossible'))
        return
      }
      resolve(blob)
    }, 'image/jpeg', quality)
  })
}

async function compressImage(file) {
  const image = await loadImage(file)

  let maxSide = 1600
  let quality = 0.84
  let blob = null

  for (let i = 0; i < 7; i += 1) {
    const scale = Math.min(1, maxSide / Math.max(image.width, image.height))
    const width = Math.max(1, Math.round(image.width * scale))
    const height = Math.max(1, Math.round(image.height * scale))

    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height

    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('Canvas indisponible')
    ctx.drawImage(image, 0, 0, width, height)

    blob = await canvasToJpegBlob(canvas, quality)
    if (blob.size <= MAX_UPLOAD_BYTES) break

    quality = Math.max(0.45, quality - 0.08)
    maxSide = Math.max(900, maxSide - 120)
  }

  if (!blob || blob.size > MAX_UPLOAD_BYTES) {
    throw new Error('Image trop lourde après compression (max 5MB)')
  }

  return new File([blob], 'exercise-photo.jpg', { type: 'image/jpeg' })
}

async function load() {
  const res = await fetch(`/api/exercises?user_id=${profileStore.userId}`)
  exercises.value = await res.json()
}

async function addExercise() {
  if (!newName.value.trim() || !newGroup.value) return
  await fetch('/api/exercises', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: newName.value.trim(),
      muscle_group: newGroup.value,
      created_by: profileStore.userId,
    }),
  })
  newName.value = ''
  newGroup.value = ''
  await load()
}

async function onPhotoSelected(exercise, event) {
  const input = event.target
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  uploadingExerciseId.value = exercise.id
  setPhotoFeedback('', 'success')

  try {
    const compressed = await compressImage(file)
    const formData = new FormData()
    formData.append('file', compressed)

    const res = await fetch(`/api/exercises/${exercise.id}/photo?user_id=${profileStore.userId}`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(readErrorDetail(data) || 'Upload impossible')
    }
    const updated = await res.json()
    replaceExercise(updated)
    setPhotoFeedback('Photo mise à jour', 'success')
  } catch (err) {
    setPhotoFeedback(err instanceof Error ? err.message : 'Upload impossible', 'error')
  } finally {
    uploadingExerciseId.value = null
  }
}

async function deletePhoto(exercise) {
  uploadingExerciseId.value = exercise.id
  setPhotoFeedback('', 'success')
  try {
    const res = await fetch(`/api/exercises/${exercise.id}/photo?user_id=${profileStore.userId}`, {
      method: 'DELETE',
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(readErrorDetail(data) || 'Suppression impossible')
    }
    const updated = await res.json()
    replaceExercise(updated)
    setPhotoFeedback('Photo supprimée', 'success')
  } catch (err) {
    setPhotoFeedback(err instanceof Error ? err.message : 'Suppression impossible', 'error')
  } finally {
    uploadingExerciseId.value = null
  }
}

async function deleteExercise(id) {
  await fetch(`/api/exercises/${id}?user_id=${profileStore.userId}`, { method: 'DELETE' })
  await load()
}

onMounted(async () => {
  await load()
  loading.value = false
})
</script>
