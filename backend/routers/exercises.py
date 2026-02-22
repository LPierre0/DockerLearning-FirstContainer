from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Exercise, User
from schemas import ExerciseOut, ExerciseCreate

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseOut])
def get_exercises(user_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Exercise).filter(Exercise.is_custom == False)
    if user_id:
        custom = db.query(Exercise).filter(
            Exercise.is_custom == True,
            Exercise.created_by == user_id,
        )
        return query.all() + custom.all()
    return query.all()


@router.post("", response_model=ExerciseOut, status_code=201)
def create_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.created_by).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    exercise = Exercise(
        name=payload.name,
        muscle_group=payload.muscle_group,
        is_custom=True,
        created_by=payload.created_by,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}", status_code=200)
def delete_exercise(exercise_id: int, user_id: int, db: Session = Depends(get_db)):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if not exercise.is_custom:
        raise HTTPException(status_code=403, detail="Cannot delete predefined exercises")
    if exercise.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not your exercise")
    db.delete(exercise)
    db.commit()
    return {"ok": True}
