from datetime import datetime
import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Workout, WorkoutSet, Exercise, User
from schemas import (
    WorkoutOut, WorkoutDetail, WorkoutCreate, WorkoutUpdate,
    SetOut, SetCreate,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _workout_to_out(w: Workout) -> WorkoutOut:
    exercise_ids = {s.exercise_id for s in w.sets}
    return WorkoutOut(
        id=w.id,
        user_id=w.user_id,
        type=w.type,
        name=w.name,
        notes=w.notes,
        started_at=w.started_at,
        completed_at=w.completed_at,
        set_count=len(w.sets),
        exercise_count=len(exercise_ids),
    )


def _set_to_out(s: WorkoutSet) -> SetOut:
    return SetOut(
        id=s.id,
        workout_id=s.workout_id,
        exercise_id=s.exercise_id,
        exercise_name=s.exercise.name,
        exercise_muscle_group=s.exercise.muscle_group,
        set_number=s.set_number,
        weight_kg=s.weight_kg,
        reps=s.reps,
        rpe=s.rpe,
        duration_seconds=s.duration_seconds,
        resistance=s.resistance,
        calories=s.calories,
        notes=s.notes,
        status=s.status,
        logged_at=s.logged_at,
    )


@router.get("", response_model=list[WorkoutOut])
def get_workouts(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == user_id)
        .order_by(Workout.started_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_workout_to_out(w) for w in workouts]


@router.post("", response_model=WorkoutOut, status_code=201)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    workout = Workout(
        user_id=payload.user_id,
        type=payload.type,
        name=payload.name,
    )
    db.add(workout)
    db.flush()  # get workout.id before commit

    if payload.template_id:
        template = db.query(Workout).filter(Workout.id == payload.template_id).first()
        if template:
            for s in sorted(template.sets, key=lambda x: (x.exercise_id, x.set_number)):
                copied = WorkoutSet(
                    workout_id=workout.id,
                    exercise_id=s.exercise_id,
                    set_number=s.set_number,
                    weight_kg=s.weight_kg,
                    reps=s.reps,
                    rpe=s.rpe,
                    duration_seconds=s.duration_seconds,
                    resistance=s.resistance,
                    calories=s.calories,
                    status="pending",
                )
                db.add(copied)

    db.commit()
    db.refresh(workout)
    return _workout_to_out(workout)


@router.get("/last", response_model=WorkoutDetail)
def get_last_workout(user_id: int, type: str, db: Session = Depends(get_db)):
    workout = (
        db.query(Workout)
        .filter(
            Workout.user_id == user_id,
            Workout.type == type,
            Workout.completed_at.isnot(None),
        )
        .order_by(Workout.started_at.desc())
        .first()
    )
    if not workout:
        raise HTTPException(status_code=404, detail="No previous workout of this type")
    return WorkoutDetail(
        id=workout.id,
        user_id=workout.user_id,
        type=workout.type,
        name=workout.name,
        notes=workout.notes,
        started_at=workout.started_at,
        completed_at=workout.completed_at,
        sets=[_set_to_out(s) for s in sorted(workout.sets, key=lambda x: (x.exercise_id, x.set_number))],
    )


@router.get("/export")
def export_workouts(user_id: int, db: Session = Depends(get_db)):
    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == user_id, Workout.completed_at.isnot(None))
        .order_by(Workout.completed_at.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "type", "exercise", "set", "weight_kg", "reps", "rpe", "duration_min", "resistance", "calories", "status"])
    for w in workouts:
        for s in sorted(w.sets, key=lambda x: (x.exercise_id, x.set_number)):
            writer.writerow([
                w.completed_at.strftime("%Y-%m-%d") if w.completed_at else "",
                w.type,
                s.exercise.name,
                s.set_number,
                s.weight_kg or "",
                s.reps or "",
                s.rpe or "",
                round(s.duration_seconds / 60, 1) if s.duration_seconds else "",
                s.resistance or "",
                s.calories or "",
                s.status,
            ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=workouts.csv"},
    )


@router.get("/{workout_id}/previous", response_model=WorkoutDetail)
def get_previous_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    previous = (
        db.query(Workout)
        .filter(
            Workout.user_id == workout.user_id,
            Workout.type == workout.type,
            Workout.completed_at.isnot(None),
            Workout.id != workout_id,
            Workout.started_at < workout.started_at,
        )
        .order_by(Workout.started_at.desc())
        .first()
    )
    if not previous:
        raise HTTPException(status_code=404, detail="No previous workout of this type")
    return WorkoutDetail(
        id=previous.id,
        user_id=previous.user_id,
        type=previous.type,
        name=previous.name,
        notes=previous.notes,
        started_at=previous.started_at,
        completed_at=previous.completed_at,
        sets=[_set_to_out(s) for s in sorted(previous.sets, key=lambda x: (x.exercise_id, x.set_number))],
    )


@router.get("/{workout_id}", response_model=WorkoutDetail)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return WorkoutDetail(
        id=workout.id,
        user_id=workout.user_id,
        type=workout.type,
        name=workout.name,
        notes=workout.notes,
        started_at=workout.started_at,
        completed_at=workout.completed_at,
        sets=[_set_to_out(s) for s in sorted(workout.sets, key=lambda x: (x.exercise_id, x.set_number))],
    )


@router.patch("/{workout_id}", response_model=WorkoutOut)
def update_workout(workout_id: int, payload: WorkoutUpdate, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if payload.completed_at is not None:
        workout.completed_at = payload.completed_at
    if payload.notes is not None:
        workout.notes = payload.notes
    if payload.name is not None:
        workout.name = payload.name
    db.commit()
    db.refresh(workout)
    return _workout_to_out(workout)


@router.delete("/{workout_id}", status_code=200)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
    return {"ok": True}


@router.post("/{workout_id}/sets", response_model=SetOut, status_code=201)
def add_set(workout_id: int, payload: SetCreate, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    exercise = db.query(Exercise).filter(Exercise.id == payload.exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    ws = WorkoutSet(
        workout_id=workout_id,
        exercise_id=payload.exercise_id,
        set_number=payload.set_number,
        weight_kg=payload.weight_kg,
        reps=payload.reps,
        rpe=payload.rpe,
        duration_seconds=payload.duration_seconds,
        resistance=payload.resistance,
        calories=payload.calories,
        status=payload.status,
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return _set_to_out(ws)
