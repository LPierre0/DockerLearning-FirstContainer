<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

// -- STATE --
const terminalOutput = ref([
  { type: 'info', text: 'INITIALIZING SYSTEM...' },
  { type: 'info', text: 'CONNECTING TO DOCKER MAINFRAME...' },
  { type: 'success', text: 'CONNECTION ESTABLISHED.' }
])
const commandInput = ref('')
const matrixCanvas = ref(null)
const hackLogs = ref([])
const systemStatus = ref('ONLINE')
const cpuLoad = ref(0)
const sphereCanvas = ref(null)

// -- TERMINAL LOGIC --
const executeCommand = async () => {
  const cmd = commandInput.value.trim()
  if (!cmd) return

  // Client-side commands
  if (cmd.toLowerCase() === 'clear') {
      terminalOutput.value = []
      commandInput.value = ''
      return
  }

  terminalOutput.value.push({ type: 'user', text: `> ${cmd}` })
  commandInput.value = ''

  try {
    const res = await fetch(`/api/terminal/${encodeURIComponent(cmd)}`)
    const data = await res.json()
    // The backend returns { output: "..." }
    terminalOutput.value.push({ type: 'system', text: data.output })
  } catch (e) {
    terminalOutput.value.push({ type: 'error', text: 'CONNECTION ERROR' })
  }
  
  // Auto scroll
  scrollToBottom()
}

const scrollToBottom = () => {
    nextTick(() => {
        const el = document.getElementById('terminal-content')
        if (el) el.scrollTop = el.scrollHeight
    })
}

// -- MATRIX RAIN (Visual Only for BG) --
// We will use a local simulation for the smooth 60fps background,
// but we will overlay the backend data stream in the "Data Stream" panel.
const initMatrix = () => {
  const canvas = matrixCanvas.value
  if(!canvas) return
  const ctx = canvas.getContext('2d')
  
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const nums = '0123456789'
  const katakana = 'abcdefghijklmnopqrstuvwxyz'
  const alphabet = latin + nums + katakana

  const fontSize = 16
  const columns = canvas.width/fontSize

  const rainDrops = []

  for( let x = 0; x < columns; x++ ) {
      rainDrops[x] = 1;
  }

  const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#0F0';
      ctx.font = fontSize + 'px monospace';

      for(let i = 0; i < rainDrops.length; i++)
      {
          const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
          ctx.fillText(text, i*fontSize, rainDrops[i]*fontSize);

          if(rainDrops[i]*fontSize > canvas.height && Math.random() > 0.975){
              rainDrops[i] = 0;
          }
          rainDrops[i]++;
      }
  }
  
  return setInterval(draw, 30);
}

// -- DATA STREAMS (SSE) --
let hackSource = null
const initStreams = () => {
    // Connect to the 'Hack' stream for the log panel
    hackSource = new EventSource('/api/stream/hack')
    hackSource.onmessage = (event) => {
        const data = JSON.parse(event.data)
        // Keep last 20 logs
        const logMsg = data.message ? `[${data.tag}] ${data.message}` : JSON.stringify(data)
        hackLogs.value.unshift(logMsg)
        if (hackLogs.value.length > 20) hackLogs.value.pop()
        
        // Randomize CPU load for effect
        cpuLoad.value = Math.floor(Math.random() * 30 + 70) 
    }
}

// -- 3D SPHERE (Wireframe) --
// Simple 3D projection on 2D canvas
const initSphere = () => {
    const canvas = sphereCanvas.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let width = canvas.width = canvas.parentElement.clientWidth
    let height = canvas.height = canvas.parentElement.clientHeight
    
    // Resize observer could be added here
    
    let rotation = 0
    const points = []
    const numPoints = 150
    const rad = Math.min(width, height) * 0.4

    // Gen points on sphere
    for (let i =0; i<numPoints; i++){
        const y = 1 - (i / (numPoints - 1)) * 2;
        const radius = Math.sqrt(1 - y * y);
        const theta = 2.39996323 * i; // Golden angle inc
        
        const x = Math.cos(theta) * radius;
        const z = Math.sin(theta) * radius;
        points.push({x: x*rad, y: y*rad, z: z*rad})
    }
    
    const drawSphere = () => {
        ctx.clearRect(0,0,width,height)
        ctx.strokeStyle = '#00ff41'
        ctx.fillStyle = '#00ff41'
        
        rotation += 0.01
        
        // Rotation Matrix (Y axis)
        const cos = Math.cos(rotation)
        const sin = Math.sin(rotation)
        
        points.forEach(p => {
            // Rotate
            const rx = p.x * cos - p.z * sin
            const rz = p.x * sin + p.z * cos
            
            // Project
            const scale = 300 / (300 + rz + rad) // perspective
            const px = rx * scale + width/2
            const py = p.y * scale + height/2
            
            ctx.beginPath()
            ctx.arc(px, py, 1.5, 0, Math.PI*2)
            ctx.fill()
            
            // Connect lines (simple distance check or just draw points for 'cloud')
            // For wireframe effect, connect to neighbor? Too expensive for O(N^2) here in JS without optimization
            // Let's just draw lines to center or random glitch lines
        })
        
        requestAnimationFrame(drawSphere)
    }
    drawSphere()
}

