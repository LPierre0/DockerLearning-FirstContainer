<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'

// ═══════════════════════════════════════════════════════════════
// 🎯 STATE
// ═══════════════════════════════════════════════════════════════

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

// Navigation
const activeSection = ref('hero')
const sections = ['hero', 'metrics', 'training', 'pipeline', 'skills']

// Profile data
const profile = ref(null)
const skills = ref([])

// Real-time metrics
const metrics = ref({
  cpu: 0,
  memory: 0,
  network_in: 0,
  network_out: 0,
  latency_ms: 0,
  active_jobs: 0,
  queue_size: 0
})
const metricsHistory = ref([])
const maxHistoryLength = 50

// ML Training
const trainingActive = ref(false)
const trainingMetrics = ref([])
const trainingComplete = ref(false)
const currentEpoch = ref(0)

// Pipeline
const pipelineActive = ref(false)
const pipelineStages = ref([
  { id: 'extract', name: 'Extract', icon: '📥', status: 'pending', progress: 0 },
  { id: 'validate', name: 'Validate', icon: '✅', status: 'pending', progress: 0 },
  { id: 'transform', name: 'Transform', icon: '⚙️', status: 'pending', progress: 0 },
  { id: 'enrich', name: 'Enrich', icon: '✨', status: 'pending', progress: 0 },
  { id: 'load', name: 'Load', icon: '📤', status: 'pending', progress: 0 },
  { id: 'index', name: 'Index', icon: '🔍', status: 'pending', progress: 0 },
])
const pipelineLogs = ref([])
const pipelineMetrics = ref(null)

// Neural network canvas
const canvasRef = ref(null)
const particles = ref([])
const mousePos = ref({ x: 0, y: 0 })
let animationId = null
let metricsEventSource = null

// ═══════════════════════════════════════════════════════════════
// 🧠 NEURAL NETWORK ANIMATION
// ═══════════════════════════════════════════════════════════════

class Particle {
  constructor(canvas) {
    this.canvas = canvas
    this.reset()
  }

  reset() {
    this.x = Math.random() * this.canvas.width
    this.y = Math.random() * this.canvas.height
    this.vx = (Math.random() - 0.5) * 0.5
    this.vy = (Math.random() - 0.5) * 0.5
    this.radius = Math.random() * 2 + 1
    this.baseRadius = this.radius
    this.color = `hsl(${200 + Math.random() * 60}, 70%, 60%)`
    this.pulsePhase = Math.random() * Math.PI * 2
  }

  update(mouse) {
    // Movement
    this.x += this.vx
    this.y += this.vy

    // Pulse effect
    this.pulsePhase += 0.02
    this.radius = this.baseRadius + Math.sin(this.pulsePhase) * 0.5

    // Mouse attraction
    const dx = mouse.x - this.x
    const dy = mouse.y - this.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist < 200 && dist > 0) {
      const force = (200 - dist) / 200 * 0.02
      this.vx += (dx / dist) * force
      this.vy += (dy / dist) * force
    }

    // Velocity damping
    this.vx *= 0.99
    this.vy *= 0.99

    // Boundary wrapping
    if (this.x < 0) this.x = this.canvas.width
    if (this.x > this.canvas.width) this.x = 0
    if (this.y < 0) this.y = this.canvas.height
    if (this.y > this.canvas.height) this.y = 0
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()

    // Glow effect
    ctx.shadowBlur = 10
    ctx.shadowColor = this.color
    ctx.fill()
    ctx.shadowBlur = 0
  }
}

function initCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width
  canvas.height = rect.height

  // Initialize particles
  particles.value = []
  const numParticles = Math.floor((canvas.width * canvas.height) / 8000)
  for (let i = 0; i < numParticles; i++) {
    particles.value.push(new Particle(canvas))
  }

  animate()
}

