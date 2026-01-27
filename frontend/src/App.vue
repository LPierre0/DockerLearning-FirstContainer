<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

// -- STATE --
const activeTab = ref('home')
const activeProject = ref(null) 
const isMoving = ref(false)

// -- DATA --
const projects = ref([])
const posts = ref([])
const profile = ref({ name: 'Loading...', title: '' })

// -- 3D CONFIG --
const cameraTarget = { x: 0, y: 0, z: 60 }
const lookTarget = { x: 0, y: 0, z: 0 }
const currentCameraPos = { x: 0, y: 0, z: 60 }
const currentLookAt = { x: 0, y: 0, z: 0 }

// Base Zones
const LOCATIONS = {
    home: { pos: { x: 0, y: 0, z: 60 }, look: { x: 0, y: 0, z: 0 } },
    projects: { pos: { x: -40, y: 15, z: 40 }, look: { x: -25, y: 5, z: 0 } },
    blog: { pos: { x: 40, y: -10, z: 40 }, look: { x: 25, y: -5, z: 0 } }
}

// -- NAVIGATION --
const navigateTo = (tab) => {
    if (activeTab.value === tab && !activeProject.value) return
    isMoving.value = true
    activeTab.value = tab
    activeProject.value = null
    const loc = LOCATIONS[tab]
    setTarget(loc.pos, loc.look)
    setTimeout(() => { isMoving.value = false }, 1200)
}

const selectProject = (p) => {
    activeProject.value = p
    isMoving.value = true
    // Fly to specific planet
    // We used World Coordinates (calculated in initProjectPlanets), so we fly there.
    const targetPos = { x: p.coords.x + 8, y: p.coords.y + 4, z: p.coords.z + 8 }
    const targetLook = { x: p.coords.x, y: p.coords.y, z: p.coords.z }
    setTarget(targetPos, targetLook)
    setTimeout(() => { isMoving.value = false }, 1000)
}

const setTarget = (pos, look) => {
    cameraTarget.x = pos.x; cameraTarget.y = pos.y; cameraTarget.z = pos.z
    lookTarget.x = look.x; lookTarget.y = look.y; lookTarget.z = look.z
}

// -- FETCHING --
const fetchData = async () => {
  try {
    const [profRes, projRes, blogRes] = await Promise.all([
      fetch('/api/profile'),
      fetch('/api/projects'),
      fetch('/api/blog')
    ])
    profile.value = await profRes.json()
    const rawProjects = await projRes.json()
    posts.value = await blogRes.json()
    initProjectPlanets(rawProjects)
  } catch (e) {
      console.error("Data load failed", e)
      // Fallback data if API fails
      if(projects.value.length === 0) {
          initProjectPlanets([{id:1, name:'Demo Project', status:'Error', stack:['Offline'], description:'Could not load projects.'}])
      }
  }
}

// -- 3D ENGINE --
const canvasRef = ref(null)
let renderer, scene, camera, animationId
let projGroup, blogGroup, core
const projectMeshes = []

