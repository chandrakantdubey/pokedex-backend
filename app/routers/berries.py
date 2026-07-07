from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, dependencies

router = APIRouter(
    prefix="/berries",
    tags=["berries"],
)

@router.get("/", response_model=List[schemas.BerryBase])
def read_berries(db: Session = Depends(dependencies.get_db)):
    return crud.get_berries(db)

@router.get("/plots", response_model=List[schemas.UserBerryPlotDisplay])
def get_plots(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.get_user_plots(db, current_user.id)

@router.post("/plant", response_model=schemas.UserBerryPlotDisplay)
def plant_berry(request: schemas.PlantBerryRequest, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    plot = crud.plant_berry(db, current_user.id, request.plot_id, request.berry_id)
    if not plot:
        raise HTTPException(status_code=400, detail="Failed to plant berry. Check plot status and inventory.")
    return plot