// -- LIFECYCLE --
let matrixInterval = null

onMounted(() => {
    // Wait for DOM
    nextTick(() => {
        matrixInterval = initMatrix()
        initStreams()
        initSphere()
    })
    
    // Resize listeners
    window.addEventListener('resize', () => {
       if (matrixCanvas.value) {
           matrixCanvas.value.width = window.innerWidth
           matrixCanvas.value.height = window.innerHeight
       }
    })
})

onUnmounted(() => {
    if (matrixInterval) clearInterval(matrixInterval)
    if (hackSource) hackSource.close()
})

</script>

<template>
  <div class="cyber-container">
    
    <!-- BACKGROUND LAYER -->
    <canvas ref="matrixCanvas" class="matrix-bg"></canvas>
    
    <!-- UI LAYER -->
    <div class="ui-grid">
        
        <!-- HEADER -->
        <header class="header">
            <h1 class="glitch" data-text="DOCKER_MAINFRAME // V1.0">DOCKER_MAINFRAME // V1.0</h1>
            <div class="status-badge">
                STATUS: <span class="blink">{{ systemStatus }}</span>
                <span class="load-bar">CPU: {{ cpuLoad }}%</span>
            </div>
        </header>

        <!-- LEFT PANEL: VISUALIZATION -->
        <aside class="panel left-panel">
            <div class="panel-header">>> NEURALNET_VISUALIZER</div>
            <div class="visualizer-container">
                <canvas ref="sphereCanvas"></canvas>
            </div>
            <div class="data-readout">
                <div v-for="(log, i) in hackLogs.slice(0, 5)" :key="i" class="log-line">
                    <template v-if="log">
                        {{ log.split(' ')[0] }} <span class="hex-block">{{ log.split(' ').slice(1).join(' ') }}</span>
                    </template>
                </div>
            </div>
        </aside>

        <!-- CENTER PANEL: TERMINAL -->
        <main class="panel center-panel">
            <div class="panel-header">>> REMOTE_SHELL_ACCESS</div>
            <div class="terminal-window" id="terminal-content">
                <div v-for="(line, idx) in terminalOutput" :key="idx" :class="['term-line', line.type]">
                    <span class="timestamp">[{{ new Date().toLocaleTimeString() }}]</span>
                    <span v-if="line.type === 'user'" class="prompt">$ </span>
                    <pre>{{ line.text }}</pre>
                </div>
            </div>
            <div class="input-line">
                <span class="prompt">root@container:~#</span>
                <input 
                    v-model="commandInput" 
                    @keyup.enter="executeCommand"
                    type="text" 
                    autofocus
                    placeholder="Enter command..."
                />
            </div>
        </main>

        <!-- RIGHT PANEL: LOGS -->
        <aside class="panel right-panel">
            <div class="panel-header">>> ACTIVE_STREAMS</div>
            <div class="stream-container">
                 <div v-for="(log, i) in hackLogs" :key="i" class="stream-item">
                    <span class="icon">⚠</span> {{ log }}
                 </div>
            </div>
        </aside>
        
    </div>
  </div>
</template>

<style scoped>
/* LAYOUT */
.cyber-container {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}

.matrix-bg {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 0;
    /* Opacity is handled in draw loop by clearing with non-opaque black */
}

.ui-grid {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
    padding: 20px;
    display: grid;
    grid-template-columns: 300px 1fr 300px;
    grid-template-rows: 60px 1fr;
    gap: 20px;
}

/* HEADER */
.header {
    grid-column: 1 / -1;
    border-bottom: 2px solid var(--c-text);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0,0,0,0.8);
    backdrop-filter: blur(5px);
}

.header h1 {
    font-size: 1.5rem;
    margin: 0;
    padding-left: 10px;
    text-shadow: 2px 2px 0px var(--c-accent);
}

.status-badge {
    padding-right: 10px;
    font-weight: bold;
    color: var(--c-text);
}

.blink {
    animation: blinker 1s linear infinite;
    color: var(--c-alert);
}

