from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Exercise, User, Workout, WorkoutSet
from schemas import ExerciseCreate, ExerciseOut

router = APIRouter(prefix="/exercises", tags=["exercises"])

BASE_DIR = Path(__file__).resolve().parents[1]
PHOTO_DIR = BASE_DIR / "data" / "exercise_photos"
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

MAX_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
EXT_MEDIA_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def exercise_photo_url(exercise_id: int, photo_filename: str | None) -> str | None:
    if not photo_filename:
        return None
    return f"/api/exercises/{exercise_id}/photo"


def exercise_to_out(
    exercise: Exercise,
    usage_count_by_exercise: dict[int, int] | None = None,
) -> ExerciseOut:
    usage_count = 0
    if usage_count_by_exercise is not None:
        usage_count = usage_count_by_exercise.get(exercise.id, 0)
    return ExerciseOut(
        id=exercise.id,
        name=exercise.name,
        muscle_group=exercise.muscle_group,
        is_custom=exercise.is_custom,
        created_by=exercise.created_by,
        photo_url=exercise_photo_url(exercise.id, exercise.photo_filename),
        usage_count=usage_count,
    )


def _get_user(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _get_exercise(exercise_id: int, db: Session) -> Exercise:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


def _assert_can_edit_photo(exercise: Exercise, user_id: int):
    if exercise.is_custom and exercise.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not your exercise")


def _delete_photo_file(filename: str | None):
    if not filename:
        return
    file_path = PHOTO_DIR / filename
    if file_path.exists():
        file_path.unlink()


def _usage_count_by_exercise(db: Session, user_id: int) -> dict[int, int]:
    rows = (
        db.query(WorkoutSet.exercise_id, func.count(WorkoutSet.id))
        .join(Workout, WorkoutSet.workout_id == Workout.id)
        .filter(Workout.user_id == user_id)
        .group_by(WorkoutSet.exercise_id)
        .all()
    )
    return {exercise_id: count for exercise_id, count in rows}


@router.get("", response_model=list[ExerciseOut])
def get_exercises(user_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Exercise).filter(Exercise.is_custom == False)
    if user_id:
        usage_map = _usage_count_by_exercise(db, user_id)
        custom = db.query(Exercise).filter(
            Exercise.is_custom == True,
            Exercise.created_by == user_id,
        )
        return [exercise_to_out(e, usage_map) for e in query.all() + custom.all()]
    return [exercise_to_out(e) for e in query.all()]


@router.post("", response_model=ExerciseOut, status_code=201)
def create_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)):
    _get_user(payload.created_by, db)
    exercise = Exercise(
        name=payload.name,
        muscle_group=payload.muscle_group,
        is_custom=True,
        created_by=payload.created_by,
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise_to_out(exercise)


@router.get("/{exercise_id}/photo")
def get_exercise_photo(exercise_id: int, db: Session = Depends(get_db)):
    exercise = _get_exercise(exercise_id, db)
    if not exercise.photo_filename:
        raise HTTPException(status_code=404, detail="Photo not found")

    photo_path = PHOTO_DIR / exercise.photo_filename
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")

    ext = photo_path.suffix.lower()
    media_type = EXT_MEDIA_TYPE.get(ext, "application/octet-stream")
    return FileResponse(photo_path, media_type=media_type)


@router.post("/{exercise_id}/photo", response_model=ExerciseOut, status_code=201)
async def upload_exercise_photo(
    exercise_id: int,
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _get_user(user_id, db)
    exercise = _get_exercise(exercise_id, db)
    _assert_can_edit_photo(exercise, user_id)

    content_type = (file.content_type or "").lower()
    ext = ALLOWED_CONTENT_TYPES.get(content_type)
    if not ext:
        raise HTTPException(status_code=422, detail="Only JPEG, PNG and WEBP are supported")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=422, detail="Empty file")
    if len(file_bytes) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=422, detail="File too large (max 5MB)")

    _delete_photo_file(exercise.photo_filename)

    filename = f"exercise_{exercise.id}_{uuid4().hex}{ext}"
    photo_path = PHOTO_DIR / filename
    photo_path.write_bytes(file_bytes)

    exercise.photo_filename = filename
    db.commit()
    db.refresh(exercise)
    return exercise_to_out(exercise)


@router.delete("/{exercise_id}/photo", response_model=ExerciseOut)
def delete_exercise_photo(exercise_id: int, user_id: int, db: Session = Depends(get_db)):
    _get_user(user_id, db)
    exercise = _get_exercise(exercise_id, db)
    _assert_can_edit_photo(exercise, user_id)

    _delete_photo_file(exercise.photo_filename)
    exercise.photo_filename = None
    db.commit()
    db.refresh(exercise)
    return exercise_to_out(exercise)


@router.delete("/{exercise_id}", status_code=200)
def delete_exercise(exercise_id: int, user_id: int, db: Session = Depends(get_db)):
    exercise = _get_exercise(exercise_id, db)
    if not exercise.is_custom:
        raise HTTPException(status_code=403, detail="Cannot delete predefined exercises")
    if exercise.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not your exercise")
    _delete_photo_file(exercise.photo_filename)
    db.delete(exercise)
    db.commit()
    return {"ok": True}
