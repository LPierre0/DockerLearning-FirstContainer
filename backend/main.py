from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:7958",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données du portfolio
PROFILE = {
    "name": "Pierre Lafage",
    "title": "Data Scientist",
    "bio": "Passionné par la data science et le machine learning, je développe des solutions innovantes pour extraire de la valeur des données.",
    "github": "https://github.com/LPierre0",
    "linkedin": "https://www.linkedin.com/in/pierre-lafage-31b520251/"
}

PROJECTS = [
    {
        "id": 1,
        "title": "Analyse Prédictive",
        "description": "Modèle de machine learning pour prédire les tendances du marché.",
        "tags": ["Python", "Scikit-learn", "Pandas"],
        "github_url": "https://github.com/LPierre0"
    },
    {
        "id": 2,
        "title": "Dashboard Analytics",
        "description": "Tableau de bord interactif pour visualiser des KPIs en temps réel.",
        "tags": ["Python", "Streamlit", "Plotly"],
        "github_url": "https://github.com/LPierre0"
    },
    {
        "id": 3,
        "title": "NLP Pipeline",
        "description": "Pipeline de traitement du langage naturel pour l'analyse de sentiments.",
        "tags": ["Python", "Transformers", "SpaCy"],
        "github_url": "https://github.com/LPierre0"
    },
    {
        "id": 4,
        "title": "Docker Learning",
        "description": "Apprentissage de la conteneurisation avec Docker et Docker Compose.",
        "tags": ["Docker", "FastAPI", "Vue.js"],
        "github_url": "https://github.com/LPierre0"
    }
]

@app.get("/")
def read_root():
    return {"message": "Portfolio API - Pierre Lafage"}

@app.get("/profile")
def get_profile():
    return PROFILE

@app.get("/projects")
def get_projects():
    return PROJECTS

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    for project in PROJECTS:
        if project["id"] == project_id:
            return project
    return {"error": "Project not found"}