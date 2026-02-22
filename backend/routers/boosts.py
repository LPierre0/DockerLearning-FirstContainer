from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Boost, User
from schemas import BoostOut, BoostCreate

router = APIRouter(prefix="/boosts", tags=["boosts"])


def _boost_to_out(b: Boost) -> BoostOut:
    return BoostOut(
        id=b.id,
        from_user_id=b.from_user_id,
        from_name=b.sender.name,
        message=b.message,
        sent_at=b.sent_at,
        read_at=b.read_at,
    )


@router.get("/{user_id}", response_model=list[BoostOut])
def get_boosts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    boosts = (
        db.query(Boost)
        .filter(Boost.to_user_id == user_id)
        .order_by(Boost.read_at.asc().nullsfirst(), Boost.sent_at.desc())
        .limit(20)
        .all()
    )
    return [_boost_to_out(b) for b in boosts]


@router.post("", response_model=BoostOut, status_code=201)
def send_boost(payload: BoostCreate, db: Session = Depends(get_db)):
    sender = db.query(User).filter(User.id == payload.from_user_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    recipient = db.query(User).filter(User.id == payload.to_user_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    boost = Boost(
        from_user_id=payload.from_user_id,
        to_user_id=payload.to_user_id,
        message=payload.message,
    )
    db.add(boost)
    db.commit()
    db.refresh(boost)
    return _boost_to_out(boost)


@router.patch("/{boost_id}/read", response_model=BoostOut)
def mark_boost_read(boost_id: int, db: Session = Depends(get_db)):
    boost = db.query(Boost).filter(Boost.id == boost_id).first()
    if not boost:
        raise HTTPException(status_code=404, detail="Boost not found")
    boost.read_at = datetime.utcnow()
    db.commit()
    db.refresh(boost)
    return _boost_to_out(boost)