function animate() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')

  // Clear with fade effect
  ctx.fillStyle = 'rgba(10, 15, 30, 0.1)'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Update and draw particles
  particles.value.forEach(p => {
    p.update(mousePos.value)
    p.draw(ctx)
  })

  // Draw connections
  ctx.strokeStyle = 'rgba(100, 180, 255, 0.1)'
  ctx.lineWidth = 0.5
  for (let i = 0; i < particles.value.length; i++) {
    for (let j = i + 1; j < particles.value.length; j++) {
      const dx = particles.value[i].x - particles.value[j].x
      const dy = particles.value[i].y - particles.value[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < 120) {
        ctx.beginPath()
        ctx.moveTo(particles.value[i].x, particles.value[i].y)
        ctx.lineTo(particles.value[j].x, particles.value[j].y)
        ctx.globalAlpha = 1 - dist / 120
        ctx.stroke()
        ctx.globalAlpha = 1
      }
    }
  }

  animationId = requestAnimationFrame(animate)
}

function handleMouseMove(e) {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  mousePos.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

function handleResize() {
  const canvas = canvasRef.value
  if (!canvas) return
  const rect = canvas.parentElement.getBoundingClientRect()
  canvas.width = rect.width
  canvas.height = rect.height
  particles.value.forEach(p => p.canvas = canvas)
}

// ═══════════════════════════════════════════════════════════════
// 📊 REAL-TIME METRICS
// ═══════════════════════════════════════════════════════════════

function connectMetricsStream() {
  if (metricsEventSource) {
    metricsEventSource.close()
  }

  metricsEventSource = new EventSource(`${API_URL}/stream/metrics`)

  metricsEventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    metrics.value = data

    // Add to history for charts
    metricsHistory.value.push({
      ...data,
      time: new Date().toLocaleTimeString()
    })
    if (metricsHistory.value.length > maxHistoryLength) {
      metricsHistory.value.shift()
    }
  }

  metricsEventSource.onerror = () => {
    console.log('Metrics stream disconnected, reconnecting...')
    setTimeout(connectMetricsStream, 3000)
  }
}

// ═══════════════════════════════════════════════════════════════
// 🤖 ML TRAINING SIMULATION
// ═══════════════════════════════════════════════════════════════

function startTraining() {
  if (trainingActive.value) return

  trainingActive.value = true
  trainingComplete.value = false
  trainingMetrics.value = []
  currentEpoch.value = 0

  const eventSource = new EventSource(`${API_URL}/stream/training`)

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.status === 'completed') {
      trainingActive.value = false
      trainingComplete.value = true
      eventSource.close()
      return
    }

    currentEpoch.value = data.epoch
    trainingMetrics.value.push(data)
  }

  eventSource.onerror = () => {
    trainingActive.value = false
    eventSource.close()
  }
}

// ═══════════════════════════════════════════════════════════════
// 🔄 PIPELINE SIMULATION
// ═══════════════════════════════════════════════════════════════

function startPipeline() {
  if (pipelineActive.value) return

  pipelineActive.value = true
  pipelineLogs.value = []
  pipelineMetrics.value = null
  pipelineStages.value.forEach(s => {
    s.status = 'pending'
    s.progress = 0
  })

  const eventSource = new EventSource(`${API_URL}/stream/pipeline`)

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)

    if (data.type === 'log') {
      pipelineLogs.value.push(data)
      const stage = pipelineStages.value.find(s => s.id === data.stage)
      if (stage) {
        stage.status = data.status
      }
      // Auto-scroll logs
      nextTick(() => {
        const logsContainer = document.querySelector('.pipeline-logs')
        if (logsContainer) {
          logsContainer.scrollTop = logsContainer.scrollHeight
        }
      })
    } else if (data.type === 'progress') {
      const stage = pipelineStages.value.find(s => s.id === data.stage)
      if (stage) {
        stage.progress = data.progress
      }
      pipelineMetrics.value = data.metrics
    } else if (data.type === 'complete') {
      pipelineActive.value = false
      eventSource.close()
    }
  }

  eventSource.onerror = () => {
    pipelineActive.value = false
    eventSource.close()
  }
}

// ═══════════════════════════════════════════════════════════════
// 🎨 COMPUTED
// ═══════════════════════════════════════════════════════════════

const skillsByCategory = computed(() => {
  const categories = {}
  skills.value.forEach(skill => {
    if (!categories[skill.category]) {
      categories[skill.category] = []
    }
    categories[skill.category].push(skill)
  })
  return categories
})

