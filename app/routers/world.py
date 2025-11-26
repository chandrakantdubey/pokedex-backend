from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, dependencies

router = APIRouter(
    prefix="/world",
    tags=["world"],
)

@router.get("/gyms", response_model=List[schemas.Gym])
def read_gyms(db: Session = Depends(dependencies.get_db)):
    return crud.get_gyms(db)

@router.get("/elite-four", response_model=List[schemas.EliteFourMember])
def read_elite_four(db: Session = Depends(dependencies.get_db)):
    return crud.get_elite_four(db)

@router.post("/gyms/{gym_id}/challenge", response_model=schemas.UserBadge)
def challenge_gym(gym_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    gym = crud.get_gym(db, gym_id=gym_id)
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")
    
    return crud.add_user_badge(db=db, user_id=current_user.id, gym_id=gym_id)

@router.get("/my-badges", response_model=List[schemas.UserBadge])
def read_my_badges(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.get_user_badges(db, user_id=current_user.id)
