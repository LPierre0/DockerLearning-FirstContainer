from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import FavoriteTemplate, User
from schemas import FavoriteOut, FavoriteCreate

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteOut])
def get_favorites(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(FavoriteTemplate)
        .filter(FavoriteTemplate.user_id == user_id)
        .order_by(FavoriteTemplate.created_at.asc())
        .all()
    )


@router.post("", response_model=FavoriteOut, status_code=201)
def create_favorite(payload: FavoriteCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    fav = FavoriteTemplate(
        user_id=payload.user_id,
        name=payload.name,
        workout_type=payload.workout_type,
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


@router.delete("/{favorite_id}", status_code=200)
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    fav = db.query(FavoriteTemplate).filter(FavoriteTemplate.id == favorite_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(fav)
    db.commit()
    return {"ok": True}
