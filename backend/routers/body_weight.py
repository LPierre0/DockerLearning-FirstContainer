from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import BodyWeight, User
from schemas import BodyWeightOut, BodyWeightCreate

router = APIRouter(prefix="/body-weight", tags=["body-weight"])


@router.get("", response_model=list[BodyWeightOut])
def get_body_weights(user_id: int, limit: int = 90, db: Session = Depends(get_db)):
    entries = (
        db.query(BodyWeight)
        .filter(BodyWeight.user_id == user_id)
        .order_by(BodyWeight.logged_at.desc())
        .limit(limit)
        .all()
    )
    return entries


@router.post("", response_model=BodyWeightOut, status_code=201)
def log_body_weight(payload: BodyWeightCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    entry = BodyWeight(
        user_id=payload.user_id,
        weight_kg=payload.weight_kg,
        logged_at=payload.logged_at or datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=200)
def delete_body_weight(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(BodyWeight).filter(BodyWeight.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"ok": True}
