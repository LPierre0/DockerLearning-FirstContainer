from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Workout, Boost
from schemas import DashboardOut, DashboardUser
from routers.users import compute_stats
from routers.workouts import _workout_to_out
from routers.boosts import _boost_to_out

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    users = db.query(User).all()
    dashboard_users = []
    for user in users:
        stats = compute_stats(user.id, db)
        recent_workouts = (
            db.query(Workout)
            .filter(Workout.user_id == user.id, Workout.completed_at.isnot(None))
            .order_by(Workout.completed_at.desc())
            .limit(3)
            .all()
        )
        dashboard_users.append(DashboardUser(
            id=user.id,
            name=user.name,
            theme_key=user.theme_key,
            stats=stats,
            recent_workouts=[_workout_to_out(w) for w in recent_workouts],
        ))

    recent_boosts = (
        db.query(Boost)
        .order_by(Boost.sent_at.desc())
        .limit(5)
        .all()
    )

    return DashboardOut(
        users=dashboard_users,
        recent_boosts=[_boost_to_out(b) for b in recent_boosts],
    )
