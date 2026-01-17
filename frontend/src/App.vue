<script setup>
import { ref, onMounted } from 'vue';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const profile = ref({
  name: 'Pierre Lafage',
  title: 'Data Scientist',
  bio: '',
  github: '',
  linkedin: ''
});

const projects = ref([]);
const loading = ref(true);

async function fetchData() {
  try {
    const [profileRes, projectsRes] = await Promise.all([
      fetch(`${API_URL}/profile`),
      fetch(`${API_URL}/projects`)
    ]);
    profile.value = await profileRes.json();
    projects.value = await projectsRes.json();
  } catch (error) {
    console.error('Erreur API:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);
</script>

<template>
  <div class="portfolio">
    <!-- Hero Section -->
    <header class="hero">
      <div class="hero-content">
        <div class="avatar">PL</div>
        <h1>{{ profile.name }}</h1>
        <p class="title">{{ profile.title }}</p>
        <p class="bio">{{ profile.bio }}</p>
        
        <div class="social-links">
          <a :href="profile.github" target="_blank" class="social-btn github">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
          <a :href="profile.linkedin" target="_blank" class="social-btn linkedin">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
            </svg>
            LinkedIn
          </a>
        </div>
      </div>
    </header>

    <!-- Projects Section -->
    <main class="projects-section">
      <h2>Mes Projets</h2>
      
      <div v-if="loading" class="loading">Chargement...</div>
      
      <div v-else class="projects-grid">
        <article v-for="project in projects" :key="project.id" class="project-card">
          <h3>{{ project.title }}</h3>
          <p>{{ project.description }}</p>
          <div class="tags">
            <span v-for="tag in project.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <a :href="project.github_url" target="_blank" class="project-link">
            Voir sur GitHub →
          </a>
        </article>
      </div>
    </main>

    <!-- Footer -->
    <footer>
      <p>© 2026 Pierre Lafage • Fait avec Vue.js & FastAPI</p>
    </footer>
  </div>
</template>


<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  background-color: #030712;
  background-image: 
    radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
  color: #e2e8f0;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 10px;
}
::-webkit-scrollbar-track {
  background: #0f172a;
}
::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

.portfolio {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  animation: fadeIn 1s ease-out;
}

/* Hero Section */
.hero {
  text-align: center;
  padding: 6rem 1rem;
  margin-bottom: 2rem;
  position: relative;
}

.hero::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
  z-index: -1;
  filter: blur(60px);
}

.avatar {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 700;
  margin: 0 auto 2rem;
  color: white;
  box-shadow: 0 0 40px rgba(99, 102, 241, 0.4);
  border: 4px solid rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.hero h1 {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(to right, #ffffff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.05em;
}

.title {
  font-size: 1.5rem;
  color: #818cf8;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.bio {
  max-width: 600px;
  margin: 0 auto 2.5rem;
  line-height: 1.8;
  font-size: 1.1rem;
  color: #94a3b8;
}

.social-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.social-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.8rem 1.75rem;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.social-btn.github {
  background: rgba(36, 41, 46, 0.6);
  color: white;
}

.social-btn.linkedin {
  background: rgba(0, 119, 181, 0.6);
  color: white;
}

.social-btn:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.3);
}

/* Projects Section */
.projects-section {
  padding: 4rem 0;
}

.projects-section h2 {
  font-size: 2.25rem;
  margin-bottom: 3rem;
  text-align: center;
  color: #f8fafc;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  padding: 1rem;
}

.project-card {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 2rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.03), transparent);
  transform: translateX(-100%);
  transition: 0.5s;
}

.project-card:hover {
  transform: translateY(-8px);
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.4);
  background: rgba(30, 41, 59, 0.6);
}

.project-card:hover::before {
  transform: translateX(100%);
}

.project-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #f1f5f9;
  font-weight: 600;
}

.project-card p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
  line-height: 1.6;
  flex-grow: 1;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tag {
  background: rgba(99, 102, 241, 0.1);
  color: #818cf8;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.025em;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.project-link {
  color: #818cf8;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  padding: 0.5rem 0;
}

.project-link:hover {
  color: #a5b4fc;
  gap: 0.75rem;
}

/* Footer */
footer {
  text-align: center;
  padding: 4rem 2rem 2rem;
  color: #64748b;
  font-size: 0.9rem;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .hero {
    padding: 3rem 1rem;
  }
}
</style>