@keyframes blinker {
  50% { opacity: 0; }
}

/* PANELS */
.panel {
    border: 1px solid var(--c-text);
    background: rgba(5, 5, 5, 0.85);
    display: flex;
    flex-direction: column;
    box-shadow: 0 0 10px var(--c-grid);
    position: relative;
    overflow: hidden;
}

.panel::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: var(--c-text);
    box-shadow: 0 0 10px var(--c-text);
    animation: scan 3s linear infinite;
    opacity: 0.3;
}

@keyframes scan {
    0% { top: 0%; }
    100% { top: 100%; }
}

.panel-header {
    background: var(--c-text);
    color: var(--c-bg);
    padding: 5px 10px;
    font-weight: bold;
    font-size: 1.1rem;
    text-transform: uppercase;
}

/* TERMINAL */
.center-panel {
    grid-column: 2 / 3;
}

.terminal-window {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
    font-family: 'Courier New', monospace;
    scrollbar-width: thin;
    scrollbar-color: var(--c-text) #000;
}

.term-line {
    margin-bottom: 5px;
    word-break: break-all;
}

.term-line pre {
    display: inline;
    white-space: pre-wrap;
    margin: 0;
}

.term-line.user { color: var(--c-accent); }
.term-line.system { color: var(--c-text); }
.term-line.error { color: var(--c-alert); }

.timestamp {
    color: #555;
    margin-right: 10px;
    font-size: 0.8em;
}

.input-line {
    display: flex;
    padding: 10px;
    border-top: 1px dashed var(--c-text);
    background: #000;
}

.input-line input {
    background: transparent;
    border: none;
    color: var(--c-text);
    font-family: inherit;
    font-size: 1rem;
    flex: 1;
    margin-left: 10px;
    outline: none;
}

/* VISUALIZER */
.visualizer-container {
    flex: 1;
    position: relative;
    background: #000;
}

.visualizer-container canvas {
    display: block;
}

.data-readout {
    height: 150px;
    overflow: hidden;
    padding: 10px;
    font-size: 0.7rem;
    color: #555;
    border-top: 1px solid #333;
    background: #080808;
}

.log-line {
    color: #008f11;
    margin-bottom: 2px;
}
.hex-block {
    color: #444;
}

/* STREAMS */
.stream-container {
    padding: 10px;
    overflow-y: auto;
    font-size: 0.8rem;
    flex: 1;
}

.stream-item {
    margin-bottom: 8px;
    border-left: 2px solid var(--c-accent);
    padding-left: 5px;
    animation: slideIn 0.3s ease;
    background: rgba(255, 0, 255, 0.05);
    padding: 5px;
}

@keyframes slideIn {
    from { transform: translateX(20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Glitch Effect */
.glitch {
  position: relative;
  color: var(--c-text);
  font-weight: 900;
}

.glitch::before,
.glitch::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.glitch::before {
  left: 2px;
  text-shadow: -1px 0 #ff00c1;
  clip: rect(44px, 450px, 56px, 0);
  animation: glitch-anim 5s infinite linear alternate-reverse;
}

.glitch::after {
  left: -2px;
  text-shadow: -1px 0 #00fff9;
  clip: rect(44px, 450px, 56px, 0);
  animation: glitch-anim2 5s infinite linear alternate-reverse;
}

@keyframes glitch-anim {
  0% { clip: rect(11px, 9999px, 26px, 0); }
  20% { clip: rect(82px, 9999px, 12px, 0); }
  40% { clip: rect(45px, 9999px, 86px, 0); }
  60% { clip: rect(5px, 9999px, 100px, 0); }
  80% { clip: rect(66px, 9999px, 21px, 0); }
  100% { clip: rect(93px, 9999px, 5px, 0); }
}
@keyframes glitch-anim2 {
  0% { clip: rect(65px, 9999px, 100px, 0); }
  20% { clip: rect(12px, 9999px, 5px, 0); }
  40% { clip: rect(89px, 9999px, 33px, 0); }
  60% { clip: rect(2px, 9999px, 66px, 0); }
  80% { clip: rect(45px, 9999px, 12px, 0); }
  100% { clip: rect(11px, 9999px, 77px, 0); }
}

/* Responsive adjustments */
@media (max-width: 1024px) {
    .ui-grid {
        grid-template-columns: 1fr;
        grid-template-rows: 60px 300px minmax(300px, 1fr) 200px;
        overflow-y: auto;
    }
    .header { grid-column: 1; }
    .panel { grid-column: 1; }
    
    .cyber-container {
        overflow-y: auto;
    }
}
</style>