const initThreeJS = () => {
    if (!canvasRef.value) return
    
    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x020617) 
    scene.fog = new THREE.FogExp2(0x020617, 0.02)

    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000)
    camera.position.set(0, 0, 60)

    renderer = new THREE.WebGLRenderer({ canvas: canvasRef.value, antialias: true })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    
    // --- WORLD ---
    // 1. HQ Core
    const coreGeo = new THREE.IcosahedronGeometry(5, 2)
    const coreMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6, wireframe: true, transparent: true, opacity: 0.3 })
    core = new THREE.Mesh(coreGeo, coreMat)
    core.add(new THREE.PointLight(0x3b82f6, 2, 50))
    scene.add(core)
    
    // 2. Blog Cluster
    blogGroup = new THREE.Group()
    blogGroup.position.set(35, -10, 0)
    for(let i=0; i<10; i++) {
        const mesh = new THREE.Mesh(
            new THREE.ConeGeometry(1, 2, 4),
            new THREE.MeshBasicMaterial({ color: 0xf43f5e, wireframe: true })
        )
        mesh.position.set((Math.random()-0.5)*15, (Math.random()-0.5)*15, (Math.random()-0.5)*15)
        mesh.rotation.set(Math.random(), Math.random(), Math.random())
        blogGroup.add(mesh)
    }
    scene.add(blogGroup)
    
    // 3. Project Group (Container)
    // We position the GROUP at the project zone location
    projGroup = new THREE.Group()
    projGroup.position.set(-35, 10, 0) 
    scene.add(projGroup)

    // 4. Stars
    const sPos = new Float32Array(2000 * 3)
    for(let i=0; i<6000; i++) sPos[i] = (Math.random() - 0.5) * 300
    const stars = new THREE.Points(
        new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(sPos, 3)),
        new THREE.PointsMaterial({ color: 0xffffff, size: 0.2 })
    )
    scene.add(stars)

    // LOOP
    const animate = () => {
        animationId = requestAnimationFrame(animate)
        
        // Global Rotations
        if(core) core.rotation.y += 0.002
        if(blogGroup) blogGroup.rotation.y += 0.001
        
        // Individual Animations
        projectMeshes.forEach((mesh, idx) => {
            mesh.rotation.y += 0.005 + (idx * 0.001)
            mesh.rotation.x += 0.002
        })

        // Camera Lerp
        currentCameraPos.x += (cameraTarget.x - currentCameraPos.x) * 0.04
        currentCameraPos.y += (cameraTarget.y - currentCameraPos.y) * 0.04
        currentCameraPos.z += (cameraTarget.z - currentCameraPos.z) * 0.04
        
        currentLookAt.x += (lookTarget.x - currentLookAt.x) * 0.04
        currentLookAt.y += (lookTarget.y - currentLookAt.y) * 0.04
        currentLookAt.z += (lookTarget.z - currentLookAt.z) * 0.04
        
        camera.position.set(currentCameraPos.x, currentCameraPos.y, currentCameraPos.z)
        camera.lookAt(currentLookAt.x, currentLookAt.y, currentLookAt.z)

        renderer.render(scene, camera)
    }
    animate()

    window.addEventListener('resize', () => {
        if (!camera || !renderer) return
        camera.aspect = window.innerWidth / window.innerHeight
        camera.updateProjectionMatrix()
        renderer.setSize(window.innerWidth, window.innerHeight)
    })
}

// Helper: Spawn Planets
const initProjectPlanets = (data) => {
    if(!scene || !Array.isArray(data)) return

    // Clear old meshes if any
    projectMeshes.forEach(m => {
        if(m.geometry) m.geometry.dispose()
        if(m.material) m.material.dispose()
        projGroup.remove(m)
    })
    projectMeshes.length = 0

    projects.value = data.map((p, index) => {
        const angle = index * 2.5
        const radius = 8 + (index * 2) 
        
        // Local coordinates inside the projGroup
        const localX = Math.cos(angle) * radius 
        const localY = Math.sin(angle) * radius * 0.5
        const localZ = (Math.random() - 0.5) * 10 

        // World coordinates (approximate, ignoring group rotation for simplicity of flight target)
        // Since projGroup is at (-35, 10, 0)
        const worldX = localX - 35
        const worldY = localY + 10
        const worldZ = localZ

        const mesh = new THREE.Mesh(
            new THREE.SphereGeometry(2, 16, 16),
            new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true, transparent: true, opacity: 0.8 })
        )
        mesh.position.set(localX, localY, localZ)
        
        // Add to the GROUP, not the SCENE directly
        projGroup.add(mesh)
        projectMeshes.push(mesh)

        return {
            ...p,
            coords: { x: worldX, y: worldY, z: worldZ }
        }
    })
}