const latestLoss = computed(() => {
  if (trainingMetrics.value.length === 0) return null
  return trainingMetrics.value[trainingMetrics.value.length - 1]
})

// ═══════════════════════════════════════════════════════════════
// 🔧 UTILITIES
// ═══════════════════════════════════════════════════════════════

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function scrollToSection(sectionId) {
  activeSection.value = sectionId
  const el = document.getElementById(sectionId)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

// ═══════════════════════════════════════════════════════════════
// 🚀 LIFECYCLE
// ═══════════════════════════════════════════════════════════════

onMounted(async () => {
  // Fetch initial data
  try {
    const [profileRes, skillsRes] = await Promise.all([
      fetch(`${API_URL}/profile`),
      fetch(`${API_URL}/skills`)
    ])
    profile.value = await profileRes.json()
    skills.value = await skillsRes.json()
  } catch (error) {
    console.error('Failed to fetch data:', error)
  }

  // Initialize canvas
  await nextTick()
  initCanvas()

  // Connect to real-time metrics
  connectMetricsStream()

  // Handle resize
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (metricsEventSource) {
    metricsEventSource.close()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="dashboard">
    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-brand">
        <span class="nav-logo">⚡</span>
        <span class="nav-title">DataLab</span>
      </div>
      <div class="nav-links">
        <button
          v-for="section in sections"
          :key="section"
          :class="['nav-link', { active: activeSection === section }]"
          @click="scrollToSection(section)"
        >
          {{ section.charAt(0).toUpperCase() + section.slice(1) }}
        </button>
      </div>
    </nav>

    <!-- Hero Section with Neural Network -->
    <section id="hero" class="section hero">
      <canvas
        ref="canvasRef"
        class="neural-canvas"
        @mousemove="handleMouseMove"
      ></canvas>
      <div class="hero-content">
        <div class="hero-badge">🚀 Data Scientist & Engineer</div>
        <h1 class="hero-title">
          <span class="gradient-text">{{ profile?.name || 'Loading...' }}</span>
        </h1>
        <p class="hero-subtitle">{{ profile?.bio }}</p>
        <div class="hero-stats">
          <div class="stat-card">
            <span class="stat-value">{{ skills.length }}</span>
            <span class="stat-label">Technologies</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ metrics.active_jobs }}</span>
            <span class="stat-label">Active Jobs</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">{{ metrics.cpu.toFixed(0) }}%</span>
            <span class="stat-label">CPU Usage</span>
          </div>
        </div>
        <div class="hero-actions">
          <a :href="profile?.github" target="_blank" class="btn btn-primary">
            <span>GitHub</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
          </a>
          <a :href="profile?.linkedin" target="_blank" class="btn btn-secondary">
            <span>LinkedIn</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </a>
        </div>
      </div>
    </section>

    <!-- Real-time Metrics Section -->
    <section id="metrics" class="section metrics-section">
      <div class="section-header">
        <h2 class="section-title">📊 Real-time Metrics</h2>
        <p class="section-subtitle">Live system monitoring dashboard</p>
      </div>

      <div class="metrics-grid">
        <!-- CPU Gauge -->
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-icon">🖥️</span>
            <span class="metric-name">CPU Usage</span>
          </div>
          <div class="gauge-container">
            <svg class="gauge" viewBox="0 0 100 50">
              <path
                class="gauge-bg"
                d="M 10 45 A 35 35 0 0 1 90 45"
                fill="none"
                stroke="#1e293b"
                stroke-width="8"
              />
              <path
                class="gauge-fill"
                d="M 10 45 A 35 35 0 0 1 90 45"
                fill="none"
                stroke="url(#cpuGradient)"
                stroke-width="8"
                :stroke-dasharray="`${metrics.cpu * 1.1} 110`"
              />
              <defs>
                <linearGradient id="cpuGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#22d3ee"/>
                  <stop offset="100%" style="stop-color:#8b5cf6"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="gauge-value">{{ metrics.cpu.toFixed(1) }}%</div>
          </div>
        </div>

        <!-- Memory Gauge -->
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-icon">🧠</span>
            <span class="metric-name">Memory</span>
          </div>
          <div class="gauge-container">
            <svg class="gauge" viewBox="0 0 100 50">
              <path
                class="gauge-bg"
                d="M 10 45 A 35 35 0 0 1 90 45"
                fill="none"
                stroke="#1e293b"
                stroke-width="8"
              />
              <path
                class="gauge-fill"
                d="M 10 45 A 35 35 0 0 1 90 45"
                fill="none"
                stroke="url(#memGradient)"
                stroke-width="8"
                :stroke-dasharray="`${metrics.memory * 1.1} 110`"
              />
              <defs>
                <linearGradient id="memGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#f472b6"/>
                  <stop offset="100%" style="stop-color:#fb923c"/>
                </linearGradient>
              </defs>
            </svg>
            <div class="gauge-value">{{ metrics.memory.toFixed(1) }}%</div>
          </div>
        </div>

        <!-- Network Stats -->
        <div class="metric-card wide">
          <div class="metric-header">
            <span class="metric-icon">🌐</span>
            <span class="metric-name">Network I/O</span>
          </div>
          <div class="network-stats">
            <div class="network-stat">
              <span class="network-arrow up">↑</span>
              <span class="network-value">{{ formatBytes(metrics.network_out) }}/s</span>
            </div>
            <div class="network-stat">
              <span class="network-arrow down">↓</span>
              <span class="network-value">{{ formatBytes(metrics.network_in) }}/s</span>
            </div>
          </div>
        </div>

        <!-- Latency -->
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-icon">⚡</span>
            <span class="metric-name">Latency</span>
          </div>
          <div class="metric-big-value">
            {{ metrics.latency_ms.toFixed(1) }}<span class="unit">ms</span>
          </div>
        </div>

        <!-- Queue -->
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-icon">📋</span>
            <span class="metric-name">Queue Size</span>
          </div>
          <div class="metric-big-value">
            {{ metrics.queue_size }}<span class="unit">jobs</span>
          </div>
        </div>
      </div>

      <!-- Mini Chart -->
      <div class="chart-container">
        <h3 class="chart-title">CPU History (Last 50 samples)</h3>
        <div class="mini-chart">
          <svg viewBox="0 0 500 100" preserveAspectRatio="none">
            <defs>
              <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#22d3ee;stop-opacity:0.5"/>
                <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:0"/>
              </linearGradient>
            </defs>
            <path
              v-if="metricsHistory.length > 1"
              :d="'M 0 ' + (100 - metricsHistory[0]?.cpu) + ' ' + metricsHistory.map((m, i) => `L ${i * (500 / maxHistoryLength)} ${100 - m.cpu}`).join(' ') + ` L ${(metricsHistory.length - 1) * (500 / maxHistoryLength)} 100 L 0 100 Z`"
              fill="url(#chartGradient)"
            />
            <path
              v-if="metricsHistory.length > 1"
              :d="'M 0 ' + (100 - metricsHistory[0]?.cpu) + ' ' + metricsHistory.map((m, i) => `L ${i * (500 / maxHistoryLength)} ${100 - m.cpu}`).join(' ')"
              fill="none"
              stroke="#22d3ee"
              stroke-width="2"
            />
          </svg>
        </div>
      </div>
    </section>

    <!-- ML Training Section -->
    <section id="training" class="section training-section">
      <div class="section-header">
        <h2 class="section-title">🤖 ML Training Simulator</h2>
        <p class="section-subtitle">Watch a neural network learn in real-time</p>
      </div>

      <div class="training-controls">
        <button
          class="btn btn-primary btn-lg"
          :disabled="trainingActive"
          @click="startTraining"
        >
          {{ trainingActive ? '🔄 Training...' : '🚀 Start Training' }}
        </button>
        <div v-if="trainingComplete" class="training-complete">
          ✅ Training Complete!
        </div>
      </div>

      <div class="training-dashboard">
        <!-- Current Metrics -->
        <div class="training-current">
          <div class="training-metric">
            <span class="training-metric-label">Epoch</span>
            <span class="training-metric-value">{{ currentEpoch }} / 50</span>
          </div>
          <div class="training-metric">
            <span class="training-metric-label">Loss</span>
            <span class="training-metric-value loss">{{ latestLoss?.loss?.toFixed(4) || '—' }}</span>
          </div>
          <div class="training-metric">
            <span class="training-metric-label">Accuracy</span>
            <span class="training-metric-value accuracy">{{ latestLoss ? (latestLoss.accuracy * 100).toFixed(2) + '%' : '—' }}</span>
          </div>
          <div class="training-metric">
            <span class="training-metric-label">Val Loss</span>
            <span class="training-metric-value">{{ latestLoss?.val_loss?.toFixed(4) || '—' }}</span>
          </div>
        </div>

        <!-- Training Charts -->
        <div class="training-charts">
          <div class="training-chart">
            <h4>Loss Curve</h4>
            <svg viewBox="0 0 500 200" preserveAspectRatio="none" class="chart-svg">
              <defs>
                <linearGradient id="lossGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#ef4444;stop-opacity:0.3"/>
                  <stop offset="100%" style="stop-color:#ef4444;stop-opacity:0"/>
                </linearGradient>
              </defs>
              <!-- Grid lines -->
              <line x1="0" y1="50" x2="500" y2="50" stroke="#334155" stroke-dasharray="4"/>
              <line x1="0" y1="100" x2="500" y2="100" stroke="#334155" stroke-dasharray="4"/>
              <line x1="0" y1="150" x2="500" y2="150" stroke="#334155" stroke-dasharray="4"/>
              <!-- Loss line -->
              <path
                v-if="trainingMetrics.length > 1"
                :d="'M ' + trainingMetrics.map((m, i) => `${i * (500 / 50)} ${200 - m.loss * 70}`).join(' L ')"
                fill="none"
                stroke="#ef4444"
                stroke-width="2"
              />
              <!-- Val Loss line -->
              <path
                v-if="trainingMetrics.length > 1"
                :d="'M ' + trainingMetrics.map((m, i) => `${i * (500 / 50)} ${200 - m.val_loss * 70}`).join(' L ')"
                fill="none"
                stroke="#f97316"
                stroke-width="2"
                stroke-dasharray="5,5"
              />
            </svg>
            <div class="chart-legend">
              <span class="legend-item"><span class="legend-color" style="background:#ef4444"></span>Train Loss</span>
              <span class="legend-item"><span class="legend-color" style="background:#f97316"></span>Val Loss</span>
            </div>
          </div>

          <div class="training-chart">
            <h4>Accuracy Curve</h4>
            <svg viewBox="0 0 500 200" preserveAspectRatio="none" class="chart-svg">
              <defs>
                <linearGradient id="accGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#22c55e;stop-opacity:0.3"/>
                  <stop offset="100%" style="stop-color:#22c55e;stop-opacity:0"/>
                </linearGradient>
              </defs>
              <!-- Grid lines -->
              <line x1="0" y1="50" x2="500" y2="50" stroke="#334155" stroke-dasharray="4"/>
              <line x1="0" y1="100" x2="500" y2="100" stroke="#334155" stroke-dasharray="4"/>
              <line x1="0" y1="150" x2="500" y2="150" stroke="#334155" stroke-dasharray="4"/>
              <!-- Accuracy line -->
              <path
                v-if="trainingMetrics.length > 1"
                :d="'M ' + trainingMetrics.map((m, i) => `${i * (500 / 50)} ${200 - m.accuracy * 200}`).join(' L ')"
                fill="none"
                stroke="#22c55e"
                stroke-width="2"
              />
              <!-- Val Accuracy line -->
              <path
                v-if="trainingMetrics.length > 1"
                :d="'M ' + trainingMetrics.map((m, i) => `${i * (500 / 50)} ${200 - m.val_accuracy * 200}`).join(' L ')"
                fill="none"
                stroke="#84cc16"
                stroke-width="2"
                stroke-dasharray="5,5"
              />
            </svg>
            <div class="chart-legend">
              <span class="legend-item"><span class="legend-color" style="background:#22c55e"></span>Train Acc</span>
              <span class="legend-item"><span class="legend-color" style="background:#84cc16"></span>Val Acc</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pipeline Section -->
    <section id="pipeline" class="section pipeline-section">
      <div class="section-header">
        <h2 class="section-title">🔄 ETL Pipeline Demo</h2>
        <p class="section-subtitle">Watch a data pipeline execute in real-time</p>
      </div>

      <button
        class="btn btn-primary btn-lg"
        :disabled="pipelineActive"
        @click="startPipeline"
      >
        {{ pipelineActive ? '⏳ Running...' : '▶️ Run Pipeline' }}
      </button>

      <div class="pipeline-visualization">
        <!-- Pipeline Stages -->
        <div class="pipeline-stages">
          <div
            v-for="(stage, index) in pipelineStages"
            :key="stage.id"
            :class="['pipeline-stage', stage.status]"
          >
            <div class="stage-icon">{{ stage.icon }}</div>
            <div class="stage-name">{{ stage.name }}</div>
            <div class="stage-progress-bar">
              <div
                class="stage-progress-fill"
                :style="{ width: stage.progress + '%' }"
              ></div>
            </div>
            <div v-if="index < pipelineStages.length - 1" class="stage-connector">
              <div class="connector-line"></div>
              <div class="connector-arrow">→</div>
            </div>
          </div>
        </div>

        <!-- Live Metrics -->
        <div v-if="pipelineMetrics" class="pipeline-metrics">
          <div class="pipeline-metric">
            <span class="pm-label">Rows/sec</span>
            <span class="pm-value">{{ pipelineMetrics.throughput.toLocaleString() }}</span>
          </div>
          <div class="pipeline-metric">
            <span class="pm-label">CPU</span>
            <span class="pm-value">{{ pipelineMetrics.cpu_usage }}%</span>
          </div>
          <div class="pipeline-metric">
            <span class="pm-label">Memory</span>
            <span class="pm-value">{{ pipelineMetrics.memory_usage }}%</span>
          </div>
          <div class="pipeline-metric">
            <span class="pm-label">Processed</span>
            <span class="pm-value">{{ pipelineMetrics.rows_processed.toLocaleString() }}</span>
          </div>
        </div>

        <!-- Logs -->
        <div class="pipeline-logs">
          <div class="logs-header">📜 Live Logs</div>
          <div class="logs-content">
            <div
              v-for="(log, index) in pipelineLogs"
              :key="index"
              :class="['log-entry', log.level.toLowerCase()]"
            >
              <span class="log-time">{{ new Date(log.timestamp).toLocaleTimeString() }}</span>
              <span :class="['log-level', log.level.toLowerCase()]">{{ log.level }}</span>
              <span class="log-stage">[{{ log.stage }}]</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="pipelineLogs.length === 0" class="logs-empty">
              Waiting for pipeline execution...
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Skills Section -->
    <section id="skills" class="section skills-section">
      <div class="section-header">
        <h2 class="section-title">🛠️ Tech Stack</h2>
        <p class="section-subtitle">Technologies I work with daily</p>
      </div>

      <div class="skills-grid">
        <div
          v-for="(categorySkills, category) in skillsByCategory"
          :key="category"
          class="skill-category"
        >
          <h3 class="category-title">{{ category }}</h3>
          <div class="skills-list">
            <div
              v-for="skill in categorySkills"
              :key="skill.name"
              class="skill-item"
            >
              <div class="skill-header">
                <span class="skill-icon">{{ skill.icon }}</span>
                <span class="skill-name">{{ skill.name }}</span>
                <span class="skill-level">{{ skill.level }}%</span>
              </div>
              <div class="skill-bar">
                <div
                  class="skill-bar-fill"
                  :style="{ width: skill.level + '%', '--delay': Math.random() * 0.5 + 's' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <p>Built with ❤️ using Vue.js + FastAPI + Docker</p>
        <p class="footer-tech">Real-time data streaming • Server-Sent Events • Canvas animations</p>
      </div>
    </footer>
  </div>
</template>

<style>
/* ═══════════════════════════════════════════════════════════════
   🎨 BASE STYLES & VARIABLES
   ═══════════════════════════════════════════════════════════════ */

:root {
  --bg-primary: #0a0f1e;
  --bg-secondary: #111827;
  --bg-card: #1e293b;
  --bg-card-hover: #334155;

  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;

  --accent-cyan: #22d3ee;
  --accent-purple: #8b5cf6;
  --accent-pink: #f472b6;
  --accent-orange: #fb923c;
  --accent-green: #22c55e;
  --accent-red: #ef4444;

  --gradient-primary: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
  --gradient-secondary: linear-gradient(135deg, var(--accent-pink), var(--accent-orange));

  --shadow-lg: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 30px rgba(34, 211, 238, 0.3);

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-full: 9999px;

  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --transition-slow: 500ms ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  overflow-x: hidden;
}

/* ═══════════════════════════════════════════════════════════════
   🧭 NAVIGATION
   ═══════════════════════════════════════════════════════════════ */

.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(10, 15, 30, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-logo {
  font-size: 1.5rem;
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: var(--radius-full);
  transition: var(--transition-fast);
}

.nav-link:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.nav-link.active {
  color: var(--accent-cyan);
  background: rgba(34, 211, 238, 0.1);
}

/* ═══════════════════════════════════════════════════════════════
   📄 SECTIONS
   ═══════════════════════════════════════════════════════════════ */

.section {
  min-height: 100vh;
  padding: 6rem 2rem 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

/* ═══════════════════════════════════════════════════════════════
   🦸 HERO SECTION
   ═══════════════════════════════════════════════════════════════ */

.hero {
  position: relative;
  justify-content: center;
  overflow: hidden;
  background: radial-gradient(ellipse at center, #1a1f3c 0%, var(--bg-primary) 70%);
}

.neural-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 800px;
}

.hero-badge {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: var(--radius-full);
  font-size: 0.9rem;
  color: var(--accent-cyan);
  margin-bottom: 1.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.hero-title {
  font-size: 4rem;
  font-weight: 900;
  margin-bottom: 1rem;
  line-height: 1.1;
}

.gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  backdrop-filter: blur(10px);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-cyan);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

/* ═══════════════════════════════════════════════════════════════
   🔘 BUTTONS
   ═══════════════════════════════════════════════════════════════ */

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition-normal);
  text-decoration: none;
  border: none;
}

.btn-primary {
  background: var(--gradient-primary);
  color: var(--bg-primary);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

/* ═══════════════════════════════════════════════════════════════
   📊 METRICS SECTION
   ═══════════════════════════════════════════════════════════════ */

.metrics-section {
  background: var(--bg-secondary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  width: 100%;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: var(--transition-normal);
}

.metric-card:hover {
  transform: translateY(-4px);
  border-color: rgba(34, 211, 238, 0.3);
  box-shadow: var(--shadow-glow);
}

.metric-card.wide {
  grid-column: span 2;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.metric-icon {
  font-size: 1.25rem;
}

.metric-name {
  font-weight: 600;
  color: var(--text-secondary);
}

.gauge-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge {
  width: 100%;
  max-width: 150px;
}

.gauge-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: -1rem;
}

.network-stats {
  display: flex;
  justify-content: space-around;
}

.network-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.network-arrow {
  font-size: 1.5rem;
  font-weight: bold;
}

.network-arrow.up {
  color: var(--accent-green);
}

.network-arrow.down {
  color: var(--accent-cyan);
}

.network-value {
  font-size: 1.25rem;
  font-weight: 600;
}

.metric-big-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--accent-cyan);
  text-align: center;
}

.metric-big-value .unit {
  font-size: 1rem;
  color: var(--text-muted);
  margin-left: 0.25rem;
}

/* Chart Container */
.chart-container {
  width: 100%;
  max-width: 1200px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.chart-title {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.mini-chart {
  height: 100px;
}

.mini-chart svg {
  width: 100%;
  height: 100%;
}

/* ═══════════════════════════════════════════════════════════════
   🤖 TRAINING SECTION
   ═══════════════════════════════════════════════════════════════ */

.training-section {
  background: var(--bg-primary);
}

.training-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.training-complete {
  padding: 0.5rem 1rem;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid var(--accent-green);
  border-radius: var(--radius-md);
  color: var(--accent-green);
  font-weight: 600;
}

.training-dashboard {
  width: 100%;
  max-width: 1200px;
}

.training-current {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.training-metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  min-width: 120px;
}

.training-metric-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.training-metric-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.training-metric-value.loss {
  color: var(--accent-red);
}

.training-metric-value.accuracy {
  color: var(--accent-green);
}

.training-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.training-chart {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.training-chart h4 {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.chart-svg {
  width: 100%;
  height: 200px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* ═══════════════════════════════════════════════════════════════
   🔄 PIPELINE SECTION
   ═══════════════════════════════════════════════════════════════ */

.pipeline-section {
  background: var(--bg-secondary);
}

.pipeline-visualization {
  width: 100%;
  max-width: 1200px;
  margin-top: 2rem;
}

.pipeline-stages {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.pipeline-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  min-width: 100px;
  position: relative;
  border: 2px solid transparent;
  transition: var(--transition-normal);
}

.pipeline-stage.pending {
  opacity: 0.5;
}

.pipeline-stage.running {
  border-color: var(--accent-cyan);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
  animation: stagePulse 1s infinite;
}

@keyframes stagePulse {
  0%, 100% { box-shadow: 0 0 20px rgba(34, 211, 238, 0.3); }
  50% { box-shadow: 0 0 30px rgba(34, 211, 238, 0.5); }
}

.pipeline-stage.completed {
  border-color: var(--accent-green);
  opacity: 1;
}

.stage-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.stage-name {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.stage-progress-bar {
  width: 100%;
  height: 4px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.stage-progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.1s linear;
}

.stage-connector {
  position: absolute;
  right: -30px;
  display: flex;
  align-items: center;
}

.connector-arrow {
  color: var(--text-muted);
  font-size: 1.25rem;
}

.pipeline-metrics {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.pipeline-metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: var(--radius-md);
}

.pm-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.pm-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--accent-cyan);
}

.pipeline-logs {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.logs-header {
  padding: 1rem;
  background: var(--bg-secondary);
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logs-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 1rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.85rem;
}

.log-entry {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

.log-time {
  color: var(--text-muted);
  min-width: 80px;
}

.log-level {
  min-width: 70px;
  font-weight: 600;
}

.log-level.info {
  color: var(--accent-cyan);
}

.log-level.success {
  color: var(--accent-green);
}

.log-level.error {
  color: var(--accent-red);
}

.log-stage {
  color: var(--accent-purple);
  min-width: 100px;
}

.log-message {
  color: var(--text-secondary);
}

.logs-empty {
  color: var(--text-muted);
  text-align: center;
  padding: 2rem;
}

/* ═══════════════════════════════════════════════════════════════
   🛠️ SKILLS SECTION
   ═══════════════════════════════════════════════════════════════ */

.skills-section {
  background: var(--bg-primary);
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  width: 100%;
}

.skill-category {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.category-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--accent-cyan);
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skill-item {
  transition: var(--transition-fast);
}

.skill-item:hover {
  transform: translateX(4px);
}

.skill-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.skill-icon {
  font-size: 1.1rem;
}

.skill-name {
  font-weight: 500;
  flex: 1;
}

.skill-level {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.skill-bar {
  height: 6px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.skill-bar-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
  animation: skillFill 1s ease-out forwards;
  animation-delay: var(--delay, 0s);
  width: 0;
}

@keyframes skillFill {
  from { width: 0; }
}

/* ═══════════════════════════════════════════════════════════════
   🦶 FOOTER
   ═══════════════════════════════════════════════════════════════ */

.footer {
  padding: 3rem 2rem;
  text-align: center;
  background: var(--bg-secondary);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-content p {
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.footer-tech {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* ═══════════════════════════════════════════════════════════════
   📱 RESPONSIVE
   ═══════════════════════════════════════════════════════════════ */

@media (max-width: 768px) {
  .nav {
    padding: 1rem;
  }

  .nav-links {
    display: none;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-stats {
    flex-direction: column;
    gap: 1rem;
  }

  .hero-actions {
    flex-direction: column;
  }

  .metric-card.wide {
    grid-column: span 1;
  }

  .training-charts {
    grid-template-columns: 1fr;
  }

  .pipeline-stages {
    flex-direction: column;
  }

  .stage-connector {
    display: none;
  }
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--bg-card-hover);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}
</style>
