from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import WorkoutSet, Exercise
from routers.exercises import exercise_photo_url
from schemas import SetOut, SetUpdate

router = APIRouter(prefix="/sets", tags=["sets"])


def _set_to_out(s: WorkoutSet) -> SetOut:
    return SetOut(
        id=s.id,
        workout_id=s.workout_id,
        exercise_id=s.exercise_id,
        exercise_name=s.exercise.name,
        exercise_muscle_group=s.exercise.muscle_group,
        exercise_photo_url=exercise_photo_url(s.exercise_id, s.exercise.photo_filename),
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


@router.patch("/{set_id}", response_model=SetOut)
def update_set(set_id: int, payload: SetUpdate, db: Session = Depends(get_db)):
    ws = db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Set not found")
    if payload.weight_kg is not None:
        ws.weight_kg = payload.weight_kg
    if payload.reps is not None:
        ws.reps = payload.reps
    if payload.rpe is not None:
        ws.rpe = payload.rpe
    if payload.duration_seconds is not None:
        ws.duration_seconds = payload.duration_seconds
    if payload.resistance is not None:
        ws.resistance = payload.resistance
    if payload.calories is not None:
        ws.calories = payload.calories
    if payload.notes is not None:
        ws.notes = payload.notes
    if payload.status is not None:
        ws.status = payload.status
    db.commit()
    db.refresh(ws)
    return _set_to_out(ws)


@router.delete("/{set_id}", status_code=200)
def delete_set(set_id: int, db: Session = Depends(get_db)):
    ws = db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="Set not found")
    db.delete(ws)
    db.commit()
    return {"ok": True}