onMounted(() => {
    initThreeJS()
    fetchData()
})
onUnmounted(() => {
    cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="immersive-layout">
    <canvas ref="canvasRef" class="world-canvas"></canvas>
    
    <!-- HUD -->
    <nav class="hud-dock">
        <button @click="navigateTo('projects')" :class="{ active: activeTab === 'projects' }">
            <span class="lbl">PROJECTS</span>
            <span class="marker green"></span>
        </button>
        <button @click="navigateTo('home')" :class="{ active: activeTab === 'home' }" class="home-btn">
            <span class="marker blue"></span>
            <span class="lbl">HQ</span>
        </button>
        <button @click="navigateTo('blog')" :class="{ active: activeTab === 'blog' }">
            <span class="marker red"></span>
            <span class="lbl">LOGS</span>
        </button>
    </nav>

    <!-- CONTENT -->
    <transition name="fade">
        <main class="content-overlay" v-if="!isMoving">
            
            <!-- HQ -->
            <div v-if="activeTab === 'home'" class="glass-panel center-panel">
                <div class="glitch-header">
                    <h1>{{ profile.name }}</h1>
                    <p>{{ profile.title }}</p>
                </div>
                <p class="bio-text">{{ profile.bio }}</p>
            </div>

            <!-- PROJECTS SELECT -->
            <div v-if="activeTab === 'projects' && !activeProject" class="glass-panel side-panel">
                <h2>Select Target</h2>
                <div class="scroll-list">
                    <div v-for="p in projects" :key="p.id" class="list-item clickable" @click="selectProject(p)">
                        <div class="item-head">
                            <strong>{{ p.name }}</strong>
                            <span class="tag">{{ p.status }}</span>
                        </div>
                        <span class="coord-text">SEC: [{{ p.coords.x.toFixed(0) }}:{{ p.coords.y.toFixed(0) }}]</span>
                    </div>
                </div>
            </div>

            <!-- PROJECTS DETAIL -->
            <div v-if="activeTab === 'projects' && activeProject" class="glass-panel detail-panel">
                <button class="back-btn" @click="navigateTo('projects')">← RETURN TO ORBIT</button>
                <div class="detail-content">
                    <h1>{{ activeProject.name }}</h1>
                    <div class="meta-row">
                        <span class="tag large">{{ activeProject.status }}</span>
                        <div class="tech-stack">
                            <span v-for="t in activeProject.stack" :key="t" class="tech-pill">{{ t }}</span>
                        </div>
                    </div>
                    <p class="desc-large">{{ activeProject.description }}</p>
                </div>
            </div>

            <!-- BLOG -->
            <div v-if="activeTab === 'blog'" class="glass-panel side-panel">
                <h2>Encrypted Logs</h2>
                <div class="scroll-list">
                    <div v-for="post in posts" :key="post.id" class="list-item">
                        <strong>{{ post.title }}</strong>
                        <span class="date">{{ post.date }}</span>
                    </div>
                </div>
            </div>

        </main>
    </transition>
  </div>
</template>

<style scoped>
.immersive-layout { width: 100vw; height: 100vh; overflow: hidden; position: relative; font-family: 'Inter', sans-serif; color: white; background: #020617; }
.world-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }

/* HUD */
.hud-dock { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; gap: 30px; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); padding: 20px; }
.hud-dock button { background: none; border: none; color: #64748b; font-weight: 700; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 8px; transition: all 0.3s; }
.hud-dock button:hover, .hud-dock button.active { color: white; text-shadow: 0 0 10px white; }
.marker { width: 8px; height: 8px; background: currentColor; border-radius: 50%; box-shadow: 0 0 10px currentColor; }
.marker.blue { color: #3b82f6; } .marker.green { color: #10b981; } .marker.red { color: #f43f5e; }

/* PANELS */
.content-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; pointer-events: none; display: flex; align-items: center; justify-content: center; }
.glass-panel { pointer-events: auto; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); padding: 2rem; border-radius: 8px; box-shadow: 0 0 40px rgba(0,0,0,0.9); color: #e2e8f0; }
.center-panel { width: 400px; text-align: center; border-top: 2px solid #3b82f6; }
.side-panel { width: 350px; position: absolute; right: 10%; border-right: 2px solid #10b981; }
.detail-panel { width: 500px; border-left: 4px solid #10b981; background: rgba(5, 20, 35, 0.95); }

/* ELEMENTS */
.back-btn { background: transparent; border: 1px solid #10b981; color: #10b981; padding: 8px 16px; margin-bottom: 20px; cursor: pointer; font-size: 0.8rem; letter-spacing: 2px; }
.back-btn:hover { background: #10b981; color: black; }
.meta-row { display: flex; gap: 10px; align-items: center; margin: 15px 0; }
.tag.large { font-size: 0.9rem; padding: 4px 10px; border: 1px solid #10b981; color: #10b981; }
.tech-pill { font-size: 0.8rem; color: #94a3b8; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; }
.desc-large { font-size: 1.1rem; line-height: 1.6; color: #cbd5e1; }
.scroll-list { max-height: 60vh; overflow-y: auto; margin-top: 1rem; }
.list-item { padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.2s; }
.clickable { cursor: pointer; }
.clickable:hover { background: rgba(16, 185, 129, 0.1); }
.tag { font-size: 0.7rem; color: #10b981; border: 1px solid #10b981; padding: 2px 4px; }
.coord-text { display: block; font-family: monospace; font-size: 0.7rem; color: #475569; margin-top: 4px; }

/* ANIM */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
