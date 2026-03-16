from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import BodyMeasurement, User
from schemas import BodyMeasurementCreate, BodyMeasurementOut

router = APIRouter(prefix="/body-measurements", tags=["body-measurements"])


@router.get("", response_model=list[BodyMeasurementOut])
def get_body_measurements(user_id: int, limit: int = 120, db: Session = Depends(get_db)):
    return (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.logged_at.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=BodyMeasurementOut, status_code=201)
def log_body_measurement(payload: BodyMeasurementCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    logged_at = payload.logged_at or datetime.utcnow()
    day_str = logged_at.date().isoformat()
    existing = (
        db.query(BodyMeasurement)
        .filter(
            BodyMeasurement.user_id == payload.user_id,
            func.date(BodyMeasurement.logged_at) == day_str,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Measurement already logged for this date")

    entry = BodyMeasurement(
        user_id=payload.user_id,
        chest_cm=payload.chest_cm,
        waist_cm=payload.waist_cm,
        hips_cm=payload.hips_cm,
        arm_cm=payload.arm_cm,
        thigh_cm=payload.thigh_cm,
        calf_cm=payload.calf_cm,
        logged_at=logged_at,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=200)
def delete_body_measurement(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(BodyMeasurement).filter(BodyMeasurement.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"ok": True}
