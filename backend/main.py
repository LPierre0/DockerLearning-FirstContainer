from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import engine, Base
from seed import seed_initial_data
import models  # noqa: F401 – registers ORM models with Base
from routers import (
    body_measurements,
    body_weight,
    boosts,
    dashboard,
    exercises,
    favorites,
    insights,
    progress,
    sets,
    users,
    workouts,
)


def run_migrations():
    """Add new columns to existing tables (SQLAlchemy create_all won't do this)."""
    with engine.connect() as conn:
        # Columns added to workout_sets after initial schema creation
        existing_sets = {row[1] for row in conn.execute(text("PRAGMA table_info(workout_sets)"))}
        for col, definition in [
            ("duration_seconds", "INTEGER"),
            ("resistance",       "INTEGER"),
            ("calories",         "INTEGER"),
            ("notes",            "TEXT"),
        ]:
            if col not in existing_sets:
                conn.execute(text(f"ALTER TABLE workout_sets ADD COLUMN {col} {definition}"))

        # Columns added to users after initial schema creation
        existing_users = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "target_weight_kg" not in existing_users:
            conn.execute(text("ALTER TABLE users ADD COLUMN target_weight_kg REAL"))

        # Columns added to exercises after initial schema creation
        existing_exercises = {row[1] for row in conn.execute(text("PRAGMA table_info(exercises)"))}
        if "photo_filename" not in existing_exercises:
            conn.execute(text("ALTER TABLE exercises ADD COLUMN photo_filename TEXT"))

        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    seed_initial_data()
    yield


app = FastAPI(title="FitCouple API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(exercises.router)
app.include_router(workouts.router)
app.include_router(sets.router)
app.include_router(progress.router)
app.include_router(boosts.router)
app.include_router(dashboard.router)
app.include_router(body_weight.router)
app.include_router(body_measurements.router)
app.include_router(favorites.router)
app.include_router(insights.router)


@app.get("/")
def root():
    return {"status": "ok", "app": "FitCouple API"}
