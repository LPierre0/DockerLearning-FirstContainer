from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Workout, WorkoutSet
from schemas import UserOut, UserStats, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def compute_stats(user_id: int, db: Session) -> UserStats:
    total_workouts = (
        db.query(Workout)
        .filter(Workout.user_id == user_id, Workout.completed_at.isnot(None))
        .count()
    )
    total_sets = (
        db.query(WorkoutSet)
        .join(Workout)
        .filter(Workout.user_id == user_id, WorkoutSet.status == "done")
        .count()
    )

    # Streak: consecutive days with at least one completed workout, from today backwards
    completed_dates = (
        db.query(func.date(Workout.completed_at))
        .filter(Workout.user_id == user_id, Workout.completed_at.isnot(None))
        .distinct()
        .order_by(func.date(Workout.completed_at).desc())
        .all()
    )
    date_set = {row[0] for row in completed_dates}

    current_streak = 0
    longest_streak = 0
    streak = 0
    check_date = date.today()

    # Allow today or yesterday as the start of a streak
    if str(check_date) not in date_set and str(check_date - timedelta(days=1)) in date_set:
        check_date = check_date - timedelta(days=1)

    while str(check_date) in date_set:
        streak += 1
        check_date -= timedelta(days=1)

    current_streak = streak

    # Longest streak (scan all dates)
    if date_set:
        sorted_dates = sorted(date_set)
        s = 1
        max_s = 1
        for i in range(1, len(sorted_dates)):
            d1 = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date() if isinstance(sorted_dates[i - 1], str) else sorted_dates[i - 1]
            d2 = datetime.strptime(sorted_dates[i], "%Y-%m-%d").date() if isinstance(sorted_dates[i], str) else sorted_dates[i]
            if (d2 - d1).days == 1:
                s += 1
                max_s = max(max_s, s)
            else:
                s = 1
        longest_streak = max_s

    last_workout = (
        db.query(Workout)
        .filter(Workout.user_id == user_id, Workout.completed_at.isnot(None))
        .order_by(Workout.completed_at.desc())
        .first()
    )

    return UserStats(
        total_workouts=total_workouts,
        total_sets=total_sets,
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_workout_at=last_workout.completed_at if last_workout else None,
    )


@router.get("", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}/stats", response_model=UserStats)
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return compute_stats(user_id, db)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.target_weight_kg is not None:
        user.target_weight_kg = payload.target_weight_kg
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/activity")
def get_user_activity(user_id: int, days: int = 91, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(func.date(Workout.completed_at), func.count(Workout.id))
        .filter(
            Workout.user_id == user_id,
            Workout.completed_at.isnot(None),
            Workout.completed_at >= since,
        )
        .group_by(func.date(Workout.completed_at))
        .all()
    )
    return {str(row[0]): row[1] for row in rows}
