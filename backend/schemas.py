from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ─── Users ────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    name: str
    theme_key: str
    target_weight_kg: Optional[float] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    target_weight_kg: Optional[float] = None


class UserStats(BaseModel):
    total_workouts: int
    total_sets: int
    current_streak: int
    longest_streak: int
    last_workout_at: Optional[datetime]


# ─── Exercises ────────────────────────────────────────────────────────────────

class ExerciseOut(BaseModel):
    id: int
    name: str
    muscle_group: str
    is_custom: bool
    created_by: Optional[int]

    model_config = {"from_attributes": True}


class ExerciseCreate(BaseModel):
    name: str
    muscle_group: str
    created_by: int


# ─── Workout Sets ─────────────────────────────────────────────────────────────

class SetOut(BaseModel):
    id: int
    workout_id: int
    exercise_id: int
    exercise_name: str
    exercise_muscle_group: str
    set_number: int
    weight_kg: Optional[float]
    reps: Optional[int]
    rpe: Optional[int]
    duration_seconds: Optional[int]
    resistance: Optional[int]
    calories: Optional[int]
    notes: Optional[str] = None
    status: str
    logged_at: datetime

    model_config = {"from_attributes": True}


class SetCreate(BaseModel):
    exercise_id: int
    set_number: int
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    rpe: Optional[int] = None
    duration_seconds: Optional[int] = None
    resistance: Optional[int] = None
    calories: Optional[int] = None
    notes: Optional[str] = None
    status: str = "pending"


class SetUpdate(BaseModel):
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    rpe: Optional[int] = None
    duration_seconds: Optional[int] = None
    resistance: Optional[int] = None
    calories: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None


# ─── Workouts ─────────────────────────────────────────────────────────────────

class WorkoutOut(BaseModel):
    id: int
    user_id: int
    type: str
    name: Optional[str]
    notes: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime]
    set_count: int = 0
    exercise_count: int = 0

    model_config = {"from_attributes": True}


class WorkoutDetail(BaseModel):
    id: int
    user_id: int
    type: str
    name: Optional[str]
    notes: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    sets: list[SetOut]

    model_config = {"from_attributes": True}


class WorkoutCreate(BaseModel):
    user_id: int
    type: str
    name: Optional[str] = None
    template_id: Optional[int] = None


class WorkoutUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    name: Optional[str] = None


# ─── Progress ─────────────────────────────────────────────────────────────────

class PROut(BaseModel):
    exercise_id: int
    exercise_name: str
    muscle_group: str
    weight_kg: Optional[float]
    reps: Optional[int]
    date: Optional[datetime]


class ProgressEntry(BaseModel):
    date: datetime
    max_weight: Optional[float]
    total_volume: Optional[float]


class ExerciseProgress(BaseModel):
    exercise: ExerciseOut
    pr: Optional[PROut]
    history: list[ProgressEntry]


# ─── Boosts ───────────────────────────────────────────────────────────────────

class BoostOut(BaseModel):
    id: int
    from_user_id: int
    from_name: str
    message: str
    sent_at: datetime
    read_at: Optional[datetime]

    model_config = {"from_attributes": True}


class BoostCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    message: str


# ─── Body Weight ──────────────────────────────────────────────────────────────

class BodyWeightOut(BaseModel):
    id: int
    user_id: int
    weight_kg: float
    logged_at: datetime

    model_config = {"from_attributes": True}


class BodyWeightCreate(BaseModel):
    user_id: int
    weight_kg: float
    logged_at: Optional[datetime] = None


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardUser(BaseModel):
    id: int
    name: str
    theme_key: str
    stats: UserStats
    recent_workouts: list[WorkoutOut]


class DashboardOut(BaseModel):
    users: list[DashboardUser]
    recent_boosts: list[BoostOut]
