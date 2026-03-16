from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Workout, WorkoutSet, Exercise, User
from routers.exercises import exercise_photo_url
from schemas import PROut, ExerciseProgress, ExerciseOut, ProgressEntry

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{user_id}/prs", response_model=list[PROut])
def get_prs(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # For each exercise, find the set with the highest weight_kg
    subq = (
        db.query(
            WorkoutSet.exercise_id,
            func.max(WorkoutSet.weight_kg).label("max_weight"),
        )
        .join(Workout)
        .filter(
            Workout.user_id == user_id,
            WorkoutSet.status == "done",
            WorkoutSet.weight_kg.isnot(None),
        )
        .group_by(WorkoutSet.exercise_id)
        .subquery()
    )

    rows = db.query(subq).all()
    prs = []
    for row in rows:
        exercise_id, max_weight = row
        # Find the actual set for the date
        best_set = (
            db.query(WorkoutSet)
            .join(Workout)
            .filter(
                Workout.user_id == user_id,
                WorkoutSet.exercise_id == exercise_id,
                WorkoutSet.weight_kg == max_weight,
                WorkoutSet.status == "done",
            )
            .order_by(WorkoutSet.logged_at.desc())
            .first()
        )
        if best_set:
            ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
            prs.append(PROut(
                exercise_id=exercise_id,
                exercise_name=ex.name,
                muscle_group=ex.muscle_group,
                exercise_photo_url=exercise_photo_url(exercise_id, ex.photo_filename),
                weight_kg=max_weight,
                reps=best_set.reps,
                date=best_set.logged_at,
            ))

    return prs


@router.get("/{user_id}/exercise/{exercise_id}", response_model=ExerciseProgress)
def get_exercise_progress(user_id: int, exercise_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Group sets by workout date
    workouts_with_sets = (
        db.query(Workout)
        .join(WorkoutSet)
        .filter(
            Workout.user_id == user_id,
            WorkoutSet.exercise_id == exercise_id,
            WorkoutSet.status == "done",
        )
        .order_by(Workout.started_at)
        .all()
    )

    history = []
    pr_weight = None
    pr_reps = None
    pr_date = None

    for workout in workouts_with_sets:
        sets_for_ex = [
            s for s in workout.sets
            if s.exercise_id == exercise_id and s.status == "done"
        ]
        if not sets_for_ex:
            continue
        max_w = max((s.weight_kg for s in sets_for_ex if s.weight_kg), default=None)
        total_v = sum(
            (s.weight_kg or 0) * (s.reps or 0) for s in sets_for_ex
        ) or None

        if max_w and (pr_weight is None or max_w > pr_weight):
            pr_weight = max_w
            best = max(sets_for_ex, key=lambda s: s.weight_kg or 0)
            pr_reps = best.reps
            pr_date = best.logged_at

        history.append(ProgressEntry(
            date=workout.started_at,
            max_weight=max_w,
            total_volume=total_v,
        ))

    pr = None
    if pr_weight is not None:
        pr = PROut(
            exercise_id=exercise_id,
            exercise_name=exercise.name,
            muscle_group=exercise.muscle_group,
            exercise_photo_url=exercise_photo_url(exercise_id, exercise.photo_filename),
            weight_kg=pr_weight,
            reps=pr_reps,
            date=pr_date,
        )

    return ExerciseProgress(
        exercise=ExerciseOut(
            id=exercise.id,
            name=exercise.name,
            muscle_group=exercise.muscle_group,
            is_custom=exercise.is_custom,
            created_by=exercise.created_by,
            photo_url=exercise_photo_url(exercise.id, exercise.photo_filename),
        ),
        pr=pr,
        history=history,
    )
